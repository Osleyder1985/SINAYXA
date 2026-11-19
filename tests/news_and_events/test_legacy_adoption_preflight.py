"""Tests for the strictly read-only legacy adoption preflight."""
from __future__ import annotations

import os
import unittest
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from scripts.news_and_events.catalog_fingerprint import fingerprint_schema
from scripts.news_and_events.legacy_adoption_preflight import (
    LEGACY_MIGRATION_IDS,
    LegacyAdoptionPreflightError,
    preflight_legacy_adoption,
)

DATABASE_URL = os.environ.get("SINAYXA_DATABASE_URL")


class LegacyAdoptionPreflightUnitTests(unittest.TestCase):
    def test_preflight_requires_an_explicit_sha256_baseline(self) -> None:
        with self.assertRaisesRegex(LegacyAdoptionPreflightError, "approved lowercase SHA-256"):
            preflight_legacy_adoption(
                None, approved_baseline_sha256="", approved_identity="test_reader"
            )

    def test_preflight_rejects_non_idle_connections_before_queries(self) -> None:
        class ConnectionInfo:
            transaction_status = 1

        class Connection:
            info = ConnectionInfo()

        with self.assertRaisesRegex(LegacyAdoptionPreflightError, "idle connection"):
            preflight_legacy_adoption(
                Connection(),
                approved_baseline_sha256="a" * 64,
                approved_identity="test_reader",
            )


