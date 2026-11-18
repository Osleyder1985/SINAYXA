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
            preflight_legacy_adoption(None, approved_baseline_sha256="")

    def test_preflight_rejects_non_idle_connections_before_queries(self) -> None:
        class ConnectionInfo:
            transaction_status = 1

        class Connection:
            info = ConnectionInfo()

        with self.assertRaisesRegex(LegacyAdoptionPreflightError, "idle connection"):
            preflight_legacy_adoption(
                Connection(), approved_baseline_sha256="a" * 64
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
        self.approved_digest = fingerprint_schema(self.connection).sha256

    def tearDown(self) -> None:
        self.connection.close()
        self.admin.execute(
            sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(
                sql.Identifier(self.database_name)
            )
        )
        self.admin.close()

    def test_matching_legacy_inventory_and_catalog_are_read_only(self) -> None:
        before = self.connection.execute(
            "SELECT count(*) FROM sinayxa.schema_migrations"
        ).fetchone()[0]
        self.connection.commit()

        result = preflight_legacy_adoption(
            self.connection, approved_baseline_sha256=self.approved_digest
        )

        self.assertEqual("PREFLIGHT_MATCH", result.status)
        self.assertEqual((), result.reasons)
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
            self.connection, approved_baseline_sha256=self.approved_digest
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
            self.connection, approved_baseline_sha256=self.approved_digest
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
            self.connection, approved_baseline_sha256=self.approved_digest
        )

        self.assertEqual("LEGACY_UNVERIFIED", result.status)
        self.assertTrue(any("already exists" in reason for reason in result.reasons))
