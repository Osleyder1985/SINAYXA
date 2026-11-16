"""Deterministic semantic checks for the five corrective areas of contract 0.2.1.

This module is technology-neutral and operates only on synthetic in-memory records.
It does not establish legal authorization, factual truth, or archive authenticity.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


class ContractViolation(ValueError):
    """Raised when a synthetic contract scenario violates a normative invariant."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractViolation(message)


def validate_independence(units: list[dict[str, Any]], paths: list[dict[str, Any]], cutoff: str) -> None:
    """Validate complete, distinct, cutoff-available direct-origin paths."""
    _require(len(units) >= 2, "independence requires at least two evaluated units")
    source_ids = {unit["source_id"] for unit in units}
    _require(len(source_ids) >= 2, "multiple versions of one source are not independent")
    versions = {unit["source_version_id"] for unit in units}
    _require(len(paths) == len(units), "every evaluated source version needs exactly one direct path")
    path_versions = [path["source_version_id"] for path in paths]
    _require(set(path_versions) == versions and len(path_versions) == len(set(path_versions)),
             "paths must cover every evaluated source version exactly once")
    component_versions = {unit["claim_component_version_id"] for unit in units}
    _require(len(component_versions) == 1, "independence cannot mix component versions")
    _require(all(path["claim_component_version_id"] in component_versions for path in paths),
             "path must apply to the exact component version")
    _require(all(path["relation_type"] == "ORIGEN_DIRECTO" for path in paths),
             "independent path must be a direct-origin path")
    origins = [path["origin_id"] for path in paths]
    _require(all(origins) and len(origins) == len(set(origins)),
             "independent paths must have distinct identified terminal origins")
    _require(all(path["evidence_ref"] for path in paths), "each path needs evidence")
    _require(all(path["available_at"] <= cutoff for path in paths),
             "path evidence must be available at or before the cutoff")
    _require(all(path.get("origin_terminal") is True for path in paths),
             "origin must be terminal; unresolved shared intermediaries are insufficient")


def validate_corroboration(
    status: str,
    basis: str,
    supporting_units: list[dict[str, Any]],
    primary_direct_evidence: list[dict[str, Any]],
    reviewed_independent_unit_ids: set[str],
    cutoff: str,
) -> None:
    """Validate the evidentiary basis without conflating authenticity and truth."""
    if status != "CORROBORADA":
        return
    _require(bool(supporting_units), "corroboration requires supporting units")
    non_primary = [unit for unit in supporting_units if unit["source_type"] != "PRIMARIA"]
    if non_primary:
        _require(basis in {"CORROBORACION_INDEPENDIENTE", "AMBAS"},
                 "non-primary support requires an independent-corroboration basis")
        _require(len({u["source_id"] for u in supporting_units}) >= 2,
                 "independent corroboration requires distinct source identities")
        _require(all(u["assessment_unit_id"] in reviewed_independent_unit_ids for u in supporting_units),
                 "every supporting unit must be covered by reviewed independence")
    if basis in {"EVIDENCIA_PRIMARIA_DIRECTA", "AMBAS"}:
        eligible = [
            item for item in primary_direct_evidence
            if item.get("source_type") == "PRIMARIA"
            and item.get("authenticity_status") == "AUTENTICADA"
            and item.get("access_status") in {"PÚBLICO_LEGÍTIMO", "PRIVADO_AUTORIZADO"}
            and item.get("knowledge_basis") in {"OBSERVACIÓN_DIRECTA", "REGISTRO_ORIGINAL"}
            and item.get("scope_note")
            and item.get("available_at", "") <= cutoff
        ]
        _require(bool(eligible),
                 "primary-direct basis requires authenticated, legitimate, direct evidence scoped to the component")
    elif basis == "CORROBORACION_INDEPENDIENTE":
        _require(bool(non_primary), "independent basis must actually use non-primary corroboration")
    else:
        raise ContractViolation("unsupported corroboration basis for CORROBORADA")


def validate_retention_scope(
    disposition: str,
    copies: list[dict[str, Any]],
    transition_events: list[dict[str, Any]],
) -> None:
    """Require complete copy/derivative scope before declaring deletion complete."""
    ids = [copy["copy_id"] for copy in copies]
    _require(len(ids) == len(set(ids)), "copy identifiers must be unique")
    known = set(ids)
    for copy in copies:
        parent = copy.get("parent_copy_id")
        _require(parent is None or parent in known, "copy lineage contains an unknown parent")
        _require(copy["state"] in {"PRESENT", "DELETE_PENDING", "DELETED"},
                 "unsupported copy lifecycle state")
    for copy in copies:
        seen = set()
        current = copy
        while current.get("parent_copy_id") is not None:
            _require(current["copy_id"] not in seen, "copy lineage cannot contain cycles")
            seen.add(current["copy_id"])
            current = next(item for item in copies if item["copy_id"] == current["parent_copy_id"])
    _require(len(transition_events) == len(copies),
             "each in-scope copy requires exactly one correlated transition event")
    event_copy_ids = [event["copy_id"] for event in transition_events]
    _require(set(event_copy_ids) == known and len(event_copy_ids) == len(set(event_copy_ids)),
             "transition events must cover each in-scope copy exactly once")
    if disposition == "DELETED":
        _require(all(copy["state"] == "DELETED" and copy.get("verified_at") and copy.get("verification_reference")
                     for copy in copies),
                 "DELETED requires verified deletion of every in-scope copy and derivative")
    elif disposition == "DELETE_PENDING":
        _require(any(copy["state"] in {"PRESENT", "DELETE_PENDING"} for copy in copies),
                 "DELETE_PENDING must retain an explicitly tracked outstanding copy")
    else:
        raise ContractViolation("this check accepts only DELETE_PENDING or DELETED dispositions")


