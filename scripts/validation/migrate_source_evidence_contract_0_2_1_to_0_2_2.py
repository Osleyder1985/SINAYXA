"""Fail-closed migration from source-evidence contract 0.2.1 to 0.2.2."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SCHEMA = ROOT / "schemas" / "source-evidence-contract-0.2.1.schema.json"
TARGET_SCHEMA = ROOT / "schemas" / "source-evidence-contract-0.2.2.schema.json"
ROLE_CATALOG = ROOT / "schemas" / "catalogs" / "audit-actor-roles-1.0.0.json"
REASON_CATALOG = ROOT / "schemas" / "catalogs" / "audit-reason-codes-1.0.0.json"
UUID4 = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
MIGRATOR_VERSION = "0.1.0"


class MigrationRejected(ValueError):
    """Raised when a source package cannot be migrated without guessing or loss."""


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def require_uuid4(value: Any, path: str) -> str:
    if not isinstance(value, str) or UUID4.fullmatch(value) is None:
        raise MigrationRejected(f"{path}: identifier is not an existing canonical UUIDv4; no replacement is generated")
    return value


def validate_schema(package: dict[str, Any], schema_path: Path, label: str) -> None:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(package),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        details = "; ".join(
            f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
            for error in errors[:8]
        )
        raise MigrationRejected(f"{label} schema validation failed: {details}")


def migrate_package(
    source: dict[str, Any],
    mappings: dict[str, Any],
    *,
    migration_id: str,
    executed_at: str,
    source_snapshot_ref: str,
    target_snapshot_ref: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if source.get("contract_version") != "0.2.1":
        raise MigrationRejected("only contract_version 0.2.1 is supported; 0.2.0 must use its own reviewed migration path")
    validate_schema(source, SOURCE_SCHEMA, "source 0.2.1")

    roles = load_json(ROLE_CATALOG)
    reasons = load_json(REASON_CATALOG)
    role_codes = {item["code"] for item in roles["roles"]}
    reason_actions = {item["code"]: set(item["allowed_actions"]) for item in reasons["reasons"]}

    role_map = mappings.get("actor_roles", {})
    reason_map = mappings.get("reasons", {})
    if not isinstance(role_map, dict) or not isinstance(reason_map, dict):
        raise MigrationRejected("mapping file must contain actor_roles and reasons objects")
    if not all(isinstance(key, str) and isinstance(value, str) for key, value in role_map.items()):
        raise MigrationRejected("actor_roles mapping must contain only string-to-string entries")
    if not all(isinstance(key, str) and isinstance(value, str) for key, value in reason_map.items()):
        raise MigrationRejected("reasons mapping must contain only string-to-string entries")

    output = copy.deepcopy(source)
    losses: list[str] = []
    # Preserve subject identity only when every historical subject_ref already is
    # a canonical UUIDv4. Never mint replacement IDs or infer a correspondence.
    subject_values = []
    for collection_name in ("retention_records", "audit_events", "retention_copy_records"):
        for record_index, record in enumerate(output.get(collection_name, [])):
            subject_values.append((f"{collection_name}[{record_index}].subject_ref", record["subject_ref"]))
    subject_tokens = set()
    for field_path, value in subject_values:
        subject_tokens.add(require_uuid4(value, field_path))
    output["audit_subject_tokens"] = sorted(subject_tokens)

    for index, record in enumerate(output.get("retention_records", [])):
        subject = record["subject_ref"]
        require_uuid4(record["retention_id"], f"retention_records[{index}].retention_id")
        require_uuid4(subject, f"retention_records[{index}].subject_ref")
        record["subject_ref"] = subject
        if record.get("authorization_reference") is not None:
            require_uuid4(record["authorization_reference"], f"retention_records[{index}].authorization_reference")
        for ref_index, ref in enumerate(record.get("copy_scope_ids", [])):
            require_uuid4(ref, f"retention_records[{index}].copy_scope_ids[{ref_index}]")

    audit_ids: set[str] = set()
    for index, event in enumerate(output.get("audit_events", [])):
        require_uuid4(event["audit_event_id"], f"audit_events[{index}].audit_event_id")
        require_uuid4(event["subject_ref"], f"audit_events[{index}].subject_ref")
        audit_ids.add(event["audit_event_id"])
        old_role = event["actor_role"]
        role_code = role_map.get(old_role)
        if role_code not in role_codes:
            raise MigrationRejected(
                f"audit_events[{index}].actor_role: no explicit mapping to a current controlled role code"
            )
        old_reason = event["reason"]
        reason_code = reason_map.get(old_reason)
        if reason_code not in reason_actions:
            raise MigrationRejected(
                f"audit_events[{index}].reason: no explicit mapping to a current controlled reason code"
            )
        if event["action"] not in reason_actions[reason_code]:
            raise MigrationRejected(
                f"audit_events[{index}].reason: mapped reason code is not permitted for the event action"
            )
        event["actor_role_code"] = role_code
        event["reason_code"] = reason_code
        event["actor_role_catalog_version"] = roles["catalog_version"]
        event["reason_catalog_version"] = reasons["catalog_version"]
        del event["actor_role"]
        del event["reason"]
        if event.get("retention_id") is not None:
            require_uuid4(event["retention_id"], f"audit_events[{index}].retention_id")
        if event.get("copy_id") is not None:
            require_uuid4(event["copy_id"], f"audit_events[{index}].copy_id")

    copy_ids: set[str] = set()
    for index, record in enumerate(output.get("retention_copy_records", [])):
        for field in ("copy_id", "retention_id", "subject_ref", "transition_event_ref"):
            require_uuid4(record[field], f"retention_copy_records[{index}].{field}")
        if record["transition_event_ref"] not in audit_ids:
            raise MigrationRejected(f"retention_copy_records[{index}].transition_event_ref is unresolved")
        for field in ("parent_copy_id", "backup_expiration_policy_ref", "verification_reference"):
            if record.get(field) is not None:
                require_uuid4(record[field], f"retention_copy_records[{index}].{field}")
        copy_ids.add(record["copy_id"])
    for index, record in enumerate(output.get("retention_copy_records", [])):
        if record.get("parent_copy_id") is not None and record["parent_copy_id"] not in copy_ids:
            raise MigrationRejected(f"retention_copy_records[{index}].parent_copy_id is unresolved")

    output["contract_version"] = "0.2.2"
    core_digest = sha256(canonical_bytes(output))
    migration_record = {
        "migration_id": migration_id,
        "source_contract_version": "0.2.1",
        "target_contract_version": "0.2.2",
        "migrator_version": MIGRATOR_VERSION,
        "executed_at": executed_at,
        "input_sha256": sha256(canonical_bytes(source)),
        "output_sha256": core_digest,
        "rules_applied": [
            "PRESERVE_EXISTING_UUIDV4_IDENTIFIERS",
            "EXPLICIT_ACTOR_ROLE_MAPPING",
            "EXPLICIT_REASON_MAPPING",
            "REJECT_UNMAPPABLE_SUBJECT_REFERENCES",
            "NO_SYNTHETIC_IDENTIFIER_GENERATION",
        ],
        "result": "PASS",
        "loss_report": [],
        "source_snapshot_ref": source_snapshot_ref,
        "target_snapshot_ref": target_snapshot_ref or f"sha256:{core_digest}",
    }
    output.setdefault("migration_records", []).append(migration_record)

    validate_schema(output, TARGET_SCHEMA, "target 0.2.2")
    from validate_source_evidence_contract_0_2_2 import validate_package
    validate_package(output, load_json(TARGET_SCHEMA), roles, reasons)

    manifest = {
        "status": "PASS",
        "source_contract_version": "0.2.1",
        "target_contract_version": "0.2.2",
        "migrator_version": MIGRATOR_VERSION,
        "input_sha256": migration_record["input_sha256"],
        "output_payload_sha256": core_digest,
        "output_file_sha256": sha256(canonical_bytes(output)),
        "mapping_sha256": sha256(canonical_bytes(mappings)),
        "loss_report": losses,
        "determinism_scope": "same source bytes, mapping file, migrator version and explicit migration metadata",
        "output_sha256_scope": "canonical target package before appending this migration record, avoiding a self-referential digest",
    }
    return output, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--mapping", required=True, type=Path, help="Explicit JSON mappings; never inferred.")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--migration-id", required=True)
    parser.add_argument("--executed-at", required=True, help="Explicit UTC timestamp for deterministic replay.")
    parser.add_argument("--source-snapshot-ref", required=True)
    parser.add_argument("--target-snapshot-ref", default="")
    args = parser.parse_args()
    resolved_paths = {
        "input": args.input.resolve(),
        "mapping": args.mapping.resolve(),
        "output": args.output.resolve(),
        "manifest": args.manifest.resolve(),
    }
    if len(set(resolved_paths.values())) != len(resolved_paths):
        parser.error("input, mapping, output and manifest must be four distinct paths")
    if args.output.exists():
        parser.error("output already exists; choose a new target path so a previous result cannot be mistaken for this run")
    try:
        source = load_json(args.input)
        mappings = load_json(args.mapping)
        output, manifest = migrate_package(
            source, mappings, migration_id=args.migration_id, executed_at=args.executed_at,
            source_snapshot_ref=args.source_snapshot_ref, target_snapshot_ref=args.target_snapshot_ref,
        )
    except (OSError, json.JSONDecodeError, KeyError, MigrationRejected, ValueError) as exc:
        report = {
            "status": "REJECTED",
            "source_file": args.input.name,
            "migrator_version": MIGRATOR_VERSION,
            "loss_report": [str(exc)],
            "source_modified": False,
            "target_written": False,
        }
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    output_bytes = canonical_bytes(output)
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    args.output.write_bytes(output_bytes)
    args.manifest.write_bytes(manifest_bytes)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
