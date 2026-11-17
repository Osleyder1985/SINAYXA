"""PostgreSQL integration tests for the Issue #2 event registry."""
from __future__ import annotations

import hashlib
import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import psycopg

from scripts.news_and_events.event_registry import (
    EventRegistryError,
    add_source_reference,
    append_conflict_decision,
    append_temporal_assertion,
    connect,
    create_event,
    create_reproducibility_manifest,
    create_temporal_assessment,
    create_temporal_conflict,
    get_conflict_history,
    get_event_as_of,
    get_event_history,
    get_evidence_artifact,
    get_reproducibility_manifest,
    get_source_artifact,
    get_temporal_assessment,
    initialize_database,
    register_evidence_artifact,
    register_source_artifact,
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
            # Deliberately backdated client input must not control registry knowledge time.
            "recorded_at": iso(source_b_recorded_at - timedelta(microseconds=1)),
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
            WHERE migration_id IN ('issue-2-event-registry-0001', 'issue-2-temporal-conflicts-0002', 'issue-2-temporal-assessments-manifests-0003', 'issue-2-source-evidence-artifacts-0004', 'issue-2-append-only-truncate-guard-0005')
            """
        ).fetchone()[0]
        trigger_count = self.connection.execute(
            """
            SELECT count(*)
            FROM pg_trigger
            WHERE tgname IN (
                'events_append_only',
                'events_no_truncate',
                'event_sources_append_only',
                'event_sources_no_truncate',
                'temporal_assertions_append_only',
                'temporal_assertions_no_truncate',
                'temporal_conflicts_append_only',
                'temporal_conflicts_no_truncate',
                'conflict_decisions_append_only',
                'conflict_decisions_no_truncate',
                'temporal_assessments_append_only',
                'temporal_assessments_no_truncate',
                'reproducibility_manifests_append_only',
                'reproducibility_manifests_no_truncate',
                'source_artifacts_append_only',
                'source_artifacts_no_truncate',
                'evidence_artifacts_append_only',
                'evidence_artifacts_no_truncate'
            )
              AND NOT tgisinternal
            """
        ).fetchone()[0]
        self.assertEqual(5, migration_count)
        self.assertEqual(18, trigger_count)
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
                  ('conflict_decisions', 'inserted_at'),
                  ('temporal_assessments', 'inserted_at'),
                  ('reproducibility_manifests', 'inserted_at'),
                  ('source_artifacts', 'inserted_at'),
                  ('evidence_artifacts', 'inserted_at')
              )
            """
        ).fetchall()
        self.assertEqual(10, len(defaults))
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
        second_recorded_at = get_event_history(self.connection, event_id)[-1]["recorded_at"]

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
            "assessment_cutoff": second_recorded_at,
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
            "assessment_cutoff": second_recorded_at,
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



    def test_temporal_assessment_and_manifest_lifecycle(self) -> None:
        event_id = f"event-{uuid4().hex}"
        now = datetime.now(timezone.utc)
        source_ref = f"{event_id}-source"
        evidence_ref = f"{event_id}-evidence"
        register_source_artifact(
            self.connection,
            source_ref,
            b'{"synthetic_source": true}',
            {
                "source_uri": f"urn:sinayxa:synthetic:{source_ref}",
                "title": "Synthetic source artifact",
                "publisher": "SINAYXA test fixture",
                "media_type": "application/json",
                "license_ref": "SYNTHETIC-TEST-DATA",
                "usage_status": "SYNTHETIC",
                "metadata": {"fixture": "temporal-assessment"},
            },
        )
        register_evidence_artifact(
            self.connection,
            evidence_ref,
            b'{"synthetic_evidence": true}',
            {
                "source_ref": source_ref,
                "evidence_type": "SYNTHETIC_EXTRACT",
                "media_type": "application/json",
                "extraction_method": "synthetic-fixture",
                "extraction_version": "1.0.0",
                "license_ref": "SYNTHETIC-TEST-DATA",
                "usage_status": "SYNTHETIC",
                "metadata": {"fixture": "temporal-assessment"},
            },
        )
        create_event(
            self.connection,
            {
                "event_id": event_id,
                "description": "Synthetic event for reproducible temporal assessment.",
                "affected_asset_refs": ["asset-synthetic"],
                "source_refs": [source_ref],
                "created_at": iso(now - timedelta(minutes=2)),
            },
        )
        assertion = {
            "temporal_assertion_id": f"{event_id}-assertion-v1",
            "event_id": event_id,
            "version": 1,
            "temporal_role": "SCHEDULED",
            "precision": "DAY",
            "interval_start": {
                "value": iso(now + timedelta(days=1)),
                "inclusive": True,
            },
            "interval_end": {
                "value": iso(now + timedelta(days=1, hours=23, minutes=59, seconds=59)),
                "inclusive": True,
            },
            "approximation": False,
            "original_value": "Synthetic event scheduled for tomorrow",
            "original_timezone": "UTC",
            "original_offset": "+00:00",
            "normalized_start_utc": iso(now + timedelta(days=1)),
            "normalized_end_utc": iso(now + timedelta(days=1, hours=23, minutes=59, seconds=59)),
            "source_ref": source_ref,
            "evidence_ref": evidence_ref,
            "retrieved_at": None,
            # The registry must replace this caller-supplied timestamp.
            "recorded_at": iso(now - timedelta(days=30)),
            "supersedes_assertion_id": None,
            "published_at": None,
            "first_observed_at": None,
        }
        append_temporal_assertion(self.connection, assertion)
        inserted_at = self.connection.execute(
            """
            SELECT inserted_at
            FROM sinayxa.temporal_assertions
            WHERE temporal_assertion_id = %s
            """,
            (assertion["temporal_assertion_id"],),
        ).fetchone()[0]
        cutoff = iso(inserted_at)

        request = {
            "assessment_id": f"{event_id}-assessment-1",
            "event_id": event_id,
            "assessment_cutoff": cutoff,
            "assertion_refs": [assertion["temporal_assertion_id"]],
            "conflict_decision_refs": [],
            "rules_version": "temporal-assessment-rules-1.0.0",
            "software_version": "sinayxa-registry-0.1.0",
        }
        too_early = {
            **request,
            "assessment_id": f"{event_id}-assessment-too-early",
            "assessment_cutoff": iso(inserted_at - timedelta(microseconds=1)),
        }
        with self.assertRaises(EventRegistryError):
            create_temporal_assessment(self.connection, too_early)

        assessment = create_temporal_assessment(self.connection, request)
        self.assertEqual("FUTURE", assessment["derived_temporal_state"])
        self.assertNotEqual(assertion["recorded_at"], assessment["recorded_at"])
        stored_assessment = get_temporal_assessment(
            self.connection, assessment["assessment_id"]
        )
        self.assertEqual(assessment, stored_assessment["assessment"])
        late_source_ref = f"{event_id}-late-source"
        register_source_artifact(
            self.connection,
            late_source_ref,
            b'{"late_synthetic_source": true}',
            {
                "source_uri": f"urn:sinayxa:synthetic:{late_source_ref}",
                "media_type": "application/json",
                "license_ref": "SYNTHETIC-TEST-DATA",
                "usage_status": "SYNTHETIC",
                "metadata": {"fixture": "future-source"},
            },
        )
        add_source_reference(self.connection, event_id, late_source_ref)

        later_assertion = {
            **assertion,
            "temporal_assertion_id": f"{event_id}-assertion-v2",
            "version": 2,
            "supersedes_assertion_id": assertion["temporal_assertion_id"],
        }
        append_temporal_assertion(self.connection, later_assertion)
        with self.assertRaises(EventRegistryError):
            create_reproducibility_manifest(
                self.connection,
                {
                    "manifest_id": f"{event_id}-manifest-future-exclusion",
                    "assessment_id": assessment["assessment_id"],
                    "excluded_assertions": [
                        {
                            "assertion_id": later_assertion["temporal_assertion_id"],
                            "version": 2,
                            "reason": "Not known at the assessment cutoff",
                        }
                    ],
                },
            )

        manifest = create_reproducibility_manifest(
            self.connection,
            {
                "manifest_id": f"{event_id}-manifest-1",
                "assessment_id": assessment["assessment_id"],
                "excluded_assertions": [],
            },
        )
        self.assertEqual("RFC8785", manifest["canonicalization"])
        self.assertEqual("2026f", manifest["tzdb_version"])
        self.assertEqual("PARTIALLY_REPRODUCIBLE", manifest["reproducibility_status"])
        self.assertIn(evidence_ref, manifest["evidence_refs"])
        self.assertNotIn(f"source_artifact_missing:{source_ref}", manifest["missing_components"])
        self.assertNotIn(f"evidence_artifact_missing:{evidence_ref}", manifest["missing_components"])
        self.assertNotIn(f"source_artifact_missing:{late_source_ref}", manifest["missing_components"])
        self.assertEqual(
            [{"assertion_id": assertion["temporal_assertion_id"], "version": 1}],
            manifest["assertion_versions"],
        )
        self.assertTrue(
            all(
                len(manifest[field]) == 64
                for field in ("schema_sha256", "rules_sha256", "result_sha256")
            )
        )
        root = Path(__file__).resolve().parents[2]
        self.assertEqual(
            hashlib.sha256(
                (root / "schemas" / "temporal-event-contract-1.0.0.schema.json").read_bytes()
            ).hexdigest(),
            manifest["schema_sha256"],
        )
        self.assertEqual(
            hashlib.sha256(
                (root / "scripts" / "validation" / "validate_temporal_event_contract.py").read_bytes()
            ).hexdigest(),
            manifest["rules_sha256"],
        )
        self.assertTrue(manifest["missing_components"])
        stored_manifest = get_reproducibility_manifest(
            self.connection, manifest["manifest_id"]
        )
        self.assertEqual(manifest, stored_manifest["manifest"])
        repeated_manifest = create_reproducibility_manifest(
            self.connection,
            {
                "manifest_id": f"{event_id}-manifest-2",
                "assessment_id": assessment["assessment_id"],
                "excluded_assertions": [],
            },
        )
        self.assertEqual(manifest["result_sha256"], repeated_manifest["result_sha256"])

        mutations = (
            (
                "UPDATE sinayxa.temporal_assessments SET derived_temporal_state = 'PAST' WHERE assessment_id = %s",
                (assessment["assessment_id"],),
            ),
            (
                "DELETE FROM sinayxa.temporal_assessments WHERE assessment_id = %s",
                (assessment["assessment_id"],),
            ),
            (
                "UPDATE sinayxa.reproducibility_manifests SET result_sha256 = repeat('0', 64) WHERE manifest_id = %s",
                (manifest["manifest_id"],),
            ),
            (
                "DELETE FROM sinayxa.reproducibility_manifests WHERE manifest_id = %s",
                (manifest["manifest_id"],),
            ),
        )
        for statement, parameters in mutations:
            with self.assertRaises(psycopg.Error):
                with self.connection.transaction():
                    self.connection.execute(statement, parameters)

        for table in (
            "events",
            "event_sources",
            "temporal_assertions",
            "temporal_conflicts",
            "conflict_decisions",
            "temporal_assessments",
            "reproducibility_manifests",
            "source_artifacts",
            "evidence_artifacts",
        ):
            with self.assertRaises(psycopg.Error):
                with self.connection.transaction():
                    self.connection.execute(f"TRUNCATE TABLE sinayxa.{table} CASCADE")



    def test_source_and_evidence_artifacts_preserve_exact_bytes_and_authorization(self) -> None:
        source_ref = f"source-{uuid4().hex}"
        evidence_ref = f"evidence-{uuid4().hex}"
        source_bytes = b'{"synthetic_source":"exact bytes"}'
        evidence_bytes = b'{"synthetic_evidence":"exact bytes"}'
        source = register_source_artifact(
            self.connection,
            source_ref,
            source_bytes,
            {
                "source_uri": f"urn:sinayxa:synthetic:{source_ref}",
                "title": "Synthetic source",
                "publisher": "SINAYXA test fixture",
                "media_type": "application/json",
                "license_ref": "SYNTHETIC-TEST-DATA",
                "usage_status": "SYNTHETIC",
                "metadata": {"fixture": "artifact-integrity"},
            },
        )
        self.assertEqual(hashlib.sha256(source_bytes).hexdigest(), source["content_sha256"])
        self.assertEqual(source_bytes, get_source_artifact(self.connection, source_ref)["content_bytes"])

        evidence = register_evidence_artifact(
            self.connection,
            evidence_ref,
            evidence_bytes,
            {
                "source_ref": source_ref,
                "evidence_type": "SYNTHETIC_EXTRACT",
                "media_type": "application/json",
                "extraction_method": "synthetic-test",
                "extraction_version": "1.0.0",
                "license_ref": "SYNTHETIC-TEST-DATA",
                "usage_status": "SYNTHETIC",
                "metadata": {"fixture": "artifact-integrity"},
            },
        )
        self.assertEqual(hashlib.sha256(evidence_bytes).hexdigest(), evidence["content_sha256"])
        self.assertEqual(
            evidence_bytes,
            get_evidence_artifact(self.connection, evidence_ref)["content_bytes"],
        )

        with self.assertRaises(EventRegistryError):
            register_source_artifact(
                self.connection,
                f"source-unauthorized-{uuid4().hex}",
                b"unauthorized",
                {
                    "media_type": "text/plain",
                    "license_ref": "UNKNOWN",
                    "usage_status": "AUTHORIZED",
                },
            )
        with self.assertRaises(EventRegistryError):
            register_evidence_artifact(
                self.connection,
                f"evidence-unauthorized-{uuid4().hex}",
                b"mismatched rights",
                {
                    "source_ref": source_ref,
                    "evidence_type": "EXTRACT",
                    "media_type": "text/plain",
                    "extraction_method": "manual",
                    "extraction_version": "1.0.0",
                    "license_ref": "UNKNOWN",
                    "usage_status": "AUTHORIZED",
                    "authorization_ref": "unrelated-authorization",
                },
            )
        with self.assertRaises(EventRegistryError):
            register_evidence_artifact(
                self.connection,
                f"evidence-license-mismatch-{uuid4().hex}",
                b"mismatched license",
                {
                    "source_ref": source_ref,
                    "evidence_type": "EXTRACT",
                    "media_type": "text/plain",
                    "extraction_method": "manual",
                    "extraction_version": "1.0.0",
                    "license_ref": "DIFFERENT-LICENSE",
                    "usage_status": "SYNTHETIC",
                },
            )

        mutations = (
            (
                "UPDATE sinayxa.source_artifacts SET title = 'rewritten' WHERE source_ref = %s",
                (source_ref,),
            ),
            (
                "DELETE FROM sinayxa.source_artifacts WHERE source_ref = %s",
                (source_ref,),
            ),
            (
                "UPDATE sinayxa.evidence_artifacts SET location_hint = 'rewritten' WHERE evidence_ref = %s",
                (evidence_ref,),
            ),
            (
                "DELETE FROM sinayxa.evidence_artifacts WHERE evidence_ref = %s",
                (evidence_ref,),
            ),
        )
        for statement, parameters in mutations:
            with self.assertRaises(psycopg.Error):
                with self.connection.transaction():
                    self.connection.execute(statement, parameters)



if __name__ == "__main__":
    unittest.main()
