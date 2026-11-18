"""Pure unit tests for migration manifest structure and byte integrity."""
from __future__ import annotations

import hashlib
import json
import tempfile
import subprocess
import unittest
from pathlib import Path

from scripts.news_and_events.migration_manifest import (
    MigrationManifestError,
    MigrationRecord,
    _verify_git_provenance,
    load_and_verify_manifest,
)


class MigrationManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.migrations = self.root / "migrations"
        self.migrations.mkdir()
        self.sql_path = self.migrations / "0001_example.sql"
        self.sql_bytes = b"CREATE TABLE example (id integer);\n"
        self.sql_path.write_bytes(self.sql_bytes)
        self.manifest_path = self.root / "manifest.json"
        self.document = {
            "manifest_version": 1,
            "baseline_revision": "a" * 40,
            "migrations": [
                {
                    "version": 1,
                    "migration_id": "example-0001",
                    "path": "0001_example.sql",
                    "sha256": hashlib.sha256(self.sql_bytes).hexdigest(),
                    "source_revision": "b" * 40,
                    "execution_mode": "transactional",
                }
            ],
        }
        self.write_manifest()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_manifest(self) -> None:
        self.manifest_path.write_text(
            json.dumps(self.document), encoding="utf-8"
        )

    def test_accepts_exact_manifest_and_sql_bytes(self) -> None:
        records = load_and_verify_manifest(self.manifest_path, self.migrations)
        self.assertEqual(1, len(records))
        self.assertEqual("example-0001", records[0].migration_id)
        self.assertEqual(hashlib.sha256(self.sql_bytes).hexdigest(), records[0].sha256)

    def test_detects_modified_sql_bytes(self) -> None:
        self.sql_path.write_bytes(self.sql_bytes + b"-- modified\n")
        with self.assertRaisesRegex(MigrationManifestError, "SHA-256 mismatch"):
            load_and_verify_manifest(self.manifest_path, self.migrations)

    def test_rejects_duplicate_json_keys(self) -> None:
        self.manifest_path.write_text(
            '{"manifest_version":1,"manifest_version":1,"baseline_revision":"'
            + "a" * 40
            + '","migrations":[]}',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(MigrationManifestError, "duplicate JSON key"):
            load_and_verify_manifest(self.manifest_path, self.migrations)

    def test_rejects_duplicate_versions(self) -> None:
        duplicate = dict(self.document["migrations"][0])
        duplicate["migration_id"] = "example-0002"
        duplicate["path"] = "0002_example.sql"
        second_path = self.migrations / "0002_example.sql"
        second_path.write_bytes(b"SELECT 2;\n")
        duplicate["sha256"] = hashlib.sha256(second_path.read_bytes()).hexdigest()
        self.document["migrations"].append(duplicate)
        self.write_manifest()
        with self.assertRaisesRegex(MigrationManifestError, "duplicate migration version"):
            load_and_verify_manifest(self.manifest_path, self.migrations)

    def test_rejects_non_increasing_versions(self) -> None:
        second_path = self.migrations / "0002_example.sql"
        second_bytes = b"SELECT 2;\n"
        second_path.write_bytes(second_bytes)
        second = {
            "version": 3,
            "migration_id": "example-0003",
            "path": "0002_example.sql",
            "sha256": hashlib.sha256(second_bytes).hexdigest(),
            "source_revision": "b" * 40,
            "execution_mode": "transactional",
        }
        self.document["migrations"].append(second)
        self.document["migrations"][0]["version"] = 4
        self.write_manifest()
        with self.assertRaisesRegex(MigrationManifestError, "strictly increasing"):
            load_and_verify_manifest(self.manifest_path, self.migrations)

    def test_rejects_path_traversal(self) -> None:
        self.document["migrations"][0]["path"] = "../outside.sql"
        self.write_manifest()
        with self.assertRaisesRegex(MigrationManifestError, "canonical relative"):
            load_and_verify_manifest(self.manifest_path, self.migrations)

    def test_rejects_symlink_escape(self) -> None:
        outside = self.root / "outside.sql"
        outside.write_bytes(self.sql_bytes)
        link = self.migrations / "linked.sql"
        try:
            link.symlink_to(outside)
        except (NotImplementedError, OSError):
            self.skipTest("symlinks are unavailable on this platform")
        self.document["migrations"][0]["path"] = "linked.sql"
        self.write_manifest()
        with self.assertRaisesRegex(MigrationManifestError, "escapes"):
            load_and_verify_manifest(self.manifest_path, self.migrations)

    def test_rejects_unlisted_sql_file(self) -> None:
        (self.migrations / "0002_unlisted.sql").write_text("SELECT 2;\n", encoding="utf-8")
        with self.assertRaisesRegex(MigrationManifestError, "inventory mismatch"):
            load_and_verify_manifest(self.manifest_path, self.migrations)

    def test_rejects_unsupported_execution_mode(self) -> None:
        self.document["migrations"][0]["execution_mode"] = "non_transactional"
        self.write_manifest()
        with self.assertRaisesRegex(MigrationManifestError, "only transactional"):
            load_and_verify_manifest(self.manifest_path, self.migrations)

    def test_rejects_invalid_source_revision(self) -> None:
        self.document["migrations"][0]["source_revision"] = "not-a-git-sha"
        self.write_manifest()
        with self.assertRaisesRegex(MigrationManifestError, "source_revision"):
            load_and_verify_manifest(self.manifest_path, self.migrations)

    def test_rejects_invalid_baseline_revision(self) -> None:
        self.document["baseline_revision"] = "not-a-git-sha"
        self.write_manifest()
        with self.assertRaisesRegex(MigrationManifestError, "baseline_revision"):
            load_and_verify_manifest(self.manifest_path, self.migrations)

    def test_rejects_missing_migration_file(self) -> None:
        self.sql_path.unlink()
        with self.assertRaisesRegex(MigrationManifestError, "does not exist"):
            load_and_verify_manifest(self.manifest_path, self.migrations)

    def test_repository_manifest_matches_all_historical_sql_files(self) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        records = load_and_verify_manifest(
            repository_root / "database" / "migrations" / "manifest.json",
            repository_root / "database" / "migrations",
        )
        self.assertEqual([1, 2, 3, 4, 5], [record.version for record in records])
        self.assertEqual(5, len(records))


    def _git_repository(self) -> tuple[Path, str, str]:
        root = self.root / "git-repository"
        migrations = root / "database" / "migrations"
        migrations.mkdir(parents=True)
        (migrations / "manifest.json").write_text("{}", encoding="utf-8")
        sql = migrations / "0001_example.sql"
        sql.write_bytes(b"CREATE TABLE example (id integer);\\n")

        def git(*args: str) -> str:
            return subprocess.run(
                ["git", "-C", str(root), *args],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ).stdout.strip()

        git("init", "-q")
        git("config", "user.name", "SINAYXA tests")
        git("config", "user.email", "sinayxa-tests@example.invalid")
        git("add", ".")
        git("commit", "-q", "-m", "add migration")
        source_revision = git("rev-parse", "HEAD")
        baseline_revision = source_revision
        return root, baseline_revision, source_revision

    def test_git_provenance_rejects_digest_not_matching_baseline_blob(self) -> None:
        root, baseline, source = self._git_repository()
        record = MigrationRecord(
            version=1,
            migration_id="example-0001",
            path="0001_example.sql",
            sha256="0" * 64,
            source_revision=source,
            execution_mode="transactional",
        )
        with self.assertRaisesRegex(MigrationManifestError, "baseline SHA-256 mismatch"):
            _verify_git_provenance(
                (record,), baseline, root / "database/migrations/manifest.json",
                root / "database/migrations",
            )

    def test_git_provenance_rejects_source_commit_that_did_not_add_path(self) -> None:
        root, baseline, _ = self._git_repository()
        subprocess.run(
            ["git", "-C", str(root), "commit", "--allow-empty", "-m", "unrelated change"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        source = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True, stdout=subprocess.PIPE, text=True,
        ).stdout.strip()
        sql_bytes = (root / "database/migrations/0001_example.sql").read_bytes()
        record = MigrationRecord(
            version=1,
            migration_id="example-0001",
            path="0001_example.sql",
            sha256=hashlib.sha256(sql_bytes).hexdigest(),
            source_revision=source,
            execution_mode="transactional",
        )
        with self.assertRaisesRegex(MigrationManifestError, "source_revision did not add"):
            _verify_git_provenance(
                (record,), baseline, root / "database/migrations/manifest.json",
                root / "database/migrations",
            )


if __name__ == "__main__":
    unittest.main()
