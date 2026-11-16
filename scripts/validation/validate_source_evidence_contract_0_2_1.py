"""Validate the 0.2.1 JSON Schema fixture and its five corrective invariants."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from contract_0_2_1_extensions import (
    ContractViolation,
    canonical_migration_payload_sha256,
    validate_archive_attestation,
    validate_corroboration,
    validate_independence,
    validate_migration,
    validate_retention_scope,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "source-evidence-contract-0.2.1.schema.json"
BASE_SCHEMA_PATH = ROOT / "schemas" / "source-evidence-contract-0.2.0.schema.json"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "contracts" / "source-evidence-contract-v0.2.1.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractViolation(message)


def _index(records: list[dict[str, Any]], key: str, label: str) -> dict[str, dict[str, Any]]:
    result = {item[key]: item for item in records}
    require(len(result) == len(records), f"duplicate {label}")
    return result


def _available_at(package: dict[str, Any], evidence_id: str, unit: dict[str, Any]) -> str:
    matches = [
        item for item in package["evidence_availability"]
        if item["evidence_id"] == evidence_id
        and item["assessment_unit_id"] == unit["assessment_unit_id"]
        and item["claim_component_version_id"] == unit["claim_component_version_id"]
        and item["claim_version_id"] == unit["claim_version_id"]
    ]
    require(len(matches) == 1, "evidence requires exactly one availability record for its evaluated unit")
    item = matches[0]
    require(item["available_at"] is not None
            and item["availability_basis"] in {"SINAYXA_OBSERVATION", "INDEPENDENT_ARCHIVE"},
            "evidence is not verifiably available for the evaluated unit")
    require(item["available_at"] <= unit["assessment_cutoff"],
            "evidence availability is later than the unit assessment cutoff")
    return item["available_at"]


def _validate_independence_assessments(package: dict[str, Any]) -> None:
    units_by_id = _index(package["evaluation_units"], "assessment_unit_id", "assessment_unit_id")
    nodes_by_id = _index(package["provenance_nodes"], "node_id", "provenance node_id")
    edges_by_id = _index(package["provenance_edges"], "edge_id", "provenance edge_id")
    evidence_by_id = _index(package["evidence_items"], "evidence_id", "evidence_id")
    source_versions = _index(package["source_versions"], "source_version_id", "source_version_id")
    all_edges = package["provenance_edges"]

    for assessment in package["independence_assessments"]:
        units = []
        for unit_id in assessment["assessment_unit_ids"]:
            require(unit_id in units_by_id, "independence assessment references an unknown evaluation unit")
            unit = units_by_id[unit_id]
            require(
                unit["claim_id"] == assessment["claim_id"]
                and unit["claim_component_id"] == assessment["claim_component_id"]
                and unit["claim_version_id"] == assessment["claim_version_id"]
                and unit["claim_component_version_id"] == assessment["claim_component_version_id"]
                and unit["assessment_cutoff"] == assessment["assessment_cutoff"],
                "independence assessment mixes claim, component, version, or cutoff scopes",
            )
            units.append(unit)

        expected_ids = {
            unit["assessment_unit_id"] for unit in package["evaluation_units"]
            if unit["claim_id"] == assessment["claim_id"]
            and unit["claim_component_id"] == assessment["claim_component_id"]
            and unit["claim_version_id"] == assessment["claim_version_id"]
            and unit["claim_component_version_id"] == assessment["claim_component_version_id"]
            and unit["assessment_cutoff"] == assessment["assessment_cutoff"]
        }
        require(set(assessment["assessment_unit_ids"]) == expected_ids,
                "independence assessment must cover the exact evaluation-unit set for its component and cutoff")

        if assessment["status"] == "INDEPENDIENTE":
            paths = []
            for edge_id in assessment["independent_path_edge_refs"]:
                require(edge_id in edges_by_id, "independence assessment references an unknown path edge")
                edge = edges_by_id[edge_id]
                require(
                    edge["claim_component_id"] == assessment["claim_component_id"]
                    and edge["claim_component_version_id"] == assessment["claim_component_version_id"],
                    "independent path edge is scoped to a different claim component version",
                )
                dependent = nodes_by_id.get(edge["dependent_node_id"])
                origin = nodes_by_id.get(edge["origin_node_id"])
                require(dependent is not None and origin is not None, "independent path references an unknown provenance node")
                require(dependent["node_type"] == "SOURCE_VERSION", "independent path must start at a source-version node")
                source_version_id = dependent["entity_ref"]
                require(source_version_id in source_versions, "independent path references an unknown source version")
                source_version = source_versions[source_version_id]
                unit = next((item for item in units if item["source_version_id"] == source_version_id), None)
                require(unit is not None and source_version["source_id"] == unit["source_id"],
                        "independent path does not map to an evaluated source version")
                require(edge["relation_type"] == "ORIGEN_DIRECTO", "independent path must use ORIGEN_DIRECTO")
                require(origin["node_type"] != "UNKNOWN_ORIGIN" and bool(origin["entity_ref"]),
                        "independent path must terminate at an identified origin")
                require(not any(item["dependent_node_id"] == origin["node_id"] for item in all_edges),
                        "independent path origin is not terminal")
                require(bool(edge["evidence_refs"]), "independent path requires supporting evidence")
                available_times = []
                for evidence_id in edge["evidence_refs"]:
                    require(evidence_id in evidence_by_id, "independent path references unknown evidence")
                    evidence = evidence_by_id[evidence_id]
                    require(evidence["source_version_id"] == source_version_id,
                            "independence evidence must belong to the exact evaluated source version")
                    available_times.append(_available_at(package, evidence_id, unit))
                paths.append({
                    "source_id": unit["source_id"],
                    "source_version_id": source_version_id,
                    "evidence_source_version_id": evidence["source_version_id"],
                    "claim_component_version_id": assessment["claim_component_version_id"],
                    "relation_type": edge["relation_type"],
                    "origin_id": origin["entity_ref"],
                    "origin_terminal": True,
                    "evidence_ref": edge["evidence_refs"][0],
                    "available_at": max(available_times),
                })
                require(set(edge["evidence_refs"]).issubset(set(assessment["supporting_evidence_refs"])),
                        "independent path evidence must be included in assessment supporting evidence")
            validate_independence(units, paths, assessment["assessment_cutoff"])
        elif assessment["status"] == "DEPENDIENTE":
            require(bool(assessment["dependency_edge_refs"]), "DEPENDIENTE requires positive dependency edges")
            dependency_relations = {"CITA_DE", "SINDICADA_DE", "DERIVADA_DE", "DOCUMENTO_COMÚN", "CONTACTO_COMÚN"}
            for edge_id in assessment["dependency_edge_refs"]:
                require(edge_id in edges_by_id, "dependency assessment references an unknown provenance edge")
                edge = edges_by_id[edge_id]
                require(edge["relation_type"] in dependency_relations,
                        "dependency assessment references a non-dependency relation")
                require(edge["claim_component_version_id"] == assessment["claim_component_version_id"],
                        "dependency edge belongs to a different component version")
                require(bool(edge["evidence_refs"]), "dependency edge requires evidence")
                require(set(edge["evidence_refs"]).issubset(set(assessment["supporting_evidence_refs"])),
                        "dependency edge evidence must be included in assessment supporting evidence")


def _validate_corroborated_claims(package: dict[str, Any]) -> None:
    evidence_by_id = _index(package["evidence_items"], "evidence_id", "evidence_id")
    independence_by_id = _index(
        package["independence_assessments"], "independence_assessment_id", "independence_assessment_id"
    )
    units = package["evaluation_units"]
    links = package["claim_evidence_links"]

    for assessment in package["claim_assessments"]:
        if assessment["evidentiary_status"] != "CORROBORADA":
            continue
        supporting_refs = set(assessment["supporting_evidence_refs"])
        scoped_links = [
            link for link in links
            if link["claim_id"] == assessment["claim_id"]
            and link["claim_component_id"] == assessment["claim_component_id"]
            and link["claim_version_id"] == assessment["claim_version_id"]
            and link["claim_component_version_id"] == assessment["claim_component_version_id"]
            and link["evidence_id"] in supporting_refs
            and link["evidence_role"] == "SUPPORTING"
        ]
        require({link["evidence_id"] for link in scoped_links} == supporting_refs,
                "every corroborating evidence item requires an exact SUPPORTING component link")

        supporting_units = []
        primary_direct_evidence = []
        for evidence_id in supporting_refs:
            require(evidence_id in evidence_by_id, "claim assessment references unknown supporting evidence")
            evidence = evidence_by_id[evidence_id]
            matching_units = [
                unit for unit in units
                if unit["claim_id"] == assessment["claim_id"]
                and unit["claim_component_id"] == assessment["claim_component_id"]
                and unit["claim_version_id"] == assessment["claim_version_id"]
                and unit["claim_component_version_id"] == assessment["claim_component_version_id"]
                and unit["assessment_cutoff"] == assessment["assessment_cutoff"]
                and unit["source_version_id"] == evidence["source_version_id"]
            ]
            require(bool(matching_units), "supporting evidence has no evaluation unit for the exact component and cutoff")
            link = next(item for item in scoped_links if item["evidence_id"] == evidence_id)
            for unit in matching_units:
                supporting_units.append(unit)
                available_at = _available_at(package, evidence_id, unit)
                primary_direct_evidence.append({
                    "source_type": unit["source_type"],
                    "source_id": unit["source_id"],
                    "source_version_id": unit["source_version_id"],
                    "authenticity_status": evidence["authenticity_status"],
                    "access_status": unit["access_status"],
                    "knowledge_basis": unit["knowledge_basis"],
                    "scope_note": link["scope_note"],
                    "available_at": available_at,
                })

        reviewed_independent_unit_ids = set()
        for independence_ref in assessment["independence_assessment_refs"]:
            require(independence_ref in independence_by_id,
                    "corroborated assessment references an unknown independence assessment")
            independence = independence_by_id[independence_ref]
            require(
                independence["claim_id"] == assessment["claim_id"]
                and independence["claim_component_id"] == assessment["claim_component_id"]
                and independence["claim_version_id"] == assessment["claim_version_id"]
                and independence["claim_component_version_id"] == assessment["claim_component_version_id"]
                and independence["assessment_cutoff"] == assessment["assessment_cutoff"],
                "corroboration references independence from a different component, version, or cutoff",
            )
            if independence["status"] == "INDEPENDIENTE" and independence["human_review_status"] == "REVIEWED":
                reviewed_independent_unit_ids.update(independence["assessment_unit_ids"])

        validate_corroboration(
            assessment["evidentiary_status"],
            assessment["corroboration_basis"],
            supporting_units,
            primary_direct_evidence,
            reviewed_independent_unit_ids,
            assessment["assessment_cutoff"],
        )


def validate_package(
    package: dict[str, Any],
    base_schema: dict[str, Any] | None = None,
    current_schema: dict[str, Any] | None = None,
) -> None:
    units_by_id = _index(package["evaluation_units"], "assessment_unit_id", "assessment_unit_id")
    source_versions = _index(package["source_versions"], "source_version_id", "source_version_id")
    evidence_by_id = _index(package["evidence_items"], "evidence_id", "evidence_id")
    for unit in package["evaluation_units"]:
        require(unit["source_version_id"] in source_versions, "evaluation unit references an unknown source version")
        require(source_versions[unit["source_version_id"]]["source_id"] == unit["source_id"],
                "evaluation unit source identity differs from its source version")
    for evidence in package["evidence_items"]:
        require(evidence["source_version_id"] is None or evidence["source_version_id"] in source_versions,
                "evidence item references an unknown source version")

    archive_by_id = _index(package["archive_attestations"], "archive_attestation_id", "archive_attestation_id")
    for availability in package["evidence_availability"]:
        require(availability["evidence_id"] in evidence_by_id, "availability references unknown evidence")
        require(availability["assessment_unit_id"] in units_by_id, "availability references unknown evaluation unit")
        unit = units_by_id[availability["assessment_unit_id"]]
        evidence = evidence_by_id[availability["evidence_id"]]
        require(
            availability["claim_id"] == unit["claim_id"]
            and availability["claim_component_id"] == unit["claim_component_id"]
            and availability["claim_version_id"] == unit["claim_version_id"]
            and availability["claim_component_version_id"] == unit["claim_component_version_id"]
            and evidence["source_version_id"] == unit["source_version_id"],
            "availability record does not match its exact evidence and evaluation unit",
        )
        if availability["availability_basis"] == "INDEPENDENT_ARCHIVE":
            ref = availability["archive_attestation_id"]
            require(ref in archive_by_id, "INDEPENDENT_ARCHIVE availability lacks a matching capture attestation")
            validate_archive_attestation(availability, archive_by_id[ref], unit["assessment_cutoff"])
        else:
            require(availability["archive_attestation_id"] is None,
                    "non-archive availability cannot reference an archive attestation")
            if availability["available_at"] is not None:
                require(availability["availability_basis"] == "SINAYXA_OBSERVATION",
                        "a declared source timestamp cannot establish verified historical availability")
                require(availability["available_at"] <= unit["assessment_cutoff"],
                        "observed evidence is later than the evaluation-unit cutoff")
    referenced_archive_ids = {
        item["archive_attestation_id"] for item in package["evidence_availability"]
        if item["availability_basis"] == "INDEPENDENT_ARCHIVE"
    }
    require(set(archive_by_id) == referenced_archive_ids,
            "archive attestation collection contains an orphan capture record")

    _validate_independence_assessments(package)
    _validate_corroborated_claims(package)

    retention_by_id = _index(package["retention_records"], "retention_id", "retention_id")
    copy_ids = [item["copy_id"] for item in package["retention_copy_records"]]
    require(len(copy_ids) == len(set(copy_ids)), "duplicate copy_id across retention scopes")
    event_ids = [event["audit_event_id"] for event in package["audit_events"]]
    require(len(event_ids) == len(set(event_ids)), "duplicate audit_event_id")
    copies_by_retention = {key: [] for key in retention_by_id}
    for copy_record in package["retention_copy_records"]:
        retention_id = copy_record["retention_id"]
        require(retention_id in retention_by_id, "copy record references unknown retention_id")
        require(copy_record["subject_ref"] == retention_by_id[retention_id]["subject_ref"],
                "copy record subject differs from its retention subject")
        copies_by_retention[retention_id].append(copy_record)

    all_copy_ids = set(copy_ids)
    all_copy_events = [event for event in package["audit_events"] if event.get("copy_id") is not None]
    require(all(event["copy_id"] in all_copy_ids for event in all_copy_events),
            "copy audit event references an unknown copy")
    for retention_id, record in retention_by_id.items():
        copies = copies_by_retention[retention_id]
        declared = set(record["copy_scope_ids"])
        actual = {item["copy_id"] for item in copies}
        require(declared == actual, "retention copy_scope_ids must exactly match its copy inventory")
        if copies:
            scoped_copy_ids = {item["copy_id"] for item in copies}
            events = [event for event in all_copy_events if event["copy_id"] in scoped_copy_ids]
            validate_retention_scope(record["disposition"], copies, events)
        else:
            require(not record["content_retained"] and record["disposition"] == "REFERENCE_ONLY",
                    "a retention state involving content requires an explicit copy inventory")

    migration_ids = [item["migration_id"] for item in package["migration_records"]]
    require(len(migration_ids) == len(set(migration_ids)), "duplicate migration_id")
    for record in package["migration_records"]:
        require(record["source_contract_version"] != record["target_contract_version"],
                "migration source and target contract versions must differ")
        if record["result"] == "PASS":
            require(not record["loss_report"], "successful migration cannot report data loss")
            require(base_schema is not None and current_schema is not None,
                    "migration verification requires both source and target JSON Schemas")
            source_snapshot = record["source_snapshot"]
            target_snapshot = record["target_snapshot"]
            source_errors = list(Draft202012Validator(base_schema, format_checker=FormatChecker()).iter_errors(source_snapshot))
            target_errors = list(Draft202012Validator(current_schema, format_checker=FormatChecker()).iter_errors(target_snapshot))
            require(not source_errors and not target_errors,
                    "migration source or target snapshot fails its versioned JSON Schema")
            require(not target_snapshot["migration_records"],
                    "migration target snapshot cannot recursively embed migration records")
            validate_package(target_snapshot, base_schema, current_schema)
            validate_migration(source_snapshot, target_snapshot, record)


def main() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    base_schema = json.loads(BASE_SCHEMA_PATH.read_text(encoding="utf-8"))
    package = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    vocabulary_paths = (
        ("claimAssessment", "evidentiary_status"),
        ("evaluationUnit", "source_type"),
        ("evaluationUnit", "source_subtype"),
        ("evaluationUnit", "knowledge_basis"),
        ("evaluationUnit", "institutional_character"),
        ("evaluationUnit", "dissemination"),
        ("identityAssessment", "identity"),
        ("independenceAssessment", "status"),
        ("factorAssessment", "dimension"),
        ("factorAssessment", "status"),
        ("evidence", "information_nature"),
    )
    for definition, property_name in vocabulary_paths:
        base_enum = base_schema["$defs"][definition]["properties"][property_name].get("enum")
        current_enum = schema["$defs"][definition]["properties"][property_name].get("enum")
        require(base_enum == current_enum,
                f"0.2.1 changed the approved 0.2.0 vocabulary: {definition}.{property_name}")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(package), key=lambda error: list(error.path))
    if errors:
        details = "\n".join(f"- {list(error.path)}: {error.message}" for error in errors)
        raise SystemExit(f"Contract 0.2.1 schema validation failed:\n{details}")
    validate_package(package, base_schema, schema)
    print("Result: PASS")
    print("ContractVersion: 0.2.1")
    print(f"ArchiveAttestations: {len(package['archive_attestations'])}")
    print(f"RetentionCopyRecords: {len(package['retention_copy_records'])}")
    print(f"MigrationRecords: {len(package['migration_records'])}")
    print("Issue #15/#16 vocabulary: exact preservation of the 0.2.0 validated catalogues")
    print("Scope: synthetic schema and semantic extension conformance only")


if __name__ == "__main__":
    main()
