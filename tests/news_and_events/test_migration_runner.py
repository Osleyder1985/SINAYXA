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
from scripts.news_and_events.contract_package_store import (
    load_claim_assessments_as_of,
    load_contract_package,
    persist_contract_package,
)
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

        self.assertEqual(6, len(first))
        self.assertEqual((), second)
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
        self.assertEqual(
            BOOTSTRAP_SHA256,
            self.connection.execute(
                "SELECT bootstrap_sha256::text FROM sinayxa_control.bootstrap_state"
            ).fetchone()[0].strip(),
        )


    def test_contract_0_2_1_migration_creates_typed_append_only_relations(self) -> None:
        apply_migrations(self.connection)
        expected_tables = {
            "contract_packages", "claims", "claim_components", "contract_sources",
            "source_versions", "identity_assessments", "evaluation_units",
            "contract_evidence_items", "evidence_availability", "claim_evidence_links",
            "provenance_nodes", "provenance_edges", "factor_assessments",
            "independence_assessments", "claim_assessments", "retention_records",
            "audit_events", "archive_attestations", "retention_copy_records",
            "contract_migration_records", "analysis_processes",
        }
        actual_tables = {
            row[0] for row in self.connection.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'sinayxa'"
            ).fetchall()
        }
        self.assertTrue(expected_tables.issubset(actual_tables))

        event_id = "issue153-synthetic-event"
        now = "2026-01-02T03:04:05+00:00"
        self.connection.execute(
            """
            INSERT INTO sinayxa.events
                (event_id, description, affected_asset_refs, source_refs,
                 created_at, contract_version, event_payload)
            VALUES (%s, 'Synthetic event for contract persistence test',
                    '{}', '{}', %s, '1.0.0', '{"synthetic":true}'::jsonb)
            """,
            (event_id, now),
        )
        self.connection.execute(
            """
            INSERT INTO sinayxa.contract_packages
                (package_id, event_id, contract_version, created_at, schema_sha256)
            VALUES (%s, %s, '0.2.1', %s, %s)
            """,
            ("issue153-synthetic-package", event_id, now, "a" * 64),
        )
        self.connection.commit()

        with self.assertRaisesRegex(
            psycopg.errors.ObjectNotInPrerequisiteState, "append-only"
        ):
            self.connection.execute(
                "UPDATE sinayxa.contract_packages SET contract_version = '0.2.1' "
                "WHERE package_id = 'issue153-synthetic-package'"
            )
        self.connection.rollback()

        with self.assertRaises(psycopg.errors.ForeignKeyViolation):
            self.connection.execute(
                """
                INSERT INTO sinayxa.contract_packages
                    (package_id, event_id, contract_version, created_at, schema_sha256)
                VALUES ('issue153-orphan-package', 'missing-event', '0.2.1', %s, %s)
                """,
                (now, "a" * 64),
            )
        self.connection.rollback()


    def test_contract_package_store_persists_fixture_atomically(self) -> None:
        apply_migrations(self.connection)
        event_id = f"issue153-store-{uuid4().hex}"
        now = "2026-01-02T03:04:05+00:00"
        self.connection.execute(
            """
            INSERT INTO sinayxa.events
                (event_id, description, affected_asset_refs, source_refs,
                 created_at, contract_version, event_payload)
            VALUES (%s, 'Synthetic package persistence integration test',
                    '{}', '{}', %s, '1.0.0', '{"synthetic":true}'::jsonb)
            """,
            (event_id, now),
        )
        self.connection.commit()

        fixture = (
            Path(__file__).resolve().parents[1]
            / "fixtures"
            / "contracts"
            / "source-evidence-contract-v0.2.1.json"
        )
        package = json.loads(fixture.read_text(encoding="utf-8"))
        result = persist_contract_package(
            self.connection,
            package,
            event_id=event_id,
        )

        self.assertEqual(package["package_id"], result["package_id"])
        loaded = load_contract_package(self.connection, package["package_id"])
        self.assertEqual(package["package_id"], loaded["package_id"])
        self.assertEqual(package["contract_version"], loaded["contract_version"])

        future_cutoff = self.connection.execute(
            "SELECT clock_timestamp() + interval '1 minute'"
        ).fetchone()[0]
        as_of_result = load_claim_assessments_as_of(
            self.connection, package["package_id"], future_cutoff
        )
        self.assertEqual(2, len(as_of_result["assessments"]))
        entity_assessment = next(
            item for item in as_of_result["assessments"]
            if item["claim_assessment_id"] == "assessment-entity-v1"
        )
        self.assertEqual(["evidence-a"], entity_assessment["supporting_evidence_refs"])

        past_cutoff = self.connection.execute(
            "SELECT clock_timestamp() - interval '1 minute'"
        ).fetchone()[0]
        self.assertEqual(
            [],
            load_claim_assessments_as_of(
                self.connection, package["package_id"], past_cutoff
            )["assessments"],
        )
        self.assertEqual(1, len(loaded["claims"]))
        self.assertEqual(2, len(loaded["claim_components"]))
        self.assertEqual(
            package["source_versions"][0]["original_timestamps"],
            loaded["source_versions"][0]["original_timestamps"],
        )
        self.assertEqual(1, result["inserted_counts"]["claims"])
        self.assertEqual(2, result["inserted_counts"]["claim_components"])
        self.assertEqual(40, result["inserted_counts"]["factor_assessments"])
        self.assertEqual(
            1,
            self.connection.execute(
                "SELECT count(*) FROM sinayxa.contract_packages WHERE package_id = %s",
                (package["package_id"],),
            ).fetchone()[0],
        )
        self.assertEqual(
            2,
            self.connection.execute(
                "SELECT count(*) FROM sinayxa.source_versions WHERE package_id = %s",
                (package["package_id"],),
            ).fetchone()[0],
        )
        self.assertIsNotNone(
            self.connection.execute(
                "SELECT inserted_at FROM sinayxa.claims WHERE claim_version_id = %s",
                (package["claims"][0]["claim_version_id"],),
            ).fetchone()[0]
        )

        with self.assertRaises(psycopg.errors.UniqueViolation):
            persist_contract_package(self.connection, package, event_id=event_id)
        self.connection.rollback()
        self.assertEqual(
            1,
            self.connection.execute(
                "SELECT count(*) FROM sinayxa.contract_packages WHERE package_id = %s",
                (package["package_id"],),
            ).fetchone()[0],
        )

    def test_synthetic_historical_snapshots_upgrade_and_preserve_invariants(self) -> None:
        """Exercise synthetic snapshots at every migration boundary, then roll forward."""
        event_id = "issue-121-snapshot-event"
        assertion_ids = (
            "issue-121-snapshot-assertion-1",
            "issue-121-snapshot-assertion-2",
        )
        conflict_id = "issue-121-snapshot-conflict"
        decision_id = "issue-121-snapshot-decision"
        assessment_id = "issue-121-snapshot-assessment"
        manifest_id = "issue-121-snapshot-manifest"
        source_ref = "urn:sinayxa:synthetic:issue-121-source"
        evidence_ref = "urn:sinayxa:synthetic:issue-121-evidence"
        source_bytes = b"issue-121 synthetic historical source bytes"
        evidence_bytes = b"issue-121 synthetic historical evidence bytes"
        source_digest = hashlib.sha256(source_bytes).hexdigest()
        evidence_digest = hashlib.sha256(evidence_bytes).hexdigest()
        now = "2026-01-02T03:04:05+00:00"

        with tempfile.TemporaryDirectory() as temporary:
            # Explicit pre-0001 snapshot: a genuinely empty disposable database.
            self.assertEqual(
                (None, None),
                self.connection.execute(
                    "SELECT to_regnamespace('sinayxa'), "
                    "to_regnamespace('sinayxa_control')"
                ).fetchone(),
            )
            # The inspection SELECT opened an implicit transaction; the
            # migration runner deliberately requires an idle connection.
            self.connection.commit()
            source_migrations = migration_runner.MIGRATIONS_DIR
            complete_manifest = json.loads(
                (source_migrations / "manifest.json").read_text(encoding="utf-8")
            )

            # Each prefix is a separate, inventory-consistent synthetic snapshot.
            for boundary in range(1, 7):
                snapshot_dir = Path(temporary) / f"snapshot-{boundary}"
                snapshot_dir.mkdir()
                snapshot_manifest = dict(complete_manifest)
                snapshot_manifest["migrations"] = complete_manifest["migrations"][:boundary]
                for record in snapshot_manifest["migrations"]:
                    shutil.copy2(source_migrations / record["path"], snapshot_dir / record["path"])
                manifest_path = snapshot_dir / "manifest.json"
                manifest_path.write_text(
                    json.dumps(snapshot_manifest, indent=2) + "\n",
                    encoding="utf-8",
                )
                apply_migrations(
                    self.connection,
                    manifest_path=manifest_path,
                    migrations_dir=snapshot_dir,
                )

                if boundary == 1:
                    self.connection.execute(
                        """
                        INSERT INTO sinayxa.events
                            (event_id, description, affected_asset_refs, source_refs,
                             created_at, contract_version, event_payload)
                        VALUES (%s, %s, %s, %s, %s, '1.0.0', %s::jsonb)
                        """,
                        (
                            event_id,
                            "Synthetic event retained across historical upgrades",
                            ["BTC"],
                            [source_ref],
                            now,
                            json.dumps({"fixture": "issue-121", "synthetic": True}),
                        ),
                    )
                    self.connection.execute(
                        """
                        INSERT INTO sinayxa.event_sources (event_id, source_ref)
                        VALUES (%s, %s)
                        """,
                        (event_id, source_ref),
                    )
                    for version, assertion_id in enumerate(assertion_ids, start=1):
                        self.connection.execute(
                            """
                            INSERT INTO sinayxa.temporal_assertions
                                (temporal_assertion_id, event_id, version, temporal_role,
                                 precision, interval_start, interval_end, approximation,
                                 recorded_at, assertion_payload)
                            VALUES (%s, %s, %s, 'ACTUAL', 'DAY',
                                    '{"value":"2026-01-01","inclusive":true}'::jsonb,
                                    '{"value":"2026-01-02","inclusive":true}'::jsonb,
                                    false, %s, %s::jsonb)
                            """,
                            (
                                assertion_id,
                                event_id,
                                version,
                                now,
                                json.dumps({"fixture": "issue-121", "version": version}),
                            ),
                        )

                elif boundary == 2:
                    self.connection.execute(
                        """
                        INSERT INTO sinayxa.temporal_conflicts
                            (conflict_id, event_id, assertion_refs, disputed_component,
                             classification, status, recorded_at, conflict_payload)
                        VALUES (%s, %s, %s, 'DATE', 'DIRECT_CONTRADICTION',
                                'OPEN', %s, %s::jsonb)
                        """,
                        (
                            conflict_id,
                            event_id,
                            list(assertion_ids),
                            now,
                            json.dumps({"fixture": "issue-121"}),
                        ),
                    )
                    self.connection.execute(
                        """
                        INSERT INTO sinayxa.conflict_decisions
                            (decision_id, conflict_id, from_status, to_status,
                             assertion_refs, supporting_evidence_refs,
                             contrary_evidence_refs, scope, rationale, limitations,
                             actor_ref, decided_at, assessment_cutoff, rules_version,
                             decision_payload)
                        VALUES (%s, %s, 'OPEN', 'UNDER_REVIEW', %s, '{}', '{}',
                                'synthetic fixture', 'preserve the unresolved conflict',
                                'synthetic data only', 'issue-121-test', %s, %s,
                                'snapshot-rules-1', %s::jsonb)
                        """,
                        (
                            decision_id,
                            conflict_id,
                            [assertion_ids[0]],
                            now,
                            now,
                            json.dumps({"fixture": "issue-121"}),
                        ),
                    )

                elif boundary == 3:
                    self.connection.execute(
                        """
                        INSERT INTO sinayxa.temporal_assessments
                            (assessment_id, event_id, assessment_cutoff, assertion_refs,
                             conflict_decision_refs, derived_temporal_state, rules_version,
                             software_version, recorded_at, assessment_payload)
                        VALUES (%s, %s, %s, %s, %s, 'UNDETERMINED',
                                'snapshot-rules-1', 'snapshot-runner-1', %s, %s::jsonb)
                        """,
                        (
                            assessment_id,
                            event_id,
                            now,
                            list(assertion_ids),
                            [decision_id],
                            now,
                            json.dumps({"fixture": "issue-121"}),
                        ),
                    )
                    self.connection.execute(
                        """
                        INSERT INTO sinayxa.reproducibility_manifests
                            (manifest_id, assessment_id, assessment_cutoff,
                             contract_version, schema_sha256, assertion_versions,
                             excluded_assertions, evidence_refs, conflict_decision_refs,
                             rules_version, rules_sha256, tzdb_version, software_version,
                             result_sha256, canonicalization, reproducibility_status,
                             missing_components, created_at, manifest_payload)
                        VALUES (%s, %s, %s, '1.0.0', %s, %s::jsonb, '[]'::jsonb,
                                '{}', %s, 'snapshot-rules-1', %s, 'synthetic-tzdb',
                                'snapshot-runner-1', %s, 'RFC8785',
                                'PARTIALLY_REPRODUCIBLE', '{}', %s, %s::jsonb)
                        """,
                        (
                            manifest_id,
                            assessment_id,
                            now,
                            "a" * 64,
                            json.dumps([{"assertion_id": assertion_ids[0], "version": 1}]),
                            [decision_id],
                            "b" * 64,
                            "c" * 64,
                            now,
                            json.dumps({"fixture": "issue-121"}),
                        ),
                    )

                elif boundary == 4:
                    self.connection.execute(
                        """
                        INSERT INTO sinayxa.source_artifacts
                            (source_ref, source_uri, title, publisher, media_type,
                             content_sha256, content_length, content_bytes, license_ref,
                             usage_status, captured_at, recorded_at, metadata)
                        VALUES (%s, %s, 'Synthetic source', 'SINAYXA test fixture',
                                'application/octet-stream', %s, %s, %s,
                                'SYNTHETIC-TEST-DATA', 'SYNTHETIC', %s, %s,
                                '{"fixture":"issue-121"}'::jsonb)
                        """,
                        (
                            source_ref,
                            source_ref,
                            source_digest,
                            len(source_bytes),
                            source_bytes,
                            now,
                            now,
                        ),
                    )
                    self.connection.execute(
                        """
                        INSERT INTO sinayxa.evidence_artifacts
                            (evidence_ref, source_ref, evidence_type, media_type,
                             content_sha256, content_length, content_bytes,
                             extraction_method, extraction_version, license_ref,
                             usage_status, captured_at, recorded_at, metadata)
                        VALUES (%s, %s, 'SYNTHETIC_EXTRACT', 'application/octet-stream',
                                %s, %s, %s, 'snapshot-test', '1.0.0',
                                'SYNTHETIC-TEST-DATA', 'SYNTHETIC', %s, %s,
                                '{"fixture":"issue-121"}'::jsonb)
                        """,
                        (
                            evidence_ref,
                            source_ref,
                            evidence_digest,
                            len(evidence_bytes),
                            evidence_bytes,
                            now,
                            now,
                        ),
                    )

                # Commit each synthetic snapshot before the next runner invocation.
                self.connection.commit()

            complete_dir = Path(temporary) / "complete-manifest"
            shutil.copytree(source_migrations, complete_dir)
            complete_manifest_path = complete_dir / "manifest.json"
            self.assertEqual(
                (),
                apply_migrations(
                    self.connection,
                    manifest_path=complete_manifest_path,
                    migrations_dir=complete_dir,
                ),
            )

        self.assertEqual(
            (event_id, "Synthetic event retained across historical upgrades",
             ["BTC"], [source_ref]),
            self.connection.execute(
                "SELECT event_id, description, affected_asset_refs, source_refs "
                "FROM sinayxa.events WHERE event_id = %s",
                (event_id,),
            ).fetchone(),
        )
        self.assertEqual(
            list(assertion_ids),
            [
                row[0]
                for row in self.connection.execute(
                    "SELECT temporal_assertion_id FROM sinayxa.temporal_assertions "
                    "WHERE event_id = %s ORDER BY version",
                    (event_id,),
                ).fetchall()
            ],
        )
        self.assertEqual(
            (conflict_id, event_id, list(assertion_ids)),
            self.connection.execute(
                "SELECT conflict_id, event_id, assertion_refs "
                "FROM sinayxa.temporal_conflicts WHERE conflict_id = %s",
                (conflict_id,),
            ).fetchone(),
        )
        self.assertEqual(
            (decision_id, conflict_id, "OPEN", "UNDER_REVIEW"),
            self.connection.execute(
                "SELECT decision_id, conflict_id, from_status, to_status "
                "FROM sinayxa.conflict_decisions WHERE decision_id = %s",
                (decision_id,),
            ).fetchone(),
        )
        self.assertEqual(
            (assessment_id, event_id, list(assertion_ids), [decision_id]),
            self.connection.execute(
                "SELECT assessment_id, event_id, assertion_refs, conflict_decision_refs "
                "FROM sinayxa.temporal_assessments WHERE assessment_id = %s",
                (assessment_id,),
            ).fetchone(),
        )
        self.assertEqual(
            (manifest_id, assessment_id, "PARTIALLY_REPRODUCIBLE"),
            self.connection.execute(
                "SELECT manifest_id, assessment_id, reproducibility_status "
                "FROM sinayxa.reproducibility_manifests WHERE manifest_id = %s",
                (manifest_id,),
            ).fetchone(),
        )
        self.assertEqual(
            (source_digest, len(source_bytes), source_bytes),
            self.connection.execute(
                "SELECT content_sha256, content_length, content_bytes "
                "FROM sinayxa.source_artifacts WHERE source_ref = %s",
                (source_ref,),
            ).fetchone(),
        )
        self.assertEqual(
            (evidence_digest, len(evidence_bytes), evidence_bytes),
            self.connection.execute(
                "SELECT content_sha256, content_length, content_bytes "
                "FROM sinayxa.evidence_artifacts WHERE evidence_ref = %s",
                (evidence_ref,),
            ).fetchone(),
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

        # Logical data backup: schema is recreated from the approved migrations.
        tables = (
            "events",
            "event_sources",
            "temporal_assertions",
            "temporal_conflicts",
            "conflict_decisions",
            "temporal_assessments",
            "reproducibility_manifests",
            "source_artifacts",
            "evidence_artifacts",
        )
        self.connection.commit()
        target_database = f"sinayxa_restore_{uuid4().hex}"
        self.admin.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_database))
        )
        target_parameters = conninfo_to_dict(DATABASE_URL)
        target_parameters["dbname"] = target_database
        target_url = make_conninfo(**target_parameters)
        restored = None
        backup_temporary = tempfile.TemporaryDirectory()
        try:
            backup_dir = Path(backup_temporary.name)
            backup_digests: dict[str, str] = {}
            for table in tables:
                chunks: list[bytes] = []
                with self.connection.cursor().copy(
                    f"COPY (SELECT * FROM sinayxa.{table} ORDER BY 1, 2) "
                    "TO STDOUT (FORMAT BINARY)"
                ) as copy:
                    while chunk := copy.read():
                        chunks.append(chunk)
                backup_bytes = b"".join(chunks)
                (backup_dir / f"{table}.copy").write_bytes(backup_bytes)
                backup_digests[table] = hashlib.sha256(backup_bytes).hexdigest()
            self.connection.commit()

            restored = psycopg.connect(target_url)
            self.assertEqual(6, len(apply_migrations(restored)))
            for table in tables:
                backup_bytes = (backup_dir / f"{table}.copy").read_bytes()
                with restored.cursor().copy(
                    f"COPY sinayxa.{table} FROM STDIN (FORMAT BINARY)"
                ) as copy:
                    copy.write(backup_bytes)
            restored.commit()

            for table in tables:
                restored_chunks: list[bytes] = []
                with restored.cursor().copy(
                    f"COPY (SELECT * FROM sinayxa.{table} ORDER BY 1, 2) "
                    "TO STDOUT (FORMAT BINARY)"
                ) as copy:
                    while chunk := copy.read():
                        restored_chunks.append(chunk)
                restored_bytes = b"".join(restored_chunks)
                self.assertEqual(
                    backup_digests[table],
                    hashlib.sha256(restored_bytes).hexdigest(),
                    f"logical backup restore differs for sinayxa.{table}",
                )
            restored.commit()
        finally:
            if restored is not None:
                restored.close()
            self.admin.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = %s AND pid <> pg_backend_pid()",
                (target_database,),
            )
            self.admin.execute(
                sql.SQL("DROP DATABASE {}").format(sql.Identifier(target_database))
            )
            backup_temporary.cleanup()

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
            6,
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
            self.assertEqual(6, len(first_run))

            document = json.loads(manifest.read_text(encoding="utf-8"))
            new_sql = (
                "CREATE TABLE sinayxa.runner_extension_marker (id integer PRIMARY KEY);\n"
                "INSERT INTO sinayxa.schema_migrations (migration_id) "
                "VALUES ('issue-121-runner-extension-0007');\n"
            )
            filename = "0007_runner_extension.sql"
            (migrations / filename).write_text(new_sql, encoding="utf-8")
            document["migrations"].append(
                {
                    "version": 7,
                    "migration_id": "issue-121-runner-extension-0007",
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

        self.assertEqual(("issue-121-runner-extension-0007",), second_run)
        self.assertIsNotNone(
            self.connection.execute(
                "SELECT to_regclass('sinayxa.runner_extension_marker')"
            ).fetchone()[0]
        )
        self.assertEqual(
            7,
            self.connection.execute(
                "SELECT count(*) FROM sinayxa_control.migration_integrity"
            ).fetchone()[0],
        )
        self.assertEqual(
            7,
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

    def test_applied_ledger_must_be_a_continuous_prefix_before_migration_sql(self) -> None:
        migration_runner._bootstrap_or_verify(
            self.connection, migration_runner._read_bootstrap()
        )
        self.connection.execute("CREATE SCHEMA sinayxa")
        self.connection.execute(
            """
            CREATE TABLE sinayxa.schema_migrations (
                migration_id text PRIMARY KEY,
                applied_at timestamptz NOT NULL DEFAULT clock_timestamp()
            )
            """
        )
        manifest = json.loads(
            migration_runner.MANIFEST_PATH.read_text(encoding="utf-8")
        )
        second = manifest["migrations"][1]
        self.connection.execute(
            """
            INSERT INTO sinayxa.schema_migrations (migration_id) VALUES (%s)
            """,
            (second["migration_id"],),
        )
        self.connection.execute(
            """
            INSERT INTO sinayxa_control.migration_integrity
                (migration_id, version, sha256, source_revision, runner_version)
            VALUES (%s, %s, %s, %s, 'test')
            """,
            (
                second["migration_id"],
                second["version"],
                second["sha256"],
                second["source_revision"],
            ),
        )
        self.connection.commit()

        with self.assertRaisesRegex(
            MigrationRunnerError, "not a continuous manifest prefix"
        ):
            apply_migrations(self.connection)

        self.assertIsNone(
            self.connection.execute("SELECT to_regclass('sinayxa.events')").fetchone()[0]
        )
        self.assertEqual(
            [(second["migration_id"],)],
            self.connection.execute(
                "SELECT migration_id FROM sinayxa_control.migration_integrity"
            ).fetchall(),
        )
        self.assertEqual(
            [(second["migration_id"],)],
            self.connection.execute(
                "SELECT migration_id FROM sinayxa.schema_migrations"
            ).fetchall(),
        )

    def test_integrity_ledger_rejects_duplicate_ids_before_dict_conversion(self) -> None:
        apply_migrations(self.connection)
        row = self.connection.execute(
            """
            SELECT migration_id, version, sha256, source_revision
            FROM sinayxa_control.migration_integrity
            WHERE version = 1
            """
        ).fetchone()
        self.connection.execute(
            "ALTER TABLE sinayxa_control.migration_integrity "
            "DROP CONSTRAINT migration_integrity_pkey"
        )
        self.connection.execute(
            "ALTER TABLE sinayxa_control.migration_integrity "
            "DROP CONSTRAINT migration_integrity_version_key"
        )
        self.connection.execute(
            """
            INSERT INTO sinayxa_control.migration_integrity
                (migration_id, version, sha256, source_revision, runner_version)
            VALUES (%s, %s, %s, %s, 'duplicate-test')
            """,
            row,
        )
        self.connection.commit()

        with self.assertRaisesRegex(
            MigrationRunnerError, "duplicate migration ID"
        ):
            migration_runner._load_ledger(self.connection)

    def test_legacy_ledger_rejects_duplicate_ids_before_set_conversion(self) -> None:
        apply_migrations(self.connection)
        migration_id = self.connection.execute(
            "SELECT migration_id FROM sinayxa.schema_migrations ORDER BY migration_id LIMIT 1"
        ).fetchone()[0]
        self.connection.execute(
            "ALTER TABLE sinayxa.schema_migrations "
            "DROP CONSTRAINT schema_migrations_pkey"
        )
        self.connection.execute(
            "INSERT INTO sinayxa.schema_migrations (migration_id) VALUES (%s)",
            (migration_id,),
        )
        self.connection.commit()

        with self.assertRaisesRegex(
            MigrationRunnerError, "duplicate migration IDs"
        ):
            migration_runner._load_legacy_ids(self.connection)

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
            # This is a corrected, still-unapplied migration artifact. Its
            # provenance must advance with the bytes; the failed attempt did
            # not persist a digest or claim that the old source was applied.
            entries[1]["source_revision"] = "b" * 40
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

        self.assertEqual(6, sum(len(result) for result in results))
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

    def test_control_plane_structural_drift_fails_closed_without_repair(self) -> None:
        apply_migrations(self.connection)
        before = self.connection.execute(
            "SELECT count(*) FROM sinayxa_control.migration_integrity"
        ).fetchone()[0]
        self.connection.execute(
            "ALTER TABLE sinayxa_control.migration_integrity "
            "DROP CONSTRAINT migration_integrity_pkey"
        )
        self.connection.commit()

        with self.assertRaisesRegex(
            MigrationRunnerError, "control-plane structural drift detected"
        ):
            apply_migrations(self.connection)

        self.assertEqual(
            before,
            self.connection.execute(
                "SELECT count(*) FROM sinayxa_control.migration_integrity"
            ).fetchone()[0],
        )
        self.assertFalse(
            self.connection.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM pg_constraint con
                    JOIN pg_class c ON c.oid = con.conrelid
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE n.nspname = 'sinayxa_control'
                      AND c.relname = 'migration_integrity'
                      AND con.contype = 'p'
                )
                """
            ).fetchone()[0]
        )

    def test_legacy_ledger_structural_drift_fails_closed_without_repair(self) -> None:
        apply_migrations(self.connection)
        before = self.connection.execute(
            "SELECT count(*) FROM sinayxa.schema_migrations"
        ).fetchone()[0]
        self.connection.execute(
            "ALTER TABLE sinayxa.schema_migrations "
            "DROP CONSTRAINT schema_migrations_pkey"
        )
        self.connection.commit()

        with self.assertRaisesRegex(
            MigrationRunnerError, "legacy migration ledger structural drift detected"
        ):
            apply_migrations(self.connection)

        self.assertEqual(
            before,
            self.connection.execute(
                "SELECT count(*) FROM sinayxa.schema_migrations"
            ).fetchone()[0],
        )
        self.assertFalse(
            self.connection.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM pg_constraint con
                    JOIN pg_class c ON c.oid = con.conrelid
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE n.nspname = 'sinayxa'
                      AND c.relname = 'schema_migrations'
                      AND con.contype = 'p'
                )
                """
            ).fetchone()[0]
        )


    def test_control_plane_column_default_drift_fails_closed_without_repair(self) -> None:
        apply_migrations(self.connection)
        before = self.connection.execute(
            "SELECT count(*) FROM sinayxa_control.migration_integrity"
        ).fetchone()[0]
        self.connection.execute(
            "ALTER TABLE sinayxa_control.migration_integrity "
            "ALTER COLUMN applied_at DROP DEFAULT"
        )
        self.connection.commit()

        with self.assertRaisesRegex(
            MigrationRunnerError, "control-plane structural drift detected in columns"
        ):
            apply_migrations(self.connection)

        self.assertIsNone(
            self.connection.execute(
                """
                SELECT column_default
                FROM information_schema.columns
                WHERE table_schema = 'sinayxa_control'
                  AND table_name = 'migration_integrity'
                  AND column_name = 'applied_at'
                """
            ).fetchone()[0]
        )
        self.assertEqual(
            before,
            self.connection.execute(
                "SELECT count(*) FROM sinayxa_control.migration_integrity"
            ).fetchone()[0],
        )

    def test_control_plane_column_type_drift_fails_closed_without_repair(self) -> None:
        apply_migrations(self.connection)
        self.connection.execute(
            "ALTER TABLE sinayxa_control.migration_integrity "
            "ALTER COLUMN source_revision TYPE varchar(64)"
        )
        self.connection.commit()

        with self.assertRaisesRegex(
            MigrationRunnerError, "control-plane structural drift detected in columns"
        ):
            apply_migrations(self.connection)

        self.assertEqual(
            "character varying(64)",
            self.connection.execute(
                """
                SELECT format_type(a.atttypid, a.atttypmod)
                FROM pg_attribute a
                JOIN pg_class c ON c.oid = a.attrelid
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = 'sinayxa_control'
                  AND c.relname = 'migration_integrity'
                  AND a.attname = 'source_revision'
                  AND NOT a.attisdropped
                """
            ).fetchone()[0],
        )

if __name__ == "__main__":
    unittest.main()