def validate_archive_attestation(availability: dict[str, Any], attestation: dict[str, Any], cutoff: str) -> None:
    """Check archive capture provenance; never infer authenticity or truth."""
    _require(availability.get("availability_basis") == "INDEPENDENT_ARCHIVE",
             "archive attestation applies only to INDEPENDENT_ARCHIVE")
    _require(bool(attestation.get("archive_service")), "archive service must be identified")
    _require(bool(attestation.get("capture_record_reference")), "capture record reference is required")
    _require(bool(attestation.get("captured_at")), "capture timestamp is required")
    _require(attestation.get("integrity_result") == "MATCH",
             "archive capture integrity must be verified for temporal availability")
    _require(attestation["captured_at"] <= availability["available_at"] <= cutoff,
             "archive capture and availability must not exceed the assessment cutoff")
    _require(attestation.get("capture_record_verified") is True,
             "the specific capture record must be verified")
    _require(attestation.get("content_authenticity") in {"UNKNOWN", "NOT_ASSESSED"},
             "archive attestation cannot promote content authenticity")
    _require(attestation.get("content_truth") in {"UNKNOWN", "NOT_ASSESSED"},
             "archive attestation cannot promote factual truth")


def validate_backup_expiration(copy_record: dict[str, Any], checked_at: str) -> None:
    """Keep a backup pending until its documented expiry and deletion are verified."""
    _require(copy_record.get("copy_type") == "BACKUP", "backup expiry rules apply only to backup copies")
    _require(bool(copy_record.get("expiry_policy_ref")), "backup expiry policy reference is required")
    expires_at = copy_record.get("expires_at")
    _require(bool(expires_at), "documented backup expiry timestamp is required")
    _require(copy_record.get("state") in {"DELETE_PENDING", "DELETED"},
             "backup must remain DELETE_PENDING or become DELETED after verification")
    if checked_at < expires_at:
        _require(copy_record.get("state") == "DELETE_PENDING",
                 "backup cannot be DELETED before its documented expiry")
        _require(not copy_record.get("deletion_verified_at"),
                 "backup deletion cannot be verified before its documented expiry")
        return
    if copy_record.get("state") == "DELETED":
        verified_at = copy_record.get("deletion_verified_at")
        _require(bool(verified_at), "expired backup requires an explicit deletion verification")
        _require(expires_at <= verified_at <= checked_at,
                 "backup deletion verification must occur after expiry and no later than the check")
        _require(bool(copy_record.get("verification_reference")),
                 "backup deletion verification reference is required")


def validate_backup_restore(restore_record: dict[str, Any], reconciliation: dict[str, Any]) -> None:
    """Prevent restored deleted material from becoming available before reconciliation."""
    _require(restore_record.get("source_disposition") == "DELETED",
             "restore reconciliation applies to material previously declared DELETED")
    _require(bool(restore_record.get("restore_id")), "restore event identity is required")
    _require(bool(restore_record.get("restored_copy_id")), "restored copy identity is required")
    _require(restore_record.get("restored_state") == "DELETE_PENDING",
             "restored material must enter DELETE_PENDING before reconciliation")
    _require(restore_record.get("exposed") is False,
             "restored material cannot be exposed before reconciliation and suppression")
    _require(reconciliation.get("restore_id") == restore_record.get("restore_id"),
             "reconciliation must reference the exact restore event")
    _require(reconciliation.get("copy_id") == restore_record.get("restored_copy_id"),
             "reconciliation must reference the exact restored copy")
    _require(reconciliation.get("status") == "VERIFIED",
             "restored material requires verified reconciliation")
    _require(reconciliation.get("suppression_applied") is True,
             "restored deleted material must be suppressed before any exposure")
    _require(bool(reconciliation.get("verified_at")) and bool(reconciliation.get("verification_reference")),
             "reconciliation requires a timestamp and verification reference")


PROTECTED_HISTORY_FIELDS = (
    "claims", "claim_components", "sources", "source_versions", "identity_assessments",
    "evaluation_units", "evidence_items", "evidence_availability", "claim_evidence_links",
    "provenance_nodes", "provenance_edges", "factor_assessments", "independence_assessments",
    "claim_assessments", "retention_records", "audit_events",
)


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_migration(source: dict[str, Any], target: dict[str, Any], manifest: dict[str, Any]) -> None:
    """Verify declared migration provenance and preservation of protected history."""
    _require(manifest.get("source_contract_version") == source.get("contract_version"),
             "migration source version does not match source package")
    _require(manifest.get("target_contract_version") == target.get("contract_version"),
             "migration target version does not match target package")
    _require(manifest.get("input_sha256") == canonical_sha256(source),
             "migration input digest does not match source package")
    _require(manifest.get("output_sha256") == canonical_sha256(target),
             "migration output digest does not match target package")
    _require(bool(manifest.get("migration_id")) and bool(manifest.get("migrator_version")),
             "migration identity and migrator version are required")
    _require(bool(manifest.get("rules_applied")), "migration rules must be declared")
    _require(manifest.get("result") == "PASS", "migration manifest must report PASS")
    for field in PROTECTED_HISTORY_FIELDS:
        _require(source.get(field) == target.get(field),
                 f"migration changed protected historical field: {field}")
