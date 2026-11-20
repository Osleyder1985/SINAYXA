"""Deterministic semantic checks for the five corrective areas of contract 0.2.1.

This module is technology-neutral and operates only on synthetic in-memory records.
It does not establish legal authorization, factual truth, or archive authenticity.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


class ContractViolation(ValueError):
    """Raised when a synthetic contract scenario violates a normative invariant."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractViolation(message)


def utc_instant(value: str) -> datetime:
    """Parse a schema-validated UTC timestamp before chronological comparison.

    Lexicographic ISO-8601 comparison is unsafe when fractional-second precision
    differs (for example, ...00.1Z versus ...00Z).
    """
    _require(isinstance(value, str) and value.endswith("Z"),
             "temporal comparisons require a UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ContractViolation("invalid UTC timestamp for chronological comparison") from exc
    _require(parsed.utcoffset() == timezone.utc.utcoffset(parsed),
             "temporal comparisons require UTC timestamps")
    return parsed


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
    _require(all(utc_instant(path["available_at"]) <= utc_instant(cutoff) for path in paths),
             "path evidence must be available at or before the cutoff")
    _require(all(path.get("origin_terminal") is True for path in paths),
             "origin must be terminal; unresolved shared intermediaries are insufficient")


def validate_analytic_replication(analyses: list[dict[str, Any]], cutoff: str) -> None:
    """Represent distinct analytical processes over common data without asserting source independence."""
    _require(len(analyses) >= 2, "analytic replication requires at least two analysis records")
    process_ids = {item["process_id"] for item in analyses}
    _require(len(process_ids) >= 2, "replication requires distinct analytical processes")
    output_refs = {item["output_evidence_ref"] for item in analyses}
    _require(len(output_refs) >= 2, "replication requires distinct output evidence for each process")
    dataset_ids = {item["dataset_origin_id"] for item in analyses}
    _require(len(dataset_ids) == 1, "this replication scenario must identify the common dataset origin")
    component_versions = {item["claim_component_version_id"] for item in analyses}
    _require(len(component_versions) == 1, "replication records must target the same component version")
    _require(all(item.get("method_reference") and item.get("output_evidence_ref") for item in analyses),
             "each analytical process requires method and output evidence references")
    _require(all(utc_instant(item.get("available_at", "")) <= utc_instant(cutoff) for item in analyses),
             "analytical output evidence must be available at the assessment cutoff")
    _require(all(item.get("assessment_cutoff") == cutoff for item in analyses),
             "replication records must share the exact assessment cutoff")


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
    component_versions = {unit.get("claim_component_version_id") for unit in supporting_units}
    cutoffs = {unit.get("assessment_cutoff") for unit in supporting_units}
    _require(len(component_versions) == 1 and None not in component_versions,
             "corroboration units must cover one exact component version")
    _require(cutoffs == {cutoff}, "corroboration units must share the exact assessment cutoff")
    non_primary = [unit for unit in supporting_units if unit["source_type"] != "PRIMARIA"]
    if non_primary:
        _require(basis in {"CORROBORACION_INDEPENDIENTE", "AMBAS"},
                 "non-primary support requires an independent-corroboration basis")
    if basis == "AMBAS":
        _require(bool(non_primary),
                 "AMBAS requires both primary-direct evidence and at least one non-primary supporting source")
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
            and item.get("unit_access_status") in {"PÚBLICO_LEGÍTIMO", "PRIVADO_AUTORIZADO"}
            and item.get("knowledge_basis") in {"OBSERVACIÓN_DIRECTA", "REGISTRO_ORIGINAL"}
            and item.get("scope_note")
            and utc_instant(item.get("available_at", "")) <= utc_instant(cutoff)
            and any(unit["source_id"] == item.get("source_id")
                    and unit["source_version_id"] == item.get("source_version_id")
                    for unit in supporting_units)
        ]
        eligible_sources = {(item["source_id"], item["source_version_id"]) for item in eligible}
        primary_supporting_sources = {
            (unit["source_id"], unit["source_version_id"])
            for unit in supporting_units
            if unit["source_type"] == "PRIMARIA"
        }
        if basis == "AMBAS":
            _require(bool(primary_supporting_sources),
                     "AMBAS requires at least one primary supporting unit")
        _require(primary_supporting_sources.issubset(eligible_sources),
                 "every primary supporting unit must have authenticated, legitimate, direct evidence scoped to the component")
    elif basis == "CORROBORACION_INDEPENDIENTE":
        _require(bool(non_primary), "independent basis must actually use non-primary corroboration")
    else:
        raise ContractViolation("unsupported corroboration basis for CORROBORADA")


