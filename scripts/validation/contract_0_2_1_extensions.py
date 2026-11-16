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
    _require(all(unit.get("assessment_cutoff") == cutoff for unit in units),
             "all evaluated units must share the exact independence cutoff")
    _require(len(paths) == len(units), "every evaluated source version needs exactly one direct path")
    path_versions = [path["source_version_id"] for path in paths]
    unit_by_version = {unit["source_version_id"]: unit for unit in units}
    for path in paths:
        unit = unit_by_version.get(path["source_version_id"])
        _require(unit is not None and path.get("source_id") == unit["source_id"],
                 "provenance path must map to the exact evaluated source identity")
        _require(path.get("evidence_source_version_id") == path["source_version_id"],
                 "path evidence must originate from the exact evaluated source version")
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
    if basis in {"CORROBORACION_INDEPENDIENTE", "AMBAS"}:
        _require(len(supporting_units) >= 2
                 and len({u["source_id"] for u in supporting_units}) >= 2,
                 "independent corroboration requires at least two distinct source identities")
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
    """Require an auditable copy/derivative inventory before declaring deletion complete."""
    ids = [copy["copy_id"] for copy in copies]
    _require(len(ids) == len(set(ids)), "copy identifiers must be unique")
    known = set(ids)
    event_ids = [event["audit_event_id"] for event in transition_events]
    _require(len(event_ids) == len(set(event_ids)), "copy transition event identifiers must be unique")
    event_by_id = {event["audit_event_id"]: event for event in transition_events}
    for copy in copies:
        parent = copy.get("parent_copy_id")
        _require(parent is None or parent in known, "copy lineage contains an unknown parent")
        _require(copy["state"] in {"PRESENT", "DELETE_PENDING", "DELETED"},
                 "unsupported copy lifecycle state")
        previous = copy.get("previous_state")
        allowed = {None: {"PRESENT"}, "PRESENT": {"DELETE_PENDING"},
                   "DELETE_PENDING": {"DELETED"}, "DELETED": set()}
        _require(copy["state"] in allowed.get(previous, set()), "invalid or terminal copy lifecycle transition")
        event = event_by_id.get(copy.get("transition_event_ref"))
        _require(event is not None, "copy transition event reference is missing")
        _require(event.get("copy_id") == copy["copy_id"]
                 and event.get("retention_id") == copy["retention_id"]
                 and event.get("subject_ref") == copy["subject_ref"]
                 and event.get("from_copy_state") == previous
                 and event.get("to_copy_state") == copy["state"],
                 "copy transition audit event does not match the copy, subject, or recorded state transition")
        _require(event.get("occurred_at", "") >= copy.get("recorded_at", ""),
                 "copy transition audit event cannot predate the recorded state")
        expected_action = {"PRESENT": "COPY_DISCOVERED",
                           "DELETE_PENDING": "COPY_DELETION_REQUESTED",
                           "DELETED": "COPY_DELETED"}[copy["state"]]
        _require(event.get("action") == expected_action, "copy transition audit action is inconsistent")
        _require(bool(event.get("reason")) and bool(event.get("actor_role"))
                 and bool(event.get("occurred_at")), "copy transition audit event lacks actor, time, or reason")
    for copy in copies:
        seen = set()
        current = copy
        while current.get("parent_copy_id") is not None:
            _require(current["copy_id"] not in seen, "copy lineage cannot contain cycles")
            seen.add(current["copy_id"])
            current = next(item for item in copies if item["copy_id"] == current["parent_copy_id"])
    if disposition == "DELETED":
        _require(bool(copies), "DELETED scope must declare every copy in its scope")
        _require(all(copy["state"] == "DELETED" and copy.get("verified_at")
                     and copy.get("verification_reference") for copy in copies),
                 "DELETED requires verified deletion of every in-scope copy and derivative")
    elif disposition == "DELETE_PENDING":
        _require(bool(copies) and any(copy["state"] in {"PRESENT", "DELETE_PENDING"} for copy in copies),
                 "DELETE_PENDING must retain an explicitly tracked outstanding copy")
    elif disposition in {"RETAIN", "RESTRICTED"}:
        _require(bool(copies) and all(copy["state"] == "PRESENT" for copy in copies),
                 "RETAIN/RESTRICTED requires a complete inventory of present copies")
    elif disposition == "REFERENCE_ONLY":
        _require(all(copy["state"] == "DELETED" and copy.get("verified_at")
                     and copy.get("verification_reference") for copy in copies),
                 "REFERENCE_ONLY with copy history requires every retained copy to be verified as deleted")
    else:
        raise ContractViolation("unsupported retention disposition for copy-scope validation")

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
    def preserves(previous: Any, migrated: Any, path: str) -> None:
        if isinstance(previous, dict):
            _require(isinstance(migrated, dict), f"migration changed object type at {path}")
            for key, value in previous.items():
                if path == "$" and key == "contract_version":
                    continue
                _require(key in migrated, f"migration dropped historical field: {path}.{key}")
                preserves(value, migrated[key], f"{path}.{key}")
        elif isinstance(previous, list):
            _require(isinstance(migrated, list) and len(previous) == len(migrated),
                     f"migration changed historical collection cardinality at {path}")
            for index, value in enumerate(previous):
                preserves(value, migrated[index], f"{path}[{index}]")
        else:
            _require(previous == migrated, f"migration changed historical value at {path}")

    preserves(source, target, "$")
    for field in PROTECTED_HISTORY_FIELDS:
        _require(field in source and field in target,
                 f"migration omitted required historical collection: {field}")
