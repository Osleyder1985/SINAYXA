"""Tests for the persisted contract migration laboratory."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.validation.contract_snapshot_migration_lab import (
    MigrationLabError,
    execute_persisted_migration,
    historical_identifier_sets,
    run_lab,
)


CONTRACT_SOURCE = Path(__file__).resolve().parents[2] / "contract-source"


class ContractSnapshotMigrationLabTests(unittest.TestCase):
    def test_full_lab_passes_and_cleans_up(self) -> None:
        report = run_lab(CONTRACT_SOURCE)
        self.assertEqual("PASS", report["status"])
        self.assertTrue(all(value == "PASS" for value in report["checks"].values()))
        self.assertEqual("PASS", report["cleanup"])
        self.assertFalse(report["production_data_used"])
        self.assertFalse(report["external_services_used"])

    def test_historical_identifier_sets_reject_duplicate_ids(self) -> None:
        package = {collection: [] for collection in (
            "claims", "claim_components", "sources", "source_versions",
            "identity_assessments", "evaluation_units", "evidence_items",
            "evidence_availability", "claim_evidence_links", "provenance_nodes",
            "provenance_edges", "factor_assessments", "independence_assessments",
            "claim_assessments", "retention_records", "audit_events",
        )}
        package["claims"] = [{"claim_id": "claim-1"}, {"claim_id": "claim-1"}]
        with self.assertRaisesRegex(MigrationLabError, "duplicate historical identifier"):
            historical_identifier_sets(package)

    def test_historical_identifier_sets_reject_missing_ids(self) -> None:
        package = {collection: [] for collection in (
            "claims", "claim_components", "sources", "source_versions",
            "identity_assessments", "evaluation_units", "evidence_items",
            "evidence_availability", "claim_evidence_links", "provenance_nodes",
            "provenance_edges", "factor_assessments", "independence_assessments",
            "claim_assessments", "retention_records", "audit_events",
        )}
        package["claims"] = [{"claim_id": ""}]
        with self.assertRaisesRegex(MigrationLabError, "historical identifier missing"):
            historical_identifier_sets(package)

    def test_existing_target_root_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "migration"
            root.mkdir()
            (root / "keep.txt").write_text("preserve", encoding="utf-8")
            with self.assertRaisesRegex(MigrationLabError, "migration root"):
                execute_persisted_migration(root, CONTRACT_SOURCE)
            self.assertEqual("preserve", (root / "keep.txt").read_text(encoding="utf-8"))

    def test_published_target_cannot_be_migrated_twice(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "migration"
            root.mkdir()
            execute_persisted_migration(root, CONTRACT_SOURCE)
            with self.assertRaisesRegex(MigrationLabError, "migration root"):
                execute_persisted_migration(root, CONTRACT_SOURCE)


if __name__ == "__main__":
    unittest.main()
