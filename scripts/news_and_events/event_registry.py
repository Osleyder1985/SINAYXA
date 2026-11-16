"""Explicit, append-only event registry backed by the approved temporal contract."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import psycopg
from jsonschema import Draft202012Validator, FormatChecker
from psycopg.types.json import Jsonb

from scripts.validation.validate_temporal_event_contract import validate_semantics

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "temporal-event-contract-1.0.0.schema.json"
MIGRATION_PATH = ROOT / "database" / "migrations" / "0001_event_registry.sql"
EMPTY_COLLECTIONS = {
    "temporal_conflicts": [],
    "conflict_decisions": [],
    "temporal_assessments": [],
    "reproducibility_manifests": [],
}


class EventRegistryError(ValueError):
    """Raised when a registry operation violates the temporal contract."""


def _utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise EventRegistryError("timestamp must be explicit UTC with a Z suffix")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise EventRegistryError("timestamp is not valid ISO-8601 UTC") from exc
    if parsed.utcoffset() is None:
        raise EventRegistryError("timestamp must include a UTC offset")
    return parsed


def _validate_package(events: list[dict[str, Any]], assertions: list[dict[str, Any]]) -> None:
    package = {
        "contract_version": "1.0.0",
        "events": events,
        "temporal_assertions": assertions,
        **EMPTY_COLLECTIONS,
    }
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(package),
        key=lambda error: list(map(str, error.absolute_path)),
    )
    if errors:
        detail = "; ".join(
            f"{list(error.absolute_path)}: {error.message}" for error in errors
        )
        raise EventRegistryError(f"temporal contract validation failed: {detail}")
    try:
        validate_semantics(package)
    except (KeyError, TypeError, ValueError) as exc:
        raise EventRegistryError(f"temporal semantic validation failed: {exc}") from exc


def connect(database_url: str | None = None) -> psycopg.Connection:
    """Open a PostgreSQL connection; credentials are supplied by the caller."""
    dsn = database_url or os.environ.get("SINAYXA_DATABASE_URL")
    if not dsn:
        raise EventRegistryError("SINAYXA_DATABASE_URL is required")
    return psycopg.connect(dsn)


def initialize_database(connection: psycopg.Connection) -> None:
    """Apply the local registry migration; no remote services are contacted."""
    migration = MIGRATION_PATH.read_text(encoding="utf-8")
    with connection.transaction():
        connection.execute(migration)


def create_event(connection: psycopg.Connection, event: dict[str, Any]) -> None:
    """Insert an immutable event identity and its initially known references."""
    _validate_package([event], [])
    with connection.transaction():
        connection.execute(
            """
            INSERT INTO sinayxa.events
                (event_id, description, affected_asset_refs, source_refs,
                 created_at, contract_version, event_payload)
            VALUES (%s, %s, %s, %s, %s, '1.0.0', %s)
            """,
            (
                event["event_id"],
                event["description"],
                event["affected_asset_refs"],
                event["source_refs"],
                _utc(event["created_at"]),
                Jsonb(event),
            ),
        )
        for source_ref in event["source_refs"]:
            connection.execute(
                "INSERT INTO sinayxa.event_sources (event_id, source_ref) VALUES (%s, %s)",
                (event["event_id"], source_ref),
            )


def add_source_reference(
    connection: psycopg.Connection, event_id: str, source_ref: str
) -> None:
    """Append a source identifier without altering the immutable event record."""
    if not source_ref or not source_ref.strip():
        raise EventRegistryError("source_ref must be non-empty")
    with connection.transaction():
        connection.execute(
            "INSERT INTO sinayxa.event_sources (event_id, source_ref) VALUES (%s, %s)",
            (event_id, source_ref),
        )


def append_temporal_assertion(
    connection: psycopg.Connection, assertion: dict[str, Any]
) -> None:
    """Append the next temporal assertion version; prior versions are never replaced."""
    with connection.transaction():
        event_row = connection.execute(
            "SELECT event_payload FROM sinayxa.events WHERE event_id = %s",
            (assertion["event_id"],),
        ).fetchone()
        if event_row is None:
            raise EventRegistryError(f"unknown event_id: {assertion['event_id']}")

        event = dict(event_row[0])
        source_rows = connection.execute(
            "SELECT source_ref FROM sinayxa.event_sources WHERE event_id = %s ORDER BY source_ref",
            (assertion["event_id"],),
        ).fetchall()
        event["source_refs"] = [row[0] for row in source_rows]

        previous_rows = connection.execute(
            """
            SELECT assertion_payload
            FROM sinayxa.temporal_assertions
            WHERE event_id = %s
            ORDER BY version
            FOR UPDATE
            """,
            (assertion["event_id"],),
        ).fetchall()
        previous = [dict(row[0]) for row in previous_rows]
        _validate_package([event], previous + [assertion])

        connection.execute(
            """
            INSERT INTO sinayxa.temporal_assertions (
                temporal_assertion_id, event_id, version, temporal_role, precision,
                interval_start, interval_end, approximation, original_value,
                original_timezone, original_offset, normalized_start_utc,
                normalized_end_utc, source_ref, evidence_ref, retrieved_at,
                recorded_at, supersedes_assertion_id, published_at,
                first_observed_at, assertion_payload
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            """,
            (
                assertion["temporal_assertion_id"],
                assertion["event_id"],
                assertion["version"],
                assertion["temporal_role"],
                assertion["precision"],
                Jsonb(assertion["interval_start"]),
                Jsonb(assertion["interval_end"]),
                assertion["approximation"],
                assertion["original_value"],
                assertion["original_timezone"],
                assertion["original_offset"],
                _utc(assertion["normalized_start_utc"]) if assertion["normalized_start_utc"] else None,
                _utc(assertion["normalized_end_utc"]) if assertion["normalized_end_utc"] else None,
                assertion["source_ref"],
                assertion["evidence_ref"],
                _utc(assertion["retrieved_at"]) if assertion["retrieved_at"] else None,
                _utc(assertion["recorded_at"]),
                assertion["supersedes_assertion_id"],
                _utc(assertion["published_at"]) if assertion["published_at"] else None,
                _utc(assertion["first_observed_at"]) if assertion["first_observed_at"] else None,
                Jsonb(assertion),
            ),
        )


def get_event_as_of(
    connection: psycopg.Connection, event_id: str, cutoff_utc: str
) -> dict[str, Any] | None:
    """Return only assertion versions recorded no later than the requested cutoff."""
    cutoff = _utc(cutoff_utc)
    row = connection.execute(
        "SELECT event_payload FROM sinayxa.events WHERE event_id = %s",
        (event_id,),
    ).fetchone()
    if row is None:
        return None
    event = dict(row[0])
    sources = connection.execute(
        "SELECT source_ref FROM sinayxa.event_sources WHERE event_id = %s ORDER BY source_ref",
        (event_id,),
    ).fetchall()
    event["source_refs"] = [item[0] for item in sources]
    assertions = connection.execute(
        """
        SELECT assertion_payload
        FROM sinayxa.temporal_assertions
        WHERE event_id = %s AND recorded_at <= %s
        ORDER BY version
        """,
        (event_id, cutoff),
    ).fetchall()
    return {
        "event": event,
        "temporal_assertions": [dict(item[0]) for item in assertions],
        "as_of_utc": cutoff_utc,
    }


def get_event_history(
    connection: psycopg.Connection, event_id: str
) -> list[dict[str, Any]]:
    """Return the complete append-only temporal assertion history for one event."""
    rows = connection.execute(
        """
        SELECT assertion_payload
        FROM sinayxa.temporal_assertions
        WHERE event_id = %s
        ORDER BY version
        """,
        (event_id,),
    ).fetchall()
    return [dict(row[0]) for row in rows]
