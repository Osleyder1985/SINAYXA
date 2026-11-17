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
MIGRATION_DIR = ROOT / "database" / "migrations"
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


def _validate_package(
    events: list[dict[str, Any]],
    assertions: list[dict[str, Any]],
    conflicts: list[dict[str, Any]] | None = None,
    decisions: list[dict[str, Any]] | None = None,
) -> None:
    package = {
        "contract_version": "1.0.0",
        "events": events,
        "temporal_assertions": assertions,
        "temporal_conflicts": conflicts or [],
        "conflict_decisions": decisions or [],
        **{key: value for key, value in EMPTY_COLLECTIONS.items() if key not in {"temporal_conflicts", "conflict_decisions"}},
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
    for migration_path in sorted(MIGRATION_DIR.glob("*.sql")):
        migration = migration_path.read_text(encoding="utf-8")
        with connection.transaction():
            connection.execute(migration, prepare=False)


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
) -> datetime:
    """Append a source identifier without altering the immutable event record."""
    if not source_ref or not source_ref.strip():
        raise EventRegistryError("source_ref must be non-empty")
    with connection.transaction():
        event_row = connection.execute(
            "SELECT inserted_at FROM sinayxa.events WHERE event_id = %s FOR KEY SHARE",
            (event_id,),
        ).fetchone()
        if event_row is None:
            raise EventRegistryError(f"unknown event_id: {event_id}")
        row = connection.execute(
            """
            INSERT INTO sinayxa.event_sources (event_id, source_ref)
            VALUES (%s, %s)
            RETURNING recorded_at
            """,
            (event_id, source_ref),
        ).fetchone()
        if row[0] < event_row[0]:
            raise EventRegistryError("source reference cannot be recorded before the event entered the registry")
        return row[0]


def append_temporal_assertion(
    connection: psycopg.Connection, assertion: dict[str, Any]
) -> None:
    """Append the next temporal assertion version; prior versions are never replaced."""
    with connection.transaction():
        event_row = connection.execute(
            "SELECT event_payload, inserted_at FROM sinayxa.events WHERE event_id = %s FOR UPDATE",
            (assertion["event_id"],),
        ).fetchone()
        if event_row is None:
            raise EventRegistryError(f"unknown event_id: {assertion['event_id']}")

        event = dict(event_row[0])
        assertion_recorded_at = _utc(assertion["recorded_at"])
        if assertion_recorded_at < event_row[1]:
            raise EventRegistryError("temporal assertion cannot be recorded before the event entered the registry")
        source_rows = connection.execute(
            """
            SELECT source_ref, recorded_at
            FROM sinayxa.event_sources
            WHERE event_id = %s
            ORDER BY source_ref
            """,
            (assertion["event_id"],),
        ).fetchall()
        event["source_refs"] = [row[0] for row in source_rows]
        if assertion["source_ref"] is not None:
            source_recorded_at = next(
                (row[1] for row in source_rows if row[0] == assertion["source_ref"]),
                None,
            )
            if source_recorded_at is None:
                raise EventRegistryError("assertion source_ref is not registered on the event")
            if source_recorded_at > assertion_recorded_at:
                raise EventRegistryError("assertion cannot reference a source registered after its recorded_at")

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


