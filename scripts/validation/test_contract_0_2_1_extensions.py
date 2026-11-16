"""Unit tests for the five corrective contract 0.2.1 verification areas."""
import copy
import unittest

from contract_0_2_1_extensions import (
    ContractViolation,
    canonical_sha256,
    validate_archive_attestation,
    validate_corroboration,
    validate_independence,
    validate_migration,
    validate_retention_scope,
)


class Contract021ExtensionTests(unittest.TestCase):
    def setUp(self):
        self.units = [
            {"assessment_unit_id": "u1", "source_id": "s1", "source_version_id": "v1",
             "claim_component_version_id": "cv1", "source_type": "SECUNDARIA",
             "assessment_cutoff": "2026-01-02T00:00:00Z"},
            {"assessment_unit_id": "u2", "source_id": "s2", "source_version_id": "v2",
             "claim_component_version_id": "cv1", "source_type": "SECUNDARIA",
             "assessment_cutoff": "2026-01-02T00:00:00Z"},
        ]
        self.paths = [
            {"source_version_id": "v1", "claim_component_version_id": "cv1",
             "relation_type": "ORIGEN_DIRECTO", "origin_id": "origin-1", "source_id": "s1",
             "evidence_source_version_id": "v1",
             "origin_terminal": True, "evidence_ref": "e1", "available_at": "2026-01-01T00:00:00Z"},
            {"source_version_id": "v2", "claim_component_version_id": "cv1",
             "relation_type": "ORIGEN_DIRECTO", "origin_id": "origin-2", "source_id": "s2",
             "evidence_source_version_id": "v2",
             "origin_terminal": True, "evidence_ref": "e2", "available_at": "2026-01-01T00:00:00Z"},
        ]
        self.cutoff = "2026-01-02T00:00:00Z"

    def test_independent_distinct_observation_paths_pass(self):
        validate_independence(self.units, self.paths, self.cutoff)

    def test_independence_rejects_two_versions_of_same_source(self):
        units = copy.deepcopy(self.units)
        units[1]["source_id"] = "s1"
        with self.assertRaises(ContractViolation):
            validate_independence(units, self.paths, self.cutoff)

    def test_independence_rejects_shared_terminal_origin(self):
        paths = copy.deepcopy(self.paths)
        paths[1]["origin_id"] = "origin-1"
        with self.assertRaises(ContractViolation):
            validate_independence(self.units, paths, self.cutoff)

    def test_independence_rejects_late_path_evidence(self):
        paths = copy.deepcopy(self.paths)
        paths[1]["available_at"] = "2026-01-03T00:00:00Z"
        with self.assertRaises(ContractViolation):
            validate_independence(self.units, paths, self.cutoff)

    def test_independence_rejects_missing_source_path(self):
        with self.assertRaises(ContractViolation):
            validate_independence(self.units, self.paths[:1], self.cutoff)

    def test_secondary_corroboration_requires_reviewed_coverage(self):
        validate_corroboration(
            "CORROBORADA", "CORROBORACION_INDEPENDIENTE", self.units, [],
            {"u1", "u2"}, self.cutoff
        )

    def test_secondary_corroboration_rejects_incomplete_review(self):
        with self.assertRaises(ContractViolation):
            validate_corroboration(
                "CORROBORADA", "CORROBORACION_INDEPENDIENTE", self.units, [],
                {"u1"}, self.cutoff
            )

    def test_primary_statement_scope_passes_only_for_direct_act(self):
        primary = [{"source_type": "PRIMARIA", "authenticity_status": "AUTENTICADA",
                    "access_status": "PÚBLICO_LEGÍTIMO", "knowledge_basis": "REGISTRO_ORIGINAL",
                    "scope_note": "La institución emitió el comunicado.",
                    "available_at": "2026-01-01T00:00:00Z"}]
        validate_corroboration(
            "CORROBORADA", "EVIDENCIA_PRIMARIA_DIRECTA",
            [{"assessment_unit_id": "u1", "source_id": "s1", "source_type": "PRIMARIA"}],
            primary, set(), self.cutoff
        )

    def test_ambas_requires_independence_even_when_primary_evidence_exists(self):
        primary = [{"source_type": "PRIMARIA", "authenticity_status": "AUTENTICADA",
                    "access_status": "PÚBLICO_LEGÍTIMO", "knowledge_basis": "REGISTRO_ORIGINAL",
                    "scope_note": "La institución emitió el documento.",
                    "available_at": "2026-01-01T00:00:00Z"}]
        primary_units = [
            {"assessment_unit_id": "u1", "source_id": "s1", "source_type": "PRIMARIA"},
            {"assessment_unit_id": "u2", "source_id": "s2", "source_type": "PRIMARIA"},
        ]
        with self.assertRaises(ContractViolation):
            validate_corroboration("CORROBORADA", "AMBAS", primary_units, primary, set(), self.cutoff)
        validate_corroboration("CORROBORADA", "AMBAS", primary_units, primary, {"u1", "u2"}, self.cutoff)

    def test_primary_authenticity_does_not_allow_unsupported_external_claim(self):
        primary = [{"source_type": "PRIMARIA", "authenticity_status": "AUTENTICADA",
                    "access_status": "PÚBLICO_LEGÍTIMO", "knowledge_basis": "DOCUMENTO_DE_TERCEROS",
                    "scope_note": "La institución repite un dato externo.",
                    "available_at": "2026-01-01T00:00:00Z"}]
        with self.assertRaises(ContractViolation):
            validate_corroboration(
                "CORROBORADA", "EVIDENCIA_PRIMARIA_DIRECTA",
                [{"assessment_unit_id": "u1", "source_id": "s1", "source_type": "PRIMARIA"}],
                primary, set(), self.cutoff
            )

    def test_retained_copy_inventory_has_discovery_audit(self):
        copies = [{"copy_id": "primary", "retention_id": "retention-a", "subject_ref": "evidence-a", "parent_copy_id": None, "state": "PRESENT",
                   "previous_state": None, "transition_event_ref": "event-1", "recorded_at": "2026-01-01T00:00:00Z"}]
        events = [{"audit_event_id": "event-1", "copy_id": "primary", "retention_id": "retention-a", "subject_ref": "evidence-a",
                   "from_copy_state": None, "to_copy_state": "PRESENT",
                   "action": "COPY_DISCOVERED", "actor_role": "DATA_CUSTODIAN",
                   "occurred_at": "2026-01-01T00:00:00Z", "reason": "Synthetic copy inventory"}]
        validate_retention_scope("RETAIN", copies, events)

    def test_delete_pending_requires_outstanding_copy_inventory(self):
        copies = [{"copy_id": "primary", "retention_id": "retention-a", "subject_ref": "evidence-a", "parent_copy_id": None, "state": "DELETE_PENDING",
                   "previous_state": "PRESENT", "transition_event_ref": "event-1", "recorded_at": "2026-01-01T00:00:00Z"}]
        events = [{"audit_event_id": "event-1", "copy_id": "primary", "retention_id": "retention-a", "subject_ref": "evidence-a",
                   "from_copy_state": "PRESENT", "to_copy_state": "DELETE_PENDING",
                   "action": "COPY_DELETION_REQUESTED", "actor_role": "DATA_CUSTODIAN",
                   "occurred_at": "2026-01-01T00:00:00Z", "reason": "Synthetic deletion request"}]
        validate_retention_scope("DELETE_PENDING", copies, events)

    def test_deleted_requires_every_copy_and_derivative_verified(self):
        copies = [
            {"copy_id": "primary", "retention_id": "retention-a", "subject_ref": "evidence-a", "parent_copy_id": None, "state": "DELETED", "previous_state": "DELETE_PENDING",
             "transition_event_ref": "event-1", "recorded_at": "2026-01-01T01:00:00Z", "verified_at": "2026-01-01T01:00:00Z", "verification_reference": "verify-1"},
            {"copy_id": "replica", "retention_id": "retention-a", "subject_ref": "evidence-a", "parent_copy_id": "primary", "state": "DELETED", "previous_state": "DELETE_PENDING",
             "transition_event_ref": "event-2", "recorded_at": "2026-01-01T01:01:00Z", "verified_at": "2026-01-01T01:01:00Z", "verification_reference": "verify-2"},
        ]
        events = [
            {"audit_event_id": "event-1", "copy_id": "primary", "retention_id": "retention-a", "subject_ref": "evidence-a", "from_copy_state": "DELETE_PENDING", "to_copy_state": "DELETED",
             "action": "COPY_DELETED", "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-01-01T01:00:00Z", "reason": "Verified"},
            {"audit_event_id": "event-2", "copy_id": "replica", "retention_id": "retention-a", "subject_ref": "evidence-a", "from_copy_state": "DELETE_PENDING", "to_copy_state": "DELETED",
             "action": "COPY_DELETED", "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-01-01T01:01:00Z", "reason": "Verified"},
        ]
        validate_retention_scope("DELETED", copies, events)

    def test_deleted_rejects_unverified_backup(self):
        copies = [
            {"copy_id": "primary", "retention_id": "retention-a", "subject_ref": "evidence-a", "parent_copy_id": None, "state": "DELETED", "previous_state": "DELETE_PENDING",
             "transition_event_ref": "event-1", "recorded_at": "2026-01-01T01:00:00Z", "verified_at": "2026-01-01T01:00:00Z", "verification_reference": "verify-1"},
            {"copy_id": "backup", "retention_id": "retention-a", "subject_ref": "evidence-a", "parent_copy_id": "primary", "state": "DELETE_PENDING", "previous_state": "PRESENT",
             "transition_event_ref": "event-2", "recorded_at": "2026-01-01T01:01:00Z"},
        ]
        events = [
            {"audit_event_id": "event-1", "copy_id": "primary", "retention_id": "retention-a", "subject_ref": "evidence-a", "from_copy_state": "DELETE_PENDING", "to_copy_state": "DELETED",
             "action": "COPY_DELETED", "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-01-01T01:00:00Z", "reason": "Verified"},
            {"audit_event_id": "event-2", "copy_id": "backup", "retention_id": "retention-a", "subject_ref": "evidence-a", "from_copy_state": "PRESENT", "to_copy_state": "DELETE_PENDING",
             "action": "COPY_DELETION_REQUESTED", "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-01-01T01:01:00Z", "reason": "Pending"},
        ]
        with self.assertRaises(ContractViolation):
            validate_retention_scope("DELETED", copies, events)

    def test_retention_rejects_missing_copy_transition(self):
        copies = [{"copy_id": "primary", "retention_id": "retention-a", "subject_ref": "evidence-a", "parent_copy_id": None, "state": "DELETE_PENDING",
                   "previous_state": "PRESENT", "transition_event_ref": "missing", "recorded_at": "2026-01-01T00:00:00Z"}]
        with self.assertRaises(ContractViolation):
            validate_retention_scope("DELETE_PENDING", copies, [])

    def test_archive_capture_verified_for_cutoff_passes_without_authenticating_content(self):
        availability = {"availability_basis": "INDEPENDENT_ARCHIVE",
                        "available_at": "2026-01-01T00:00:00Z"}
        attestation = {"archive_service": "Synthetic Archive", "capture_record_reference": "capture-1",
                       "captured_at": "2026-01-01T00:00:00Z", "integrity_result": "MATCH",
                       "capture_record_verified": True, "content_authenticity": "UNKNOWN",
                       "content_truth": "UNKNOWN"}
        validate_archive_attestation(availability, attestation, self.cutoff)

    def test_archive_timestamp_without_capture_proof_is_rejected(self):
        availability = {"availability_basis": "INDEPENDENT_ARCHIVE",
                        "available_at": "2026-01-01T00:00:00Z"}
        attestation = {"archive_service": "Synthetic Archive", "capture_record_reference": "capture-1",
                       "captured_at": "2026-01-01T00:00:00Z", "integrity_result": "NOT_CHECKED",
                       "capture_record_verified": False, "content_authenticity": "UNKNOWN",
                       "content_truth": "UNKNOWN"}
        with self.assertRaises(ContractViolation):
            validate_archive_attestation(availability, attestation, self.cutoff)

    def test_archive_cannot_promote_authenticity(self):
        availability = {"availability_basis": "INDEPENDENT_ARCHIVE",
                        "available_at": "2026-01-01T00:00:00Z"}
        attestation = {"archive_service": "Synthetic Archive", "capture_record_reference": "capture-1",
                       "captured_at": "2026-01-01T00:00:00Z", "integrity_result": "MATCH",
                       "capture_record_verified": True, "content_authenticity": "AUTENTICADA",
                       "content_truth": "UNKNOWN"}
        with self.assertRaises(ContractViolation):
            validate_archive_attestation(availability, attestation, self.cutoff)

    def test_migration_preserves_historical_records_and_versions(self):
        source = {"contract_version": "0.2.0", "methodology_version": "16-approved",
                  "claims": [{"claim_id": "c1"}], "claim_components": [], "sources": [],
                  "source_versions": [], "identity_assessments": [], "evaluation_units": [],
                  "evidence_items": [], "evidence_availability": [], "claim_evidence_links": [],
                  "provenance_nodes": [], "provenance_edges": [], "factor_assessments": [],
                  "independence_assessments": [], "claim_assessments": [], "retention_records": [],
                  "audit_events": []}
        target = copy.deepcopy(source)
        target["contract_version"] = "0.2.1"
        manifest = {"migration_id": "m1", "migrator_version": "1.0.0",
                    "source_contract_version": "0.2.0", "target_contract_version": "0.2.1",
                    "input_sha256": canonical_sha256(source), "output_sha256": canonical_sha256(target),
                    "rules_applied": ["preserve-history"], "result": "PASS"}
        validate_migration(source, target, manifest)

    def test_migration_rejects_dropped_unknown_source_field(self):
        source = {"contract_version": "0.2.0", "extension_metadata": {"opaque_value": "preserve"},
                  "claims": [], "claim_components": [], "sources": [], "source_versions": [],
                  "identity_assessments": [], "evaluation_units": [], "evidence_items": [],
                  "evidence_availability": [], "claim_evidence_links": [], "provenance_nodes": [],
                  "provenance_edges": [], "factor_assessments": [], "independence_assessments": [],
                  "claim_assessments": [], "retention_records": [], "audit_events": []}
        target = copy.deepcopy(source)
        target["contract_version"] = "0.2.1"
        target.pop("extension_metadata")
        manifest = {"migration_id": "m3", "migrator_version": "1.0.0",
                    "source_contract_version": "0.2.0", "target_contract_version": "0.2.1",
                    "input_sha256": canonical_sha256(source), "output_sha256": canonical_sha256(target),
                    "rules_applied": ["preserve-history"], "result": "PASS"}
        with self.assertRaises(ContractViolation):
            validate_migration(source, target, manifest)

    def test_migration_rejects_historical_status_change(self):
        source = {"contract_version": "0.2.0", "claims": [{"claim_id": "c1"}],
                  "claim_components": [], "sources": [], "source_versions": [],
                  "identity_assessments": [], "evaluation_units": [], "evidence_items": [],
                  "evidence_availability": [], "claim_evidence_links": [], "provenance_nodes": [],
                  "provenance_edges": [], "factor_assessments": [], "independence_assessments": [],
                  "claim_assessments": [{"evidentiary_status": "NO_RESUELTA"}],
                  "retention_records": [], "audit_events": []}
        target = copy.deepcopy(source)
        target["contract_version"] = "0.2.1"
        target["claim_assessments"][0]["evidentiary_status"] = "CORROBORADA"
        manifest = {"migration_id": "m2", "migrator_version": "1.0.0",
                    "source_contract_version": "0.2.0", "target_contract_version": "0.2.1",
                    "input_sha256": canonical_sha256(source), "output_sha256": canonical_sha256(target),
                    "rules_applied": ["preserve-history"], "result": "PASS"}
        with self.assertRaises(ContractViolation):
            validate_migration(source, target, manifest)


if __name__ == "__main__":
    unittest.main(verbosity=2)