def validate_backup_expiration_policy(copy: dict[str, Any]) -> None:
    """Require an explicit policy reference and scheduled date for backup copies.

    A scheduled expiry is a policy date, not evidence that the backup was deleted.
    """
    if copy.get("copy_kind") == "BACKUP":
        _require(bool(copy.get("backup_expiration_policy_ref")),
                 "backup copy requires a documented expiration policy reference")
        _require(bool(copy.get("scheduled_disposition_at")),
                 "backup copy requires its policy-scheduled expiration time")
    else:
        _require(copy.get("backup_expiration_policy_ref") is None,
                 "non-backup copy cannot carry a backup expiration policy reference")


def validate_retention_scope(
    disposition: str,
    copies: list[dict[str, Any]],
    transition_events: list[dict[str, Any]],
) -> None:
    """Validate complete copy lineage and every audited lifecycle transition."""
    ids = [copy["copy_id"] for copy in copies]
    _require(len(ids) == len(set(ids)), "copy identifiers must be unique")
    known = set(ids)
    event_ids = [event["audit_event_id"] for event in transition_events]
    _require(len(event_ids) == len(set(event_ids)), "copy transition event identifiers must be unique")
    _require(all(event.get("copy_id") in known for event in transition_events),
             "copy transition event references a copy outside this retention scope")
    allowed = {None: {"PRESENT"}, "PRESENT": {"DELETE_PENDING"},
               "DELETE_PENDING": {"DELETED"}, "DELETED": set()}
    actions = {"PRESENT": "COPY_DISCOVERED",
               "DELETE_PENDING": "COPY_DELETION_REQUESTED",
               "DELETED": "COPY_DELETED"}
    for copy in copies:
        parent = copy.get("parent_copy_id")
        _require(parent is None or parent in known, "copy lineage contains an unknown parent")
        _require(copy["state"] in {"PRESENT", "DELETE_PENDING", "DELETED"},
                 "unsupported copy lifecycle state")
        copy_events = sorted(
            (event for event in transition_events if event.get("copy_id") == copy["copy_id"]),
            key=lambda event: event.get("occurred_at", "")
        )
        _require(bool(copy_events), "every copy requires a complete audited lifecycle")
        previous_state = None
        previous_time = None
        for event in copy_events:
            _require(event.get("retention_id") == copy["retention_id"]
                     and event.get("subject_ref") == copy["subject_ref"],
                     "copy transition audit event does not match its retention subject")
            _require(event.get("from_copy_state") == previous_state,
                     "copy lifecycle audit history contains a broken state transition chain")
            next_state = event.get("to_copy_state")
            _require(next_state in allowed.get(previous_state, set()),
                     "copy lifecycle audit history contains an invalid or terminal transition")
            _require(event.get("action") == actions[next_state],
                     "copy transition audit action is inconsistent")
            _require(bool(event.get("reason")) and bool(event.get("actor_role"))
                     and bool(event.get("occurred_at")),
                     "copy transition audit event lacks actor, time, or reason")
            if previous_time is not None:
                _require(utc_instant(event["occurred_at"]) > utc_instant(previous_time),
                         "copy lifecycle audit timestamps must be strictly increasing")
            previous_state = next_state
            previous_time = event["occurred_at"]
        latest = copy_events[-1]
        _require(latest["audit_event_id"] == copy.get("transition_event_ref")
                 and latest.get("from_copy_state") == copy.get("previous_state")
                 and latest.get("to_copy_state") == copy["state"],
                 "copy record must reference its exact latest audited state transition")
        _require(utc_instant(copy.get("recorded_at", "")) >= utc_instant(latest["occurred_at"]),
                 "copy state cannot be recorded before its latest transition event")
        if copy["state"] == "DELETED":
            _require(bool(copy.get("verified_at")) and bool(copy.get("verification_reference")),
                     "DELETED copy requires a verification timestamp and reference")
            _require(utc_instant(copy["verified_at"]) >= utc_instant(latest["occurred_at"]),
                     "copy deletion verification cannot predate its deletion event")
        else:
            _require(copy.get("verified_at") is None and copy.get("verification_reference") is None,
                     "non-deleted copy cannot carry deletion verification")
    for copy in copies:
        seen = set()
        current = copy
        while current.get("parent_copy_id") is not None:
            _require(current["copy_id"] not in seen, "copy lineage cannot contain cycles")
            seen.add(current["copy_id"])
            current = next(item for item in copies if item["copy_id"] == current["parent_copy_id"])
    if disposition == "DELETED":
        _require(bool(copies), "DELETED scope must declare every copy in its scope")
        _require(all(copy["state"] == "DELETED" for copy in copies),
                 "DELETED requires verified deletion of every in-scope copy and derivative")
    elif disposition == "DELETE_PENDING":
        _require(bool(copies) and any(copy["state"] in {"PRESENT", "DELETE_PENDING"} for copy in copies),
                 "DELETE_PENDING must retain an explicitly tracked outstanding copy")
    elif disposition in {"RETAIN", "RESTRICTED"}:
        _require(bool(copies) and all(copy["state"] == "PRESENT" for copy in copies),
                 "RETAIN/RESTRICTED requires a complete inventory of present copies")
    elif disposition == "REFERENCE_ONLY":
        _require(all(copy["state"] == "DELETED" for copy in copies),
                 "REFERENCE_ONLY with copy history requires every retained copy to be verified as deleted")
    else:
        raise ContractViolation("unsupported retention disposition for copy-scope validation")