def _load_event_contract_state(
    connection: psycopg.Connection, event_id: str
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    event_row = connection.execute(
        "SELECT event_payload FROM sinayxa.events WHERE event_id = %s",
        (event_id,),
    ).fetchone()
    if event_row is None:
        raise EventRegistryError(f"unknown event_id: {event_id}")
    event = dict(event_row[0])
    source_rows = connection.execute(
        "SELECT source_ref FROM sinayxa.event_sources WHERE event_id = %s ORDER BY source_ref",
        (event_id,),
    ).fetchall()
    event["source_refs"] = [row[0] for row in source_rows]
    assertion_rows = connection.execute(
        "SELECT assertion_payload FROM sinayxa.temporal_assertions WHERE event_id = %s ORDER BY version",
        (event_id,),
    ).fetchall()
    conflict_rows = connection.execute(
        "SELECT conflict_payload FROM sinayxa.temporal_conflicts WHERE event_id = %s ORDER BY conflict_id",
        (event_id,),
    ).fetchall()
    decision_rows = connection.execute(
        """
        SELECT decisions.decision_payload
        FROM sinayxa.conflict_decisions AS decisions
        JOIN sinayxa.temporal_conflicts AS conflicts
          ON conflicts.conflict_id = decisions.conflict_id
        WHERE conflicts.event_id = %s
        ORDER BY decisions.decided_at
        """,
        (event_id,),
    ).fetchall()
    return (
        event,
        [dict(row[0]) for row in assertion_rows],
        [dict(row[0]) for row in conflict_rows],
        [dict(row[0]) for row in decision_rows],
    )


def _apply_latest_conflict_statuses(
    conflicts: list[dict[str, Any]], decisions: list[dict[str, Any]]
) -> None:
    """Project each conflict's current state from its immutable decision history."""
    decisions_by_conflict: dict[str, list[dict[str, Any]]] = {}
    for decision in decisions:
        decisions_by_conflict.setdefault(decision["conflict_id"], []).append(decision)
    for conflict in conflicts:
        history = decisions_by_conflict.get(conflict["conflict_id"], [])
        if history:
            latest = max(history, key=lambda item: _utc(item["decided_at"]))
            conflict["status"] = latest["to_status"]



def create_temporal_conflict(
    connection: psycopg.Connection, conflict: dict[str, Any]
) -> dict[str, Any]:
    """Create an OPEN conflict after verifying its assertions belong to the event."""
    event_id = conflict["event_id"]
    with connection.transaction():
        event_row = connection.execute(
            "SELECT event_id FROM sinayxa.events WHERE event_id = %s FOR UPDATE",
            (event_id,),
        ).fetchone()
        if event_row is None:
            raise EventRegistryError(f"unknown event_id: {event_id}")
        candidate = dict(conflict)
        recorded_at = connection.execute("SELECT clock_timestamp()").fetchone()[0]
        candidate["recorded_at"] = recorded_at.isoformat(timespec="microseconds").replace("+00:00", "Z")
        event, assertions, conflicts, decisions = _load_event_contract_state(connection, event_id)
        _apply_latest_conflict_statuses(conflicts, decisions)
        _validate_package([event], assertions, conflicts + [candidate], decisions)
        connection.execute(
            """
            INSERT INTO sinayxa.temporal_conflicts (
                conflict_id, event_id, assertion_refs, disputed_component,
                classification, status, recorded_at, conflict_payload
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                candidate["conflict_id"],
                event_id,
                candidate["assertion_refs"],
                candidate["disputed_component"],
                candidate["classification"],
                candidate["status"],
                recorded_at,
                Jsonb(candidate),
            ),
        )
        return candidate


def append_conflict_decision(
    connection: psycopg.Connection, decision: dict[str, Any]
) -> None:
    """Append a validated conflict-state transition without rewriting prior decisions."""
    with connection.transaction():
        conflict_ref = connection.execute(
            "SELECT event_id FROM sinayxa.temporal_conflicts WHERE conflict_id = %s",
            (decision["conflict_id"],),
        ).fetchone()
        if conflict_ref is None:
            raise EventRegistryError(f"unknown conflict_id: {decision['conflict_id']}")
        event_id = conflict_ref[0]
        event_row = connection.execute(
            "SELECT event_id FROM sinayxa.events WHERE event_id = %s FOR UPDATE",
            (event_id,),
        ).fetchone()
        if event_row is None:
            raise EventRegistryError(f"unknown event_id: {event_id}")
        conflict_row = connection.execute(
            "SELECT conflict_payload FROM sinayxa.temporal_conflicts WHERE conflict_id = %s FOR UPDATE",
            (decision["conflict_id"],),
        ).fetchone()
        if conflict_row is None:
            raise EventRegistryError(f"unknown conflict_id: {decision['conflict_id']}")
        event, assertions, conflicts, decisions = _load_event_contract_state(connection, event_id)
        _apply_latest_conflict_statuses(conflicts, decisions)
        current_conflict = next(
            item for item in conflicts if item["conflict_id"] == decision["conflict_id"]
        )
        current_conflict["status"] = decision["to_status"]
        _validate_package([event], assertions, conflicts, decisions + [decision])
        connection.execute(
            """
            INSERT INTO sinayxa.conflict_decisions (
                decision_id, conflict_id, from_status, to_status, assertion_refs,
                supporting_evidence_refs, contrary_evidence_refs, scope, rationale,
                limitations, actor_ref, decided_at, assessment_cutoff, rules_version,
                supersedes_decision_id, decision_payload
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                decision["decision_id"],
                decision["conflict_id"],
                decision["from_status"],
                decision["to_status"],
                decision["assertion_refs"],
                decision["supporting_evidence_refs"],
                decision["contrary_evidence_refs"],
                decision["scope"],
                decision["rationale"],
                decision["limitations"],
                decision["actor_ref"],
                _utc(decision["decided_at"]),
                _utc(decision["assessment_cutoff"]),
                decision["rules_version"],
                decision["supersedes_decision_id"],
                Jsonb(decision),
            ),
        )


def get_conflict_history(
    connection: psycopg.Connection, conflict_id: str, cutoff_utc: str | None = None
) -> dict[str, Any] | None:
    """Return the conflict and decisions known by registry insertion time at a cutoff."""
    cutoff = _utc(cutoff_utc) if cutoff_utc is not None else None
    with connection.transaction():
        if cutoff is None:
            row = connection.execute(
                "SELECT conflict_payload, inserted_at FROM sinayxa.temporal_conflicts WHERE conflict_id = %s",
                (conflict_id,),
            ).fetchone()
        else:
            row = connection.execute(
                """
                SELECT conflict_payload, inserted_at
                FROM sinayxa.temporal_conflicts
                WHERE conflict_id = %s AND inserted_at <= %s
                """,
                (conflict_id, cutoff),
            ).fetchone()
        if row is None:
            return None
        conflict = dict(row[0])
        if cutoff is None:
            decisions = connection.execute(
                """
                SELECT decision_payload, inserted_at
                FROM sinayxa.conflict_decisions
                WHERE conflict_id = %s
                ORDER BY decided_at
                """,
                (conflict_id,),
            ).fetchall()
        else:
            decisions = connection.execute(
                """
                SELECT decision_payload, inserted_at
                FROM sinayxa.conflict_decisions
                WHERE conflict_id = %s AND inserted_at <= %s
                ORDER BY decided_at
                """,
                (conflict_id, cutoff),
            ).fetchall()
        decision_history = [
            {
                "decision": dict(item[0]),
                "recorded_in_registry_at": item[1].isoformat(timespec="microseconds").replace("+00:00", "Z"),
            }
            for item in decisions
        ]
        if decision_history:
            conflict["status"] = decision_history[-1]["decision"]["to_status"]
        return {
            "conflict": conflict,
            "decisions": decision_history,
            "as_of_utc": cutoff_utc,
        }


def get_event_as_of(
    connection: psycopg.Connection, event_id: str, cutoff_utc: str
) -> dict[str, Any] | None:
    """Return only assertion versions recorded no later than the requested cutoff."""
    cutoff = _utc(cutoff_utc)
    row = connection.execute(
        """
        SELECT event_payload
        FROM sinayxa.events
        WHERE event_id = %s AND inserted_at <= %s
        """,
        (event_id, cutoff),
    ).fetchone()
    if row is None:
        return None
    event = dict(row[0])
    sources = connection.execute(
        """
        SELECT source_ref
        FROM sinayxa.event_sources
        WHERE event_id = %s AND recorded_at <= %s
        ORDER BY source_ref
        """,
        (event_id, cutoff),
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
