"""PostgreSQL integration tests for the fresh-database migration runner."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from unittest.mock import patch
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from scripts.news_and_events import migration_runner
from scripts.news_and_events.migration_runner import (
    BOOTSTRAP_SHA256,
    MigrationRunnerError,
    apply_migrations,
)


DATABASE_URL = os.environ.get("SINAYXA_DATABASE_URL")


@unittest.skipUnless(DATABASE_URL, "PostgreSQL integration database is not configured")
class MigrationRunnerIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.admin = psycopg.connect(DATABASE_URL, autocommit=True)
        self.database_name = f"sinayxa_mig_{uuid4().hex}"
        self.admin.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.database_name))
        )
        parameters = conninfo_to_dict(DATABASE_URL)
        parameters["dbname"] = self.database_name
        self.database_url = make_conninfo(**parameters)
        self.connection = psycopg.connect(self.database_url)

    def tearDown(self) -> None:
        self.connection.close()
        self.admin.execute(
            """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s AND pid <> pg_backend_pid()
            """,
            (self.database_name,),
        )
        self.admin.execute(
            sql.SQL("DROP DATABASE {}").format(sql.Identifier(self.database_name))
        )
        self.admin.close()

    def test_runner_rejects_caller_owned_transaction(self) -> None:
        with self.connection.transaction():
            with self.assertRaisesRegex(MigrationRunnerError, "requires an idle connection"):
                apply_migrations(self.connection)
            self.assertIsNone(
                self.connection.execute(
                    "SELECT to_regnamespace('sinayxa_control')"
                ).fetchone()[0]
            )

    def test_fresh_database_applies_exact_manifest_once(self) -> None:
        first = apply_migrations(self.connection)
        second = apply_migrations(self.connection)

        self.assertEqual(5, len(first))
        self.assertEqual((), second)
        self.assertEqual(
            5,
            self.connection.execute(
                "SELECT count(*) FROM sinayxa_control.migration_integrity"
            ).fetchone()[0],
        )
        self.assertEqual(
            5,
            self.connection.execute(
                "SELECT count(*) FROM sinayxa.schema_migrations"
            ).fetchone()[0],
        )
        self.assertEqual(
            BOOTSTRAP_SHA256,
            self.connection.execute(
                "SELECT bootstrap_sha256::text FROM sinayxa_control.bootstrap_state"
            ).fetchone()[0].strip(),
        )

    def test_modified_applied_sql_artifact_fails_before_database_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            migrations = Path(temporary) / "migrations"
            shutil.copytree(migration_runner.MIGRATIONS_DIR, migrations)
            manifest = migrations / "manifest.json"
            apply_migrations(
                self.connection,
                manifest_path=manifest,
                migrations_dir=migrations,
            )

            historical_sql = migrations / "0001_event_registry.sql"
            historical_sql.write_bytes(
                historical_sql.read_bytes()
                + b"\nCREATE TABLE sinayxa.must_not_execute (id integer);\n"
            )
            with self.assertRaisesRegex(
                MigrationRunnerError, "migration manifest verification failed"
            ):
                apply_migrations(
                    self.connection,
                    manifest_path=manifest,
                    migrations_dir=migrations,
                )

        self.assertIsNone(
            self.connection.execute(
                "SELECT to_regclass('sinayxa.must_not_execute')"
            ).fetchone()[0]
        )
        self.assertEqual(
            5,
            self.connection.execute(
                "SELECT count(*) FROM sinayxa_control.migration_integrity"
            ).fetchone()[0],
        )

    def test_new_migration_applies_only_pending_manifest_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            migrations = Path(temporary) / "migrations"
            shutil.copytree(migration_runner.MIGRATIONS_DIR, migrations)
            manifest = migrations / "manifest.json"
            first_run = apply_migrations(
                self.connection,
                manifest_path=manifest,
                migrations_dir=migrations,
            )
            self.assertEqual(5, len(first_run))

            document = json.loads(manifest.read_text(encoding="utf-8"))
            new_sql = (
                "CREATE TABLE sinayxa.runner_extension_marker (id integer PRIMARY KEY);\n"
                "INSERT INTO sinayxa.schema_migrations (migration_id) "
                "VALUES ('issue-121-runner-extension-0006');\n"
            )
            filename = "0006_runner_extension.sql"
            (migrations / filename).write_text(new_sql, encoding="utf-8")
            document["migrations"].append(
                {
                    "version": 6,
                    "migration_id": "issue-121-runner-extension-0006",
                    "path": filename,
                    "sha256": hashlib.sha256(new_sql.encode("utf-8")).hexdigest(),
                    "execution_mode": "transactional",
                    "source_revision": "a" * 40,
                }
            )
            manifest.write_text(
                json.dumps(document, indent=2) + "\n",
                encoding="utf-8",
            )

            second_run = apply_migrations(
                self.connection,
                manifest_path=manifest,
                migrations_dir=migrations,
            )

        self.assertEqual(("issue-121-runner-extension-0006",), second_run)
        self.assertIsNotNone(
            self.connection.execute(
                "SELECT to_regclass('sinayxa.runner_extension_marker')"
            ).fetchone()[0]
        )
        self.assertEqual(
            6,
            self.connection.execute(
                "SELECT count(*) FROM sinayxa_control.migration_integrity"
            ).fetchone()[0],
        )
        self.assertEqual(
            6,
            self.connection.execute(
                "SELECT count(*) FROM sinayxa.schema_migrations"
            ).fetchone()[0],
        )

    def test_modified_bootstrap_artifact_fails_before_database_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            altered = Path(temporary) / "bootstrap.sql"
            altered.write_text("CREATE SCHEMA should_not_be_created;\\n", encoding="utf-8")
            with patch(
                "scripts.news_and_events.migration_runner.BOOTSTRAP_PATH", altered
            ):
                with self.assertRaisesRegex(MigrationRunnerError, "bootstrap SHA-256 mismatch"):
                    apply_migrations(self.connection)

        self.assertIsNone(
            self.connection.execute(
                "SELECT to_regnamespace('sinayxa_control')"
            ).fetchone()[0]
        )

    def test_unknown_integrity_ledger_entry_fails_closed(self) -> None:
        apply_migrations(self.connection)
        self.connection.execute(
            """
            INSERT INTO sinayxa_control.migration_integrity
                (migration_id, version, sha256, source_revision, runner_version)
            VALUES ('unrecognized-migration', 99, repeat('0', 64), repeat('a', 40), 'test')
            """
        )
        self.connection.commit()

        with self.assertRaisesRegex(MigrationRunnerError, "unknown migration ID"):
            apply_migrations(self.connection)

    def test_legacy_compatibility_ledger_disagreement_fails_closed(self) -> None:
        apply_migrations(self.connection)
        self.connection.execute(
            "DELETE FROM sinayxa.schema_migrations "
            "WHERE migration_id = 'issue-2-event-registry-0001'"
        )
        self.connection.commit()

        with self.assertRaisesRegex(MigrationRunnerError, "ledger disagreement"):
            apply_migrations(self.connection)

    def test_applied_migration_digest_drift_fails_closed(self) -> None:
        apply_migrations(self.connection)
        self.connection.execute(
            """
            UPDATE sinayxa_control.migration_integrity
            SET sha256 = repeat('0', 64)
            WHERE migration_id = 'issue-2-event-registry-0001'
            """
        )
        self.connection.commit()

        with self.assertRaisesRegex(MigrationRunnerError, "migration drift detected"):
            apply_migrations(self.connection)

    def test_partial_control_plane_fails_closed_without_repair(self) -> None:
        self.connection.execute("CREATE SCHEMA sinayxa_control")
        self.connection.commit()

        with self.assertRaisesRegex(MigrationRunnerError, "partial or unsupported control plane"):
            apply_migrations(self.connection)

        self.assertIsNone(
            self.connection.execute(
                "SELECT to_regclass('sinayxa_control.migration_integrity')"
            ).fetchone()[0]
        )

    def test_ledger_version_collision_fails_closed(self) -> None:
        apply_migrations(self.connection)
        self.connection.execute(
            "UPDATE sinayxa_control.migration_integrity SET version = 99 "
            "WHERE migration_id = 'issue-2-event-registry-0001'"
        )
        self.connection.commit()

        with self.assertRaisesRegex(MigrationRunnerError, "version collision or drift"):
            apply_migrations(self.connection)

    def test_legacy_database_is_not_bootstrapped_or_adopted(self) -> None:
        self.connection.execute("CREATE SCHEMA sinayxa")
        self.connection.execute(
            """
            CREATE TABLE sinayxa.schema_migrations (
                migration_id text PRIMARY KEY,
                applied_at timestamptz NOT NULL DEFAULT clock_timestamp()
            )
            """
        )
        self.connection.execute(
            "INSERT INTO sinayxa.schema_migrations (migration_id) VALUES (%s)",
            ("issue-2-event-registry-0001",),
        )
        self.connection.commit()

        with self.assertRaisesRegex(MigrationRunnerError, "LEGACY_UNVERIFIED"):
            apply_migrations(self.connection)

        self.assertIsNone(
            self.connection.execute(
                "SELECT to_regnamespace('sinayxa_control')"
            ).fetchone()[0]
        )

    def test_failed_migration_rolls_back_its_ddl_and_ledger_row(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            migrations = root / "migrations"
            migrations.mkdir()
            first_sql = (
                "CREATE SCHEMA sinayxa;\n"
                "CREATE TABLE sinayxa.schema_migrations ("
                "migration_id text PRIMARY KEY, "
                "applied_at timestamptz NOT NULL DEFAULT clock_timestamp());\n"
                "INSERT INTO sinayxa.schema_migrations (migration_id) "
                "VALUES ('fixture-0001');\n"
            )
            failing_sql = (
                "CREATE TABLE sinayxa.must_rollback (id integer);\n"
                "SELECT 1 / 0;\n"
                "INSERT INTO sinayxa.schema_migrations (migration_id) "
                "VALUES ('fixture-0002');\n"
            )
            (migrations / "0001_fixture.sql").write_text(first_sql, encoding="utf-8")
            (migrations / "0002_fixture.sql").write_text(failing_sql, encoding="utf-8")
            entries = []
            for version, migration_id, filename, source in (
                (1, "fixture-0001", "0001_fixture.sql", first_sql),
                (2, "fixture-0002", "0002_fixture.sql", failing_sql),
            ):
                entries.append(
                    {
                        "version": version,
                        "migration_id": migration_id,
                        "path": filename,
                        "sha256": hashlib.sha256(source.encode()).hexdigest(),
                        "source_revision": "a" * 40,
                        "execution_mode": "transactional",
                    }
                )
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "manifest_version": 1,
                        "baseline_revision": "a" * 40,
                        "migrations": entries,
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaises(psycopg.errors.DivisionByZero):
                apply_migrations(
                    self.connection,
                    manifest_path=manifest,
                    migrations_dir=migrations,
                )

            self.assertEqual(
                ["fixture-0001"],
                [row[0] for row in self.connection.execute(
                    "SELECT migration_id FROM sinayxa_control.migration_integrity"
                ).fetchall()],
            )
            self.assertIsNone(
                self.connection.execute(
                    "SELECT to_regclass('sinayxa.must_rollback')"
                ).fetchone()[0]
            )

            recovered_sql = (
                "CREATE TABLE sinayxa.recovered (id integer);\n"
                "INSERT INTO sinayxa.schema_migrations (migration_id) "
                "VALUES ('fixture-0002');\n"
            )
            (migrations / "0002_fixture.sql").write_text(recovered_sql, encoding="utf-8")
            entries[1]["sha256"] = hashlib.sha256(recovered_sql.encode()).hexdigest()
            manifest.write_text(
                json.dumps({
                    "manifest_version": 1,
                    "baseline_revision": "a" * 40,
                    "migrations": entries,
                }),
                encoding="utf-8",
            )
            # The verification SELECTs above opened an implicit transaction.
            # End it before retrying the runner, which deliberately requires IDLE.
            self.connection.commit()
            resumed = apply_migrations(
                self.connection,
                manifest_path=manifest,
                migrations_dir=migrations,
            )
            self.assertEqual(("fixture-0002",), resumed)
            self.assertIsNotNone(
                self.connection.execute(
                    "SELECT to_regclass('sinayxa.recovered')"
                ).fetchone()[0]
            )

        self.assertEqual(
            ["fixture-0001", "fixture-0002"],
            [
                row[0]
                for row in self.connection.execute(
                    "SELECT migration_id FROM sinayxa_control.migration_integrity ORDER BY version"
                ).fetchall()
            ],
        )
        self.assertIsNone(
            self.connection.execute(
                "SELECT to_regclass('sinayxa.must_rollback')"
            ).fetchone()[0]
        )
        self.assertEqual(
            2,
            self.connection.execute(
                "SELECT count(*) FROM sinayxa.schema_migrations"
            ).fetchone()[0],
        )

    def test_concurrent_initializers_apply_each_migration_once(self) -> None:
        barrier = Barrier(2)

        def run_initializer() -> tuple[str, ...]:
            with psycopg.connect(self.database_url) as connection:
                barrier.wait(timeout=20)
                return apply_migrations(connection)

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: run_initializer(), range(2)))

        self.assertEqual(5, sum(len(result) for result in results))
        self.assertEqual(
            5,
            self.connection.execute(
                "SELECT count(*) FROM sinayxa_control.migration_integrity"
            ).fetchone()[0],
        )
        self.assertEqual(
            5,
            self.connection.execute(
                "SELECT count(*) FROM sinayxa.schema_migrations"
            ).fetchone()[0],
        )


if __name__ == "__main__":
    unittest.main()
