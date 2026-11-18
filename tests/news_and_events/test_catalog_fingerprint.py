"""Unit and PostgreSQL integration tests for catalog fingerprint preview."""
from __future__ import annotations

import os
import unittest
from uuid import uuid4

import psycopg

from scripts.news_and_events.catalog_fingerprint import (
    CatalogFingerprintError,
    canonicalize_records,
    fingerprint_schema,
)


class CatalogCanonicalizationTests(unittest.TestCase):
    def test_record_order_does_not_change_canonical_bytes(self) -> None:
        left = [
            {"object_type": "table", "qualified_name": "sinayxa.b", "identity": "b"},
            {"object_type": "schema", "qualified_name": "sinayxa", "identity": "sinayxa"},
        ]
        right = list(reversed(left))
        self.assertEqual(canonicalize_records(left), canonicalize_records(right))

    def test_json_object_key_order_does_not_change_canonical_bytes(self) -> None:
        left = [{"object_type": "column", "qualified_name": "sinayxa.t", "identity": "1:x",
                 "properties": {"nullable": False, "name": "x"}}]
        right = [{"properties": {"name": "x", "nullable": False}, "identity": "1:x",
                  "qualified_name": "sinayxa.t", "object_type": "column"}]
        self.assertEqual(canonicalize_records(left), canonicalize_records(right))

    def test_non_json_values_fail_closed(self) -> None:
        with self.assertRaises(CatalogFingerprintError):
            canonicalize_records([{"object_type": "invalid", "payload": object()}])


DATABASE_URL = os.environ.get("SINAYXA_DATABASE_URL")


@unittest.skipUnless(DATABASE_URL, "PostgreSQL integration database is not configured")
class CatalogFingerprintIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = psycopg.connect(DATABASE_URL)
        from scripts.news_and_events.migration_runner import apply_migrations
        apply_migrations(self.connection)
        self.connection.commit()

    def tearDown(self) -> None:
        self.connection.close()

    def test_fingerprint_is_deterministic_and_reports_semantic_inventory(self) -> None:
        first = fingerprint_schema(self.connection)
        second = fingerprint_schema(self.connection)

        self.assertEqual("sinayxa-catalog-v1-preview", first.algorithm_version)
        self.assertEqual(first.sha256, second.sha256)
        self.assertEqual(first.canonical_json, second.canonical_json)
        self.assertGreater(first.record_count, 0)
        self.assertEqual(180007, first.server_version_num)
        self.assertIn("sinayxa.events", {
            record["qualified_name"] for record in first.records
        })
        self.assertIn("function", {record["object_type"] for record in first.records})
        self.assertIn("trigger", {record["object_type"] for record in first.records})
        relations = [r for r in first.records if r["object_type"] == "relation"]
        functions = [r for r in first.records if r["object_type"] == "function"]
        triggers = [r for r in first.records if r["object_type"] == "trigger"]
        columns = [r for r in first.records if r["object_type"] == "column"]
        types = [r for r in first.records if r["object_type"] == "type"]
        self.assertEqual(10, len(relations))
        self.assertEqual(2, len(functions))
        self.assertEqual(18, len(triggers))
        self.assertTrue(all("acl" in item for item in columns))
        self.assertTrue(all("owner" in item and "acl" in item for item in types))
        self.assertEqual(0, self.connection.info.transaction_status)

    def test_fingerprint_excludes_business_rows(self) -> None:
        before = fingerprint_schema(self.connection)
        event_id = f"catalog-fingerprint-{uuid4().hex}"
        self.connection.execute(
            """
            INSERT INTO sinayxa.events
                (event_id, description, created_at, contract_version, event_payload)
            VALUES (%s, %s, clock_timestamp(), '1.0.0', '{}'::jsonb)
            """,
            (event_id, "Synthetic row proving data is outside the catalog digest"),
        )
        self.connection.commit()

        after = fingerprint_schema(self.connection)
        self.assertEqual(before.sha256, after.sha256)

    def test_preview_rejects_schema_outside_approved_scope(self) -> None:
        with self.assertRaisesRegex(CatalogFingerprintError, "restricted to schema"):
            fingerprint_schema(self.connection, "public")

    def test_fingerprint_requires_idle_connection(self) -> None:
        with self.connection.transaction():
            with self.assertRaisesRegex(CatalogFingerprintError, "idle connection"):
                fingerprint_schema(self.connection)

    def test_fingerprint_does_not_create_or_change_application_objects(self) -> None:
        before = self.connection.execute(
            """
            SELECT count(*)
            FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'sinayxa'
            """
        ).fetchone()[0]
        self.connection.commit()
        fingerprint_schema(self.connection)
        after = self.connection.execute(
            """
            SELECT count(*)
            FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'sinayxa'
            """
        ).fetchone()[0]
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
