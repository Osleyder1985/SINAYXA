"""Migration 0.2.1 -> 0.2.2 tests: preserve or reject, never infer."""
import copy
import json
import unittest

from migrate_source_evidence_contract_0_2_1_to_0_2_2 import (
    ROOT, MigrationRejected, canonical_bytes, sha256, migrate_package,
)


class Contract022MigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(
            (ROOT / "tests/fixtures/contracts/source-evidence-contract-v0.2.1.json").read_text(encoding="utf-8")
        )


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

    @staticmethod
    def _mapping_for(source):
        evidence_refs = [item["evidence_id"] for item in source.get("evidence_items", [])]
        action_codes = {
            "CREATED": "RECORD_CREATED",
            "REFERENCE_ONLY": "REFERENCE_ONLY_SELECTED",
        }
        roles = {}
        reasons = {}
        for event in source.get("audit_events", []):
            roles[event["actor_role"]] = {
                "target_code": "SYSTEM",
                "evidence_refs": evidence_refs,
                "rationale": "Correspondencia artificial limitada al fixture sintético; no reutilizable en datos reales.",
            }
            reasons[event["reason"]] = {
                "target_code": action_codes[event["action"]],
                "evidence_refs": evidence_refs,
                "rationale": "Correspondencia artificial limitada al fixture sintético y a la acción declarada.",
            }
        return {"actor_roles": roles, "reasons": reasons}

    def _migrate(self, source, mappings=None):
        return migrate_package(
            source,
            copy.deepcopy(self._mapping_for(source) if mappings is None else mappings),
            migration_id="migration-0-2-1-to-0-2-2-test",
            executed_at="2026-11-16T12:00:00Z",
            source_snapshot_ref="sha256:" + sha256(canonical_bytes(source)),
            target_snapshot_ref="",
        )

    def test_semantic_historical_ids_are_rejected_without_mapping_store(self):
        with self.assertRaisesRegex(MigrationRejected, "UUIDv4"):
            self._migrate(copy.deepcopy(self.source))

    def test_uuid_compatible_package_migrates_and_validates(self):
        migrated, manifest = self._migrate(self._uuid_compatible_source())
        self.assertEqual(migrated["contract_version"], "0.2.2")
        self.assertEqual(manifest["status"], "PASS")
        self.assertEqual(migrated["audit_events"][0]["actor_role_code"], "SYSTEM")
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
        mappings = self._mapping_for(self._uuid_compatible_source())
        mappings["actor_roles"] = {}
        with self.assertRaisesRegex(MigrationRejected, "actor_role"):
            self._migrate(self._uuid_compatible_source(), mappings)

    def test_unmapped_reason_is_rejected(self):
        mappings = self._mapping_for(self._uuid_compatible_source())
        mappings["reasons"] = {}
        with self.assertRaisesRegex(MigrationRejected, "reason"):
            self._migrate(self._uuid_compatible_source(), mappings)

    def test_reason_action_mismatch_is_rejected(self):
        mappings = self._mapping_for(self._uuid_compatible_source())
        mappings["reasons"]["Registro sintético de referencia sin conservar contenido."]["target_code"] = "RECORD_CREATED"
        with self.assertRaisesRegex(MigrationRejected, "not permitted"):
            self._migrate(self._uuid_compatible_source(), mappings)

    def test_non_object_mapping_entries_are_rejected(self):
        mappings = self._mapping_for(self._uuid_compatible_source())
        mappings["actor_roles"]["SYNTHETIC_TEST"] = ["SYSTEM"]
        with self.assertRaisesRegex(MigrationRejected, "mapping entry"):
            self._migrate(self._uuid_compatible_source(), mappings)

    def test_stale_mapping_entries_are_rejected(self):
        mappings = self._mapping_for(self._uuid_compatible_source())
        mappings["actor_roles"]["OLD_UNUSED_ROLE"] = {"target_code": "SYSTEM", "evidence_refs": ["evidence-a"], "rationale": "stale"}
        with self.assertRaisesRegex(MigrationRejected, "exactly match"):
            self._migrate(self._uuid_compatible_source(), mappings)

    def test_mapping_root_must_be_an_object(self):
        with self.assertRaisesRegex(MigrationRejected, "mapping file root"):
            self._migrate(self._uuid_compatible_source(), [])

    def test_source_root_must_be_an_object(self):
        with self.assertRaisesRegex(MigrationRejected, "source package root"):
            self._migrate([], {})

    def test_mapping_requires_resolvable_evidence_references(self):
        source = self._uuid_compatible_source()
        mappings = self._mapping_for(source)
        mappings["actor_roles"]["SYNTHETIC_TEST"]["evidence_refs"] = ["missing-evidence"]
        with self.assertRaisesRegex(MigrationRejected, "evidence_refs"):
            self._migrate(source, mappings)

    def test_mapping_requires_non_empty_rationale(self):
        source = self._uuid_compatible_source()
        mappings = self._mapping_for(source)
        mappings["actor_roles"]["SYNTHETIC_TEST"]["rationale"] = " "
        with self.assertRaisesRegex(MigrationRejected, "rationale"):
            self._migrate(source, mappings)

    def test_source_snapshot_reference_must_match_canonical_input_hash(self):
        source = self._uuid_compatible_source()
        with self.assertRaisesRegex(MigrationRejected, "source_snapshot_ref"):
            migrate_package(
                source, self._mapping_for(source),
                migration_id="migration-0-2-1-to-0-2-2-test",
                executed_at="2026-11-16T12:00:00Z",
                source_snapshot_ref="sha256:incorrect",
                target_snapshot_ref="",
            )

    def test_duplicate_migration_id_is_rejected(self):
        source = self._uuid_compatible_source()
        source["migration_records"].append({
            "migration_id": "migration-0-2-1-to-0-2-2-test",
            "source_contract_version": "0.2.0",
            "target_contract_version": "0.2.1",
            "migrator_version": "0.1.0",
            "executed_at": "2026-11-15T12:00:00Z",
            "input_sha256": "0" * 64,
            "output_sha256": "1" * 64,
            "rules_applied": ["HISTORICAL_TEST"],
            "result": "PASS",
            "loss_report": [],
            "source_snapshot_ref": "sha256:" + "0" * 64,
            "target_snapshot_ref": "sha256:" + "1" * 64,
        })
        with self.assertRaisesRegex(MigrationRejected, "migration_id already exists"):
            self._migrate(source)

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
