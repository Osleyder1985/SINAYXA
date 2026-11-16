"""Migration 0.2.1 -> 0.2.2 tests: preserve or reject, never infer."""
import copy
import json
import unittest

from migrate_source_evidence_contract_0_2_1_to_0_2_2 import (
    ROOT, MigrationRejected, migrate_package,
)


class Contract022MigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(
            (ROOT / "tests/fixtures/contracts/source-evidence-contract-v0.2.1.json").read_text(encoding="utf-8")
        )
        cls.mappings = {
            "actor_roles": {"SYNTHETIC_TEST": "SYNTHETIC_TEST"},
            "reasons": {
                "Creación de fixture sintético de conformidad.": "RECORD_CREATED",
                "Registro sintético de referencia sin conservar contenido.": "REFERENCE_ONLY_SELECTED",
            },
        }

    @staticmethod
    def _replace_exact(value, replacements):
        if isinstance(value, dict):
            return {key: Contract022MigrationTests._replace_exact(item, replacements) for key, item in value.items()}
        if isinstance(value, list):
            return [Contract022MigrationTests._replace_exact(item, replacements) for item in value]
        if isinstance(value, str):
            return replacements.get(value, value)
        return value

    def _uuid_compatible_source(self):
        replacements = {
            "assessment-entity-v1": "00000000-0000-4000-8000-000000000101",
            "evidence-a": "00000000-0000-4000-8000-000000000102",
            "audit-created": "00000000-0000-4000-8000-000000000201",
            "audit-retention-reference": "00000000-0000-4000-8000-000000000202",
            "retention-a": "00000000-0000-4000-8000-000000000301",
        }
        return self._replace_exact(copy.deepcopy(self.source), replacements)

    def _migrate(self, source, mappings=None):
        return migrate_package(
            source,
            copy.deepcopy(self.mappings if mappings is None else mappings),
            migration_id="migration-0-2-1-to-0-2-2-test",
            executed_at="2026-11-16T12:00:00Z",
            source_snapshot_ref="sha256:source-fixture",
            target_snapshot_ref="",
        )

    def test_semantic_historical_ids_are_rejected_without_mapping_store(self):
        with self.assertRaisesRegex(MigrationRejected, "UUIDv4"):
            self._migrate(copy.deepcopy(self.source))

    def test_uuid_compatible_package_migrates_and_validates(self):
        migrated, manifest = self._migrate(self._uuid_compatible_source())
        self.assertEqual(migrated["contract_version"], "0.2.2")
        self.assertEqual(manifest["status"], "PASS")
        self.assertEqual(migrated["audit_events"][0]["actor_role_code"], "SYNTHETIC_TEST")
        self.assertNotIn("actor_role", migrated["audit_events"][0])
        self.assertNotIn("reason", migrated["audit_events"][0])
        self.assertEqual(
            migrated["audit_subject_tokens"],
            [
                "00000000-0000-4000-8000-000000000101",
                "00000000-0000-4000-8000-000000000102",
            ],
        )

    def test_unmapped_role_is_rejected(self):
        mappings = copy.deepcopy(self.mappings)
        mappings["actor_roles"] = {}
        with self.assertRaisesRegex(MigrationRejected, "actor_role"):
            self._migrate(self._uuid_compatible_source(), mappings)

    def test_unmapped_reason_is_rejected(self):
        mappings = copy.deepcopy(self.mappings)
        mappings["reasons"] = {}
        with self.assertRaisesRegex(MigrationRejected, "reason"):
            self._migrate(self._uuid_compatible_source(), mappings)

    def test_reason_action_mismatch_is_rejected(self):
        mappings = copy.deepcopy(self.mappings)
        mappings["reasons"]["Registro sintético de referencia sin conservar contenido."] = "RECORD_CREATED"
        with self.assertRaisesRegex(MigrationRejected, "not permitted"):
            self._migrate(self._uuid_compatible_source(), mappings)

    def test_non_string_mapping_values_are_rejected(self):
        mappings = copy.deepcopy(self.mappings)
        mappings["actor_roles"]["SYNTHETIC_TEST"] = ["SYNTHETIC_TEST"]
        with self.assertRaisesRegex(MigrationRejected, "string-to-string"):
            self._migrate(self._uuid_compatible_source(), mappings)

    def test_migration_is_deterministic_for_identical_inputs_and_parameters(self):
        source = self._uuid_compatible_source()
        first, first_manifest = self._migrate(source)
        second, second_manifest = self._migrate(source)
        self.assertEqual(first, second)
        self.assertEqual(first_manifest, second_manifest)

    def test_source_package_is_not_mutated(self):
        source = self._uuid_compatible_source()
        original = copy.deepcopy(source)
        self._migrate(source)
        self.assertEqual(source, original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
