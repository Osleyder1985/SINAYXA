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
    append_temporal_assertion,
    connect,
    create_event,
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

        second_recorded = source_b_recorded_at + timedelta(microseconds=4)
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
            "recorded_at": iso(second_recorded),
            "supersedes_assertion_id": first["temporal_assertion_id"],
            "published_at": iso(source_b_recorded_at + timedelta(microseconds=1)),
            "first_observed_at": iso(source_b_recorded_at + timedelta(microseconds=2)),
        }
        premature = {
            **second,
            "temporal_assertion_id": f"{event_id}-v2-premature",
            "retrieved_at": iso(source_b_recorded_at - timedelta(microseconds=2)),
            "recorded_at": iso(source_b_recorded_at - timedelta(microseconds=1)),
            "published_at": iso(source_b_recorded_at - timedelta(microseconds=4)),
            "first_observed_at": iso(source_b_recorded_at - timedelta(microseconds=3)),
        }
        with self.assertRaises(EventRegistryError):
            append_temporal_assertion(self.connection, premature)

        append_temporal_assertion(self.connection, second)

        historical = get_event_as_of(
            self.connection, event_id, iso(source_b_recorded_at - timedelta(microseconds=1))
        )
        current = get_event_as_of(
            self.connection, event_id, iso(second_recorded + timedelta(seconds=1))
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
            WHERE migration_id = 'issue-2-event-registry-0001'
            """
        ).fetchone()[0]
        trigger_count = self.connection.execute(
            """
            SELECT count(*)
            FROM pg_trigger
            WHERE tgname IN (
                'events_append_only',
                'event_sources_append_only',
                'temporal_assertions_append_only'
            )
              AND NOT tgisinternal
            """
        ).fetchone()[0]
        self.assertEqual(1, migration_count)
        self.assertEqual(3, trigger_count)

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



if __name__ == "__main__":
    unittest.main()
