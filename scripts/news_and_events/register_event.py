"""Command-line entry point for explicit SINAYXA event registry operations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.news_and_events.event_registry import (
    add_source_reference,
    append_temporal_assertion,
    connect,
    create_event,
    get_event_as_of,
    get_event_history,
    initialize_database,
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
