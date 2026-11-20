"""JSON Schema and cross-entity validation for Source & Evidence contract 0.2.1."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = ROOT / "schemas" / "source-evidence-contract-0.2.1.schema.json"


class ContractPackageError(ValueError):
    """Raised when a contract package is structurally or semantically invalid."""


def _index(rows: list[dict[str, Any]], key: str, label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = row[key]
        if value in result:
            raise ContractPackageError(f"duplicate {label}: {value}")
        result[value] = row
    return result


def _require_ref(index: dict[str, dict[str, Any]], value: str | None, label: str) -> dict[str, Any]:
    if value is None or value not in index:
        raise ContractPackageError(f"unknown {label} reference: {value}")
    return index[value]


def _require_refs(index: dict[str, dict[str, Any]], values: list[str], label: str) -> None:
    for value in values:
        _require_ref(index, value, label)


def validate_contract_package(
    package: dict[str, Any],
    schema_path: Path | str = DEFAULT_SCHEMA_PATH,
) -> dict[str, Any]:
    """Validate the pinned JSON Schema and cross-entity references.

    No source collection, identity inference, timestamp repair, credibility,
    independence or causality scoring is performed.
    """
    path = Path(schema_path)
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractPackageError(f"cannot load contract schema: {exc}") from exc

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(package), key=lambda item: list(item.absolute_path))
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.absolute_path) or "$"
        raise ContractPackageError(f"schema validation failed at {location}: {first.message}")

    claims = _index(package["claims"], "claim_version_id", "claim_version_id")
    components = _index(
        package["claim_components"], "claim_component_version_id", "claim_component_version_id"
    )
    sources = _index(package["sources"], "source_id", "source_id")
    source_versions = _index(package["source_versions"], "source_version_id", "source_version_id")
    units = _index(package["evaluation_units"], "assessment_unit_id", "assessment_unit_id")
    evidence = _index(package["evidence_items"], "evidence_id", "evidence_id")
    availability = _index(
        package["evidence_availability"], "availability_id", "availability_id"
    )
    nodes = _index(package["provenance_nodes"], "node_id", "node_id")
    edges = _index(package["provenance_edges"], "edge_id", "edge_id")
    independence = _index(
        package["independence_assessments"],
        "independence_assessment_id",
        "independence_assessment_id",
    )
    claim_assessments = _index(
        package["claim_assessments"], "claim_assessment_id", "claim_assessment_id"
    )
    retention = _index(package["retention_records"], "retention_id", "retention_id")
    audit = _index(package["audit_events"], "audit_event_id", "audit_event_id")
    archive = _index(
        package["archive_attestations"], "archive_attestation_id", "archive_attestation_id"
    )
    copies = _index(package["retention_copy_records"], "copy_id", "copy_id")
    _index(package["migration_records"], "migration_id", "migration_id")

    claim_versions: dict[str, set[str]] = {}
    for row in package["claims"]:
        claim_versions.setdefault(row["claim_id"], set()).add(row["claim_version_id"])
    for row in package["claims"]:
        previous = row["supersedes_claim_version_id"]
        if previous is not None and previous not in claim_versions[row["claim_id"]]:
            raise ContractPackageError("claim supersession must reference a version of the same claim")

    component_versions: dict[str, set[str]] = {}
    for row in package["claim_components"]:
        component_versions.setdefault(row["claim_component_id"], set()).add(
            row["claim_component_version_id"]
        )
        claim = _require_ref(claims, row["claim_version_id"], "claim_version_id")
        if claim["claim_id"] != row["claim_id"]:
            raise ContractPackageError("claim component references a mismatched claim version")
    for row in package["claim_components"]:
        previous = row["supersedes_component_version_id"]
        if previous is not None and previous not in component_versions[row["claim_component_id"]]:
            raise ContractPackageError(
                "component supersession must reference a version of the same component"
            )

    source_version_ids: dict[str, set[str]] = {}
    for row in package["source_versions"]:
        _require_ref(sources, row["source_id"], "source_id")
        source_version_ids.setdefault(row["source_id"], set()).add(row["source_version_id"])
    for row in package["source_versions"]:
        previous = row["supersedes_source_version_id"]
        if previous is not None and previous not in source_version_ids[row["source_id"]]:
            raise ContractPackageError(
                "source-version supersession must reference a version of the same source"
            )

    for row in package["identity_assessments"]:
        _require_ref(sources, row["source_id"], "source_id")
        _require_refs(evidence, row["verification_evidence_refs"], "evidence_id")

    for row in package["evaluation_units"]:
        claim = _require_ref(claims, row["claim_version_id"], "claim_version_id")
        component = _require_ref(
            components, row["claim_component_version_id"], "claim_component_version_id"
        )
        source_version = _require_ref(
            source_versions, row["source_version_id"], "source_version_id"
        )
        if claim["claim_id"] != row["claim_id"]:
            raise ContractPackageError("evaluation unit references a mismatched claim")
        if component["claim_component_id"] != row["claim_component_id"]:
            raise ContractPackageError("evaluation unit references a mismatched component")
        if component["claim_id"] != row["claim_id"]:
            raise ContractPackageError("evaluation unit component belongs to another claim")
        if source_version["source_id"] != row["source_id"]:
            raise ContractPackageError("evaluation unit references a mismatched source version")
        _require_ref(sources, row["source_id"], "source_id")

    for row in package["evidence_items"]:
        _require_ref(source_versions, row["source_version_id"], "source_version_id")

    for row in package["evidence_availability"]:
        _require_ref(evidence, row["evidence_id"], "evidence_id")
        unit = _require_ref(units, row["assessment_unit_id"], "assessment_unit_id")
        for key in ("claim_id", "claim_component_id", "claim_version_id", "claim_component_version_id"):
            if unit[key] != row[key]:
                raise ContractPackageError(f"evidence availability mismatches evaluation unit field {key}")
        if row["archive_attestation_id"] is not None:
            _require_ref(archive, row["archive_attestation_id"], "archive_attestation_id")

    for row in package["claim_evidence_links"]:
        claim = _require_ref(claims, row["claim_version_id"], "claim_version_id")
        component = _require_ref(
            components, row["claim_component_version_id"], "claim_component_version_id"
        )
        _require_ref(evidence, row["evidence_id"], "evidence_id")
        if claim["claim_id"] != row["claim_id"]:
            raise ContractPackageError("claim-evidence link references a mismatched claim")
        if component["claim_component_id"] != row["claim_component_id"]:
            raise ContractPackageError("claim-evidence link references a mismatched component")
        if component["claim_id"] != row["claim_id"]:
            raise ContractPackageError("claim-evidence link component belongs to another claim")

    for row in package["provenance_nodes"]:
        if row["node_type"] == "SOURCE_VERSION" and row["entity_ref"] is not None:
            _require_ref(source_versions, row["entity_ref"], "source_version_id")
        elif row["node_type"] == "EVIDENCE_ITEM" and row["entity_ref"] is not None:
            _require_ref(evidence, row["entity_ref"], "evidence_id")

    for row in package["provenance_edges"]:
        _require_ref(nodes, row["dependent_node_id"], "dependent_node_id")
        _require_ref(nodes, row["origin_node_id"], "origin_node_id")
        component = _require_ref(
            components, row["claim_component_version_id"], "claim_component_version_id"
        )
        if component["claim_component_id"] != row["claim_component_id"]:
            raise ContractPackageError("provenance edge references a mismatched component")
        _require_refs(evidence, row["evidence_refs"], "evidence_id")

    for row in package["factor_assessments"]:
        _require_ref(units, row["assessment_unit_id"], "assessment_unit_id")
        _require_refs(evidence, row["supporting_evidence_refs"], "evidence_id")
        _require_refs(evidence, row["contrary_evidence_refs"], "evidence_id")

    for row in package["independence_assessments"]:
        claim = _require_ref(claims, row["claim_version_id"], "claim_version_id")
        component = _require_ref(
            components, row["claim_component_version_id"], "claim_component_version_id"
        )
        if claim["claim_id"] != row["claim_id"] or component["claim_component_id"] != row["claim_component_id"]:
            raise ContractPackageError("independence assessment references mismatched claim/component")
        if component["claim_id"] != row["claim_id"]:
            raise ContractPackageError("independence assessment component belongs to another claim")
        _require_refs(units, row["assessment_unit_ids"], "assessment_unit_id")
        _require_refs(edges, row["dependency_edge_refs"], "edge_id")
        _require_refs(edges, row["independent_path_edge_refs"], "edge_id")
        _require_refs(edges, row.get("unresolved_provenance_edge_refs", []), "edge_id")
        _require_refs(evidence, row["supporting_evidence_refs"], "evidence_id")

    for row in package["claim_assessments"]:
        claim = _require_ref(claims, row["claim_version_id"], "claim_version_id")
        component = _require_ref(
            components, row["claim_component_version_id"], "claim_component_version_id"
        )
        if claim["claim_id"] != row["claim_id"] or component["claim_component_id"] != row["claim_component_id"]:
            raise ContractPackageError("claim assessment references mismatched claim/component")
        if component["claim_id"] != row["claim_id"]:
            raise ContractPackageError("claim assessment component belongs to another claim")
        _require_refs(evidence, row["supporting_evidence_refs"], "evidence_id")
        _require_refs(evidence, row["contrary_evidence_refs"], "evidence_id")
        _require_refs(independence, row["independence_assessment_refs"], "independence_assessment_id")
        previous = row["supersedes_assessment_id"]
        if previous is not None:
            _require_ref(claim_assessments, previous, "claim_assessment_id")

    for row in package["audit_events"]:
        if row.get("retention_id") is not None:
            _require_ref(retention, row["retention_id"], "retention_id")

    for row in package["archive_attestations"]:
        _require_ref(evidence, row["evidence_id"], "evidence_id")
        _require_ref(source_versions, row["source_version_id"], "source_version_id")

    for row in package["retention_copy_records"]:
        _require_ref(retention, row["retention_id"], "retention_id")
        if row["parent_copy_id"] is not None:
            _require_ref(copies, row["parent_copy_id"], "copy_id")
        _require_ref(audit, row["transition_event_ref"], "audit_event_id")

    for row in package["analysis_processes"]:
        _require_ref(components, row["claim_component_version_id"], "claim_component_version_id")
        _require_ref(evidence, row["output_evidence_ref"], "evidence_id")

    return package
