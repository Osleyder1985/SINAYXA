#!/usr/bin/env python3
"""Validate the SINAYXA Issue #78 JSON Schema and synthetic v0.2.0 fixture."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "source-evidence-contract-0.2.0.schema.json"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "contracts" / "source-evidence-contract-v0.2.0.json"


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(fixture), key=lambda error: list(map(str, error.absolute_path)))
    if errors:
        for error in errors:
            location = "$" + "".join(f"[{part!r}]" for part in error.absolute_path)
            print(f"FAIL {location}: {error.message}", file=sys.stderr)
        return 1
    print("JSON Schema Draft 2020-12: valid")
    print(f"Fixture contract_version: {fixture['contract_version']}")
    print(f"Fixture claims: {len(fixture['claims'])}")
    print("Scope: synthetic structural conformance only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
