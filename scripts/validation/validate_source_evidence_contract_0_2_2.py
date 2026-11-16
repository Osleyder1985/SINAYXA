"""Validate contract 0.2.2 schema, controlled catalogs and audit invariants."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "source-evidence-contract-0.2.2.schema.json"
FIXTURE = ROOT / "tests" / "fixtures" / "contracts" / "source-evidence-contract-v0.2.2.json"
ROLE_CATALOG = ROOT / "schemas" / "catalogs" / "audit-actor-roles-1.0.0.json"
REASON_CATALOG = ROOT / "schemas" / "catalogs" / "audit-reason-codes-1.0.0.json"
UUID4 = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


class Contract022Violation(ValueError):
    """Raised when a contract 0.2.2 invariant is violated."""


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Contract022Violation(message)


def validate_catalogs(roles: dict[str, Any], reasons: dict[str, Any]) -> None:
    _require(roles.get("catalog_version") == "1.0.0", "unsupported actor-role catalog version")
    _require(reasons.get("catalog_version") == "1.0.0", "unsupported reason-code catalog version")
    role_codes = [item["code"] for item in roles.get("roles", [])]
    reason_codes = [item["code"] for item in reasons.get("reasons", [])]
    _require(bool(role_codes) and len(role_codes) == len(set(role_codes)), "actor-role codes must be non-empty and unique")
    _require(bool(reason_codes) and len(reason_codes) == len(set(reason_codes)), "reason codes must be non-empty and unique")
    _require(all(re.fullmatch(r"[A-Z][A-Z0-9_]{1,63}", code) for code in role_codes + reason_codes),
             "catalog codes must use stable uppercase identifiers")


def validate_package(package: dict[str, Any], schema: dict[str, Any], roles: dict[str, Any], reasons: dict[str, Any]) -> None:
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(package),
        key=lambda error: list(error.absolute_path),
    )
    _require(not errors, "JSON Schema violation: " + "; ".join(error.message for error in errors[:5]))
    validate_catalogs(roles, reasons)

    role_codes = {item["code"] for item in roles["roles"]}
    reason_by_code = {item["code"]: set(item["allowed_actions"]) for item in reasons["reasons"]}
    subject_tokens = package.get("audit_subject_tokens", [])
    _require(bool(subject_tokens) or not (
        package.get("retention_records") or package.get("audit_events") or package.get("retention_copy_records")
    ), "audit_subject_tokens are required when audit, retention or copy records exist")
    _require(len(subject_tokens) == len(set(subject_tokens)), "audit subject tokens must be unique")
    _require(all(isinstance(token, str) and UUID4.fullmatch(token) for token in subject_tokens),
             "audit subject tokens must be canonical UUIDv4 values")
    subject_token_set = set(subject_tokens)

    retention_by_id = {item["retention_id"]: item for item in package.get("retention_records", [])}
    _require(len(retention_by_id) == len(package.get("retention_records", [])), "duplicate retention_id")
    for record in package.get("retention_records", []):
        _require(record["subject_ref"] in subject_token_set,
                 "retention subject_ref must resolve to a declared opaque audit subject token")

    audit_ids: set[str] = set()
    for event in package.get("audit_events", []):
        event_id = event["audit_event_id"]
        _require(UUID4.fullmatch(event_id) is not None, "audit_event_id must be UUIDv4")
        _require(event_id not in audit_ids, "duplicate audit_event_id")
        audit_ids.add(event_id)
        _require(event["actor_role_code"] in role_codes, "unknown actor_role_code")
        _require(event["reason_code"] in reason_by_code, "unknown reason_code")
        _require(event["action"] in reason_by_code[event["reason_code"]],
                 "reason_code is not permitted for the declared action")
        _require(event["actor_role_catalog_version"] == roles["catalog_version"],
                 "actor-role catalog version mismatch")
        _require(event["reason_catalog_version"] == reasons["catalog_version"],
                 "reason catalog version mismatch")
        _require(event["subject_ref"] in subject_token_set,
                 "audit subject_ref does not resolve to a declared opaque subject token")
        if event.get("retention_id") is not None:
            _require(event["retention_id"] in retention_by_id, "audit retention_id is unresolved")
            _require(retention_by_id[event["retention_id"]]["subject_ref"] == event["subject_ref"],
                     "audit event and retention record subject references differ")

    copy_ids = {item["copy_id"] for item in package.get("retention_copy_records", [])}
    _require(len(copy_ids) == len(package.get("retention_copy_records", [])), "duplicate copy_id")
    for copy in package.get("retention_copy_records", []):
        _require(copy["subject_ref"] in subject_token_set, "copy subject_ref does not resolve to a declared opaque subject token")
        _require(copy["retention_id"] in retention_by_id, "copy retention_id is unresolved")
        _require(retention_by_id[copy["retention_id"]]["subject_ref"] == copy["subject_ref"],
                 "copy and retention subject references differ")
        if copy.get("parent_copy_id") is not None:
            _require(copy["parent_copy_id"] in copy_ids, "parent_copy_id is unresolved")
    for copy in package.get("retention_copy_records", []):
        _require(copy["transition_event_ref"] in audit_ids, "copy transition_event_ref is unresolved")


def main() -> None:
    schema = _load(SCHEMA)
    package = _load(FIXTURE)
    roles = _load(ROLE_CATALOG)
    reasons = _load(REASON_CATALOG)
    validate_package(package, schema, roles, reasons)
    print("Contract 0.2.2: schema, catalogs and audit invariants PASS")


if __name__ == "__main__":
    main()