def validate_archive_attestation(
    availability: dict[str, Any], attestation: dict[str, Any], cutoff: str,
    evidence: dict[str, Any],
) -> None:
    """Bind verified archive capture to one evidence item, source version, and SHA-256 digest."""
    _require(availability.get("availability_basis") == "INDEPENDENT_ARCHIVE",
             "archive attestation applies only to INDEPENDENT_ARCHIVE")
    _require(attestation.get("evidence_id") == availability.get("evidence_id")
             == evidence.get("evidence_id"),
             "archive attestation must bind the exact evidence item in the availability record")
    _require(attestation.get("source_version_id") == evidence.get("source_version_id"),
             "archive attestation must bind the exact source version")
    integrity = evidence.get("integrity_check", {})
    _require(attestation.get("hash_algorithm") == "SHA-256"
             and integrity.get("algorithm") == "SHA-256",
             "archive content binding requires SHA-256 on both evidence and attestation")
    expected_digest = integrity.get("expected_digest")
    observed_digest = integrity.get("observed_digest")
    checked_at = integrity.get("checked_at")
    _require(integrity.get("result") == "MATCH"
             and bool(expected_digest)
             and expected_digest == observed_digest == attestation.get("captured_content_hash"),
             "archive captured content hash must match the expected and observed evidence digests")
    _require(bool(checked_at) and utc_instant(attestation["captured_at"]) <= utc_instant(checked_at) <= utc_instant(attestation["recorded_at"]),
             "evidence digest verification must follow capture and precede attestation recording")
    _require(bool(attestation.get("archive_service")), "archive service must be identified")
    _require(bool(attestation.get("capture_record_reference")), "capture record reference is required")
    _require(bool(attestation.get("captured_at")), "capture timestamp is required")
    _require(attestation.get("integrity_result") == "MATCH",
             "archive capture integrity must be verified for temporal availability")
    _require(utc_instant(attestation["captured_at"]) <= utc_instant(availability["available_at"]) <= utc_instant(cutoff),
             "archive capture and availability must not exceed the assessment cutoff")
    _require(utc_instant(attestation.get("recorded_at", "")) <= utc_instant(availability.get("recorded_at", "")),
             "archive capture attestation must be recorded before its availability record")
    _require(attestation.get("capture_record_verified") is True,
             "the specific capture record must be verified")
    _require(attestation.get("verification_method") in {
                 "ARCHIVE_API_RETRIEVAL", "SIGNATURE_OR_DIGEST_CHECK",
                 "INDEPENDENT_RECORD_REVIEW", "OTHER"
             } and bool(attestation.get("verified_by_role")) and bool(attestation.get("verified_at")),
             "capture verification requires method, role, and verification timestamp")
    _require(utc_instant(attestation["captured_at"]) <= utc_instant(attestation["verified_at"]) <= utc_instant(attestation.get("recorded_at", "")),
             "capture verification must follow capture and precede its record time")
    _require(utc_instant(attestation.get("recorded_at", "")) >= utc_instant(attestation["captured_at"]),
             "archive attestation cannot be recorded before the capture")
    if attestation.get("imported_at") is not None:
        _require(utc_instant(attestation["captured_at"]) <= utc_instant(attestation["imported_at"]) <= utc_instant(attestation["recorded_at"]),
                 "archive import time must follow capture and not exceed its record time")
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


def canonical_migration_payload_sha256(package: dict[str, Any]) -> str:
    """Hash the canonical package payload, excluding embedded migration manifests."""
    payload = dict(package)
    payload.pop("migration_records", None)
    return canonical_sha256(payload)


def validate_migration(source: dict[str, Any], target: dict[str, Any], manifest: dict[str, Any]) -> None:
    """Verify declared migration provenance and preservation of protected history."""
    _require(manifest.get("source_contract_version") == source.get("contract_version"),
             "migration source version does not match source package")
    _require(manifest.get("target_contract_version") == target.get("contract_version"),
             "migration target version does not match target package")
    _require(manifest.get("input_sha256") == canonical_migration_payload_sha256(source),
             "migration input digest does not match source package")
    _require(manifest.get("output_sha256") == canonical_migration_payload_sha256(target),
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