@unittest.skipUnless(DATABASE_URL, "PostgreSQL integration database is not configured")
class LegacyAdoptionPreflightIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.admin = psycopg.connect(DATABASE_URL, autocommit=True)
        self.database_name = f"sinayxa_preflight_{uuid4().hex[:16]}"
        self.admin.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.database_name))
        )
        parameters = conninfo_to_dict(DATABASE_URL)
        parameters["dbname"] = self.database_name
        self.database_url = make_conninfo(**parameters)
        self.connection = psycopg.connect(self.database_url)

        from scripts.news_and_events.migration_runner import apply_migrations

        apply_migrations(self.connection)
        self.connection.commit()
        self.connection.execute("DROP SCHEMA sinayxa_control CASCADE")
        self.connection.commit()
        self.reader_identity = f"sinayxa_preflight_reader_{uuid4().hex[:10]}"
        self.reader_password = uuid4().hex
        self.admin.execute(
            sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                sql.Identifier(self.reader_identity),
                sql.Literal(self.reader_password),
            )
        )
        self.admin.execute(
            sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                sql.Identifier(self.database_name), sql.Identifier(self.reader_identity)
            )
        )
        self.connection.execute(
            sql.SQL("GRANT USAGE ON SCHEMA sinayxa TO {}").format(
                sql.Identifier(self.reader_identity)
            )
        )
        self.connection.execute(
            sql.SQL("GRANT SELECT ON sinayxa.schema_migrations TO {}").format(
                sql.Identifier(self.reader_identity)
            )
        )
        self.connection.commit()
        # The fingerprint includes schema/table ACLs, so capture the approved
        # baseline only after the reader's intended minimum privileges exist.
        self.approved_digest = fingerprint_schema(self.connection).sha256
        reader_parameters = conninfo_to_dict(self.database_url)
        reader_parameters["user"] = self.reader_identity
        reader_parameters["password"] = self.reader_password
        self.reader_connection = psycopg.connect(make_conninfo(**reader_parameters))

    def tearDown(self) -> None:
        self.reader_connection.close()
        self.connection.close()
        self.admin.execute(
            sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(
                sql.Identifier(self.database_name)
            )
        )
        self.admin.execute(
            sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(self.reader_identity))
        )
        self.admin.close()

    def test_matching_legacy_inventory_and_catalog_are_read_only(self) -> None:
        before = self.connection.execute(
            "SELECT count(*) FROM sinayxa.schema_migrations"
        ).fetchone()[0]
        self.connection.commit()

        result = preflight_legacy_adoption(
            self.reader_connection,
            approved_baseline_sha256=self.approved_digest,
            approved_identity=self.reader_identity,
        )

        # The current verifier is explicitly marked preview; matching bytes
        # cannot authorize adoption until its contract is finalized and reviewed.
        self.assertEqual("LEGACY_UNVERIFIED", result.status)
        self.assertTrue(
            any("still a preview" in reason for reason in result.reasons)
        )
        self.assertEqual(180007, result.server_version_num)
        self.assertEqual(tuple(sorted(LEGACY_MIGRATION_IDS)), result.legacy_migration_ids)
        self.assertEqual(self.approved_digest, result.computed_fingerprint)
        self.assertEqual(
            before,
            self.connection.execute(
                "SELECT count(*) FROM sinayxa.schema_migrations"
            ).fetchone()[0],
        )
        self.assertFalse(
            self.connection.execute(
                "SELECT to_regnamespace('sinayxa_control') IS NOT NULL"
            ).fetchone()[0]
        )
        self.connection.commit()

    def test_missing_or_unknown_legacy_ids_remain_unverified(self) -> None:
        self.connection.execute(
            "DELETE FROM sinayxa.schema_migrations WHERE migration_id = %s",
            (LEGACY_MIGRATION_IDS[-1],),
        )
        self.connection.execute(
            """
            INSERT INTO sinayxa.schema_migrations (migration_id)
            VALUES ('unrecognized-legacy-migration')
            """
        )
        self.connection.commit()

        result = preflight_legacy_adoption(
            self.reader_connection,
            approved_baseline_sha256=self.approved_digest,
            approved_identity=self.reader_identity,
        )

        self.assertEqual("LEGACY_UNVERIFIED", result.status)
        self.assertTrue(any("inventory mismatch" in reason for reason in result.reasons))
        self.assertIsNone(result.computed_fingerprint)
        self.assertFalse(
            self.connection.execute(
                "SELECT to_regnamespace('sinayxa_control') IS NOT NULL"
            ).fetchone()[0]
        )
        self.connection.commit()

    def test_catalog_mismatch_remains_unverified(self) -> None:
        self.connection.execute(
            "ALTER TABLE sinayxa.events ADD COLUMN preflight_probe text"
        )
        self.connection.commit()

        result = preflight_legacy_adoption(
            self.reader_connection,
            approved_baseline_sha256=self.approved_digest,
            approved_identity=self.reader_identity,
        )

        self.assertEqual("LEGACY_UNVERIFIED", result.status)
        self.assertTrue(
            any("does not match the approved baseline" in reason for reason in result.reasons)
        )
        self.assertFalse(
            self.connection.execute(
                "SELECT to_regnamespace('sinayxa_control') IS NOT NULL"
            ).fetchone()[0]
        )
        self.connection.commit()

    def test_existing_control_plane_is_not_treated_as_unadopted_legacy(self) -> None:
        self.connection.execute("CREATE SCHEMA sinayxa_control")
        self.connection.commit()

        result = preflight_legacy_adoption(
            self.reader_connection,
            approved_baseline_sha256=self.approved_digest,
            approved_identity=self.reader_identity,
        )

        self.assertEqual("LEGACY_UNVERIFIED", result.status)
        self.assertTrue(any("already exists" in reason for reason in result.reasons))


    def test_preflight_rejects_identity_mismatch(self) -> None:
        result = preflight_legacy_adoption(
            self.reader_connection,
            approved_baseline_sha256=self.approved_digest,
            approved_identity="not_the_authenticated_role",
        )
        self.assertEqual("LEGACY_UNVERIFIED", result.status)
        self.assertTrue(
            any("identity mismatch" in reason for reason in result.reasons)
        )
        self.assertEqual(self.reader_identity, result.session_user)
        self.assertEqual(self.reader_identity, result.current_user)
        self.assertEqual(self.reader_identity, result.current_role)

    def test_preflight_rejects_unexpected_membership_and_elevated_reachable_role(self) -> None:
        group_role = f"sinayxa_preflight_group_{uuid4().hex[:10]}"
        self.admin.execute(
            sql.SQL("CREATE ROLE {} NOLOGIN BYPASSRLS").format(sql.Identifier(group_role))
        )
        self.admin.execute(
            sql.SQL("GRANT {} TO {}").format(
                sql.Identifier(group_role), sql.Identifier(self.reader_identity)
            )
        )
        try:
            result = preflight_legacy_adoption(
                self.reader_connection,
                approved_baseline_sha256=self.approved_digest,
                approved_identity=self.reader_identity,
            )
            self.assertEqual("LEGACY_UNVERIFIED", result.status)
            self.assertTrue(
                any("membership graph differs" in reason for reason in result.reasons)
            )
            self.assertTrue(
                any("elevated role attributes" in reason for reason in result.reasons)
            )
            self.assertIn(
                self.reader_identity,
                {member for member, _, _, _, _ in result.role_memberships},
            )
            self.assertIn(
                group_role,
                {granted for _, granted, _, _, _ in result.role_memberships},
            )
        finally:
            self.admin.execute(
                sql.SQL("REVOKE {} FROM {}").format(
                    sql.Identifier(group_role), sql.Identifier(self.reader_identity)
                )
            )
            self.admin.execute(
                sql.SQL("DROP ROLE {}").format(sql.Identifier(group_role))
            )

    def test_preflight_rejects_application_table_write_privileges(self) -> None:
        self.connection.execute(
            sql.SQL("GRANT INSERT ON sinayxa.events TO {}").format(
                sql.Identifier(self.reader_identity)
            )
        )
        self.connection.commit()
        try:
            result = preflight_legacy_adoption(
                self.reader_connection,
                approved_baseline_sha256=self.approved_digest,
                approved_identity=self.reader_identity,
            )
            self.assertEqual("LEGACY_UNVERIFIED", result.status)
            self.assertTrue(
                any("write privileges on application objects" in reason for reason in result.reasons)
            )
            self.assertIsNone(result.computed_fingerprint)
        finally:
            self.connection.execute(
                sql.SQL("REVOKE INSERT ON sinayxa.events FROM {}").format(
                    sql.Identifier(self.reader_identity)
                )
            )
            self.connection.commit()

    def test_preflight_requires_select_privilege_on_legacy_ledger(self) -> None:
        self.connection.execute(
            sql.SQL("REVOKE SELECT ON sinayxa.schema_migrations FROM {}").format(
                sql.Identifier(self.reader_identity)
            )
        )
        self.connection.commit()
        try:
            result = preflight_legacy_adoption(
                self.reader_connection,
                approved_baseline_sha256=self.approved_digest,
                approved_identity=self.reader_identity,
            )
            self.assertEqual("LEGACY_UNVERIFIED", result.status)
            self.assertTrue(
                any("lacks SELECT on the legacy migration ledger" in reason for reason in result.reasons)
            )
            self.assertEqual((), result.legacy_migration_ids)
            self.assertIsNone(result.computed_fingerprint)
        finally:
            self.connection.execute(
                sql.SQL("GRANT SELECT ON sinayxa.schema_migrations TO {}").format(
                    sql.Identifier(self.reader_identity)
                )
            )
            self.connection.commit()
