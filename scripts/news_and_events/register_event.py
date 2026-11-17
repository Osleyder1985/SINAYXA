"""Command-line entry point for explicit SINAYXA event registry operations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.news_and_events.event_registry import (
    add_source_reference,
    append_conflict_decision,
    append_temporal_assertion,
    connect,
    create_reproducibility_manifest,
    create_temporal_assessment,
    create_event,
    create_temporal_conflict,
    get_conflict_history,
    get_evidence_artifact,
    get_reproducibility_manifest,
    get_source_artifact,
    get_temporal_assessment,
    get_event_as_of,
    get_event_history,
    initialize_database,
    register_evidence_artifact,
    register_source_artifact,
)


def read_json(path: str) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("input JSON root must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="SINAYXA explicit event registry")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="apply the local PostgreSQL registry migration")

    create = commands.add_parser("create-event", help="register an event from a JSON object")
    create.add_argument("--input", required=True, help="path to event JSON")

    source = commands.add_parser("add-source", help="append a source reference to an event")
    source.add_argument("--event-id", required=True)
    source.add_argument("--source-ref", required=True)

    assertion = commands.add_parser("append-assertion", help="append a temporal assertion version")
    assertion.add_argument("--input", required=True, help="path to temporal assertion JSON")

    as_of = commands.add_parser("show-as-of", help="show information known at a UTC cutoff")
    as_of.add_argument("--event-id", required=True)
    as_of.add_argument("--cutoff-utc", required=True)

    history = commands.add_parser("history", help="show all temporal assertion versions")
    history.add_argument("--event-id", required=True)

    conflict = commands.add_parser("create-conflict", help="register a conflict between temporal assertions")
    conflict.add_argument("--input", required=True, help="path to conflict JSON")

    decision = commands.add_parser("append-decision", help="append a decision to a temporal conflict")
    decision.add_argument("--input", required=True, help="path to conflict decision JSON")

    conflict_history = commands.add_parser("conflict-history", help="show a conflict and its decisions")
    conflict_history.add_argument("--conflict-id", required=True)
    conflict_history.add_argument("--cutoff-utc", help="optional registry-knowledge cutoff in UTC")

    assessment = commands.add_parser("create-assessment", help="derive and append a temporal assessment")
    assessment.add_argument("--input", required=True, help="path to assessment request JSON")

    show_assessment = commands.add_parser("show-assessment", help="retrieve a temporal assessment")
    show_assessment.add_argument("--assessment-id", required=True)

    manifest = commands.add_parser("create-manifest", help="create an RFC 8785 reproducibility manifest")
    manifest.add_argument("--input", required=True, help="path to manifest request JSON")

    show_manifest = commands.add_parser("show-manifest", help="retrieve a reproducibility manifest")
    show_manifest.add_argument("--manifest-id", required=True)

    source_artifact = commands.add_parser("register-source-artifact", help="store exact source bytes and provenance")
    source_artifact.add_argument("--input", required=True, help="path to source metadata JSON")
    source_artifact.add_argument("--file", required=True, help="path to exact source bytes")

    evidence_artifact = commands.add_parser("register-evidence-artifact", help="store exact evidence bytes and extraction provenance")
    evidence_artifact.add_argument("--input", required=True, help="path to evidence metadata JSON")
    evidence_artifact.add_argument("--file", required=True, help="path to exact evidence bytes")

    export_source = commands.add_parser("export-source-artifact", help="export and hash-verify exact source bytes")
    export_source.add_argument("--source-ref", required=True)
    export_source.add_argument("--output", required=True)

    export_evidence = commands.add_parser("export-evidence-artifact", help="export and hash-verify exact evidence bytes")
    export_evidence.add_argument("--evidence-ref", required=True)
    export_evidence.add_argument("--output", required=True)

    args = parser.parse_args()
    with connect() as connection:
        if args.command == "init":
            initialize_database(connection)
            print("Event registry migration applied.")
        elif args.command == "create-event":
            create_event(connection, read_json(args.input))
            print("Event registered.")
        elif args.command == "add-source":
            add_source_reference(connection, args.event_id, args.source_ref)
            print("Source reference appended.")
        elif args.command == "append-assertion":
            append_temporal_assertion(connection, read_json(args.input))
            print("Temporal assertion version appended.")
        elif args.command == "show-as-of":
            result = get_event_as_of(connection, args.event_id, args.cutoff_utc)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "history":
            print(json.dumps(get_event_history(connection, args.event_id), ensure_ascii=False, indent=2))
        elif args.command == "create-conflict":
            result = create_temporal_conflict(connection, read_json(args.input))
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "append-decision":
            append_conflict_decision(connection, read_json(args.input))
            print("Conflict decision appended.")
        elif args.command == "conflict-history":
            result = get_conflict_history(connection, args.conflict_id, args.cutoff_utc)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "create-assessment":
            result = create_temporal_assessment(connection, read_json(args.input))
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "show-assessment":
            result = get_temporal_assessment(connection, args.assessment_id)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "create-manifest":
            result = create_reproducibility_manifest(connection, read_json(args.input))
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "show-manifest":
            result = get_reproducibility_manifest(connection, args.manifest_id)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "register-source-artifact":
            result = register_source_artifact(connection, read_json(args.input)["source_ref"], Path(args.file).read_bytes(), read_json(args.input))
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "register-evidence-artifact":
            result = register_evidence_artifact(connection, read_json(args.input)["evidence_ref"], Path(args.file).read_bytes(), read_json(args.input))
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "export-source-artifact":
            result = get_source_artifact(connection, args.source_ref)
            if result is None:
                raise ValueError(f"unknown source_ref: {args.source_ref}")
            Path(args.output).write_bytes(result.pop("content_bytes"))
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "export-evidence-artifact":
            result = get_evidence_artifact(connection, args.evidence_ref)
            if result is None:
                raise ValueError(f"unknown evidence_ref: {args.evidence_ref}")
            Path(args.output).write_bytes(result.pop("content_bytes"))
            print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
