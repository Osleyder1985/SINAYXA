"""Tests for Source & Evidence contract package validation."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.news_and_events.contract_package_validator import (
    ContractPackageError,
    validate_contract_package,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "contracts" / "source-evidence-contract-v0.2.1.json"


class ContractPackageValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.package = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_synthetic_0_2_1_fixture_passes_schema_and_reference_validation(self) -> None:
        self.assertIs(validate_contract_package(self.package), self.package)

    def test_schema_rejects_unknown_root_fields(self) -> None:
        package = copy.deepcopy(self.package)
        package["untyped_extension"] = {"arbitrary": "data"}
        with self.assertRaisesRegex(ContractPackageError, "schema validation failed"):
            validate_contract_package(package)

    def test_duplicate_entity_identity_is_rejected(self) -> None:
        package = copy.deepcopy(self.package)
        package["sources"].append(copy.deepcopy(package["sources"][0]))
        with self.assertRaisesRegex(ContractPackageError, "duplicate source_id"):
            validate_contract_package(package)

    def test_evaluation_unit_cannot_cross_link_another_source_version(self) -> None:
        package = copy.deepcopy(self.package)
        package["evaluation_units"][0]["source_version_id"] = "missing-version"
        with self.assertRaisesRegex(ContractPackageError, "unknown source_version_id"):
            validate_contract_package(package)

    def test_component_cannot_be_attached_to_another_claim(self) -> None:
        package = copy.deepcopy(self.package)
        package["evaluation_units"][0]["claim_id"] = "different-claim"
        with self.assertRaisesRegex(ContractPackageError, "mismatched claim"):
            validate_contract_package(package)

    def test_evidence_link_requires_existing_evidence(self) -> None:
        package = copy.deepcopy(self.package)
        package["claim_evidence_links"][0]["evidence_id"] = "missing-evidence"
        with self.assertRaisesRegex(ContractPackageError, "unknown evidence_id"):
            validate_contract_package(package)

    def test_provenance_edges_require_both_nodes(self) -> None:
        package = copy.deepcopy(self.package)
        package["provenance_edges"][0]["origin_node_id"] = "missing-node"
        with self.assertRaisesRegex(ContractPackageError, "unknown origin_node_id"):
            validate_contract_package(package)

    def test_factor_assessment_requires_known_evaluation_unit(self) -> None:
        package = copy.deepcopy(self.package)
        package["factor_assessments"][0]["assessment_unit_id"] = "missing-unit"
        with self.assertRaisesRegex(ContractPackageError, "unknown assessment_unit_id"):
            validate_contract_package(package)


if __name__ == "__main__":
    unittest.main()
