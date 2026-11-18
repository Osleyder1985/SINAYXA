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
        self.assertTrue(all("kind" in item for item in functions))
        self.assertTrue(all("support_function" in item for item in functions))
        self.assertEqual(18, len(triggers))
        foreign_keys = [
            item for item in result.records
            if item["object_type"] == "constraint"
            and item["constraint_type"] == "f"
        ]
        self.assertTrue(foreign_keys)
        self.assertTrue(
            all(item["supporting_index_schema"] for item in foreign_keys)
        )
        self.assertTrue(
            all(item["supporting_index_name"] for item in foreign_keys)
        )
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
            for index, (left, right) in enumerate(
                zip(fingerprints[0].records, fingerprints[1].records, strict=True)
            ):
                if left != right:
                    differences = {
                        key: (left.get(key), right.get(key))
                        for key in sorted(set(left) | set(right))
                        if left.get(key) != right.get(key)
                    }
                    self.fail(
                        "independent catalog record mismatch at "
                        f"{index} ({left['object_type']} "
                        f"{left['qualified_name']} {left['identity']}): "
                        f"{differences}"
                    )
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


    def test_fingerprint_rejects_unrepresented_operators(self) -> None:
        self.connection.execute(
            """
            CREATE FUNCTION sinayxa.fp_probe_operator_eq(integer, integer)
            RETURNS boolean LANGUAGE sql IMMUTABLE
            AS 'SELECT $1 = $2'
            """
        )
        self.connection.execute(
            """
            CREATE OPERATOR sinayxa.=== (
                LEFTARG = integer,
                RIGHTARG = integer,
                FUNCTION = sinayxa.fp_probe_operator_eq
            )
            """
        )
        self.connection.commit()
        try:
            with self.assertRaisesRegex(
                CatalogFingerprintError, "unsupported schema objects"
            ):
                fingerprint_schema(self.connection)
        finally:
            self.connection.execute(
                "DROP OPERATOR IF EXISTS sinayxa.===(integer, integer)"
            )
            self.connection.execute(
                "DROP FUNCTION IF EXISTS "
                "sinayxa.fp_probe_operator_eq(integer, integer)"
            )
            self.connection.commit()

    def test_fingerprint_rejects_undefined_shell_types(self) -> None:
        self.connection.execute("CREATE TYPE sinayxa.fp_probe_shell")
        self.connection.commit()
        try:
            with self.assertRaisesRegex(
                CatalogFingerprintError, "unsupported pseudo or undefined shell types"
            ):
                fingerprint_schema(self.connection)
        finally:
            self.connection.execute(
                "DROP TYPE IF EXISTS sinayxa.fp_probe_shell"
            )
            self.connection.commit()

    def test_fingerprint_rejects_unrepresented_range_types(self) -> None:
        self.connection.execute(
            """
            CREATE TYPE sinayxa.fp_probe_range AS RANGE (
                subtype = integer
            )
            """
        )
        self.connection.commit()
        try:
            with self.assertRaisesRegex(
                CatalogFingerprintError, "unsupported schema objects"
            ):
                fingerprint_schema(self.connection)
        finally:
            self.connection.execute(
                "DROP TYPE IF EXISTS sinayxa.fp_probe_range CASCADE"
            )
            self.connection.commit()

    def test_fingerprint_rejects_table_inheritance(self) -> None:
        self.connection.execute(
            "CREATE TABLE sinayxa.fp_probe_inheritance_parent (value integer)"
        )
        self.connection.execute(
            """
            CREATE TABLE sinayxa.fp_probe_inheritance_child ()
            INHERITS (sinayxa.fp_probe_inheritance_parent)
            """
        )
        self.connection.commit()
        try:
            with self.assertRaisesRegex(
                CatalogFingerprintError, "unsupported table inheritance"
            ):
                fingerprint_schema(self.connection)
        finally:
            self.connection.execute(
                "DROP TABLE IF EXISTS sinayxa.fp_probe_inheritance_child"
            )
            self.connection.execute(
                "DROP TABLE IF EXISTS sinayxa.fp_probe_inheritance_parent"
            )
            self.connection.commit()

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

    def test_fingerprint_detects_not_enforced_constraint_state(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE sinayxa.fp_probe_constraint_enforcement (
                value integer
            )
            """
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                """
                ALTER TABLE sinayxa.fp_probe_constraint_enforcement
                ADD CONSTRAINT fp_probe_not_enforced
                CHECK (value > 0) NOT ENFORCED
                """
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
            constraint = next(
                item for item in after.records
                if item["object_type"] == "constraint"
                and item["identity"] == "fp_probe_not_enforced"
            )
            self.assertFalse(constraint["enforced"])
            self.assertFalse(constraint["validated"])
        finally:
            self.connection.execute(
                "DROP TABLE IF EXISTS sinayxa.fp_probe_constraint_enforcement CASCADE"
            )
            self.connection.commit()

    def test_fingerprint_detects_composite_attribute_collation_changes(self) -> None:
        self.connection.execute(
            """
            CREATE TYPE sinayxa.fp_probe_composite AS (
                label text
            )
            """
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                """
                ALTER TYPE sinayxa.fp_probe_composite
                ALTER ATTRIBUTE label SET DATA TYPE text COLLATE "C"
                """
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
            composite = next(
                item for item in after.records
                if item["object_type"] == "type"
                and item["identity"] == "fp_probe_composite"
            )
            self.assertEqual("C", composite["attributes"][0]["collation_name"])
            self.assertEqual("pg_catalog", composite["attributes"][0]["collation_schema"])
        finally:
            self.connection.execute(
                "DROP TYPE IF EXISTS sinayxa.fp_probe_composite CASCADE"
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

    def test_fingerprint_distinguishes_procedures_from_functions(self) -> None:
        self.connection.execute(
            """
            CREATE PROCEDURE sinayxa.fp_probe_procedure()
            LANGUAGE plpgsql
            AS $procedure$
            BEGIN
                NULL;
            END;
            $procedure$
            """
        )
        self.connection.commit()
        try:
            result = fingerprint_schema(self.connection)
            procedure = next(
                item for item in result.records
                if item["object_type"] == "function"
                and item["qualified_name"] == "sinayxa.fp_probe_procedure"
            )
            self.assertEqual("p", procedure["kind"])
            self.assertIsNone(procedure["support_function"])
        finally:
            self.connection.execute(
                "DROP PROCEDURE IF EXISTS sinayxa.fp_probe_procedure()"
            )
            self.connection.commit()

    def test_fingerprint_detects_replica_identity_index_selection(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE sinayxa.fp_probe_replident (
                id integer NOT NULL,
                value text NOT NULL
            )
            """
        )
        self.connection.execute(
            """
            CREATE UNIQUE INDEX fp_probe_replident_idx
            ON sinayxa.fp_probe_replident (id)
            """
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                """
                ALTER TABLE sinayxa.fp_probe_replident
                REPLICA IDENTITY USING INDEX fp_probe_replident_idx
                """
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
            before_index = next(
                item for item in before.records
                if item["object_type"] == "index"
                and item["identity"] == "fp_probe_replident_idx"
            )
            after_index = next(
                item for item in after.records
                if item["object_type"] == "index"
                and item["identity"] == "fp_probe_replident_idx"
            )
            self.assertFalse(before_index["replica_identity"])
            self.assertTrue(after_index["replica_identity"])
        finally:
            self.connection.execute(
                "DROP TABLE IF EXISTS sinayxa.fp_probe_replident CASCADE"
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
                "REVOKE USAGE ON TYPE sinayxa.fp_probe_acl_type FROM PUBLIC"
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
            typ = next(
                item for item in after.records
                if item["object_type"] == "type"
                and item["identity"] == "fp_probe_acl_type"
            )
            self.assertFalse(
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

    def test_fingerprint_detects_collation_changes(self) -> None:
        self.connection.execute(
            """
            CREATE COLLATION sinayxa.fp_probe_collation
            (provider = libc, locale = 'C')
            """
        )
        self.connection.commit()
        try:
            after = fingerprint_schema(self.connection)
            collation = next(
                item for item in after.records
                if item["object_type"] == "collation"
                and item["identity"] == "fp_probe_collation"
            )
            self.assertEqual("c", collation["provider"])
            self.assertEqual("C", collation["locale"])
            self.assertTrue(collation["owner"])
        finally:
            self.connection.execute(
                "DROP COLLATION IF EXISTS sinayxa.fp_probe_collation"
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

    def test_fingerprint_detects_relation_owner_changes(self) -> None:
        role_name = f"fp_owner_{uuid4().hex}"
        table_name = f"fp_probe_owner_{uuid4().hex}"
        self.connection.execute(f'CREATE ROLE "{role_name}"')
        self.connection.execute(
            f'CREATE TABLE sinayxa."{table_name}" (value integer)'
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                f'ALTER TABLE sinayxa."{table_name}" OWNER TO "{role_name}"'
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
            relation = next(
                item for item in after.records
                if item["object_type"] == "relation"
                and item["identity"] == f"sinayxa.{table_name}"
            )
            self.assertEqual(role_name, relation["owner"])
        finally:
            self.connection.execute(
                f'DROP TABLE IF EXISTS sinayxa."{table_name}" CASCADE'
            )
            self.connection.execute(f'DROP ROLE IF EXISTS "{role_name}"')
            self.connection.commit()

    def test_fingerprint_detects_column_storage_changes(self) -> None:
        self.connection.execute(
            "CREATE TABLE sinayxa.fp_probe_column_storage (value text)"
        )
        self.connection.commit()
        try:
            before = fingerprint_schema(self.connection)
            self.connection.execute(
                """
                ALTER TABLE sinayxa.fp_probe_column_storage
                ALTER COLUMN value SET STORAGE EXTERNAL
                """
            )
            self.connection.commit()
            after = fingerprint_schema(self.connection)
            self.assertNotEqual(before.sha256, after.sha256)
            column = next(
                item for item in after.records
                if item["object_type"] == "column"
                and item["qualified_name"] == "sinayxa.fp_probe_column_storage"
                and item["name"] == "value"
            )
            self.assertEqual("e", column["storage_strategy"])
            self.assertFalse(
                any(option.startswith("pg_attver=") for option in column["column_options"])
            )
        finally:
            self.connection.execute(
                "DROP TABLE IF EXISTS sinayxa.fp_probe_column_storage"
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
