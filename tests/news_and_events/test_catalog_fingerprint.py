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


    def test_independent_fresh_databases_produce_identical_fingerprints(self) -> None:
        """Build the same manifest in two isolated databases and compare exact records."""
        from psycopg import sql
        from psycopg.conninfo import conninfo_to_dict, make_conninfo
        from scripts.news_and_events.migration_runner import apply_migrations

        database_names = [
            f"sinayxa_fp_{uuid4().hex[:16]}",
            f"sinayxa_fp_{uuid4().hex[:16]}",
        ]
        created: list[str] = []
        admin = psycopg.connect(DATABASE_URL, autocommit=True)
        try:
            for database_name in database_names:
                admin.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name))
                )
                created.append(database_name)

            fingerprints = []
            base_parameters = conninfo_to_dict(DATABASE_URL)
            for database_name in database_names:
                parameters = dict(base_parameters)
                parameters["dbname"] = database_name
                isolated_url = make_conninfo(**parameters)
                with psycopg.connect(isolated_url) as isolated:
                    apply_migrations(isolated)
                    isolated.commit()
                    fingerprints.append(fingerprint_schema(isolated))

            self.assertEqual(fingerprints[0].algorithm_version, fingerprints[1].algorithm_version)
            self.assertEqual(fingerprints[0].record_count, fingerprints[1].record_count)
            self.assertEqual(fingerprints[0].canonical_json, fingerprints[1].canonical_json)
            self.assertEqual(fingerprints[0].sha256, fingerprints[1].sha256)
        finally:
            for database_name in created:
                admin.execute(
                    sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(
                        sql.Identifier(database_name)
                    )
                )
            admin.close()


    def test_fingerprint_rejects_partitioned_relations(self) -> None:
        self.connection.execute(
            "CREATE TABLE sinayxa.fp_probe_partitioned "
            "(value integer) PARTITION BY RANGE (value)"
        )
        self.connection.execute(
            "CREATE TABLE sinayxa.fp_probe_partitioned_0 "
            "PARTITION OF sinayxa.fp_probe_partitioned "
            "FOR VALUES FROM (0) TO (100)"
        )
        self.connection.commit()
        try:
            with self.assertRaisesRegex(
                CatalogFingerprintError, "unsupported partitioned relations"
            ):
                fingerprint_schema(self.connection)
        finally:
            self.connection.execute(
                "DROP TABLE IF EXISTS sinayxa.fp_probe_partitioned CASCADE"
            )
            self.connection.commit()

    def test_fingerprint_detects_global_default_privilege_changes(self) -> None:
        existing = self.connection.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM pg_default_acl d
                CROSS JOIN LATERAL aclexplode(d.defaclacl) x
                WHERE d.defaclnamespace = 0
                  AND d.defaclrole = (SELECT oid FROM pg_roles WHERE rolname = current_user)
                  AND x.grantee = 0
                  AND x.privilege_type = 'TRUNCATE'
            )
            """
        ).fetchone()[0]
        self.connection.commit()
        if existing:
            self.skipTest("current role already has a global PUBLIC TRUNCATE default")

        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                "ALTER DEFAULT PRIVILEGES "
                "GRANT TRUNCATE ON TABLES TO PUBLIC"
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
            self.assertTrue(
                any(
                    item["object_type"] == "default_privileges"
                    and item["scope"] == "GLOBAL"
                    and item["owner"] == self.connection.info.user
                    for item in after.records
                )
            )
        finally:
            self.connection.execute(
                "ALTER DEFAULT PRIVILEGES "
                "REVOKE TRUNCATE ON TABLES FROM PUBLIC"
            )
            self.connection.commit()

    def test_fingerprint_detects_enum_type_changes(self) -> None:
        self.connection.execute(
            "CREATE TYPE sinayxa.fp_probe_enum AS ENUM ('alpha')"
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                "ALTER TYPE sinayxa.fp_probe_enum ADD VALUE 'beta'"
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
        finally:
            self.connection.execute(
                "DROP TYPE IF EXISTS sinayxa.fp_probe_enum CASCADE"
            )
            self.connection.commit()

    def test_fingerprint_detects_function_definition_changes(self) -> None:
        self.connection.execute(
            """
            CREATE FUNCTION sinayxa.fp_probe_function()
            RETURNS integer LANGUAGE sql IMMUTABLE AS 'SELECT 1'
            """
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                """
                CREATE OR REPLACE FUNCTION sinayxa.fp_probe_function()
                RETURNS integer LANGUAGE sql IMMUTABLE AS 'SELECT 2'
                """
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
        finally:
            self.connection.execute(
                "DROP FUNCTION IF EXISTS sinayxa.fp_probe_function()"
            )
            self.connection.commit()

    def test_fingerprint_detects_sequence_semantic_changes(self) -> None:
        self.connection.execute(
            "CREATE SEQUENCE sinayxa.fp_probe_sequence START WITH 7 INCREMENT BY 1"
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                "ALTER SEQUENCE sinayxa.fp_probe_sequence INCREMENT BY 3"
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
            before_record = next(
                item for item in before.records
                if item["object_type"] == "sequence"
                and item["identity"] == "sinayxa.fp_probe_sequence"
            )
            after_record = next(
                item for item in after.records
                if item["object_type"] == "sequence"
                and item["identity"] == "sinayxa.fp_probe_sequence"
            )
            self.assertNotEqual(
                before_record["increment"], after_record["increment"]
            )
        finally:
            self.connection.execute(
                "DROP SEQUENCE IF EXISTS sinayxa.fp_probe_sequence"
            )
            self.connection.commit()

    def test_fingerprint_detects_rewrite_rule_changes(self) -> None:
        self.connection.execute(
            "CREATE TABLE sinayxa.fp_probe_rule_table (value integer)"
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                """
                CREATE RULE fp_probe_rule AS
                ON INSERT TO sinayxa.fp_probe_rule_table
                DO INSTEAD NOTHING
                """
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
            self.assertTrue(
                any(
                    item["object_type"] == "rule"
                    and item["identity"] == "fp_probe_rule"
                    for item in after.records
                )
            )
        finally:
            self.connection.execute(
                "DROP TABLE IF EXISTS sinayxa.fp_probe_rule_table CASCADE"
            )
            self.connection.commit()

    def test_fingerprint_detects_materialized_view_population_state(self) -> None:
        self.connection.execute(
            "CREATE MATERIALIZED VIEW sinayxa.fp_probe_matview AS "
            "SELECT 1 AS value"
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                "REFRESH MATERIALIZED VIEW sinayxa.fp_probe_matview WITH NO DATA"
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
        finally:
            self.connection.execute(
                "DROP MATERIALIZED VIEW IF EXISTS sinayxa.fp_probe_matview"
            )
            self.connection.commit()

    def test_fingerprint_detects_function_acl_changes(self) -> None:
        self.connection.execute(
            """
            CREATE FUNCTION sinayxa.fp_probe_function_acl()
            RETURNS integer LANGUAGE sql IMMUTABLE AS 'SELECT 1'
            """
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                "REVOKE EXECUTE ON FUNCTION "
                "sinayxa.fp_probe_function_acl() FROM PUBLIC"
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
            function = next(
                item for item in after.records
                if item["object_type"] == "function"
                and item["identity"] == "fp_probe_function_acl()"
            )
            self.assertFalse(
                any(privilege["grantee"] == "PUBLIC" and
                    privilege["privilege"] == "EXECUTE"
                    for privilege in function["acl"])
            )
        finally:
            self.connection.execute(
                "DROP FUNCTION IF EXISTS sinayxa.fp_probe_function_acl()"
            )
            self.connection.commit()

    def test_fingerprint_detects_type_acl_changes(self) -> None:
        self.connection.execute(
            "CREATE TYPE sinayxa.fp_probe_acl_type AS ENUM ('one', 'two')"
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                "GRANT USAGE ON TYPE sinayxa.fp_probe_acl_type TO PUBLIC"
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
            typ = next(
                item for item in after.records
                if item["object_type"] == "type"
                and item["identity"] == "fp_probe_acl_type"
            )
            self.assertTrue(
                any(privilege["grantee"] == "PUBLIC" and
                    privilege["privilege"] == "USAGE"
                    for privilege in typ["acl"])
            )
        finally:
            self.connection.execute(
                "DROP TYPE IF EXISTS sinayxa.fp_probe_acl_type CASCADE"
            )
            self.connection.commit()

    def test_fingerprint_detects_sequence_acl_changes(self) -> None:
        self.connection.execute(
            "CREATE SEQUENCE sinayxa.fp_probe_acl_sequence"
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                "GRANT SELECT ON SEQUENCE "
                "sinayxa.fp_probe_acl_sequence TO PUBLIC"
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
            sequence = next(
                item for item in after.records
                if item["object_type"] == "relation"
                and item["identity"] == "sinayxa.fp_probe_acl_sequence"
            )
            self.assertTrue(
                any(privilege["grantee"] == "PUBLIC" and
                    privilege["privilege"] == "SELECT"
                    for privilege in sequence["acl"])
            )
        finally:
            self.connection.execute(
                "DROP SEQUENCE IF EXISTS sinayxa.fp_probe_acl_sequence"
            )
            self.connection.commit()

    def test_fingerprint_detects_constraint_changes(self) -> None:
        self.connection.execute(
            "CREATE TABLE sinayxa.fp_probe_constraint (value integer)"
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                "ALTER TABLE sinayxa.fp_probe_constraint "
                "ADD CONSTRAINT fp_probe_constraint_positive CHECK (value > 0)"
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
        finally:
            self.connection.execute(
                "DROP TABLE IF EXISTS sinayxa.fp_probe_constraint CASCADE"
            )
            self.connection.commit()

    def test_fingerprint_detects_index_changes(self) -> None:
        self.connection.execute(
            "CREATE TABLE sinayxa.fp_probe_index (value integer)"
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                "CREATE INDEX fp_probe_index_value_idx "
                "ON sinayxa.fp_probe_index (value)"
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
        finally:
            self.connection.execute(
                "DROP TABLE IF EXISTS sinayxa.fp_probe_index CASCADE"
            )
            self.connection.commit()

    def test_fingerprint_detects_trigger_changes(self) -> None:
        self.connection.execute(
            "CREATE TABLE sinayxa.fp_probe_trigger (value integer)"
        )
        self.connection.execute(
            """
            CREATE FUNCTION sinayxa.fp_probe_trigger_fn()
            RETURNS trigger LANGUAGE plpgsql
            AS 'BEGIN RETURN NEW; END;'
            """
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                """
                CREATE TRIGGER fp_probe_trigger
                BEFORE INSERT ON sinayxa.fp_probe_trigger
                FOR EACH ROW EXECUTE FUNCTION sinayxa.fp_probe_trigger_fn()
                """
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
        finally:
            self.connection.execute(
                "DROP TABLE IF EXISTS sinayxa.fp_probe_trigger CASCADE"
            )
            self.connection.execute(
                "DROP FUNCTION IF EXISTS sinayxa.fp_probe_trigger_fn()"
            )
            self.connection.commit()

    def test_fingerprint_detects_relation_acl_changes(self) -> None:
        self.connection.execute(
            "CREATE TABLE sinayxa.fp_probe_acl (value integer)"
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                "GRANT SELECT ON sinayxa.fp_probe_acl TO PUBLIC"
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
        finally:
            self.connection.execute(
                "REVOKE SELECT ON sinayxa.fp_probe_acl FROM PUBLIC"
            )
            self.connection.execute(
                "DROP TABLE IF EXISTS sinayxa.fp_probe_acl CASCADE"
            )
            self.connection.commit()

    def test_fingerprint_detects_view_definition_changes(self) -> None:
        self.connection.execute(
            "CREATE TABLE sinayxa.fp_probe_view_source (value integer)"
        )
        self.connection.execute(
            "CREATE VIEW sinayxa.fp_probe_view AS "
            "SELECT value FROM sinayxa.fp_probe_view_source"
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                "CREATE OR REPLACE VIEW sinayxa.fp_probe_view AS "
                "SELECT value + 1 AS value FROM sinayxa.fp_probe_view_source"
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
        finally:
            self.connection.execute("DROP VIEW IF EXISTS sinayxa.fp_probe_view")
            self.connection.execute("DROP TABLE IF EXISTS sinayxa.fp_probe_view_source")
            self.connection.commit()

    def test_fingerprint_detects_row_level_security_policy_changes(self) -> None:
        self.connection.execute(
            "CREATE TABLE sinayxa.fp_probe_policy (value integer)"
        )
        self.connection.execute(
            "ALTER TABLE sinayxa.fp_probe_policy ENABLE ROW LEVEL SECURITY"
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                "CREATE POLICY fp_probe_policy ON sinayxa.fp_probe_policy "
                "USING (value > 0)"
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
            policy = next(
                item for item in after.records
                if item["object_type"] == "policy"
                and item["identity"] == "fp_probe_policy"
            )
            self.assertEqual(["PUBLIC"], policy["roles"])
        finally:
            self.connection.execute("DROP TABLE IF EXISTS sinayxa.fp_probe_policy")
            self.connection.commit()


if __name__ == "__main__":
    unittest.main()
