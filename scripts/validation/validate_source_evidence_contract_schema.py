#!/usr/bin/env python3
"""Validate the SINAYXA Issue #78 JSON Schema and #15/#16 vocabulary compatibility."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "source-evidence-contract-0.2.0.schema.json"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "contracts" / "source-evidence-contract-v0.2.0.json"
EVIDENCE_FIXTURE_PATH = ROOT / "tests" / "fixtures" / "methodology" / "evidence-standard" / "e01-e18-synthetic-conformance-v1.2.2.json"
SOURCE_FIXTURE_PATH = ROOT / "tests" / "fixtures" / "methodology" / "source-independence" / "s01-s16-synthetic-conformance-v1.0.0.json"


def require_equal(label: str, actual: list[str], expected: list[str]) -> None:
    if actual != expected:
        raise ValueError(f"{label} differs from approved fixture vocabulary. actual={actual!r}; expected={expected!r}")


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE_FIXTURE_PATH.read_text(encoding="utf-8"))
    source = json.loads(SOURCE_FIXTURE_PATH.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(fixture), key=lambda error: list(map(str, error.absolute_path)))
    if errors:
        for error in errors:
            location = "$" + "".join(f"[{part!r}]" for part in error.absolute_path)
            print(f"FAIL {location}: {error.message}", file=sys.stderr)
        return 1

    definitions = schema["$defs"]
    require_equal(
        "Issue #15 evidentiary states",
        definitions["claimAssessment"]["properties"]["evidentiary_status"]["enum"],
        evidence["permitted_evidentiary_states"],
    )
    allowed = source["allowed"]
    enum_paths = {
        "source_type": definitions["evaluationUnit"]["properties"]["source_type"]["enum"],
        "knowledge_basis": definitions["evaluationUnit"]["properties"]["knowledge_basis"]["enum"],
        "identity": definitions["identityAssessment"]["properties"]["identity"]["enum"],
        "independence": definitions["independenceAssessment"]["properties"]["status"]["enum"],
        "dissemination": definitions["evaluationUnit"]["properties"]["dissemination"]["enum"],
        "institutional_character": definitions["evaluationUnit"]["properties"]["institutional_character"]["enum"],
        "source_subtype": definitions["evaluationUnit"]["properties"]["source_subtype"]["enum"],
        "factor_status": definitions["factorAssessment"]["properties"]["status"]["enum"],
    }
    for name, actual in enum_paths.items():
        require_equal(f"Issue #16 {name}", actual, allowed[name])
    require_equal(
        "Issue #16 factor dimensions",
        definitions["factorAssessment"]["properties"]["dimension"]["enum"],
        [dimension["id"] for dimension in source["factor_dimensions"]],
    )

    nature_values = definitions["evidence"]["properties"]["information_nature"]["enum"]
    for case in evidence["cases"]:
        if case["nature"] not in nature_values:
            raise ValueError(f"Issue #15 case {case['id']} uses unsupported information nature {case['nature']!r}.")
        if case["expected"]["evidentiary_status"] not in definitions["claimAssessment"]["properties"]["evidentiary_status"]["enum"]:
            raise ValueError(f"Issue #15 case {case['id']} uses an unsupported evidentiary state.")

    if len(evidence["cases"]) != 18 or len(source["cases"]) != 16:
        raise ValueError("Expected complete E01-E18 and S01-S16 compatibility fixtures.")

    print("JSON Schema Draft 2020-12: valid")
    print("Synthetic v0.2.0 package: valid")
    print("Issue #15 compatibility: E01-E18 and exact evidentiary-state vocabulary")
    print("Issue #16 compatibility: S01-S16 and exact source/factor/independence catalogues")
    print("Scope: structural and vocabulary compatibility only; no empirical truth or production authorization")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
