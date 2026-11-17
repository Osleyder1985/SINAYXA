"""PostgreSQL integration tests for the Issue #2 event registry."""
from __future__ import annotations

import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import psycopg

from scripts.news_and_events.event_registry import (
    EventRegistryError,
    add_source_reference,
    append_conflict_decision,
    append_temporal_assertion,
    connect,
    create_event,
    create_temporal_conflict,
    get_conflict_history,
    get_event_as_of,
    get_event_history,
    initialize_database,
)


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


@unittest.skipUnless(os.environ.get("SINAYXA_DATABASE_URL"), "PostgreSQL integration database is not configured")
class EventRegistryIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.connection = connect()
        initialize_database(cls.connection)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.connection.close()

    def test_append_versions_and_query_historical_cutoff(self) -> None:
        event_id = f"event-{uuid4().hex}"
        now = datetime.now(timezone.utc).replace(microsecond=0)
        created_at = iso(now - timedelta(minutes=5))
        event = {
            "event_id": event_id,
            "description": "Synthetic scheduled protocol event for integration testing.",
            "affected_asset_refs": ["asset-btc"],
            "source_refs": ["source-calendar-a"],
            "created_at": created_at,
        }
        create_event(self.connection, event)

        first = {
            "temporal_assertion_id": f"{event_id}-v1",
            "event_id": event_id,
            "version": 1,
            "temporal_role": "SCHEDULED",
            "precision": "DAY",
            "interval_start": {"value": iso(now + timedelta(days=4)), "inclusive": True},
            "interval_end": {"value": iso(now + timedelta(days=4, hours=23, minutes=59, seconds=59)), "inclusive": True},
            "approximation": False,
            "original_value": "Synthetic event scheduled in four days",
            "original_timezone": "UTC",
            "original_offset": "+00:00",
            "normalized_start_utc": iso(now + timedelta(days=4)),
            "normalized_end_utc": iso(now + timedelta(days=4, hours=23, minutes=59, seconds=59)),
            "source_ref": "source-calendar-a",
            "evidence_ref": "evidence-calendar-a",
            "retrieved_at": iso(now - timedelta(minutes=3)),
            "recorded_at": iso(now - timedelta(minutes=2)),
            "supersedes_assertion_id": None,
            "published_at": iso(now - timedelta(minutes=4)),
            "first_observed_at": iso(now - timedelta(minutes=3, seconds=30)),
        }
        first["recorded_at"] = iso(datetime.now(timezone.utc))
        append_temporal_assertion(self.connection, first)
        source_b_recorded_at = add_source_reference(
            self.connection, event_id, "source-calendar-b"
        )

        second = {
            **first,
            "temporal_assertion_id": f"{event_id}-v2",
            "version": 2,
            "temporal_role": "ESTIMATED",
            "precision": "RANGE",
            "interval_start": {"value": iso(now + timedelta(days=5)), "inclusive": True},
            "interval_end": {"value": iso(now + timedelta(days=7, hours=23, minutes=59, seconds=59)), "inclusive": True},
            "approximation": True,
            "original_value": "Synthetic event moved to an estimated five-to-seven-day window",
            "original_timezone": None,
            "original_offset": None,
            "normalized_start_utc": iso(now + timedelta(days=5)),
            "normalized_end_utc": iso(now + timedelta(days=7, hours=23, minutes=59, seconds=59)),
            "source_ref": "source-calendar-b",
            "evidence_ref": "evidence-calendar-b",
            "retrieved_at": iso(source_b_recorded_at + timedelta(microseconds=3)),
            # Deliberately backdated client input must not control registry knowledge time.\n            "recorded_at": iso(source_b_recorded_at - timedelta(microseconds=1)),
            "supersedes_assertion_id": first["temporal_assertion_id"],
            "published_at": iso(source_b_recorded_at + timedelta(microseconds=1)),
            "first_observed_at": iso(source_b_recorded_at + timedelta(microseconds=2)),
        }
        append_temporal_assertion(self.connection, second)
        stored_second = self.connection.execute(
            """
            SELECT assertion_payload
            FROM sinayxa.temporal_assertions
            WHERE temporal_assertion_id = %s
            """,
            (second["temporal_assertion_id"],),
        ).fetchone()[0]
        stored_recorded_at = datetime.fromisoformat(
            stored_second["recorded_at"].replace("Z", "+00:00")
        )
        self.assertGreaterEqual(stored_recorded_at, source_b_recorded_at)

        historical = get_event_as_of(
            self.connection, event_id, iso(source_b_recorded_at - timedelta(microseconds=1))
        )
        current = get_event_as_of(
            self.connection, event_id, iso(datetime.now(timezone.utc) + timedelta(seconds=1))
        )
        self.assertIsNotNone(historical)
        self.assertEqual([1], [item["version"] for item in historical["temporal_assertions"]])
        self.assertEqual(["source-calendar-a"], historical["event"]["source_refs"])
        self.assertEqual([1, 2], [item["version"] for item in current["temporal_assertions"]])
        self.assertEqual(
            ["source-calendar-a", "source-calendar-b"],
            current["event"]["source_refs"],
        )
        self.assertEqual(2, len(get_event_history(self.connection, event_id)))

    def test_version_gap_is_rejected_without_mutating_history(self) -> None:
        event_id = f"event-{uuid4().hex}"
        now = datetime.now(timezone.utc).replace(microsecond=0)
        event = {
            "event_id": event_id,
            "description": "Synthetic event for rejected version-gap test.",
            "affected_asset_refs": [],
            "source_refs": ["source-a"],
            "created_at": iso(now - timedelta(minutes=1)),
        }
        create_event(self.connection, event)
        invalid = {
            "temporal_assertion_id": f"{event_id}-v2",
            "event_id": event_id,
            "version": 2,
            "temporal_role": "UNKNOWN",
            "precision": "UNKNOWN",
            "interval_start": {"value": None, "inclusive": False},
            "interval_end": {"value": None, "inclusive": False},
            "approximation": False,
            "original_value": None,
            "original_timezone": None,
            "original_offset": None,
            "normalized_start_utc": None,
            "normalized_end_utc": None,
            "source_ref": None,
            "evidence_ref": None,
            "retrieved_at": None,
            "recorded_at": iso(now + timedelta(minutes=1)),
            "supersedes_assertion_id": None,
            "published_at": None,
            "first_observed_at": None,
        }
        with self.assertRaises(EventRegistryError):
            append_temporal_assertion(self.connection, invalid)
        self.assertEqual([], get_event_history(self.connection, event_id))

    def test_registry_rejects_updates_to_event_identity(self) -> None:
        event_id = f"event-{uuid4().hex}"
        now = datetime.now(timezone.utc).replace(microsecond=0)
        create_event(
            self.connection,
            {
                "event_id": event_id,
                "description": "Synthetic immutable event identity.",
                "affected_asset_refs": [],
                "source_refs": [],
                "created_at": iso(now),
            },
        )
        with self.assertRaises(psycopg.Error):
            with self.connection.transaction():
                self.connection.execute(
                    "UPDATE sinayxa.events SET description = 'rewritten' WHERE event_id = %s",
                    (event_id,),
                )


    def test_migration_is_idempotent(self) -> None:
        initialize_database(self.connection)
        initialize_database(self.connection)
        migration_count = self.connection.execute(
            """
            SELECT count(*)
            FROM sinayxa.schema_migrations
            WHERE migration_id IN ('issue-2-event-registry-0001', 'issue-2-temporal-conflicts-0002')
            """
        ).fetchone()[0]
        trigger_count = self.connection.execute(
            """
            SELECT count(*)
            FROM pg_trigger
            WHERE tgname IN (
                'events_append_only',
                'event_sources_append_only',
                'temporal_assertions_append_only',
                'temporal_conflicts_append_only',
                'conflict_decisions_append_only'
            )
              AND NOT tgisinternal
            """
        ).fetchone()[0]
        self.assertEqual(2, migration_count)
        self.assertEqual(5, trigger_count)
        defaults = self.connection.execute(
            """
            SELECT relation.relname, attribute.attname, pg_get_expr(definition.adbin, definition.adrelid)
            FROM pg_attrdef AS definition
            JOIN pg_class AS relation ON relation.oid = definition.adrelid
            JOIN pg_namespace AS namespace ON namespace.oid = relation.relnamespace
            JOIN pg_attribute AS attribute
              ON attribute.attrelid = relation.oid
             AND attribute.attnum = definition.adnum
            WHERE namespace.nspname = 'sinayxa'
              AND (relation.relname, attribute.attname) IN (
                  ('events', 'inserted_at'),
                  ('event_sources', 'recorded_at'),
                  ('event_sources', 'inserted_at'),
                  ('temporal_assertions', 'inserted_at'),
                  ('temporal_conflicts', 'inserted_at'),
                  ('conflict_decisions', 'inserted_at')
              )
            """
        ).fetchall()
        self.assertEqual(6, len(defaults))
        self.assertTrue(
            all(expression == "clock_timestamp()" for _, _, expression in defaults),
            defaults,
        )

    def test_registry_rejects_update_and_delete_for_all_append_only_tables(self) -> None:
        event_id = f"event-{uuid4().hex}"
        now = datetime.now(timezone.utc)
        create_event(
            self.connection,
            {
                "event_id": event_id,
                "description": "Synthetic event for append-only enforcement coverage.",
                "affected_asset_refs": [],
                "source_refs": [],
                "created_at": iso(now - timedelta(minutes=1)),
            },
        )
        add_source_reference(self.connection, event_id, "source-append-only")
        assertion = {
            "temporal_assertion_id": f"{event_id}-v1",
            "event_id": event_id,
            "version": 1,
            "temporal_role": "UNKNOWN",
            "precision": "UNKNOWN",
            "interval_start": {"value": None, "inclusive": False},
            "interval_end": {"value": None, "inclusive": False},
            "approximation": False,
            "original_value": None,
            "original_timezone": None,
            "original_offset": None,
            "normalized_start_utc": None,
            "normalized_end_utc": None,
            "source_ref": None,
            "evidence_ref": None,
            "retrieved_at": None,
            "recorded_at": iso(now + timedelta(seconds=1)),
            "supersedes_assertion_id": None,
            "published_at": None,
            "first_observed_at": None,
        }
        append_temporal_assertion(self.connection, assertion)

        mutations = [
            (
                "UPDATE sinayxa.events SET description = 'rewritten' WHERE event_id = %s",
                (event_id,),
            ),
            ("DELETE FROM sinayxa.events WHERE event_id = %s", (event_id,)),
            (
                """
                UPDATE sinayxa.event_sources
                SET source_ref = 'rewritten'
                WHERE event_id = %s AND source_ref = 'source-append-only'
                """,
                (event_id,),
            ),
            (
                "DELETE FROM sinayxa.event_sources WHERE event_id = %s",
                (event_id,),
            ),
            (
                """
                UPDATE sinayxa.temporal_assertions
                SET original_value = 'rewritten'
                WHERE event_id = %s
                """,
                (event_id,),
            ),
            (
                "DELETE FROM sinayxa.temporal_assertions WHERE event_id = %s",
                (event_id,),
            ),
        ]
        for statement, parameters in mutations:
            with self.subTest(statement=statement.split()[0:3]):
                with self.assertRaises(psycopg.Error):
                    with self.connection.transaction():
                        self.connection.execute(statement, parameters)

    def test_concurrent_writers_cannot_append_the_same_version(self) -> None:
        event_id = f"event-{uuid4().hex}"
        now = datetime.now(timezone.utc)
        create_event(
            self.connection,
            {
                "event_id": event_id,
                "description": "Synthetic event for concurrent version assignment.",
                "affected_asset_refs": [],
                "source_refs": [],
                "created_at": iso(now - timedelta(minutes=1)),
            },
        )
        # Publish the fixture before independent writer connections begin.
        self.connection.commit()
        barrier = Barrier(2)
        recorded_at = iso(now + timedelta(minutes=1))

        def append_from_independent_connection(index: int) -> str:
            assertion = {
                "temporal_assertion_id": f"{event_id}-writer-{index}",
                "event_id": event_id,
                "version": 1,
                "temporal_role": "UNKNOWN",
                "precision": "UNKNOWN",
                "interval_start": {"value": None, "inclusive": False},
                "interval_end": {"value": None, "inclusive": False},
                "approximation": False,
                "original_value": None,
                "original_timezone": None,
                "original_offset": None,
                "normalized_start_utc": None,
                "normalized_end_utc": None,
                "source_ref": None,
                "evidence_ref": None,
                "retrieved_at": None,
                "recorded_at": recorded_at,
                "supersedes_assertion_id": None,
                "published_at": None,
                "first_observed_at": None,
            }
            with connect() as connection:
                barrier.wait(timeout=15)
                try:
                    append_temporal_assertion(connection, assertion)
                except EventRegistryError as exc:
                    return f"rejected: {exc}"
                return "accepted"

        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(executor.map(append_from_independent_connection, (1, 2)))

        self.assertEqual(1, outcomes.count("accepted"), outcomes)
        rejected = [outcome for outcome in outcomes if outcome.startswith("rejected:")]
        self.assertEqual(1, len(rejected), outcomes)
        self.assertIn("contiguous", rejected[0], outcomes)
        history = get_event_history(self.connection, event_id)
        self.assertEqual(1, len(history))
        self.assertEqual(1, history[0]["version"])



    def test_conflict_decision_lifecycle_and_historical_registry_cutoff(self) -> None:
        event_id = f"event-{uuid4().hex}"
        now = datetime.now(timezone.utc)
        create_event(
            self.connection,
            {
                "event_id": event_id,
                "description": "Synthetic event for temporal conflict lifecycle testing.",
                "affected_asset_refs": ["asset-synthetic"],
                "source_refs": [],
                "created_at": iso(now - timedelta(minutes=2)),
            },
        )
        self.connection.commit()

        first = {
            "temporal_assertion_id": f"{event_id}-assertion-v1",
            "event_id": event_id,
            "version": 1,
            "temporal_role": "UNKNOWN",
            "precision": "UNKNOWN",
            "interval_start": {"value": None, "inclusive": False},
            "interval_end": {"value": None, "inclusive": False},
            "approximation": False,
            "original_value": None,
            "original_timezone": None,
            "original_offset": None,
            "normalized_start_utc": None,
            "normalized_end_utc": None,
            "source_ref": None,
            "evidence_ref": None,
            "retrieved_at": None,
            "recorded_at": iso(datetime.now(timezone.utc)),
            "supersedes_assertion_id": None,
            "published_at": None,
            "first_observed_at": None,
        }
        append_temporal_assertion(self.connection, first)
        second = {
            **first,
            "temporal_assertion_id": f"{event_id}-assertion-v2",
            "version": 2,
            "recorded_at": iso(datetime.now(timezone.utc) + timedelta(microseconds=10)),
            "supersedes_assertion_id": first["temporal_assertion_id"],
        }
        append_temporal_assertion(self.connection, second)

        cutoff_before_conflict = iso(datetime.now(timezone.utc) - timedelta(seconds=1))
        conflict = create_temporal_conflict(
            self.connection,
            {
                "conflict_id": f"conflict-{uuid4().hex}",
                "event_id": event_id,
                "assertion_refs": [
                    first["temporal_assertion_id"],
                    second["temporal_assertion_id"],
                ],
                "disputed_component": "DATE",
                "classification": "DIRECT_CONTRADICTION",
                "status": "OPEN",
            },
        )
        self.assertIsNone(
            get_conflict_history(self.connection, conflict["conflict_id"], cutoff_before_conflict)
        )

        decision_one = {
            "decision_id": f"{conflict['conflict_id']}-decision-1",
            "conflict_id": conflict["conflict_id"],
            "from_status": "OPEN",
            "to_status": "UNDER_REVIEW",
            "assertion_refs": conflict["assertion_refs"],
            "supporting_evidence_refs": [],
            "contrary_evidence_refs": [],
            "scope": "Synthetic temporal date discrepancy only",
            "rationale": "The two recorded assertions require review.",
            "limitations": "No factual conclusion is established by this transition.",
            "actor_ref": "operator-synthetic",
            "decided_at": iso(datetime.now(timezone.utc) + timedelta(seconds=1)),
            "assessment_cutoff": second["recorded_at"],
            "rules_version": "temporal-review-1.0.0",
            "supersedes_decision_id": None,
        }
        append_conflict_decision(self.connection, decision_one)
        after_first = get_conflict_history(self.connection, conflict["conflict_id"])
        self.assertEqual("UNDER_REVIEW", after_first["conflict"]["status"])
        self.assertEqual(1, len(after_first["decisions"]))
        first_decision_cutoff = after_first["decisions"][0]["recorded_in_registry_at"]

        decision_two = {
            "decision_id": f"{conflict['conflict_id']}-decision-2",
            "conflict_id": conflict["conflict_id"],
            "from_status": "UNDER_REVIEW",
            "to_status": "RESOLVED",
            "assertion_refs": conflict["assertion_refs"],
            "supporting_evidence_refs": ["evidence-support-synthetic"],
            "contrary_evidence_refs": ["evidence-contrary-synthetic"],
            "scope": "Resolve only the date component for this synthetic event.",
            "rationale": "The selected evidence supports the recorded resolution within the stated scope.",
            "limitations": "This does not establish market impact or causality.",
            "actor_ref": "operator-synthetic",
            "decided_at": iso(datetime.now(timezone.utc) + timedelta(seconds=2)),
            "assessment_cutoff": second["recorded_at"],
            "rules_version": "temporal-review-1.0.0",
            "supersedes_decision_id": None,
        }
        append_conflict_decision(self.connection, decision_two)
        current = get_conflict_history(self.connection, conflict["conflict_id"])
        historical = get_conflict_history(
            self.connection, conflict["conflict_id"], first_decision_cutoff
        )
        self.assertEqual("RESOLVED", current["conflict"]["status"])
        self.assertEqual(2, len(current["decisions"]))
        self.assertEqual("UNDER_REVIEW", historical["conflict"]["status"])
        self.assertEqual(1, len(historical["decisions"]))

        # A second conflict on the same event must validate against the first
        # conflict's reconstructed RESOLVED state, not its immutable OPEN payload.
        second_conflict = create_temporal_conflict(
            self.connection,
            {
                "conflict_id": f"conflict-{uuid4().hex}",
                "event_id": event_id,
                "assertion_refs": [
                    first["temporal_assertion_id"],
                    second["temporal_assertion_id"],
                ],
                "disputed_component": "INTERVAL",
                "classification": "PRECISION_DIFFERENCE",
                "status": "OPEN",
            },
        )
        self.assertEqual("OPEN", get_conflict_history(
            self.connection, second_conflict["conflict_id"]
        )["conflict"]["status"])

        invalid = {
            **decision_two,
            "decision_id": f"{conflict['conflict_id']}-decision-invalid",
            "from_status": "OPEN",
            "to_status": "UNDER_REVIEW",
            "decided_at": iso(datetime.now(timezone.utc) + timedelta(seconds=3)),
        }
        with self.assertRaises(EventRegistryError):
            append_conflict_decision(self.connection, invalid)
        self.assertEqual(2, len(get_conflict_history(self.connection, conflict["conflict_id"])["decisions"]))

        for statement in (
            "UPDATE sinayxa.temporal_conflicts SET status = 'OPEN' WHERE conflict_id = %s",
            "DELETE FROM sinayxa.temporal_conflicts WHERE conflict_id = %s",
        ):
            with self.assertRaises(psycopg.Error):
                with self.connection.transaction():
                    self.connection.execute(statement, (conflict["conflict_id"],))
        for statement in (
            "UPDATE sinayxa.conflict_decisions SET rationale = 'rewritten' WHERE conflict_id = %s",
            "DELETE FROM sinayxa.conflict_decisions WHERE conflict_id = %s",
        ):
            with self.assertRaises(psycopg.Error):
                with self.connection.transaction():
                    self.connection.execute(statement, (conflict["conflict_id"],))



if __name__ == "__main__":
    unittest.main()
