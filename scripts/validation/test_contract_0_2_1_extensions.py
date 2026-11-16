"""Unit tests for the five corrective contract 0.2.1 verification areas."""
import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from validate_source_evidence_contract_0_2_1 import _available_at, validate_package
from migrate_source_evidence_contract_0_2_0_to_0_2_1 import migrate_package

from contract_0_2_1_extensions import (
    ContractViolation,
    canonical_sha256,
    canonical_migration_payload_sha256,
    validate_analytic_replication,
    validate_archive_attestation,
    validate_corroboration,
    validate_independence,
    validate_migration,
    validate_retention_scope,
    validate_backup_expiration_policy,
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

    def archive_evidence(self):
        return {
            "evidence_id": "evidence-a",
            "source_version_id": "version-a1",
            "integrity_check": {
                "algorithm": "SHA-256",
                "observed_digest": "a" * 64,
                "result": "MATCH",
            },
        }

    def archive_attestation_base(self):
        return {
            "evidence_id": "evidence-a",
            "source_version_id": "version-a1",
            "captured_content_hash": "a" * 64,
            "hash_algorithm": "SHA-256",
        }

    def set_archive_evidence_integrity(self, package):
        item = next(item for item in package["evidence_items"] if item["evidence_id"] == "evidence-a")
        item["integrity_check"] = {
            "algorithm": "SHA-256",
            "expected_digest": "a" * 64,
            "observed_digest": "a" * 64,
            "checked_at": "2026-11-15T20:03:00Z",
            "result": "MATCH",
        }

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

    def test_separate_analysis_over_common_data_is_not_origin_independence(self):
        paths = copy.deepcopy(self.paths)
        paths[1]["relation_type"] = "ANÁLISIS_SEPARADO_SOBRE_DATOS_COMUNES"
        with self.assertRaises(ContractViolation):
            validate_independence(self.units, paths, self.cutoff)

    def test_independence_rejects_missing_source_path(self):
        with self.assertRaises(ContractViolation):
            validate_independence(self.units, self.paths[:1], self.cutoff)

    def test_distinct_analysis_processes_over_common_dataset_are_representable(self):
        analyses = [
            {"process_id": "analysis-process-1", "dataset_origin_id": "dataset-common",
             "claim_component_version_id": "cv1", "method_reference": "method-1",
             "output_evidence_ref": "analysis-output-1", "available_at": "2026-01-01T00:00:00Z",
             "assessment_cutoff": self.cutoff},
            {"process_id": "analysis-process-2", "dataset_origin_id": "dataset-common",
             "claim_component_version_id": "cv1", "method_reference": "method-2",
             "output_evidence_ref": "analysis-output-2", "available_at": "2026-01-01T00:00:00Z",
             "assessment_cutoff": self.cutoff},
        ]
        validate_analytic_replication(analyses, self.cutoff)

    def test_analytic_replication_rejects_same_process_or_late_output(self):
        analyses = [
            {"process_id": "same-process", "dataset_origin_id": "dataset-common",
             "claim_component_version_id": "cv1", "method_reference": "method-1",
             "output_evidence_ref": "analysis-output-1", "available_at": "2026-01-01T00:00:00Z",
             "assessment_cutoff": self.cutoff},
            {"process_id": "same-process", "dataset_origin_id": "dataset-common",
             "claim_component_version_id": "cv1", "method_reference": "method-2",
             "output_evidence_ref": "analysis-output-2", "available_at": "2026-01-03T00:00:00Z",
             "assessment_cutoff": self.cutoff},
        ]
        with self.assertRaises(ContractViolation):
            validate_analytic_replication(analyses, self.cutoff)
        analyses[1]["process_id"] = "analysis-process-2"
        with self.assertRaises(ContractViolation):
            validate_analytic_replication(analyses, self.cutoff)

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
        primary = [{"source_type": "PRIMARIA", "source_id": "s1", "source_version_id": "v1",
                    "authenticity_status": "AUTENTICADA", "access_status": "PÚBLICO_LEGÍTIMO", "unit_access_status": "PÚBLICO_LEGÍTIMO",
                    "knowledge_basis": "REGISTRO_ORIGINAL", "scope_note": "La institución emitió el comunicado.",
                    "available_at": "2026-01-01T00:00:00Z"}]
        validate_corroboration(
            "CORROBORADA", "EVIDENCIA_PRIMARIA_DIRECTA",
            [{"assessment_unit_id": "u1", "source_id": "s1", "source_version_id": "v1",
             "claim_component_version_id": "cv1", "assessment_cutoff": self.cutoff, "source_type": "PRIMARIA"}],
            primary, set(), self.cutoff
        )

    def test_primary_evidence_from_unrelated_source_cannot_corroborate(self):
        primary = [{"source_type": "PRIMARIA", "source_id": "other-source", "source_version_id": "other-version",
                    "authenticity_status": "AUTENTICADA", "access_status": "PÚBLICO_LEGÍTIMO", "unit_access_status": "PÚBLICO_LEGÍTIMO",
                    "knowledge_basis": "REGISTRO_ORIGINAL", "scope_note": "Acto directamente acreditado.",
                    "available_at": "2026-01-01T00:00:00Z"}]
        units = [{"assessment_unit_id": "u1", "source_id": "s1", "source_version_id": "v1",
                  "claim_component_version_id": "cv1", "assessment_cutoff": self.cutoff,
                  "source_type": "PRIMARIA"}]
        with self.assertRaises(ContractViolation):
            validate_corroboration("CORROBORADA", "EVIDENCIA_PRIMARIA_DIRECTA",
                                   units, primary, set(), self.cutoff)

    def test_corroboration_rejects_mixed_component_versions(self):
        units = copy.deepcopy(self.units)
        units[1]["claim_component_version_id"] = "cv2"
        with self.assertRaises(ContractViolation):
            validate_corroboration("CORROBORADA", "CORROBORACION_INDEPENDIENTE",
                                   units, [], {"u1", "u2"}, self.cutoff)

    def test_ambas_requires_independence_even_when_primary_evidence_exists(self):
        primary = [{"source_type": "PRIMARIA", "source_id": "s1", "source_version_id": "v1",
                    "authenticity_status": "AUTENTICADA", "access_status": "PÚBLICO_LEGÍTIMO", "unit_access_status": "PÚBLICO_LEGÍTIMO",
                    "knowledge_basis": "REGISTRO_ORIGINAL", "scope_note": "La institución emitió el documento.",
                    "available_at": "2026-01-01T00:00:00Z"}]
        primary_units = [
            {"assessment_unit_id": "u1", "source_id": "s1", "source_version_id": "v1",
             "claim_component_version_id": "cv1", "assessment_cutoff": self.cutoff, "source_type": "PRIMARIA"},
            {"assessment_unit_id": "u2", "source_id": "s2", "source_version_id": "v2",
             "claim_component_version_id": "cv1", "assessment_cutoff": self.cutoff, "source_type": "SECUNDARIA"},
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
                [{"assessment_unit_id": "u1", "source_id": "s1", "source_version_id": "v1",
                 "claim_component_version_id": "cv1", "assessment_cutoff": self.cutoff, "source_type": "PRIMARIA"}],
                primary, set(), self.cutoff
            )

    def test_retained_copy_inventory_has_discovery_audit(self):
        copies = [{"copy_id": "primary", "retention_id": "retention-a", "subject_ref": "evidence-a",
                   "parent_copy_id": None, "state": "PRESENT", "previous_state": None,
                   "transition_event_ref": "event-1", "recorded_at": "2026-01-01T00:00:00Z"}]
        events = [{"audit_event_id": "event-1", "copy_id": "primary", "retention_id": "retention-a",
                   "subject_ref": "evidence-a", "from_copy_state": None, "to_copy_state": "PRESENT",
                   "action": "COPY_DISCOVERED", "actor_role": "DATA_CUSTODIAN",
                   "occurred_at": "2026-01-01T00:00:00Z", "reason": "Synthetic copy inventory"}]
        validate_retention_scope("RETAIN", copies, events)

    def test_reference_only_retains_no_content_after_verified_copy_deletion(self):
        copies = [{"copy_id": "primary", "retention_id": "retention-a", "subject_ref": "evidence-a",
                   "parent_copy_id": None, "state": "DELETED", "previous_state": "DELETE_PENDING",
                   "transition_event_ref": "event-3", "recorded_at": "2026-01-01T00:03:00Z",
                   "verified_at": "2026-01-01T00:03:00Z", "verification_reference": "verify-1"}]
        events = [
            {"audit_event_id": "event-1", "copy_id": "primary", "retention_id": "retention-a",
             "subject_ref": "evidence-a", "from_copy_state": None, "to_copy_state": "PRESENT",
             "action": "COPY_DISCOVERED", "actor_role": "DATA_CUSTODIAN",
             "occurred_at": "2026-01-01T00:01:00Z", "reason": "Discovered"},
            {"audit_event_id": "event-2", "copy_id": "primary", "retention_id": "retention-a",
             "subject_ref": "evidence-a", "from_copy_state": "PRESENT", "to_copy_state": "DELETE_PENDING",
             "action": "COPY_DELETION_REQUESTED", "actor_role": "DATA_CUSTODIAN",
             "occurred_at": "2026-01-01T00:02:00Z", "reason": "Requested"},
            {"audit_event_id": "event-3", "copy_id": "primary", "retention_id": "retention-a",
             "subject_ref": "evidence-a", "from_copy_state": "DELETE_PENDING", "to_copy_state": "DELETED",
             "action": "COPY_DELETED", "actor_role": "DATA_CUSTODIAN",
             "occurred_at": "2026-01-01T00:03:00Z", "reason": "Verified deletion"},
        ]
        validate_retention_scope("REFERENCE_ONLY", copies, events)

    def test_delete_pending_requires_outstanding_copy_inventory(self):
        copies = [{"copy_id": "primary", "retention_id": "retention-a", "subject_ref": "evidence-a",
                   "parent_copy_id": None, "state": "DELETE_PENDING", "previous_state": "PRESENT",
                   "transition_event_ref": "event-2", "recorded_at": "2026-01-01T00:02:00Z"}]
        events = [
            {"audit_event_id": "event-1", "copy_id": "primary", "retention_id": "retention-a",
             "subject_ref": "evidence-a", "from_copy_state": None, "to_copy_state": "PRESENT",
             "action": "COPY_DISCOVERED", "actor_role": "DATA_CUSTODIAN",
             "occurred_at": "2026-01-01T00:01:00Z", "reason": "Discovered"},
            {"audit_event_id": "event-2", "copy_id": "primary", "retention_id": "retention-a",
             "subject_ref": "evidence-a", "from_copy_state": "PRESENT", "to_copy_state": "DELETE_PENDING",
             "action": "COPY_DELETION_REQUESTED", "actor_role": "DATA_CUSTODIAN",
             "occurred_at": "2026-01-01T00:02:00Z", "reason": "Synthetic deletion request"},
        ]
        validate_retention_scope("DELETE_PENDING", copies, events)

    def test_deleted_requires_every_copy_and_derivative_verified(self):
        copies = [
            {"copy_id": "primary", "retention_id": "retention-a", "subject_ref": "evidence-a",
             "parent_copy_id": None, "state": "DELETED", "previous_state": "DELETE_PENDING",
             "transition_event_ref": "event-3", "recorded_at": "2026-01-01T00:03:00Z",
             "verified_at": "2026-01-01T00:03:00Z", "verification_reference": "verify-1"},
            {"copy_id": "replica", "retention_id": "retention-a", "subject_ref": "evidence-a",
             "parent_copy_id": "primary", "state": "DELETED", "previous_state": "DELETE_PENDING",
             "transition_event_ref": "event-6", "recorded_at": "2026-01-01T00:06:00Z",
             "verified_at": "2026-01-01T00:06:00Z", "verification_reference": "verify-2"},
        ]
        events = []
        for copy_id, start_minute in (("primary", 1), ("replica", 4)):
            states = [
                (None, "PRESENT", "COPY_DISCOVERED"),
                ("PRESENT", "DELETE_PENDING", "COPY_DELETION_REQUESTED"),
                ("DELETE_PENDING", "DELETED", "COPY_DELETED"),
            ]
            for offset, (before, after, action) in enumerate(states):
                minute = start_minute + offset
                event_id = f"{copy_id}-event-{offset + 1}"
                events.append({
                    "audit_event_id": event_id, "copy_id": copy_id, "retention_id": "retention-a",
                    "subject_ref": "evidence-a", "from_copy_state": before, "to_copy_state": after,
                    "action": action, "actor_role": "DATA_CUSTODIAN",
                    "occurred_at": f"2026-01-01T00:{minute:02d}:00Z", "reason": "Synthetic lifecycle transition"
                })
        copies[0]["transition_event_ref"] = "primary-event-3"
        copies[1]["transition_event_ref"] = "replica-event-3"
        validate_retention_scope("DELETED", copies, events)

    def test_deleted_rejects_unverified_backup(self):
        copies = [
            {"copy_id": "primary", "retention_id": "retention-a", "subject_ref": "evidence-a",
             "parent_copy_id": None, "state": "DELETED", "previous_state": "DELETE_PENDING",
             "transition_event_ref": "primary-event-3", "recorded_at": "2026-01-01T00:03:00Z",
             "verified_at": "2026-01-01T00:03:00Z", "verification_reference": "verify-1"},
            {"copy_id": "backup", "retention_id": "retention-a", "subject_ref": "evidence-a",
             "parent_copy_id": "primary", "state": "DELETE_PENDING", "previous_state": "PRESENT",
             "transition_event_ref": "backup-event-2", "recorded_at": "2026-01-01T00:05:00Z"},
        ]
        events = [
            {"audit_event_id": "primary-event-1", "copy_id": "primary", "retention_id": "retention-a",
             "subject_ref": "evidence-a", "from_copy_state": None, "to_copy_state": "PRESENT",
             "action": "COPY_DISCOVERED", "actor_role": "DATA_CUSTODIAN",
             "occurred_at": "2026-01-01T00:01:00Z", "reason": "Discovered"},
            {"audit_event_id": "primary-event-2", "copy_id": "primary", "retention_id": "retention-a",
             "subject_ref": "evidence-a", "from_copy_state": "PRESENT", "to_copy_state": "DELETE_PENDING",
             "action": "COPY_DELETION_REQUESTED", "actor_role": "DATA_CUSTODIAN",
             "occurred_at": "2026-01-01T00:02:00Z", "reason": "Requested"},
            {"audit_event_id": "primary-event-3", "copy_id": "primary", "retention_id": "retention-a",
             "subject_ref": "evidence-a", "from_copy_state": "DELETE_PENDING", "to_copy_state": "DELETED",
             "action": "COPY_DELETED", "actor_role": "DATA_CUSTODIAN",
             "occurred_at": "2026-01-01T00:03:00Z", "reason": "Verified"},
            {"audit_event_id": "backup-event-1", "copy_id": "backup", "retention_id": "retention-a",
             "subject_ref": "evidence-a", "from_copy_state": None, "to_copy_state": "PRESENT",
             "action": "COPY_DISCOVERED", "actor_role": "DATA_CUSTODIAN",
             "occurred_at": "2026-01-01T00:04:00Z", "reason": "Backup discovered"},
            {"audit_event_id": "backup-event-2", "copy_id": "backup", "retention_id": "retention-a",
             "subject_ref": "evidence-a", "from_copy_state": "PRESENT", "to_copy_state": "DELETE_PENDING",
             "action": "COPY_DELETION_REQUESTED", "actor_role": "DATA_CUSTODIAN",
             "occurred_at": "2026-01-01T00:05:00Z", "reason": "Backup pending"},
        ]
        with self.assertRaises(ContractViolation):
            validate_retention_scope("DELETED", copies, events)

    def test_deleted_copy_cannot_be_restored_to_present(self):
        copies = [{
            "copy_id": "primary", "retention_id": "retention-a", "subject_ref": "evidence-a",
            "parent_copy_id": None, "state": "PRESENT", "previous_state": "DELETED",
            "transition_event_ref": "restore-event", "recorded_at": "2026-01-01T00:04:00Z"
        }]
        events = [
            {"audit_event_id": "event-1", "copy_id": "primary", "retention_id": "retention-a",
             "subject_ref": "evidence-a", "from_copy_state": None, "to_copy_state": "PRESENT",
             "action": "COPY_DISCOVERED", "actor_role": "DATA_CUSTODIAN",
             "occurred_at": "2026-01-01T00:01:00Z", "reason": "Discovered"},
            {"audit_event_id": "event-2", "copy_id": "primary", "retention_id": "retention-a",
             "subject_ref": "evidence-a", "from_copy_state": "PRESENT", "to_copy_state": "DELETE_PENDING",
             "action": "COPY_DELETION_REQUESTED", "actor_role": "DATA_CUSTODIAN",
             "occurred_at": "2026-01-01T00:02:00Z", "reason": "Requested"},
            {"audit_event_id": "event-3", "copy_id": "primary", "retention_id": "retention-a",
             "subject_ref": "evidence-a", "from_copy_state": "DELETE_PENDING", "to_copy_state": "DELETED",
             "action": "COPY_DELETED", "actor_role": "DATA_CUSTODIAN",
             "occurred_at": "2026-01-01T00:03:00Z", "reason": "Verified"},
            {"audit_event_id": "restore-event", "copy_id": "primary", "retention_id": "retention-a",
             "subject_ref": "evidence-a", "from_copy_state": "DELETED", "to_copy_state": "PRESENT",
             "action": "COPY_DISCOVERED", "actor_role": "DATA_CUSTODIAN",
             "occurred_at": "2026-01-01T00:04:00Z", "reason": "Attempted restore"}
        ]
        with self.assertRaises(ContractViolation):
            validate_retention_scope("RETAIN", copies, events)

    def test_retention_rejects_missing_copy_transition(self):
        copies = [{"copy_id": "primary", "retention_id": "retention-a", "subject_ref": "evidence-a",
                   "parent_copy_id": None, "state": "DELETE_PENDING", "previous_state": "PRESENT",
                   "transition_event_ref": "missing", "recorded_at": "2026-01-01T00:02:00Z"}]
        with self.assertRaises(ContractViolation):
            validate_retention_scope("DELETE_PENDING", copies, [])

    def test_archive_capture_verified_for_cutoff_passes_without_authenticating_content(self):
        availability = {"evidence_id": "evidence-a", "availability_basis": "INDEPENDENT_ARCHIVE",
                        "available_at": "2026-01-01T00:00:00Z", "recorded_at": "2026-01-01T00:02:00Z"}
        attestation = {**self.archive_attestation_base(), "archive_service": "Synthetic Archive", "capture_record_reference": "capture-1",
                       "captured_at": "2026-01-01T00:00:00Z", "recorded_at": "2026-01-01T00:01:00Z", "integrity_result": "MATCH",
                       "capture_record_verified": True, "verification_method": "INDEPENDENT_RECORD_REVIEW",
                       "verified_at": "2026-01-01T00:01:00Z", "verified_by_role": "ARCHIVE_REVIEWER",
                       "content_authenticity": "UNKNOWN",
                       "content_truth": "UNKNOWN"}
        validate_archive_attestation(availability, attestation, self.cutoff, self.archive_evidence())

    def test_archive_timestamp_without_capture_proof_is_rejected(self):
        availability = {"availability_basis": "INDEPENDENT_ARCHIVE",
                        "available_at": "2026-01-01T00:00:00Z"}
        attestation = {"archive_service": "Synthetic Archive", "capture_record_reference": "capture-1",
                       "captured_at": "2026-01-01T00:00:00Z", "recorded_at": "2026-01-01T00:01:00Z", "integrity_result": "NOT_CHECKED",
                       "capture_record_verified": False, "content_authenticity": "UNKNOWN",
                       "content_truth": "UNKNOWN"}
        with self.assertRaises(ContractViolation):
            validate_archive_attestation(availability, attestation, self.cutoff)

    def test_archive_capture_after_cutoff_is_rejected(self):
        availability = {"availability_basis": "INDEPENDENT_ARCHIVE",
                        "available_at": "2026-01-03T00:00:00Z"}
        attestation = {"archive_service": "Synthetic Archive", "capture_record_reference": "capture-1",
                       "captured_at": "2026-01-03T00:00:00Z", "recorded_at": "2026-01-03T00:01:00Z", "integrity_result": "MATCH",
                       "capture_record_verified": True, "verification_method": "INDEPENDENT_RECORD_REVIEW",
                       "verified_at": "2026-01-03T00:01:00Z", "verified_by_role": "ARCHIVE_REVIEWER",
                       "content_authenticity": "UNKNOWN",
                       "content_truth": "UNKNOWN"}
        with self.assertRaises(ContractViolation):
            validate_archive_attestation(availability, attestation, self.cutoff)

    def test_archive_import_cannot_predate_capture(self):
        availability = {"availability_basis": "INDEPENDENT_ARCHIVE",
                        "available_at": "2026-01-01T00:00:00Z"}
        attestation = {"archive_service": "Synthetic Archive", "capture_record_reference": "capture-1",
                       "captured_at": "2026-01-01T00:00:00Z", "imported_at": "2025-12-31T23:59:00Z",
                       "recorded_at": "2026-01-01T00:01:00Z", "integrity_result": "MATCH",
                       "capture_record_verified": True, "verification_method": "INDEPENDENT_RECORD_REVIEW",
                       "verified_at": "2026-01-01T00:01:00Z", "verified_by_role": "ARCHIVE_REVIEWER",
                       "content_authenticity": "UNKNOWN",
                       "content_truth": "UNKNOWN"}
        with self.assertRaises(ContractViolation):
            validate_archive_attestation(availability, attestation, self.cutoff)

    def test_archive_cannot_promote_authenticity(self):
        availability = {"availability_basis": "INDEPENDENT_ARCHIVE",
                        "available_at": "2026-01-01T00:00:00Z"}
        attestation = {"archive_service": "Synthetic Archive", "capture_record_reference": "capture-1",
                       "captured_at": "2026-01-01T00:00:00Z", "recorded_at": "2026-01-01T00:01:00Z", "integrity_result": "MATCH",
                       "capture_record_verified": True, "verification_method": "INDEPENDENT_RECORD_REVIEW",
                       "verified_at": "2026-01-01T00:01:00Z", "verified_by_role": "ARCHIVE_REVIEWER",
                       "content_authenticity": "AUTENTICADA",
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
        target["migration_records"] = [{"migration_id": "embedded-manifest"}]
        manifest = {"migration_id": "m1", "migrator_version": "1.0.0",
                    "source_contract_version": "0.2.0", "target_contract_version": "0.2.1",
                    "input_sha256": canonical_migration_payload_sha256(source), "output_sha256": canonical_migration_payload_sha256(target),
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
                    "input_sha256": canonical_migration_payload_sha256(source), "output_sha256": canonical_migration_payload_sha256(target),
                    "rules_applied": ["preserve-history"], "result": "PASS"}
        with self.assertRaises(ContractViolation):
            validate_migration(source, target, manifest)

    def test_migration_rejects_methodology_version_rewrite(self):
        source = {"contract_version": "0.2.0", "methodology_version": "16-approved",
                  "claims": [], "claim_components": [], "sources": [], "source_versions": [],
                  "identity_assessments": [], "evaluation_units": [], "evidence_items": [],
                  "evidence_availability": [], "claim_evidence_links": [], "provenance_nodes": [],
                  "provenance_edges": [], "factor_assessments": [], "independence_assessments": [],
                  "claim_assessments": [], "retention_records": [], "audit_events": []}
        target = copy.deepcopy(source)
        target["contract_version"] = "0.2.1"
        target["methodology_version"] = "17-unapproved"
        manifest = {"migration_id": "m-methodology", "migrator_version": "1.0.0",
                    "source_contract_version": "0.2.0", "target_contract_version": "0.2.1",
                    "input_sha256": canonical_migration_payload_sha256(source),
                    "output_sha256": canonical_migration_payload_sha256(target),
                    "rules_applied": ["preserve-methodology"], "result": "PASS"}
        with self.assertRaises(ContractViolation):
            validate_migration(source, target, manifest)

    def test_migration_canonical_output_hash_is_deterministic(self):
        target = {"contract_version": "0.2.1", "claims": [{"claim_id": "c1"}]}
        first = canonical_migration_payload_sha256(target)
        second = canonical_sha256(copy.deepcopy(target))
        self.assertEqual(first, second)

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
                    "input_sha256": canonical_migration_payload_sha256(source), "output_sha256": canonical_migration_payload_sha256(target),
                    "rules_applied": ["preserve-history"], "result": "PASS"}
        with self.assertRaises(ContractViolation):
            validate_migration(source, target, manifest)


    def load_contract_021_fixture(self):
        root = Path(__file__).resolve().parents[2]
        schema = json.loads((root / "schemas" / "source-evidence-contract-0.2.1.schema.json").read_text(encoding="utf-8"))
        package = json.loads((root / "tests" / "fixtures" / "contracts" / "source-evidence-contract-v0.2.1.json").read_text(encoding="utf-8"))
        return schema, package

    def assert_schema_valid(self, schema, package):
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(package))
        self.assertEqual(errors, [], "; ".join(error.message for error in errors))

    def test_021_base_fixture_passes_schema_and_semantics(self):
        schema, package = self.load_contract_021_fixture()
        Draft202012Validator.check_schema(schema)
        self.assert_schema_valid(schema, package)
        validate_package(package)

    def test_021_archive_attestation_is_required_and_does_not_authenticate_content(self):
        schema, package = self.load_contract_021_fixture()
        self.set_archive_evidence_integrity(package)
        package["archive_attestations"].append({
            "archive_attestation_id": "archive-1",
            "evidence_id": "evidence-a",
            "source_version_id": "version-a1",
            "captured_content_hash": "a" * 64,
            "hash_algorithm": "SHA-256", "archive_service": "Synthetic Archive",
            "capture_record_reference": "capture-record-1", "captured_at": "2026-11-15T20:04:00Z",
            "imported_at": "2026-11-15T22:00:00Z", "recorded_at": "2026-11-15T22:00:00Z",
            "integrity_result": "MATCH", "capture_record_verified": True,
            "verification_method": "INDEPENDENT_RECORD_REVIEW", "verified_at": "2026-11-15T21:59:00Z",
            "verified_by_role": "ARCHIVE_REVIEWER", "content_authenticity": "UNKNOWN", "content_truth": "UNKNOWN"
        })
        package["evidence_availability"][0]["availability_basis"] = "INDEPENDENT_ARCHIVE"
        package["evidence_availability"][0]["archive_attestation_id"] = "archive-1"
        self.assert_schema_valid(schema, package)
        validate_package(package)

    def test_021_orphan_archive_attestation_is_rejected(self):
        schema, package = self.load_contract_021_fixture()
        self.set_archive_evidence_integrity(package)
        package["archive_attestations"].append({
            "archive_attestation_id": "archive-orphan",
            "evidence_id": "evidence-a",
            "source_version_id": "version-a1",
            "captured_content_hash": "a" * 64,
            "hash_algorithm": "SHA-256", "archive_service": "Synthetic Archive",
            "capture_record_reference": "capture-orphan", "captured_at": "2026-11-15T20:04:00Z",
            "imported_at": "2026-11-15T22:00:00Z", "recorded_at": "2026-11-15T22:00:00Z",
            "integrity_result": "MATCH", "capture_record_verified": True,
            "verification_method": "INDEPENDENT_RECORD_REVIEW", "verified_at": "2026-11-15T21:59:00Z",
            "verified_by_role": "ARCHIVE_REVIEWER", "content_authenticity": "UNKNOWN", "content_truth": "UNKNOWN"
        })
        self.assert_schema_valid(schema, package)
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_package_rejects_availability_record_predating_archive_attestation(self):
        schema, package = self.load_contract_021_fixture()
        self.set_archive_evidence_integrity(package)
        package["archive_attestations"].append({
            "archive_attestation_id": "archive-late-record",
            "evidence_id": "evidence-a",
            "source_version_id": "version-a1",
            "captured_content_hash": "a" * 64,
            "hash_algorithm": "SHA-256", "archive_service": "Synthetic Archive",
            "capture_record_reference": "capture-late-record", "captured_at": "2026-11-15T20:04:00Z",
            "imported_at": "2026-11-15T22:01:00Z", "recorded_at": "2026-11-15T22:01:00Z",
            "integrity_result": "MATCH", "capture_record_verified": True,
            "verification_method": "INDEPENDENT_RECORD_REVIEW", "verified_at": "2026-11-15T21:59:00Z",
            "verified_by_role": "ARCHIVE_REVIEWER", "content_authenticity": "UNKNOWN", "content_truth": "UNKNOWN"
        })
        package["evidence_availability"][0]["availability_basis"] = "INDEPENDENT_ARCHIVE"
        package["evidence_availability"][0]["archive_attestation_id"] = "archive-late-record"
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_archive_integrity_mismatch_is_not_verified_availability(self):
        schema, package = self.load_contract_021_fixture()
        self.set_archive_evidence_integrity(package)
        package["archive_attestations"].append({
            "archive_attestation_id": "archive-1",
            "evidence_id": "evidence-a",
            "source_version_id": "version-a1",
            "captured_content_hash": "a" * 64,
            "hash_algorithm": "SHA-256", "archive_service": "Synthetic Archive",
            "capture_record_reference": "capture-record-1", "captured_at": "2026-11-15T20:04:00Z",
            "imported_at": "2026-11-15T22:00:00Z", "recorded_at": "2026-11-15T22:00:00Z",
            "integrity_result": "MISMATCH", "capture_record_verified": True,
            "verification_method": "INDEPENDENT_RECORD_REVIEW", "verified_at": "2026-11-15T21:59:00Z",
            "verified_by_role": "ARCHIVE_REVIEWER", "content_authenticity": "UNKNOWN", "content_truth": "UNKNOWN"
        })
        package["evidence_availability"][0]["availability_basis"] = "INDEPENDENT_ARCHIVE"
        package["evidence_availability"][0]["archive_attestation_id"] = "archive-1"
        self.assert_schema_valid(schema, package)
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_delete_pending_copy_inventory_passes_schema_and_semantics(self):
        schema, package = self.load_contract_021_fixture()
        record = package["retention_records"][0]
        record.update({"content_retained": True, "legal_basis_status": "NOT_ESTABLISHED",
                       "disposition": "DELETE_PENDING", "previous_disposition": "RETAIN",
                       "expires_at": "2026-11-15T23:00:00Z", "recorded_at": "2026-11-15T22:01:00Z",
                       "review_at": "2026-11-15T22:01:00Z", "copy_scope_ids": ["copy-primary"]})
        package["retention_copy_records"].append({
            "copy_id": "copy-primary", "retention_id": "retention-a", "subject_ref": "evidence-a",
            "copy_kind": "PRIMARY", "parent_copy_id": None, "state": "DELETE_PENDING",
            "recorded_at": "2026-11-15T22:01:00Z", "verified_at": None,
            "verification_reference": None, "scheduled_disposition_at": "2026-11-16T00:00:00Z",
            "backup_expiration_policy_ref": None,
            "previous_state": "PRESENT", "transition_event_ref": "copy-event-2"
        })
        package["audit_events"].append({
            "audit_event_id": "retention-transition", "subject_ref": "evidence-a",
            "action": "DELETION_REQUESTED", "actor_role": "DATA_CUSTODIAN",
            "occurred_at": "2026-11-15T22:01:00Z", "reason": "Retention deletion requested",
            "retention_id": "retention-a", "from_disposition": "RETAIN",
            "to_disposition": "DELETE_PENDING", "copy_id": None,
            "from_copy_state": None, "to_copy_state": None
        })
        package["audit_events"].extend([
            {"audit_event_id": "copy-event-1", "subject_ref": "evidence-a", "action": "COPY_DISCOVERED",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:00:00Z",
             "reason": "Primary copy discovered", "retention_id": "retention-a", "copy_id": "copy-primary",
             "from_copy_state": None, "to_copy_state": "PRESENT"},
            {"audit_event_id": "copy-event-2", "subject_ref": "evidence-a", "action": "COPY_DELETION_REQUESTED",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:01:00Z",
             "reason": "Synthetic deletion request", "retention_id": "retention-a", "copy_id": "copy-primary",
             "from_copy_state": "PRESENT", "to_copy_state": "DELETE_PENDING"}
        ])
        package["claim_assessments"][0]["assessed_at"] = "2026-11-15T22:00:30Z"
        self.assert_schema_valid(schema, package)
        validate_package(package)

    def test_021_package_rejects_new_assessment_after_delete_pending(self):
        schema, package = self.load_contract_021_fixture()
        record = package["retention_records"][0]
        record.update({"content_retained": True, "legal_basis_status": "NOT_ESTABLISHED",
                       "disposition": "DELETE_PENDING", "previous_disposition": "RETAIN",
                       "expires_at": "2026-11-15T23:00:00Z", "recorded_at": "2026-11-15T22:01:00Z",
                       "review_at": "2026-11-15T22:01:00Z", "copy_scope_ids": ["copy-primary"]})
        package["retention_copy_records"].append({
            "copy_id": "copy-primary", "retention_id": "retention-a", "subject_ref": "evidence-a",
            "copy_kind": "PRIMARY", "parent_copy_id": None, "state": "DELETE_PENDING",
            "recorded_at": "2026-11-15T22:01:00Z", "verified_at": None,
            "verification_reference": None, "scheduled_disposition_at": "2026-11-16T00:00:00Z",
            "backup_expiration_policy_ref": None,
            "previous_state": "PRESENT", "transition_event_ref": "copy-event-2"
        })
        package["audit_events"].append({
            "audit_event_id": "retention-transition", "subject_ref": "evidence-a",
            "action": "DELETION_REQUESTED", "actor_role": "DATA_CUSTODIAN",
            "occurred_at": "2026-11-15T22:01:00Z", "reason": "Retention deletion requested",
            "retention_id": "retention-a", "from_disposition": "RETAIN",
            "to_disposition": "DELETE_PENDING", "copy_id": None,
            "from_copy_state": None, "to_copy_state": None
        })
        package["audit_events"].extend([
            {"audit_event_id": "copy-event-1", "subject_ref": "evidence-a", "action": "COPY_DISCOVERED",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:00:00Z",
             "reason": "Primary copy discovered", "retention_id": "retention-a", "copy_id": "copy-primary",
             "from_copy_state": None, "to_copy_state": "PRESENT"},
            {"audit_event_id": "copy-event-2", "subject_ref": "evidence-a", "action": "COPY_DELETION_REQUESTED",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:01:00Z",
             "reason": "Synthetic deletion request", "retention_id": "retention-a", "copy_id": "copy-primary",
             "from_copy_state": "PRESENT", "to_copy_state": "DELETE_PENDING"}
        ])
        package["claim_assessments"][0]["assessed_at"] = "2026-11-15T22:02:00Z"
        self.assert_schema_valid(schema, package)
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_package_accepts_deletion_after_every_copy_and_replica_is_verified(self):
        schema, package = self.load_contract_021_fixture()
        record = package["retention_records"][0]
        record.update({"content_retained": False, "legal_basis_status": "NOT_ESTABLISHED",
                       "disposition": "DELETED", "previous_disposition": "DELETE_PENDING",
                       "recorded_at": "2026-11-15T22:12:00Z", "copy_scope_ids": ["copy-primary", "copy-replica"]})
        package["retention_copy_records"].extend([
            {"copy_id": "copy-primary", "retention_id": "retention-a", "subject_ref": "evidence-a",
             "copy_kind": "PRIMARY", "parent_copy_id": None, "state": "DELETED",
             "recorded_at": "2026-11-15T22:09:00Z", "verified_at": "2026-11-15T22:09:00Z",
             "verification_reference": "verify-primary", "scheduled_disposition_at": None,
             "backup_expiration_policy_ref": None,
             "previous_state": "DELETE_PENDING", "transition_event_ref": "primary-event-3"},
            {"copy_id": "copy-replica", "retention_id": "retention-a", "subject_ref": "evidence-a",
             "copy_kind": "REPLICA", "parent_copy_id": "copy-primary", "state": "DELETED",
             "recorded_at": "2026-11-15T22:12:00Z", "verified_at": "2026-11-15T22:12:00Z",
             "verification_reference": "verify-replica", "scheduled_disposition_at": None,
             "backup_expiration_policy_ref": None,
             "previous_state": "DELETE_PENDING", "transition_event_ref": "replica-event-3"}
        ])
        package["audit_events"].extend([
            {"audit_event_id": "retention-transition", "subject_ref": "evidence-a", "action": "DELETED",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:12:00Z",
             "reason": "All copies verified deleted", "retention_id": "retention-a",
             "from_disposition": "DELETE_PENDING", "to_disposition": "DELETED",
             "copy_id": None, "from_copy_state": None, "to_copy_state": None},
            {"audit_event_id": "primary-event-1", "subject_ref": "evidence-a", "action": "COPY_DISCOVERED",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:07:00Z",
             "reason": "Primary discovered", "retention_id": "retention-a", "copy_id": "copy-primary",
             "from_copy_state": None, "to_copy_state": "PRESENT"},
            {"audit_event_id": "primary-event-2", "subject_ref": "evidence-a", "action": "COPY_DELETION_REQUESTED",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:08:00Z",
             "reason": "Primary deletion requested", "retention_id": "retention-a", "copy_id": "copy-primary",
             "from_copy_state": "PRESENT", "to_copy_state": "DELETE_PENDING"},
            {"audit_event_id": "primary-event-3", "subject_ref": "evidence-a", "action": "COPY_DELETED",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:09:00Z",
             "reason": "Primary deletion verified", "retention_id": "retention-a", "copy_id": "copy-primary",
             "from_copy_state": "DELETE_PENDING", "to_copy_state": "DELETED"},
            {"audit_event_id": "replica-event-1", "subject_ref": "evidence-a", "action": "COPY_DISCOVERED",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:10:00Z",
             "reason": "Replica discovered", "retention_id": "retention-a", "copy_id": "copy-replica",
             "from_copy_state": None, "to_copy_state": "PRESENT"},
            {"audit_event_id": "replica-event-2", "subject_ref": "evidence-a", "action": "COPY_DELETION_REQUESTED",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:11:00Z",
             "reason": "Replica deletion requested", "retention_id": "retention-a", "copy_id": "copy-replica",
             "from_copy_state": "PRESENT", "to_copy_state": "DELETE_PENDING"},
            {"audit_event_id": "replica-event-3", "subject_ref": "evidence-a", "action": "COPY_DELETED",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:12:00Z",
             "reason": "Replica deletion verified", "retention_id": "retention-a", "copy_id": "copy-replica",
             "from_copy_state": "DELETE_PENDING", "to_copy_state": "DELETED"}
        ])
        self.assert_schema_valid(schema, package)
        validate_package(package)

    def test_021_deleted_scope_rejects_uninventoried_replica(self):
        schema, package = self.load_contract_021_fixture()
        record = package["retention_records"][0]
        record.update({"content_retained": False, "disposition": "DELETED",
                       "previous_disposition": "DELETE_PENDING", "recorded_at": "2026-11-15T22:10:00Z",
                       "copy_scope_ids": ["copy-primary", "copy-replica"]})
        package["retention_copy_records"].extend([
            {
                "copy_id": "copy-primary", "retention_id": "retention-a", "subject_ref": "evidence-a",
                "copy_kind": "PRIMARY", "parent_copy_id": None, "state": "DELETED",
                "recorded_at": "2026-11-15T22:10:00Z", "verified_at": "2026-11-15T22:09:00Z",
                "verification_reference": "verify-primary", "scheduled_disposition_at": None,
             "backup_expiration_policy_ref": None,
                "previous_state": "DELETE_PENDING", "transition_event_ref": "copy-event-3"
            },
            {
                "copy_id": "copy-replica", "retention_id": "retention-a", "subject_ref": "evidence-a",
                "copy_kind": "REPLICA", "parent_copy_id": "copy-primary", "state": "PRESENT",
                "recorded_at": "2026-11-15T22:10:00Z", "verified_at": None,
                "verification_reference": None, "scheduled_disposition_at": None,
             "backup_expiration_policy_ref": None,
                "previous_state": None, "transition_event_ref": "copy-event-4"
            }
        ])
        package["audit_events"].append({
            "audit_event_id": "retention-transition", "subject_ref": "evidence-a",
            "action": "DELETED", "actor_role": "DATA_CUSTODIAN",
            "occurred_at": "2026-11-15T22:10:00Z", "reason": "Retention scope deletion verified",
            "retention_id": "retention-a", "from_disposition": "DELETE_PENDING",
            "to_disposition": "DELETED", "copy_id": None,
            "from_copy_state": None, "to_copy_state": None
        })
        package["audit_events"].extend([
            {"audit_event_id": "copy-event-1", "subject_ref": "evidence-a", "action": "COPY_DISCOVERED",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:07:00Z", "reason": "Primary discovered",
             "retention_id": "retention-a", "copy_id": "copy-primary",
             "from_copy_state": None, "to_copy_state": "PRESENT"},
            {"audit_event_id": "copy-event-2", "subject_ref": "evidence-a", "action": "COPY_DELETION_REQUESTED",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:08:00Z", "reason": "Primary pending",
             "retention_id": "retention-a", "copy_id": "copy-primary",
             "from_copy_state": "PRESENT", "to_copy_state": "DELETE_PENDING"},
            {"audit_event_id": "copy-event-3", "subject_ref": "evidence-a", "action": "COPY_DELETED",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:09:00Z", "reason": "Primary deleted",
             "retention_id": "retention-a", "copy_id": "copy-primary",
             "from_copy_state": "DELETE_PENDING", "to_copy_state": "DELETED"},
            {"audit_event_id": "copy-event-4", "subject_ref": "evidence-a", "action": "COPY_DISCOVERED",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:08:00Z", "reason": "Replica discovered",
             "retention_id": "retention-a", "copy_id": "copy-replica",
             "from_copy_state": None, "to_copy_state": "PRESENT"}
        ])
        self.assert_schema_valid(schema, package)
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_migration_manifest_is_schema_valid_and_lossless(self):
        root = Path(__file__).resolve().parents[2]
        schema, target_package = self.load_contract_021_fixture()
        base_schema = json.loads((root / "schemas" / "source-evidence-contract-0.2.0.schema.json").read_text(encoding="utf-8"))
        source_snapshot = json.loads((root / "tests" / "fixtures" / "contracts" / "source-evidence-contract-v0.2.0.json").read_text(encoding="utf-8"))
        target_snapshot = copy.deepcopy(target_package)
        target_snapshot["migration_records"] = []
        manifest = {
            "migration_id": "migration-1", "source_contract_version": "0.2.0",
            "target_contract_version": "0.2.1", "migrator_version": "1.0.0",
            "executed_at": "2026-11-15T22:00:00Z",
            "input_sha256": canonical_migration_payload_sha256(source_snapshot),
            "output_sha256": canonical_migration_payload_sha256(target_snapshot),
            "rules_applied": ["preserve-history", "add-nullable-attestation-ref"],
            "result": "PASS", "loss_report": [],
            "source_snapshot_ref": "fixture://source-evidence-contract-v0.2.0",
            "target_snapshot_ref": "fixture://source-evidence-contract-v0.2.1"
        }
        target_package["migration_records"].append(manifest)
        self.assert_schema_valid(schema, target_package)
        snapshots = {
            manifest["source_snapshot_ref"]: source_snapshot,
            manifest["target_snapshot_ref"]: target_snapshot,
        }
        validate_package(target_package, base_schema, schema, snapshots)

    def test_021_package_rejects_unresolvable_migration_snapshot_reference(self):
        root = Path(__file__).resolve().parents[2]
        schema, target_package = self.load_contract_021_fixture()
        base_schema = json.loads((root / "schemas" / "source-evidence-contract-0.2.0.schema.json").read_text(encoding="utf-8"))
        source_snapshot = json.loads((root / "tests" / "fixtures" / "contracts" / "source-evidence-contract-v0.2.0.json").read_text(encoding="utf-8"))
        target_snapshot = copy.deepcopy(target_package)
        target_snapshot["migration_records"] = []
        manifest = {
            "migration_id": "migration-unresolved-ref", "source_contract_version": "0.2.0",
            "target_contract_version": "0.2.1", "migrator_version": "1.0.0",
            "executed_at": "2026-11-15T22:00:00Z",
            "input_sha256": canonical_migration_payload_sha256(source_snapshot),
            "output_sha256": canonical_migration_payload_sha256(target_snapshot),
            "rules_applied": ["preserve-history"], "result": "PASS", "loss_report": [],
            "source_snapshot_ref": "fixture://missing-source-snapshot",
            "target_snapshot_ref": "fixture://source-evidence-contract-v0.2.1"
        }
        target_package["migration_records"].append(manifest)
        snapshots = {
            "fixture://source-evidence-contract-v0.2.1": target_snapshot,
        }
        with self.assertRaises(ContractViolation):
            validate_package(target_package, base_schema, schema, snapshots)

    def test_021_package_rejects_migration_with_incorrect_snapshot_digest(self):
        root = Path(__file__).resolve().parents[2]
        schema, target_package = self.load_contract_021_fixture()
        base_schema = json.loads((root / "schemas" / "source-evidence-contract-0.2.0.schema.json").read_text(encoding="utf-8"))
        source_snapshot = json.loads((root / "tests" / "fixtures" / "contracts" / "source-evidence-contract-v0.2.0.json").read_text(encoding="utf-8"))
        target_snapshot = copy.deepcopy(target_package)
        target_snapshot["migration_records"] = []
        manifest = {
            "migration_id": "migration-bad-digest", "source_contract_version": "0.2.0",
            "target_contract_version": "0.2.1", "migrator_version": "1.0.0",
            "executed_at": "2026-11-15T22:00:00Z", "input_sha256": "0" * 64,
            "output_sha256": canonical_migration_payload_sha256(target_snapshot),
            "rules_applied": ["preserve-history"], "result": "PASS", "loss_report": [],
            "source_snapshot_ref": "fixture://source-evidence-contract-v0.2.0",
            "target_snapshot_ref": "fixture://source-evidence-contract-v0.2.1"
        }
        target_package["migration_records"].append(manifest)
        snapshots = {
            manifest["source_snapshot_ref"]: source_snapshot,
            manifest["target_snapshot_ref"]: target_snapshot,
        }
        with self.assertRaises(ContractViolation):
            validate_package(target_package, base_schema, schema, snapshots)

    def test_021_successful_migration_cannot_report_data_loss(self):
        schema, package = self.load_contract_021_fixture()
        package["migration_records"].append({
            "migration_id": "migration-2", "source_contract_version": "0.2.0",
            "target_contract_version": "0.2.1", "migrator_version": "1.0.0",
            "executed_at": "2026-11-15T22:00:00Z", "input_sha256": "a" * 64,
            "output_sha256": "b" * 64, "rules_applied": ["preserve-history"],
            "result": "PASS", "loss_report": ["unknown field discarded"],
            "source_snapshot_ref": "fixture://source-evidence-contract-v0.2.0",
            "target_snapshot_ref": "fixture://source-evidence-contract-v0.2.1"
        })
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(package))
        self.assertTrue(errors, "PASS migration with a non-empty loss_report must be rejected by the schema")

    def test_021_package_represents_distinct_analyses_over_common_dataset(self):
        schema, package = self.load_contract_021_fixture()
        package["provenance_nodes"].append(
            {"node_id": "dataset-common", "node_type": "DATASET", "entity_ref": "dataset-origin-common"}
        )
        package["analysis_processes"] = [
            {"process_id": "analysis-a", "dataset_origin_id": "dataset-origin-common",
             "claim_component_version_id": "component-entity-v1", "method_reference": "method-a",
             "output_evidence_ref": "evidence-a", "available_at": "2026-11-15T20:05:00Z",
             "assessment_cutoff": "2026-11-15T22:00:00Z", "recorded_at": "2026-11-15T22:00:00Z"},
            {"process_id": "analysis-b", "dataset_origin_id": "dataset-origin-common",
             "claim_component_version_id": "component-entity-v1", "method_reference": "method-b",
             "output_evidence_ref": "evidence-b", "available_at": "2026-11-15T20:06:00Z",
             "assessment_cutoff": "2026-11-15T22:00:00Z", "recorded_at": "2026-11-15T22:00:00Z"}
        ]
        self.assert_schema_valid(schema, package)
        validate_package(package)

    def test_021_package_rejects_independence_from_analyses_over_common_dataset(self):
        schema, package = self.load_contract_021_fixture()
        package["provenance_nodes"].extend([
            {"node_id": "origin-a", "node_type": "DOCUMENT", "entity_ref": "analysis-output-a"},
            {"node_id": "origin-b", "node_type": "DOCUMENT", "entity_ref": "analysis-output-b"},
            {"node_id": "dataset-common", "node_type": "DATASET", "entity_ref": "dataset-origin-common"}
        ])
        package["analysis_processes"] = [
            {"process_id": "analysis-a", "dataset_origin_id": "dataset-origin-common",
             "claim_component_version_id": "component-entity-v1", "method_reference": "method-a",
             "output_evidence_ref": "evidence-a", "available_at": "2026-11-15T20:05:00Z",
             "assessment_cutoff": "2026-11-15T22:00:00Z", "recorded_at": "2026-11-15T22:00:00Z"},
            {"process_id": "analysis-b", "dataset_origin_id": "dataset-origin-common",
             "claim_component_version_id": "component-entity-v1", "method_reference": "method-b",
             "output_evidence_ref": "evidence-b", "available_at": "2026-11-15T20:06:00Z",
             "assessment_cutoff": "2026-11-15T22:00:00Z", "recorded_at": "2026-11-15T22:00:00Z"}
        ]
        package["provenance_edges"].extend([
            {"edge_id": "path-a", "dependent_node_id": "node-version-a", "origin_node_id": "origin-a",
             "relation_type": "ORIGEN_DIRECTO", "claim_component_id": "component-entity",
             "evidence_refs": ["evidence-a"], "recorded_at": "2026-11-15T22:00:00Z",
             "valid_from": None, "valid_to": None, "claim_component_version_id": "component-entity-v1"},
            {"edge_id": "path-b", "dependent_node_id": "node-version-b", "origin_node_id": "origin-b",
             "relation_type": "ORIGEN_DIRECTO", "claim_component_id": "component-entity",
             "evidence_refs": ["evidence-b"], "recorded_at": "2026-11-15T22:00:00Z",
             "valid_from": None, "valid_to": None, "claim_component_version_id": "component-entity-v1"}
        ])
        assessment = package["independence_assessments"][0]
        assessment.update({"status": "INDEPENDIENTE", "supporting_evidence_refs": ["evidence-a", "evidence-b"],
                           "independent_path_edge_refs": ["path-a", "path-b"],
                           "human_review_status": "REVIEWED", "reviewed_at": "2026-11-15T22:00:00Z"})
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_package_rejects_independent_status_without_integrated_origin_paths(self):
        schema, package = self.load_contract_021_fixture()
        assessment = package["independence_assessments"][0]
        assessment.update({"status": "INDEPENDIENTE", "supporting_evidence_refs": ["evidence-a", "evidence-b"],
                           "human_review_status": "REVIEWED", "reviewed_at": "2026-11-15T22:00:00Z"})
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_package_accepts_independent_distinct_terminal_origins(self):
        schema, package = self.load_contract_021_fixture()
        package["provenance_nodes"].extend([
            {"node_id": "origin-a", "node_type": "DATASET", "entity_ref": "origin-record-a"},
            {"node_id": "origin-b", "node_type": "DOCUMENT", "entity_ref": "origin-record-b"}
        ])
        package["provenance_edges"].extend([
            {"edge_id": "path-a", "dependent_node_id": "node-version-a", "origin_node_id": "origin-a",
             "relation_type": "ORIGEN_DIRECTO", "claim_component_id": "component-entity",
             "evidence_refs": ["evidence-a"], "recorded_at": "2026-11-15T22:00:00Z",
             "valid_from": None, "valid_to": None, "claim_component_version_id": "component-entity-v1"},
            {"edge_id": "path-b", "dependent_node_id": "node-version-b", "origin_node_id": "origin-b",
             "relation_type": "ORIGEN_DIRECTO", "claim_component_id": "component-entity",
             "evidence_refs": ["evidence-b"], "recorded_at": "2026-11-15T22:00:00Z",
             "valid_from": None, "valid_to": None, "claim_component_version_id": "component-entity-v1"}
        ])
        assessment = package["independence_assessments"][0]
        assessment.update({"status": "INDEPENDIENTE", "supporting_evidence_refs": ["evidence-a", "evidence-b"],
                           "independent_path_edge_refs": ["path-a", "path-b"],
                           "human_review_status": "REVIEWED", "reviewed_at": "2026-11-15T22:00:00Z"})
        self.assert_schema_valid(schema, package)
        validate_package(package)

    def test_021_package_accepts_corroboration_from_reviewed_independent_sources(self):
        schema, package = self.load_contract_021_fixture()
        package["provenance_nodes"].extend([
            {"node_id": "origin-a", "node_type": "DATASET", "entity_ref": "origin-record-a"},
            {"node_id": "origin-b", "node_type": "DOCUMENT", "entity_ref": "origin-record-b"}
        ])
        package["provenance_edges"].extend([
            {"edge_id": "path-a", "dependent_node_id": "node-version-a", "origin_node_id": "origin-a",
             "relation_type": "ORIGEN_DIRECTO", "claim_component_id": "component-entity",
             "evidence_refs": ["evidence-a"], "recorded_at": "2026-11-15T22:00:00Z",
             "valid_from": None, "valid_to": None, "claim_component_version_id": "component-entity-v1"},
            {"edge_id": "path-b", "dependent_node_id": "node-version-b", "origin_node_id": "origin-b",
             "relation_type": "ORIGEN_DIRECTO", "claim_component_id": "component-entity",
             "evidence_refs": ["evidence-b"], "recorded_at": "2026-11-15T22:00:00Z",
             "valid_from": None, "valid_to": None, "claim_component_version_id": "component-entity-v1"}
        ])
        independence = package["independence_assessments"][0]
        independence.update({"status": "INDEPENDIENTE", "supporting_evidence_refs": ["evidence-a", "evidence-b"],
                             "independent_path_edge_refs": ["path-a", "path-b"],
                             "human_review_status": "REVIEWED", "reviewed_at": "2026-11-15T22:00:00Z"})
        package["claim_evidence_links"][1]["evidence_role"] = "SUPPORTING"
        assessment = package["claim_assessments"][0]
        assessment.update({"evidentiary_status": "CORROBORADA", "corroboration_basis": "CORROBORACION_INDEPENDIENTE",
                           "supporting_evidence_refs": ["evidence-a", "evidence-b"],
                           "human_review_status": "REVIEWED", "reviewed_at": "2026-11-15T22:00:00Z"})
        self.assert_schema_valid(schema, package)
        validate_package(package)

    def test_021_package_rejects_independent_corroboration_without_reviewed_independence(self):
        schema, package = self.load_contract_021_fixture()
        assessment = package["claim_assessments"][0]
        assessment.update({"evidentiary_status": "CORROBORADA", "corroboration_basis": "CORROBORACION_INDEPENDIENTE",
                           "supporting_evidence_refs": ["evidence-a", "evidence-b"],
                           "human_review_status": "REVIEWED", "reviewed_at": "2026-11-15T22:00:00Z"})
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_package_rejects_primary_corroboration_overclaim(self):
        schema, package = self.load_contract_021_fixture()
        assessment = package["claim_assessments"][0]
        assessment.update({"evidentiary_status": "CORROBORADA", "corroboration_basis": "EVIDENCIA_PRIMARIA_DIRECTA",
                           "supporting_evidence_refs": ["evidence-a"], "human_review_status": "REVIEWED",
                           "reviewed_at": "2026-11-15T22:00:00Z"})
        unit = next(item for item in package["evaluation_units"] if item["assessment_unit_id"] == "unit-a-entity")
        unit.update({"source_type": "PRIMARIA", "source_subtype": "REGISTRO_ORIGINAL",
                     "knowledge_basis": "DOCUMENTO_DE_TERCEROS"})
        package["evidence_items"][0]["authenticity_status"] = "AUTENTICADA"
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_package_accepts_unknown_independence_without_asserted_paths(self):
        schema, package = self.load_contract_021_fixture()
        assessment = package["independence_assessments"][0]
        self.assertEqual(assessment["status"], "DESCONOCIDA")
        self.assertEqual(assessment["independent_path_edge_refs"], [])
        self.assertEqual(assessment["dependency_edge_refs"], [])
        self.assert_schema_valid(schema, package)
        validate_package(package)

    def test_021_package_rejects_unknown_independence_with_asserted_path(self):
        schema, package = self.load_contract_021_fixture()
        assessment = package["independence_assessments"][0]
        assessment["independent_path_edge_refs"] = ["unverified-path"]
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_package_rejects_dependency_leaking_across_components(self):
        schema, package = self.load_contract_021_fixture()
        package["provenance_edges"].append({
            "edge_id": "entity-dependency", "dependent_node_id": "node-version-a",
            "origin_node_id": "node-version-b", "relation_type": "SINDICADA_DE",
            "claim_component_id": "component-entity", "evidence_refs": ["evidence-a"],
            "recorded_at": "2026-11-15T22:00:00Z", "valid_from": None, "valid_to": None,
            "claim_component_version_id": "component-entity-v1"
        })
        amount_assessment = package["independence_assessments"][1]
        amount_assessment.update({
            "status": "DEPENDIENTE", "supporting_evidence_refs": ["evidence-a"],
            "dependency_edge_refs": ["entity-dependency"], "human_review_status": "REVIEWED",
            "reviewed_at": "2026-11-15T22:00:00Z"
        })
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_package_accepts_evidenced_dependency_for_exact_component(self):
        schema, package = self.load_contract_021_fixture()
        package["provenance_edges"].append({
            "edge_id": "dependency-edge", "dependent_node_id": "node-version-a",
            "origin_node_id": "node-version-b", "relation_type": "SINDICADA_DE",
            "claim_component_id": "component-entity", "evidence_refs": ["evidence-a"],
            "recorded_at": "2026-11-15T22:00:00Z", "valid_from": None, "valid_to": None,
            "claim_component_version_id": "component-entity-v1"
        })
        assessment = package["independence_assessments"][0]
        assessment.update({"status": "DEPENDIENTE", "supporting_evidence_refs": ["evidence-a"],
                           "dependency_edge_refs": ["dependency-edge"], "human_review_status": "REVIEWED",
                           "reviewed_at": "2026-11-15T22:00:00Z"})
        self.assert_schema_valid(schema, package)
        validate_package(package)

    def test_021_package_rejects_dependency_edge_without_evidence(self):
        schema, package = self.load_contract_021_fixture()
        package["provenance_edges"].append({
            "edge_id": "dependency-edge", "dependent_node_id": "node-version-a",
            "origin_node_id": "node-version-b", "relation_type": "SINDICADA_DE",
            "claim_component_id": "component-entity", "evidence_refs": [],
            "recorded_at": "2026-11-15T22:00:00Z", "valid_from": None, "valid_to": None,
            "claim_component_version_id": "component-entity-v1"
        })
        assessment = package["independence_assessments"][0]
        assessment.update({"status": "DEPENDIENTE", "dependency_edge_refs": ["dependency-edge"],
                           "human_review_status": "REVIEWED", "reviewed_at": "2026-11-15T22:00:00Z"})
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_package_accepts_primary_corroboration_only_for_directly_observed_act(self):
        schema, package = self.load_contract_021_fixture()
        assessment = package["claim_assessments"][0]
        assessment.update({"evidentiary_status": "CORROBORADA", "corroboration_basis": "EVIDENCIA_PRIMARIA_DIRECTA",
                           "supporting_evidence_refs": ["evidence-a"], "human_review_status": "REVIEWED",
                           "reviewed_at": "2026-11-15T22:00:00Z"})
        unit = next(item for item in package["evaluation_units"] if item["assessment_unit_id"] == "unit-a-entity")
        unit.update({"source_type": "PRIMARIA", "source_subtype": "REGISTRO_ORIGINAL",
                     "knowledge_basis": "OBSERVACIÓN_DIRECTA"})
        package["evidence_items"][0]["authenticity_status"] = "AUTENTICADA"
        self.assert_schema_valid(schema, package)
        validate_package(package)

    def test_021_package_accepts_unknown_independence_when_provenance_is_incomplete(self):
        schema, package = self.load_contract_021_fixture()
        for assessment in package["independence_assessments"]:
            assessment.update({
                "status": "DESCONOCIDA",
                "supporting_evidence_refs": [],
                "dependency_edge_refs": [],
                "independent_path_edge_refs": [],
                "human_review_status": "PENDING",
                "reviewed_at": None,
            })
        self.assert_schema_valid(schema, package)
        validate_package(package)

    def test_021_package_rejects_dependency_edge_from_another_component(self):
        schema, package = self.load_contract_021_fixture()
        package["provenance_edges"].append({
            "edge_id": "cross-component-dependency",
            "dependent_node_id": "node-version-a",
            "origin_node_id": "node-version-b",
            "relation_type": "SINDICADA_DE",
            "claim_component_id": "component-amount",
            "evidence_refs": ["evidence-a"],
            "recorded_at": "2026-11-15T22:00:00Z",
            "valid_from": None,
            "valid_to": None,
            "claim_component_version_id": "component-entity-v1",
        })
        assessment = next(
            item for item in package["independence_assessments"]
            if item["claim_component_id"] == "component-entity"
        )
        assessment.update({
            "status": "DEPENDIENTE",
            "supporting_evidence_refs": ["evidence-a"],
            "dependency_edge_refs": ["cross-component-dependency"],
            "human_review_status": "REVIEWED",
            "reviewed_at": "2026-11-15T22:00:00Z",
        })
        self.assert_schema_valid(schema, package)
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_orphan_copy_audit_event_is_rejected(self):
        schema, package = self.load_contract_021_fixture()
        package["audit_events"].append({
            "audit_event_id": "orphan-copy-event", "subject_ref": "evidence-a",
            "action": "COPY_DISCOVERED", "actor_role": "DATA_CUSTODIAN",
            "occurred_at": "2026-11-15T22:00:00Z", "reason": "Orphan synthetic event",
            "retention_id": "retention-a", "copy_id": "missing-copy",
            "from_copy_state": None, "to_copy_state": "PRESENT"
        })
        self.assert_schema_valid(schema, package)
        with self.assertRaises(ContractViolation):
            validate_package(package)


    def test_021_real_020_to_021_migration_is_deterministic_without_duplicates(self):
        root = Path(__file__).resolve().parents[2]
        source_schema = json.loads((root / "schemas" / "source-evidence-contract-0.2.0.schema.json").read_text(encoding="utf-8"))
        target_schema = json.loads((root / "schemas" / "source-evidence-contract-0.2.1.schema.json").read_text(encoding="utf-8"))
        source = json.loads((root / "tests" / "fixtures" / "contracts" / "source-evidence-contract-v0.2.0.json").read_text(encoding="utf-8"))
        plan = {
            "migration_id": "migration-020-021-synthetic-001",
            "executed_at": "2026-11-16T00:00:00Z",
            "source_snapshot_ref": "memory://migration/source-001",
            "target_snapshot_ref": "memory://migration/target-001",
        }
        migrated, snapshots = migrate_package(source, source_schema, target_schema, **plan)
        repeated, repeated_snapshots = migrate_package(source, source_schema, target_schema, **plan)
        self.assertEqual(migrated, repeated)
        self.assertEqual(snapshots, repeated_snapshots)
        self.assertEqual(migrated["contract_version"], "0.2.1")
        self.assertEqual(len(migrated["migration_records"]), 1)
        self.assertEqual(migrated["claim_assessments"][0]["assessed_at"], None)
        self.assertEqual(
            migrated["factor_assessments"][0]["assessed_at"],
            source["factor_assessments"][0]["assessed_at"],
        )
        for collection in ("archive_attestations", "retention_copy_records", "analysis_processes"):
            self.assertEqual(migrated[collection], [])
        for collection in ("claims", "claim_components", "sources", "source_versions",
                           "evaluation_units", "evidence_items", "provenance_nodes",
                           "provenance_edges", "factor_assessments", "independence_assessments",
                           "claim_assessments", "retention_records", "audit_events"):
            self.assertEqual(len(migrated[collection]), len(source[collection]), collection)
        errors = list(Draft202012Validator(target_schema, format_checker=FormatChecker()).iter_errors(migrated))
        self.assertEqual(errors, [], "; ".join(error.message for error in errors))
        validate_package(migrated, source_schema, target_schema, snapshots)
        with self.assertRaisesRegex(ValueError, "accepts only contract_version 0.2.0"):
            migrate_package(migrated, source_schema, target_schema, **plan)

    def test_021_historical_assessed_at_null_is_preserved_for_claim_and_factor(self):
        schema, package = self.load_contract_021_fixture()
        package["claim_assessments"][0]["assessed_at"] = None
        self.assertEqual(package["factor_assessments"][0]["assessed_at"], "2026-11-15T22:00:00Z")
        self.assert_schema_valid(schema, package)
        validate_package(package)

    def test_021_assessed_at_property_remains_required_when_unknown(self):
        schema, package = self.load_contract_021_fixture()
        del package["claim_assessments"][0]["assessed_at"]
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(package))
        self.assertTrue(any("assessed_at" in error.message for error in errors))




    def test_021_source_correction_is_a_new_version_and_preserves_prior_version(self):
        schema, package = self.load_contract_021_fixture()
        original = copy.deepcopy(package["source_versions"][0])
        corrected = copy.deepcopy(original)
        corrected.update({
            "source_version_id": "version-a2",
            "version_label": "v2-correction",
            "version_sequence": 2,
            "supersedes_source_version_id": original["source_version_id"],
            "recorded_at": "2026-11-15T23:00:00Z",
            "retrieved_at": "2026-11-15T22:30:00Z",
            "first_detected_at": "2026-11-15T22:25:00Z",
            "content_hash": None,
            "hash_algorithm": None,
        })
        package["source_versions"].append(corrected)
        self.assert_schema_valid(schema, package)
        validate_package(package)
        self.assertEqual(
            next(item for item in package["source_versions"] if item["source_version_id"] == original["source_version_id"]),
            original,
        )

    def test_021_source_version_chain_rejects_self_or_future_supersession(self):
        schema, package = self.load_contract_021_fixture()
        corrected = copy.deepcopy(package["source_versions"][0])
        corrected.update({
            "source_version_id": "version-a2",
            "version_label": "v2-invalid",
            "version_sequence": 2,
            "supersedes_source_version_id": "version-a2",
            "recorded_at": "2026-11-15T23:00:00Z",
        })
        package["source_versions"].append(corrected)
        self.assert_schema_valid(schema, package)
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_source_version_chain_rejects_forked_successors(self):
        schema, package = self.load_contract_021_fixture()
        for suffix in ("2", "3"):
            corrected = copy.deepcopy(package["source_versions"][0])
            corrected.update({
                "source_version_id": f"version-a{suffix}",
                "version_label": f"v{suffix}-branch",
                "version_sequence": 2,
                "supersedes_source_version_id": "version-a1",
                "recorded_at": "2026-11-15T23:00:00Z",
            })
            package["source_versions"].append(corrected)
        self.assert_schema_valid(schema, package)
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_dependency_edge_must_connect_two_assessed_source_versions(self):
        schema, package = self.load_contract_021_fixture()
        external = copy.deepcopy(next(
            node for node in package["provenance_nodes"] if node["node_id"] == "node-version-b"
        ))
        external.update({"node_id": "node-version-external", "entity_ref": "version-outside-assessment"})
        package["provenance_nodes"].append(external)
        package["provenance_edges"].append({
            "edge_id": "external-dependency",
            "dependent_node_id": "node-version-a",
            "origin_node_id": "node-version-external",
            "relation_type": "SINDICADA_DE",
            "claim_component_id": "component-entity",
            "evidence_refs": ["evidence-a"],
            "recorded_at": "2026-11-15T22:00:00Z",
            "valid_from": None,
            "valid_to": None,
            "claim_component_version_id": "component-entity-v1",
        })
        assessment = package["independence_assessments"][0]
        assessment.update({
            "status": "DEPENDIENTE",
            "supporting_evidence_refs": ["evidence-a"],
            "dependency_edge_refs": ["external-dependency"],
            "human_review_status": "REVIEWED",
            "reviewed_at": "2026-11-15T22:00:00Z",
        })
        self.assert_schema_valid(schema, package)
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_dependency_edge_cannot_connect_a_source_version_to_itself(self):
        schema, package = self.load_contract_021_fixture()
        package["provenance_edges"].append({
            "edge_id": "self-dependency",
            "dependent_node_id": "node-version-a",
            "origin_node_id": "node-version-a",
            "relation_type": "SINDICADA_DE",
            "claim_component_id": "component-entity",
            "evidence_refs": ["evidence-a"],
            "recorded_at": "2026-11-15T22:00:00Z",
            "valid_from": None,
            "valid_to": None,
            "claim_component_version_id": "component-entity-v1",
        })
        assessment = package["independence_assessments"][0]
        assessment.update({
            "status": "DEPENDIENTE",
            "supporting_evidence_refs": ["evidence-a"],
            "dependency_edge_refs": ["self-dependency"],
            "human_review_status": "REVIEWED",
            "reviewed_at": "2026-11-15T22:00:00Z",
        })
        self.assert_schema_valid(schema, package)
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_primary_hash_integrity_without_authenticity_cannot_corroborate(self):
        primary = [{
            "source_type": "PRIMARIA", "source_id": "s1", "source_version_id": "v1",
            "authenticity_status": "UNKNOWN", "access_status": "PÚBLICO_LEGÍTIMO",
            "unit_access_status": "PÚBLICO_LEGÍTIMO", "knowledge_basis": "REGISTRO_ORIGINAL",
            "scope_note": "El hash coincide, pero no acredita autoría.",
            "available_at": "2026-01-01T00:00:00Z",
        }]
        units = [{
            "assessment_unit_id": "u1", "source_id": "s1", "source_version_id": "v1",
            "claim_component_version_id": "cv1", "assessment_cutoff": self.cutoff,
            "source_type": "PRIMARIA",
        }]
        with self.assertRaises(ContractViolation):
            validate_corroboration("CORROBORADA", "EVIDENCIA_PRIMARIA_DIRECTA",
                                   units, primary, set(), self.cutoff)

    def test_primary_private_unauthorized_or_unknown_access_cannot_corroborate(self):
        for access_status in ("PRIVADO_NO_AUTORIZADO", "DESCONOCIDO"):
            primary = [{
                "source_type": "PRIMARIA", "source_id": "s1", "source_version_id": "v1",
                "authenticity_status": "AUTENTICADA", "access_status": access_status,
                "unit_access_status": access_status, "knowledge_basis": "REGISTRO_ORIGINAL",
                "scope_note": "Acceso no legitimado.",
                "available_at": "2026-01-01T00:00:00Z",
            }]
            units = [{
                "assessment_unit_id": "u1", "source_id": "s1", "source_version_id": "v1",
                "claim_component_version_id": "cv1", "assessment_cutoff": self.cutoff,
                "source_type": "PRIMARIA",
            }]
            with self.subTest(access_status=access_status):
                with self.assertRaises(ContractViolation):
                    validate_corroboration("CORROBORADA", "EVIDENCIA_PRIMARIA_DIRECTA",
                                           units, primary, set(), self.cutoff)

    def test_021_source_stated_timestamp_does_not_prove_historical_availability(self):
        schema, package = self.load_contract_021_fixture()
        availability = package["evidence_availability"][0]
        availability["availability_basis"] = "SOURCE_STATED"
        availability["available_at"] = None
        self.assert_schema_valid(schema, package)
        unit = next(item for item in package["evaluation_units"]
                    if item["assessment_unit_id"] == availability["assessment_unit_id"])
        with self.assertRaises(ContractViolation):
            _available_at(package, availability["evidence_id"], unit)

    def test_021_archived_evidence_cannot_be_rebound_to_another_source_version(self):
        schema, package = self.load_contract_021_fixture()
        package["evidence_items"][0]["source_version_id"] = "version-b1"
        self.assert_schema_valid(schema, package)
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_migration_rejects_changed_historical_assessment_cutoff(self):
        source = {"contract_version": "0.2.0", "claims": [],
                  "claim_components": [], "sources": [], "source_versions": [],
                  "identity_assessments": [], "evaluation_units": [], "evidence_items": [],
                  "evidence_availability": [], "claim_evidence_links": [], "provenance_nodes": [],
                  "provenance_edges": [], "factor_assessments": [], "independence_assessments": [],
                  "claim_assessments": [{"assessment_cutoff": "2026-01-01T00:00:00Z"}],
                  "retention_records": [], "audit_events": []}
        target = copy.deepcopy(source)
        target["contract_version"] = "0.2.1"
        target["claim_assessments"][0]["assessment_cutoff"] = "2026-01-02T00:00:00Z"
        manifest = {"migration_id": "m-cutoff", "migrator_version": "1.0.0",
                    "source_contract_version": "0.2.0", "target_contract_version": "0.2.1",
                    "input_sha256": canonical_migration_payload_sha256(source),
                    "output_sha256": canonical_migration_payload_sha256(target),
                    "rules_applied": ["preserve-cutoff"], "result": "PASS"}
        with self.assertRaises(ContractViolation):
            validate_migration(source, target, manifest)

    def test_migration_rejects_changed_historical_evidence_references(self):
        source = {"contract_version": "0.2.0", "claims": [],
                  "claim_components": [], "sources": [], "source_versions": [],
                  "identity_assessments": [], "evaluation_units": [], "evidence_items": [],
                  "evidence_availability": [], "claim_evidence_links": [], "provenance_nodes": [],
                  "provenance_edges": [], "factor_assessments": [], "independence_assessments": [],
                  "claim_assessments": [{"supporting_evidence_refs": ["evidence-original"]}],
                  "retention_records": [], "audit_events": []}
        target = copy.deepcopy(source)
        target["contract_version"] = "0.2.1"
        target["claim_assessments"][0]["supporting_evidence_refs"] = ["evidence-substituted"]
        manifest = {"migration_id": "m-evidence-ref", "migrator_version": "1.0.0",
                    "source_contract_version": "0.2.0", "target_contract_version": "0.2.1",
                    "input_sha256": canonical_migration_payload_sha256(source),
                    "output_sha256": canonical_migration_payload_sha256(target),
                    "rules_applied": ["preserve-evidence-references"], "result": "PASS"}
        with self.assertRaises(ContractViolation):
            validate_migration(source, target, manifest)


    def test_021_partial_corroboration_preserves_distinct_supported_and_unsupported_scopes(self):
        schema, package = self.load_contract_021_fixture()
        assessment = package["claim_assessments"][0]
        assessment.update({
            "evidentiary_status": "PARCIALMENTE_CORROBORADA",
            "supporting_evidence_refs": ["evidence-a"],
            "supported_scope": "La declaración fue emitida por la fuente.",
            "unsupported_scope": "La ejecución del hecho subyacente no está demostrada.",
            "human_review_status": "REVIEWED",
            "reviewed_at": "2026-11-15T22:00:00Z",
        })
        self.assert_schema_valid(schema, package)
        validate_package(package)

    def test_021_partial_corroboration_rejects_identical_scopes(self):
        schema, package = self.load_contract_021_fixture()
        assessment = package["claim_assessments"][0]
        assessment.update({
            "evidentiary_status": "PARCIALMENTE_CORROBORADA",
            "supporting_evidence_refs": ["evidence-a"],
            "supported_scope": "La declaración fue emitida.",
            "unsupported_scope": "La declaración fue emitida.",
            "human_review_status": "REVIEWED",
            "reviewed_at": "2026-11-15T22:00:00Z",
        })
        self.assert_schema_valid(schema, package)
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_contradicted_assessment_requires_exact_scoped_contrary_evidence(self):
        schema, package = self.load_contract_021_fixture()
        package["evidence_items"][1]["authenticity_status"] = "AUTENTICADA"
        unit = next(item for item in package["evaluation_units"]
                    if item["assessment_unit_id"] == "unit-b-entity")
        unit.update({
            "source_type": "PRIMARIA",
            "source_subtype": "REGISTRO_ORIGINAL",
            "knowledge_basis": "OBSERVACIÓN_DIRECTA",
        })
        package["claim_evidence_links"][1].update({
            "evidence_role": "CONTRARY",
            "scope_note": "El registro primario contradice el alcance evaluado.",
            "limitations": ["Caso sintético; revisión humana requerida."],
        })
        assessment = package["claim_assessments"][0]
        assessment.update({
            "evidentiary_status": "CONTRADICHA",
            "supporting_evidence_refs": ["evidence-a"],
            "contrary_evidence_refs": ["evidence-b"],
            "human_review_status": "REVIEWED",
            "reviewed_at": "2026-11-15T22:00:00Z",
        })
        self.assert_schema_valid(schema, package)
        validate_package(package)

    def test_021_contradicted_assessment_rejects_cross_component_contrary_link(self):
        schema, package = self.load_contract_021_fixture()
        package["claim_evidence_links"][1].update({
            "claim_component_id": "component-amount",
            "claim_component_version_id": "component-amount-v1",
            "evidence_role": "CONTRARY",
        })
        assessment = package["claim_assessments"][0]
        assessment.update({
            "evidentiary_status": "CONTRADICHA",
            "supporting_evidence_refs": ["evidence-a"],
            "contrary_evidence_refs": ["evidence-b"],
            "human_review_status": "REVIEWED",
            "reviewed_at": "2026-11-15T22:00:00Z",
        })
        self.assert_schema_valid(schema, package)
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_audit_subject_reference_must_resolve_to_internal_object(self):
        for subject_ref in (
            "person-private-identity",
            "a" * 64,
            "https://external.invalid/private-record",
        ):
            schema, package = self.load_contract_021_fixture()
            package["audit_events"][0]["subject_ref"] = subject_ref
            with self.subTest(subject_ref=subject_ref):
                with self.assertRaises(ContractViolation):
                    validate_package(package)

    def test_retention_deleted_scope_rejects_restored_backup_copy(self):
        copies = [
            {
                "copy_id": "copy-primary",
                "retention_id": "retention-a",
                "subject_ref": "evidence-a",
                "parent_copy_id": None,
                "state": "DELETED",
                "recorded_at": "2026-11-15T22:03:00Z",
                "verified_at": "2026-11-15T22:03:00Z",
                "verification_reference": "verify-primary",
                "previous_state": "DELETE_PENDING",
                "transition_event_ref": "primary-deleted",
            },
            {
                "copy_id": "backup-restored",
                "retention_id": "retention-a",
                "subject_ref": "evidence-a",
                "parent_copy_id": "copy-primary",
                "state": "PRESENT",
                "recorded_at": "2026-11-15T22:04:00Z",
                "verified_at": None,
                "verification_reference": None,
                "previous_state": None,
                "transition_event_ref": "backup-restored-event",
            },
        ]
        events = [
            {"audit_event_id": "primary-discovered", "copy_id": "copy-primary",
             "retention_id": "retention-a", "subject_ref": "evidence-a",
             "from_copy_state": None, "to_copy_state": "PRESENT",
             "action": "COPY_DISCOVERED", "reason": "Primary copy discovered",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:00:00Z"},
            {"audit_event_id": "primary-pending", "copy_id": "copy-primary",
             "retention_id": "retention-a", "subject_ref": "evidence-a",
             "from_copy_state": "PRESENT", "to_copy_state": "DELETE_PENDING",
             "action": "COPY_DELETION_REQUESTED", "reason": "Deletion requested",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:01:00Z"},
            {"audit_event_id": "primary-deleted", "copy_id": "copy-primary",
             "retention_id": "retention-a", "subject_ref": "evidence-a",
             "from_copy_state": "DELETE_PENDING", "to_copy_state": "DELETED",
             "action": "COPY_DELETED", "reason": "Deletion verified",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:03:00Z"},
            {"audit_event_id": "backup-restored-event", "copy_id": "backup-restored",
             "retention_id": "retention-a", "subject_ref": "evidence-a",
             "from_copy_state": None, "to_copy_state": "PRESENT",
             "action": "COPY_DISCOVERED", "reason": "Backup restoration detected",
             "actor_role": "DATA_CUSTODIAN", "occurred_at": "2026-11-15T22:04:00Z"},
        ]
        with self.assertRaises(ContractViolation):
            validate_retention_scope("DELETED", copies, events)


    def test_021_citation_dependency_is_explicit_between_evaluated_sources(self):
        schema, package = self.load_contract_021_fixture()
        package["provenance_edges"].append({
            "edge_id": "citation-dependency",
            "dependent_node_id": "node-version-a",
            "origin_node_id": "node-version-b",
            "relation_type": "CITA_DE",
            "claim_component_id": "component-entity",
            "evidence_refs": ["evidence-a"],
            "recorded_at": "2026-11-15T22:00:00Z",
            "valid_from": None,
            "valid_to": None,
            "claim_component_version_id": "component-entity-v1",
        })
        assessment = package["independence_assessments"][0]
        assessment.update({
            "status": "DEPENDIENTE",
            "supporting_evidence_refs": ["evidence-a"],
            "dependency_edge_refs": ["citation-dependency"],
            "human_review_status": "REVIEWED",
            "reviewed_at": "2026-11-15T22:00:00Z",
        })
        self.assert_schema_valid(schema, package)
        validate_package(package)

    def test_021_citation_edge_cannot_be_claimed_as_independent_origin(self):
        schema, package = self.load_contract_021_fixture()
        package["provenance_nodes"].extend([
            {"node_id": "origin-a", "node_type": "DATASET", "entity_ref": "origin-record-a"},
            {"node_id": "origin-b", "node_type": "DOCUMENT", "entity_ref": "origin-record-b"},
        ])
        package["provenance_edges"].extend([
            {"edge_id": "path-a", "dependent_node_id": "node-version-a", "origin_node_id": "origin-a",
             "relation_type": "ORIGEN_DIRECTO", "claim_component_id": "component-entity",
             "evidence_refs": ["evidence-a"], "recorded_at": "2026-11-15T22:00:00Z",
             "valid_from": None, "valid_to": None, "claim_component_version_id": "component-entity-v1"},
            {"edge_id": "path-b", "dependent_node_id": "node-version-b", "origin_node_id": "origin-b",
             "relation_type": "CITA_DE", "claim_component_id": "component-entity",
             "evidence_refs": ["evidence-b"], "recorded_at": "2026-11-15T22:00:00Z",
             "valid_from": None, "valid_to": None, "claim_component_version_id": "component-entity-v1"},
        ])
        assessment = package["independence_assessments"][0]
        assessment.update({
            "status": "INDEPENDIENTE",
            "supporting_evidence_refs": ["evidence-a", "evidence-b"],
            "independent_path_edge_refs": ["path-a", "path-b"],
            "human_review_status": "REVIEWED",
            "reviewed_at": "2026-11-15T22:00:00Z",
        })
        self.assert_schema_valid(schema, package)
        with self.assertRaises(ContractViolation):
            validate_package(package)

    def test_021_pre_release_detection_is_distinct_from_publication_and_retrieval(self):
        schema, package = self.load_contract_021_fixture()
        version = package["source_versions"][0]
        version.update({
            "published_at": "2026-11-15T20:00:00Z",
            "first_detected_at": "2026-11-15T19:50:00Z",
            "first_publicly_observed_at": "2026-11-15T20:00:00Z",
            "retrieved_at": "2026-11-15T19:55:00Z",
        })
        self.assert_schema_valid(schema, package)
        validate_package(package)

    def test_021_source_version_rejects_retrieval_before_first_detection(self):
        schema, package = self.load_contract_021_fixture()
        version = package["source_versions"][0]
        version.update({
            "first_detected_at": "2026-11-15T20:10:00Z",
            "retrieved_at": "2026-11-15T20:05:00Z",
        })
        self.assert_schema_valid(schema, package)
        with self.assertRaises(ContractViolation):
            validate_package(package)


    def test_021_audit_events_reject_reidentifying_metadata(self):
        forbidden_values = (
            "Se consultó https://private.example.invalid/source/123",
            "Digest observado: " + "a" * 64,
            "Contacto: analyst@example.invalid",
            "Origen remoto: 192.0.2.45",
        )
        for value in forbidden_values:
            schema, package = self.load_contract_021_fixture()
            package["audit_events"][0]["reason"] = value
            with self.subTest(value=value):
                self.assert_schema_valid(schema, package)
                with self.assertRaises(ContractViolation):
                    validate_package(package)

    def test_021_audit_actor_role_rejects_personal_contact_metadata(self):
        schema, package = self.load_contract_021_fixture()
        package["audit_events"][0]["actor_role"] = "operator@example.invalid"
        self.assert_schema_valid(schema, package)
        with self.assertRaises(ContractViolation):
            validate_package(package)


    def test_backup_copy_requires_policy_reference_and_scheduled_expiration(self):
        valid_backup = {
            "copy_kind": "BACKUP",
            "backup_expiration_policy_ref": "backup-policy-2026-01",
            "scheduled_disposition_at": "2026-12-01T00:00:00Z",
            "state": "PRESENT",
            "verified_at": None,
            "verification_reference": None,
        }
        validate_backup_expiration_policy(valid_backup)
        for field, value in (
            ("backup_expiration_policy_ref", None),
            ("scheduled_disposition_at", None),
        ):
            invalid = copy.deepcopy(valid_backup)
            invalid[field] = value
            with self.subTest(field=field):
                with self.assertRaises(ContractViolation):
                    validate_backup_expiration_policy(invalid)

    def test_backup_expiration_schedule_does_not_prove_deletion(self):
        backup = {
            "copy_id": "backup-copy",
            "retention_id": "retention-a",
            "subject_ref": "evidence-a",
            "copy_kind": "BACKUP",
            "parent_copy_id": None,
            "state": "PRESENT",
            "recorded_at": "2026-11-16T02:00:00Z",
            "verified_at": None,
            "verification_reference": None,
            "scheduled_disposition_at": "2026-11-15T00:00:00Z",
            "backup_expiration_policy_ref": "backup-policy-2026-01",
            "previous_state": None,
            "transition_event_ref": "backup-discovered",
        }
        validate_backup_expiration_policy(backup)
        event = {
            "audit_event_id": "backup-discovered",
            "copy_id": "backup-copy",
            "retention_id": "retention-a",
            "subject_ref": "evidence-a",
            "from_copy_state": None,
            "to_copy_state": "PRESENT",
            "action": "COPY_DISCOVERED",
            "reason": "Backup copy discovered after scheduled expiry",
            "actor_role": "DATA_CUSTODIAN",
            "occurred_at": "2026-11-16T02:00:00Z",
        }
        with self.assertRaises(ContractViolation):
            validate_retention_scope("DELETED", [backup], [event])

    def test_non_backup_copy_rejects_backup_expiration_policy_reference(self):
        with self.assertRaises(ContractViolation):
            validate_backup_expiration_policy({
                "copy_kind": "PRIMARY",
                "backup_expiration_policy_ref": "backup-policy-2026-01",
                "scheduled_disposition_at": None,
            })

if __name__ == "__main__":
    unittest.main(verbosity=2)
