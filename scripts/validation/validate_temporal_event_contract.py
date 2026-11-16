#!/usr/bin/env python3
"""Deterministic semantic validation for SINAYXA temporal event contract 1.0.0."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas/temporal-event-contract-1.0.0.schema.json"
FIXTURE_PATH = ROOT / "tests/fixtures/contracts/temporal-event-contract-v1.0.0.json"
TRANSITIONS = {
    "OPEN": {"UNDER_REVIEW"},
    "UNDER_REVIEW": {"RESOLVED", "CLOSED_NO_CONFLICT"},
    "RESOLVED": {"REOPENED"},
    "CLOSED_NO_CONFLICT": {"REOPENED"},
    "REOPENED": {"UNDER_REVIEW"},
}
SHA256 = re.compile(r"^[a-f0-9]{64}$")


class ContractError(ValueError):
    """Raised when a package violates a temporal semantic invariant."""


def parse_utc(value: str, path: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ContractError(f"{path}: timestamp must be explicit UTC with Z suffix")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ContractError(f"{path}: invalid ISO-8601 timestamp") from exc
    return parsed


def require_unique(items: list[dict[str, Any]], key: str, label: str) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for item in items:
        value = item[key]
        if value in index:
            raise ContractError(f"{label}: duplicate {key} {value!r}")
        index[value] = item
    return index


def validate_semantics(package: dict[str, Any]) -> None:
    assertions = package["temporal_assertions"]
    conflicts = package["temporal_conflicts"]
    decisions = package["conflict_decisions"]
    assessments = package["temporal_assessments"]
    manifests = package["reproducibility_manifests"]

    event_index = require_unique(package["events"], "event_id", "events")
    assertion_index = require_unique(assertions, "temporal_assertion_id", "temporal_assertions")
    conflict_index = require_unique(conflicts, "conflict_id", "temporal_conflicts")
    decision_index = require_unique(decisions, "decision_id", "conflict_decisions")
    assessment_index = require_unique(assessments, "assessment_id", "temporal_assessments")
    require_unique(manifests, "manifest_id", "reproducibility_manifests")

    versions: dict[str, list[dict[str, Any]]] = {}
    for item in assertions:
        aid = item["temporal_assertion_id"]
        if item["event_id"] not in event_index:
            raise ContractError(f"{aid}: unknown event reference")
        start = item["interval_start"]
        end = item["interval_end"]
        start_value, end_value = start["value"], end["value"]
        role, precision = item["temporal_role"], item["precision"]
        recorded = parse_utc(item["recorded_at"], f"{aid}.recorded_at")
        if role == "UNKNOWN":
            if precision != "UNKNOWN" or start_value is not None or end_value is not None:
                raise ContractError(f"{aid}: UNKNOWN role requires UNKNOWN precision and null interval bounds")
            if item["normalized_start_utc"] is not None or item["normalized_end_utc"] is not None:
                raise ContractError(f"{aid}: UNKNOWN role cannot contain normalized UTC bounds")
        if precision == "UNKNOWN" and role != "UNKNOWN":
            raise ContractError(f"{aid}: UNKNOWN precision requires UNKNOWN role")
        if precision == "RANGE" and (start_value is None or end_value is None):
            raise ContractError(f"{aid}: RANGE requires both interpretable bounds")
        if start_value is not None:
            start_dt = parse_utc(start_value, f"{aid}.interval_start.value")
        else:
            start_dt = None
        if end_value is not None:
            end_dt = parse_utc(end_value, f"{aid}.interval_end.value")
        else:
            end_dt = None
        if start_dt is not None and end_dt is not None:
            if start_dt > end_dt:
                raise ContractError(f"{aid}: interval is inverted")
            if start_dt == end_dt and not (start["inclusive"] and end["inclusive"]):
                raise ContractError(f"{aid}: equal bounds form an empty interval unless both are inclusive")
        if item["normalized_start_utc"] is not None:
            normalized_start = parse_utc(item["normalized_start_utc"], f"{aid}.normalized_start_utc")
            if start_dt is None or normalized_start != start_dt:
                raise ContractError(f"{aid}: normalized start must equal its deterministically represented UTC bound")
        if item["normalized_end_utc"] is not None:
            normalized_end = parse_utc(item["normalized_end_utc"], f"{aid}.normalized_end_utc")
            if end_dt is None or normalized_end != end_dt:
                raise ContractError(f"{aid}: normalized end must equal its deterministically represented UTC bound")
        event = event_index[item["event_id"]]
        if item["source_ref"] is not None and item["source_ref"] not in event["source_refs"]:
            raise ContractError(f"{aid}: source reference is not registered on its event")
        event_created = parse_utc(event["created_at"], f"{item['event_id']}.created_at")
        if event_created > recorded:
            raise ContractError(f"{aid}: event record was created after the temporal assertion")
        if item["retrieved_at"] is not None:
            retrieved = parse_utc(item["retrieved_at"], f"{aid}.retrieved_at")
            if retrieved > recorded:
                raise ContractError(f"{aid}: retrieval cannot occur after the assertion was recorded")
        if item["first_observed_at"] is not None:
            observed = parse_utc(item["first_observed_at"], f"{aid}.first_observed_at")
            if observed > recorded:
                raise ContractError(f"{aid}: first observation cannot occur after the assertion was recorded")
            if item["retrieved_at"] is not None and observed > retrieved:
                raise ContractError(f"{aid}: first observation cannot occur after retrieval")
        if role == "ACTUAL" and item["evidence_ref"] is None:
            raise ContractError(f"{aid}: ACTUAL requires an explicit evidence reference")
        if role in {"SCHEDULED", "ESTIMATED"} and item["approximation"] is False and precision == "RANGE":
            raise ContractError(f"{aid}: RANGE cannot be marked non-approximate")
        if item["recorded_at"] < "0001-01-01T00:00:00Z":
            raise ContractError(f"{aid}: invalid recorded_at")
        versions.setdefault(item["event_id"], []).append(item)

    for event_id, items in versions.items():
        items.sort(key=lambda item: item["version"])
        seen_ids: set[str] = set()
        previous_version = 0
        for item in items:
            aid = item["temporal_assertion_id"]
            if item["version"] != previous_version + 1:
                raise ContractError(f"{event_id}: assertion versions must be contiguous from 1")
            previous = item["supersedes_assertion_id"]
            if previous_version == 0 and previous is not None:
                raise ContractError(f"{aid}: first assertion version cannot supersede another assertion")
            if previous_version > 0 and previous != items[previous_version - 1]["temporal_assertion_id"]:
                raise ContractError(f"{aid}: each version must supersede the immediately previous version")
            if previous_version > 0:
                previous_recorded = parse_utc(items[previous_version - 1]["recorded_at"], f"{aid}.previous_recorded_at")
                if recorded < previous_recorded:
                    raise ContractError(f"{aid}: assertion version recording time moves backwards")
            seen_ids.add(aid)
            previous_version += 1

    for conflict in conflicts:
        conflict_recorded = parse_utc(conflict["recorded_at"], f"{conflict['conflict_id']}.recorded_at")
        refs = conflict["assertion_refs"]
        if any(ref not in assertion_index for ref in refs):
            raise ContractError(f"{conflict['conflict_id']}: unknown temporal assertion reference")
        if any(assertion_index[ref]["event_id"] != conflict["event_id"] for ref in refs):
            raise ContractError(f"{conflict['conflict_id']}: assertions must belong to the conflict event")
        if len(refs) < 2:
            raise ContractError(f"{conflict['conflict_id']}: at least two assertions are required")
        if any(parse_utc(assertion_index[ref]["recorded_at"], f"{ref}.recorded_at") > conflict_recorded for ref in refs):
            raise ContractError(f"{conflict['conflict_id']}: conflict cannot predate its referenced assertions")

    decisions_by_conflict: dict[str, list[dict[str, Any]]] = {}
    for decision in decisions:
        did = decision["decision_id"]
        cid = decision["conflict_id"]
        if cid not in conflict_index:
            raise ContractError(f"{did}: unknown conflict")
        conflict = conflict_index[cid]
        if set(decision["assertion_refs"]) - set(conflict["assertion_refs"]):
            raise ContractError(f"{did}: decision references assertions outside its conflict")
        if decision["to_status"] not in TRANSITIONS.get(decision["from_status"], set()):
            raise ContractError(f"{did}: illegal conflict transition")
        cutoff = parse_utc(decision["assessment_cutoff"], f"{did}.assessment_cutoff")
        decided = parse_utc(decision["decided_at"], f"{did}.decided_at")
        if decided < cutoff:
            raise ContractError(f"{did}: decision time cannot precede its assessment cutoff")
        if decision["to_status"] == "RESOLVED":
            if not decision["supporting_evidence_refs"] or not decision["rationale"].strip():
                raise ContractError(f"{did}: resolution requires evidence and rationale")
            if not decision["scope"].strip() or not decision["limitations"].strip():
                raise ContractError(f"{did}: resolution requires explicit scope and limitations")
        if decision["to_status"] == "CLOSED_NO_CONFLICT" and not decision["rationale"].strip():
            raise ContractError(f"{did}: no-conflict closure requires rationale")
        if decision["from_status"] in {"RESOLVED", "CLOSED_NO_CONFLICT"} and decision["to_status"] == "REOPENED":
            if decision["supersedes_decision_id"] is None:
                raise ContractError(f"{did}: reopening must reference the decision being superseded")
        if decision["supersedes_decision_id"] is not None:
            previous_decision = decision_index.get(decision["supersedes_decision_id"])
            if previous_decision is None:
                raise ContractError(f"{did}: superseded decision does not exist")
            if previous_decision["conflict_id"] != cid:
                raise ContractError(f"{did}: superseded decision belongs to another conflict")
            if parse_utc(previous_decision["decided_at"], f"{did}.superseded_decision_time") >= decided:
                raise ContractError(f"{did}: superseded decision must precede the new decision")
        decisions_by_conflict.setdefault(cid, []).append(decision)

    for cid, items in decisions_by_conflict.items():
        items.sort(key=lambda item: parse_utc(item["decided_at"], f"{item['decision_id']}.decided_at"))
        decision_times = [parse_utc(item["decided_at"], f"{item['decision_id']}.decided_at") for item in items]
        if len(decision_times) != len(set(decision_times)):
            raise ContractError(f"{cid}: decisions with identical timestamps have ambiguous order")
        if items[0]["from_status"] != "OPEN":
            raise ContractError(f"{cid}: append-only decision history must begin at OPEN")
        expected = "OPEN"
        for item in items:
            if item["from_status"] != expected:
                raise ContractError(f"{item['decision_id']}: decision history has a gap or conflicting state")
            expected = item["to_status"]
        if expected != conflict_index[cid]["status"]:
            raise ContractError(f"{cid}: current conflict status does not match decision history")

    for conflict in conflicts:
        if conflict["status"] != "OPEN" and conflict["conflict_id"] not in decisions_by_conflict:
            raise ContractError(f"{conflict['conflict_id']}: non-initial conflict status requires decision history")

    for assessment in assessments:
        aid = assessment["assessment_id"]
        cutoff = parse_utc(assessment["assessment_cutoff"], f"{aid}.assessment_cutoff")
        if len(assessment["assertion_refs"]) != len(set(assessment["assertion_refs"])):
            raise ContractError(f"{aid}: duplicate assertion reference")
        if len(assessment["conflict_decision_refs"]) != len(set(assessment["conflict_decision_refs"])):
            raise ContractError(f"{aid}: duplicate conflict decision reference")
        for ref in assessment["assertion_refs"]:
            if ref not in assertion_index:
                raise ContractError(f"{aid}: unknown assertion reference {ref}")
            if assertion_index[ref]["event_id"] != assessment["event_id"]:
                raise ContractError(f"{aid}: assertion {ref} belongs to another event")
            recorded = parse_utc(assertion_index[ref]["recorded_at"], f"{ref}.recorded_at")
            if recorded > cutoff:
                raise ContractError(f"{aid}: assertion {ref} was not known at assessment cutoff")
        for ref in assessment["conflict_decision_refs"]:
            if ref not in decision_index:
                raise ContractError(f"{aid}: unknown conflict decision reference {ref}")
            decision = decision_index[ref]
            if conflict_index[decision["conflict_id"]]["event_id"] != assessment["event_id"]:
                raise ContractError(f"{aid}: conflict decision belongs to another event")
            if parse_utc(decision["decided_at"], f"{ref}.decided_at") > cutoff:
                raise ContractError(f"{aid}: conflict decision was made after assessment cutoff")
        if assessment["recorded_at"] < assessment["assessment_cutoff"]:
            raise ContractError(f"{aid}: assessment cannot be recorded before its cutoff")

    for manifest in manifests:
        mid = manifest["manifest_id"]
        if manifest["assessment_id"] not in assessment_index:
            raise ContractError(f"{mid}: unknown assessment")
        assessment = assessment_index[manifest["assessment_id"]]
        if manifest["assessment_cutoff"] != assessment["assessment_cutoff"]:
            raise ContractError(f"{mid}: manifest cutoff differs from its assessment")
        included = manifest["assertion_versions"]
        excluded = manifest["excluded_assertions"]
        included_ids = [item["assertion_id"] for item in included]
        excluded_ids = [item["assertion_id"] for item in excluded]
        if len(included_ids) != len(set(included_ids)) or len(excluded_ids) != len(set(excluded_ids)):
            raise ContractError(f"{mid}: duplicate assertion version in manifest")
        if set(included_ids) & set(excluded_ids):
            raise ContractError(f"{mid}: an assertion cannot be both included and excluded")
        if set(included_ids) != set(assessment["assertion_refs"]):
            raise ContractError(f"{mid}: included assertion versions must match the assessment assertion set")
        for entry in included + excluded:
            assertion = assertion_index.get(entry["assertion_id"])
            if assertion is None or assertion["version"] != entry["version"]:
                raise ContractError(f"{mid}: manifest references an unknown assertion version")
            if assertion["event_id"] != assessment["event_id"]:
                raise ContractError(f"{mid}: manifest assertion belongs to another event")
        if set(manifest["conflict_decision_refs"]) != set(assessment["conflict_decision_refs"]):
            raise ContractError(f"{mid}: manifest conflict decisions differ from its assessment")
        if manifest["rules_version"] != assessment["rules_version"] or manifest["software_version"] != assessment["software_version"]:
            raise ContractError(f"{mid}: manifest rules/software versions differ from its assessment")
        required_evidence = {
            assertion_index[ref]["evidence_ref"]
            for ref in assessment["assertion_refs"]
            if assertion_index[ref]["evidence_ref"] is not None
        }
        if not required_evidence.issubset(set(manifest["evidence_refs"])):
            raise ContractError(f"{mid}: manifest omits evidence referenced by included assertions")
        if manifest["reproducibility_status"] == "REPRODUCIBLE" and manifest["missing_components"]:
            raise ContractError(f"{mid}: REPRODUCIBLE manifest cannot declare missing components")
        if manifest["reproducibility_status"] != "REPRODUCIBLE" and not manifest["missing_components"]:
            raise ContractError(f"{mid}: partial/non-reproducible manifest must enumerate missing components")
        if not SHA256.fullmatch(manifest["schema_sha256"]) or not SHA256.fullmatch(manifest["rules_sha256"]) or not SHA256.fullmatch(manifest["result_sha256"]):
            raise ContractError(f"{mid}: invalid SHA-256 digest")


def load_and_validate() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    package = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(package),
        key=lambda error: list(map(str, error.absolute_path)),
    )
    if errors:
        details = "; ".join(f"{list(error.absolute_path)}: {error.message}" for error in errors)
        raise ContractError(f"JSON Schema validation failed: {details}")
    validate_semantics(package)


def main() -> int:
    try:
        load_and_validate()
    except (ContractError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("JSON Schema Draft 2020-12: PASS")
    print("Temporal contract 1.0.0 synthetic fixture: PASS")
    print("Semantic invariants: PASS")
    print("Scope: synthetic contract conformance only; no real-world event truth, capture or production persistence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
