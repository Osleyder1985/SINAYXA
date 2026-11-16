"""Validate the 0.2.1 JSON Schema fixture and its five corrective invariants."""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from contract_0_2_1_extensions import (
    ContractViolation,
    validate_archive_attestation,
    validate_retention_scope,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "source-evidence-contract-0.2.1.schema.json"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "contracts" / "source-evidence-contract-v0.2.1.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractViolation(message)


def validate_package(package: dict) -> None:
    archive_by_id = {}
    for item in package["archive_attestations"]:
        key = item["archive_attestation_id"]
        require(key not in archive_by_id, "duplicate archive_attestation_id")
        archive_by_id[key] = item

    availability_archive_refs = set()
    for availability in package["evidence_availability"]:
        if availability["availability_basis"] == "INDEPENDENT_ARCHIVE":
            ref = availability["archive_attestation_id"]
            require(ref in archive_by_id, "INDEPENDENT_ARCHIVE availability lacks a matching capture attestation")
            require(ref not in availability_archive_refs, "one archive attestation cannot be silently reused for multiple availability records")
            availability_archive_refs.add(ref)
            unit = next(u for u in package["evaluation_units"] if u["assessment_unit_id"] == availability["assessment_unit_id"])
            validate_archive_attestation(availability, archive_by_id[ref], unit["assessment_cutoff"])
        else:
            require(availability["archive_attestation_id"] is None,
                    "non-archive availability cannot reference an archive attestation")

    retention_by_id = {r["retention_id"]: r for r in package["retention_records"]}
    require(len(retention_by_id) == len(package["retention_records"]), "duplicate retention_id")
    copies_by_retention = {key: [] for key in retention_by_id}
    for copy_record in package["retention_copy_records"]:
        retention_id = copy_record["retention_id"]
        require(retention_id in retention_by_id, "copy record references unknown retention_id")
        require(copy_record["subject_ref"] == retention_by_id[retention_id]["subject_ref"],
                "copy record subject differs from its retention subject")
        copies_by_retention[retention_id].append(copy_record)

    for retention_id, record in retention_by_id.items():
        copies = copies_by_retention[retention_id]
        declared = set(record["copy_scope_ids"])
        actual = {item["copy_id"] for item in copies}
        require(declared == actual, "retention copy_scope_ids must exactly match its copy inventory")
        if copies:
            events = [event for event in package["audit_events"] if event.get("copy_id") is not None]
            validate_retention_scope(record["disposition"], copies, events)
        else:
            require(not record["content_retained"] and record["disposition"] == "REFERENCE_ONLY",
                    "a retention state involving content requires an explicit copy inventory")

    for record in package["migration_records"]:
        require(record["source_contract_version"] != record["target_contract_version"],
                "migration source and target contract versions must differ")
        if record["result"] == "PASS":
            require(not record["loss_report"], "successful migration cannot report data loss")


def main() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    package = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(package), key=lambda error: list(error.path))
    if errors:
        details = "\n".join(f"- {list(error.path)}: {error.message}" for error in errors)
        raise SystemExit(f"Contract 0.2.1 schema validation failed:\n{details}")
    validate_package(package)
    print("Result: PASS")
    print("ContractVersion: 0.2.1")
    print(f"ArchiveAttestations: {len(package['archive_attestations'])}")
    print(f"RetentionCopyRecords: {len(package['retention_copy_records'])}")
    print(f"MigrationRecords: {len(package['migration_records'])}")
    print("Scope: synthetic schema and semantic extension conformance only")


if __name__ == "__main__":
    main()
