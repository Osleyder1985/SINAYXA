"""Positive and negative tests for contract 0.2.2 audit minimization."""
import copy
import json
import unittest
from pathlib import Path

from validate_source_evidence_contract_0_2_2 import (
    Contract022Violation, ROOT, validate_catalogs, validate_package,
)


class Contract022AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / "schemas/source-evidence-contract-0.2.2.schema.json").read_text(encoding="utf-8"))
        cls.roles = json.loads((ROOT / "schemas/catalogs/audit-actor-roles-1.0.0.json").read_text(encoding="utf-8"))
        cls.reasons = json.loads((ROOT / "schemas/catalogs/audit-reason-codes-1.0.0.json").read_text(encoding="utf-8"))
        cls.fixture = json.loads((ROOT / "tests/fixtures/contracts/source-evidence-contract-v0.2.2.json").read_text(encoding="utf-8"))

    def test_synthetic_fixture_passes(self):
        validate_package(copy.deepcopy(self.fixture), self.schema, self.roles, self.reasons)

    def test_free_text_legacy_fields_are_rejected(self):
        package = copy.deepcopy(self.fixture)
        package["audit_events"][0]["reason"] = "unrestricted text"
        with self.assertRaises(Contract022Violation):
            validate_package(package, self.schema, self.roles, self.reasons)

    def test_reason_code_must_be_allowed_for_action(self):
        package = copy.deepcopy(self.fixture)
        package["audit_events"][0]["reason_code"] = "COPY_DELETION_VERIFIED"
        with self.assertRaises(Contract022Violation):
            validate_package(package, self.schema, self.roles, self.reasons)

    def test_unknown_actor_role_is_rejected(self):
        package = copy.deepcopy(self.fixture)
        package["audit_events"][0]["actor_role_code"] = "UNCONTROLLED_ROLE"
        with self.assertRaises(Contract022Violation):
            validate_package(package, self.schema, self.roles, self.reasons)

    def test_non_uuid_subject_reference_is_rejected(self):
        package = copy.deepcopy(self.fixture)
        package["audit_events"][0]["subject_ref"] = "evidence-a"
        with self.assertRaises(Contract022Violation):
            validate_package(package, self.schema, self.roles, self.reasons)

    def test_unknown_catalog_version_is_rejected(self):
        package = copy.deepcopy(self.fixture)
        package["audit_events"][0]["reason_catalog_version"] = "9.9.9"
        with self.assertRaises(Contract022Violation):
            validate_package(package, self.schema, self.roles, self.reasons)

    def test_unresolved_subject_token_is_rejected(self):
        package = copy.deepcopy(self.fixture)
        package["retention_records"][0]["subject_ref"] = "00000000-0000-4000-8000-999999999999"
        with self.assertRaises(Contract022Violation):
            validate_package(package, self.schema, self.roles, self.reasons)

    def test_catalog_codes_must_be_unique(self):
        roles = copy.deepcopy(self.roles)
        roles["roles"].append(copy.deepcopy(roles["roles"][0]))
        with self.assertRaises(Contract022Violation):
            validate_catalogs(roles, self.reasons)


if __name__ == "__main__":
    unittest.main(verbosity=2)
