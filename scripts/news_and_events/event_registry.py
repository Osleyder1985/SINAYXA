"""Explicit, append-only event registry backed by the approved temporal contract."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import psycopg
import rfc8785
import tzdata
from jsonschema import Draft202012Validator, FormatChecker
from psycopg.types.json import Jsonb

from scripts.validation.validate_temporal_event_contract import derive_temporal_state, validate_semantics

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "temporal-event-contract-1.0.0.schema.json"
RULES_PATH = ROOT / "scripts" / "validation" / "validate_temporal_event_contract.py"
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
    assessments: list[dict[str, Any]] | None = None,
    manifests: list[dict[str, Any]] | None = None,
) -> None:
    package = {
        "contract_version": "1.0.0",
        "events": events,
        "temporal_assertions": assertions,
        "temporal_conflicts": conflicts or [],
        "conflict_decisions": decisions or [],
        "temporal_assessments": assessments or [],
        "reproducibility_manifests": manifests or [],
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
    """Append the next temporal assertion version with a database-assigned knowledge timestamp."""
    with connection.transaction():
        event_row = connection.execute(
            "SELECT event_payload, inserted_at FROM sinayxa.events WHERE event_id = %s FOR UPDATE",
            (assertion["event_id"],),
        ).fetchone()
        if event_row is None:
            raise EventRegistryError(f"unknown event_id: {assertion['event_id']}")

        candidate = dict(assertion)
        recorded_at = connection.execute("SELECT clock_timestamp()").fetchone()[0]
        candidate["recorded_at"] = recorded_at.isoformat(timespec="microseconds").replace("+00:00", "Z")
        if recorded_at < event_row[1]:
            raise EventRegistryError("temporal assertion cannot be recorded before the event entered the registry")

        event = dict(event_row[0])
        source_rows = connection.execute(
            """
            SELECT source_ref, recorded_at
            FROM sinayxa.event_sources
            WHERE event_id = %s
            ORDER BY source_ref
            """,
            (candidate["event_id"],),
        ).fetchall()
        event["source_refs"] = [row[0] for row in source_rows]
        if candidate["source_ref"] is not None:
            source_recorded_at = next(
                (row[1] for row in source_rows if row[0] == candidate["source_ref"]),
                None,
            )
            if source_recorded_at is None:
                raise EventRegistryError("assertion source_ref is not registered on the event")
            if source_recorded_at > recorded_at:
                raise EventRegistryError("assertion cannot reference a source registered after its database recording time")

        previous_rows = connection.execute(
            """
            SELECT assertion_payload
            FROM sinayxa.temporal_assertions
            WHERE event_id = %s
            ORDER BY version
            FOR UPDATE
            """,
            (candidate["event_id"],),
        ).fetchall()
        previous = [dict(row[0]) for row in previous_rows]
        _validate_package([event], previous + [candidate])

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
                candidate["temporal_assertion_id"],
                candidate["event_id"],
                candidate["version"],
                candidate["temporal_role"],
                candidate["precision"],
                Jsonb(candidate["interval_start"]),
                Jsonb(candidate["interval_end"]),
                candidate["approximation"],
                candidate["original_value"],
                candidate["original_timezone"],
                candidate["original_offset"],
                _utc(candidate["normalized_start_utc"]) if candidate["normalized_start_utc"] else None,
                _utc(candidate["normalized_end_utc"]) if candidate["normalized_end_utc"] else None,
                candidate["source_ref"],
                candidate["evidence_ref"],
                _utc(candidate["retrieved_at"]) if candidate["retrieved_at"] else None,
                recorded_at,
                candidate["supersedes_assertion_id"],
                _utc(candidate["published_at"]) if candidate["published_at"] else None,
                _utc(candidate["first_observed_at"]) if candidate["first_observed_at"] else None,
                Jsonb(candidate),
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


def _load_event_assessment_state(
    connection: psycopg.Connection, event_id: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    assessment_rows = connection.execute(
        """
        SELECT assessment_payload
        FROM sinayxa.temporal_assessments
        WHERE event_id = %s
        ORDER BY inserted_at, assessment_id
        """,
        (event_id,),
    ).fetchall()
    manifest_rows = connection.execute(
        """
        SELECT manifests.manifest_payload
        FROM sinayxa.reproducibility_manifests AS manifests
        JOIN sinayxa.temporal_assessments AS assessments
          ON assessments.assessment_id = manifests.assessment_id
        WHERE assessments.event_id = %s
        ORDER BY manifests.inserted_at, manifests.manifest_id
        """,
        (event_id,),
    ).fetchall()
    return (
        [dict(row[0]) for row in assessment_rows],
        [dict(row[0]) for row in manifest_rows],
    )


def create_temporal_assessment(
    connection: psycopg.Connection, request: dict[str, Any]
) -> dict[str, Any]:
    """Derive and append a temporal assessment from explicitly selected known records."""
    event_id = request["event_id"]
    cutoff = _utc(request["assessment_cutoff"])
    assertion_refs = request["assertion_refs"]
    decision_refs = request["conflict_decision_refs"]
    if not assertion_refs:
        raise EventRegistryError("assessment requires at least one assertion reference")
    if len(assertion_refs) != len(set(assertion_refs)):
        raise EventRegistryError("assessment contains duplicate assertion references")
    if len(decision_refs) != len(set(decision_refs)):
        raise EventRegistryError("assessment contains duplicate conflict decision references")

    with connection.transaction():
        event_row = connection.execute(
            """
            SELECT event_payload, inserted_at
            FROM sinayxa.events
            WHERE event_id = %s
            FOR UPDATE
            """,
            (event_id,),
        ).fetchone()
        if event_row is None:
            raise EventRegistryError(f"unknown event_id: {event_id}")
        if event_row[1] > cutoff:
            raise EventRegistryError("event was not present in the registry at the assessment cutoff")

        selected_assertions = connection.execute(
            """
            SELECT assertion_payload, inserted_at
            FROM sinayxa.temporal_assertions
            WHERE event_id = %s AND temporal_assertion_id = ANY(%s)
            ORDER BY version
            """,
            (event_id, assertion_refs),
        ).fetchall()
        if len(selected_assertions) != len(assertion_refs):
            raise EventRegistryError("assessment contains an unknown or cross-event assertion reference")
        if any(row[1] > cutoff for row in selected_assertions):
            raise EventRegistryError("assessment cannot include an assertion inserted after its cutoff")

        selected_decisions: list[dict[str, Any]] = []
        if decision_refs:
            decision_rows = connection.execute(
                """
                SELECT decisions.decision_payload, decisions.inserted_at
                FROM sinayxa.conflict_decisions AS decisions
                JOIN sinayxa.temporal_conflicts AS conflicts
                  ON conflicts.conflict_id = decisions.conflict_id
                WHERE conflicts.event_id = %s AND decisions.decision_id = ANY(%s)
                ORDER BY decisions.decided_at
                """,
                (event_id, decision_refs),
            ).fetchall()
            if len(decision_rows) != len(decision_refs):
                raise EventRegistryError("assessment contains an unknown or cross-event conflict decision reference")
            if any(row[1] > cutoff for row in decision_rows):
                raise EventRegistryError("assessment cannot include a decision inserted after its cutoff")
            selected_decisions = [dict(row[0]) for row in decision_rows]

        event, assertions, conflicts, decisions = _load_event_contract_state(connection, event_id)
        source_rows = connection.execute(
            """
            SELECT source_ref
            FROM sinayxa.event_sources
            WHERE event_id = %s AND inserted_at <= %s
            ORDER BY source_ref
            """,
            (event_id, cutoff),
        ).fetchall()
        event["source_refs"] = [row[0] for row in source_rows]
        _apply_latest_conflict_statuses(conflicts, decisions)
        assessment = dict(request)
        assessment["derived_temporal_state"] = derive_temporal_state(
            [dict(row[0]) for row in selected_assertions], cutoff
        )
        recorded_at = connection.execute("SELECT clock_timestamp()").fetchone()[0]
        assessment["recorded_at"] = recorded_at.isoformat(timespec="microseconds").replace("+00:00", "Z")
        assessments, manifests = _load_event_assessment_state(connection, event_id)
        _validate_package(
            [event],
            assertions,
            conflicts,
            decisions,
            assessments + [assessment],
            manifests,
        )
        connection.execute(
            """
            INSERT INTO sinayxa.temporal_assessments (
                assessment_id, event_id, assessment_cutoff, assertion_refs,
                conflict_decision_refs, derived_temporal_state, rules_version,
                software_version, recorded_at, assessment_payload
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                assessment["assessment_id"],
                event_id,
                cutoff,
                assertion_refs,
                decision_refs,
                assessment["derived_temporal_state"],
                assessment["rules_version"],
                assessment["software_version"],
                recorded_at,
                Jsonb(assessment),
            ),
        )
        return assessment


def get_temporal_assessment(
    connection: psycopg.Connection, assessment_id: str
) -> dict[str, Any] | None:
    """Retrieve one immutable temporal assessment and its actual registry insertion time."""
    with connection.transaction():
        row = connection.execute(
            """
            SELECT assessment_payload, inserted_at
            FROM sinayxa.temporal_assessments
            WHERE assessment_id = %s
            """,
            (assessment_id,),
        ).fetchone()
        if row is None:
            return None
        return {
            "assessment": dict(row[0]),
            "recorded_in_registry_at": row[1].isoformat(timespec="microseconds").replace("+00:00", "Z"),
        }


def create_reproducibility_manifest(
    connection: psycopg.Connection, request: dict[str, Any]
) -> dict[str, Any]:
    """Create an RFC 8785/SHA-256 manifest for an assessment without overstating reproducibility."""
    with connection.transaction():
        assessment_row = connection.execute(
            """
            SELECT assessment_payload, event_id
            FROM sinayxa.temporal_assessments
            WHERE assessment_id = %s
            FOR UPDATE
            """,
            (request["assessment_id"],),
        ).fetchone()
        if assessment_row is None:
            raise EventRegistryError(f"unknown assessment_id: {request['assessment_id']}")
        assessment = dict(assessment_row[0])
        event_id = assessment_row[1]
        event, assertions, conflicts, decisions = _load_event_contract_state(connection, event_id)
        _apply_latest_conflict_statuses(conflicts, decisions)
        assessments, manifests = _load_event_assessment_state(connection, event_id)
        assessment_cutoff = _utc(assessment["assessment_cutoff"])
        source_rows = connection.execute(
            """
            SELECT source_ref
            FROM sinayxa.event_sources
            WHERE event_id = %s AND inserted_at <= %s
            ORDER BY source_ref
            """,
            (event_id, assessment_cutoff),
        ).fetchall()
        event["source_refs"] = [row[0] for row in source_rows]

        assertion_index = {item["temporal_assertion_id"]: item for item in assertions}
        decision_index = {item["decision_id"]: item for item in decisions}
        selected_assertions = []
        for assertion_ref in assessment["assertion_refs"]:
            assertion = assertion_index.get(assertion_ref)
            if assertion is None:
                raise EventRegistryError(f"assessment references unknown assertion: {assertion_ref}")
            selected_assertions.append(assertion)

        excluded_assertions = request.get("excluded_assertions", [])
        if not isinstance(excluded_assertions, list):
            raise EventRegistryError("excluded_assertions must be a JSON array")
        selected_ids = set(assessment["assertion_refs"])
        excluded_payloads: list[dict[str, Any]] = []
        for excluded in excluded_assertions:
            if not isinstance(excluded, dict):
                raise EventRegistryError("each excluded assertion must be an object")
            assertion = assertion_index.get(excluded.get("assertion_id"))
            if assertion is None or assertion["event_id"] != event_id:
                raise EventRegistryError("excluded assertion is unknown or belongs to another event")
            if excluded["assertion_id"] in selected_ids:
                raise EventRegistryError("an assertion cannot be both included and excluded")
            if assertion["version"] != excluded.get("version"):
                raise EventRegistryError("excluded assertion version does not match the registry")
            inserted_row = connection.execute(
                """
                SELECT inserted_at
                FROM sinayxa.temporal_assertions
                WHERE event_id = %s AND temporal_assertion_id = %s
                """,
                (event_id, excluded["assertion_id"]),
            ).fetchone()
            if inserted_row is None or inserted_row[0] > assessment_cutoff:
                raise EventRegistryError("excluded assertion was not in the registry at the assessment cutoff")
            excluded_payloads.append(assertion)

        selected_decisions = []
        for decision_ref in assessment["conflict_decision_refs"]:
            decision = decision_index.get(decision_ref)
            if decision is None:
                raise EventRegistryError(f"assessment references unknown conflict decision: {decision_ref}")
            selected_decisions.append(decision)

        evidence_refs = {
            item["evidence_ref"]
            for item in selected_assertions
            if item["evidence_ref"] is not None
        }
        for decision in selected_decisions:
            evidence_refs.update(decision["supporting_evidence_refs"])
            evidence_refs.update(decision["contrary_evidence_refs"])

        selected_conflict_ids = {item["conflict_id"] for item in selected_decisions}
        selected_conflicts = [
            item for item in conflicts if item["conflict_id"] in selected_conflict_ids
        ]
        result_document = {
            "assessment": assessment,
            "event": event,
            "temporal_assertions": sorted(
                selected_assertions, key=lambda item: item["temporal_assertion_id"]
            ),
            "excluded_assertions": [
                {
                    "assertion": item,
                    "reason": excluded["reason"],
                }
                for item, excluded in sorted(
                    zip(excluded_payloads, excluded_assertions),
                    key=lambda pair: pair[0]["temporal_assertion_id"],
                )
            ],
            "temporal_conflicts": sorted(
                selected_conflicts, key=lambda item: item["conflict_id"]
            ),
            "conflict_decisions": sorted(
                selected_decisions, key=lambda item: item["decision_id"]
            ),
        }
        try:
            result_digest = hashlib.sha256(rfc8785.dumps(result_document)).hexdigest()
        except (TypeError, ValueError) as exc:
            raise EventRegistryError(f"assessment result cannot be canonicalized under RFC 8785: {exc}") from exc

        created_at = connection.execute("SELECT clock_timestamp()").fetchone()[0]
        created_at_text = created_at.isoformat(timespec="microseconds").replace("+00:00", "Z")
        manifest = {
            "manifest_id": request["manifest_id"],
            "assessment_id": assessment["assessment_id"],
            "assessment_cutoff": assessment["assessment_cutoff"],
            "contract_version": "1.0.0",
            "schema_sha256": hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest(),
            "assertion_versions": [
                {
                    "assertion_id": item["temporal_assertion_id"],
                    "version": item["version"],
                }
                for item in sorted(selected_assertions, key=lambda item: item["version"])
            ],
            "excluded_assertions": excluded_assertions,
            "evidence_refs": sorted(evidence_refs),
            "conflict_decision_refs": assessment["conflict_decision_refs"],
            "rules_version": assessment["rules_version"],
            "rules_sha256": hashlib.sha256(RULES_PATH.read_bytes()).hexdigest(),
            "tzdb_version": tzdata.IANA_VERSION,
            "software_version": assessment["software_version"],
            "result_sha256": result_digest,
            "canonicalization": "RFC8785",
            "reproducibility_status": "PARTIALLY_REPRODUCIBLE",
            "missing_components": [
                "source_content_not_persisted",
                "evidence_content_not_persisted",
                "runtime_environment_snapshot_not_embedded",
            ],
            "created_at": created_at_text,
        }
        _validate_package(
            [event],
            assertions,
            conflicts,
            decisions,
            assessments,
            manifests + [manifest],
        )
        connection.execute(
            """
            INSERT INTO sinayxa.reproducibility_manifests (
                manifest_id, assessment_id, assessment_cutoff, contract_version,
                schema_sha256, assertion_versions, excluded_assertions, evidence_refs,
                conflict_decision_refs, rules_version, rules_sha256, tzdb_version,
                software_version, result_sha256, canonicalization,
                reproducibility_status, missing_components, created_at, manifest_payload
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                manifest["manifest_id"],
                manifest["assessment_id"],
                _utc(manifest["assessment_cutoff"]),
                manifest["contract_version"],
                manifest["schema_sha256"],
                Jsonb(manifest["assertion_versions"]),
                Jsonb(manifest["excluded_assertions"]),
                manifest["evidence_refs"],
                manifest["conflict_decision_refs"],
                manifest["rules_version"],
                manifest["rules_sha256"],
                manifest["tzdb_version"],
                manifest["software_version"],
                manifest["result_sha256"],
                manifest["canonicalization"],
                manifest["reproducibility_status"],
                manifest["missing_components"],
                created_at,
                Jsonb(manifest),
            ),
        )
        return manifest


def get_reproducibility_manifest(
    connection: psycopg.Connection, manifest_id: str
) -> dict[str, Any] | None:
    """Retrieve one immutable reproducibility manifest and its registry insertion time."""
    with connection.transaction():
        row = connection.execute(
            """
            SELECT manifest_payload, inserted_at
            FROM sinayxa.reproducibility_manifests
            WHERE manifest_id = %s
            """,
            (manifest_id,),
        ).fetchone()
        if row is None:
            return None
        return {
            "manifest": dict(row[0]),
            "recorded_in_registry_at": row[1].isoformat(timespec="microseconds").replace("+00:00", "Z"),
        }



def get_event_as_of(
    connection: psycopg.Connection, event_id: str, cutoff_utc: str
) -> dict[str, Any] | None:
    """Return only assertion versions recorded no later than the requested cutoff."""
    cutoff = _utc(cutoff_utc)
    with connection.transaction():
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
            WHERE event_id = %s AND inserted_at <= %s
            ORDER BY source_ref
            """,
            (event_id, cutoff),
        ).fetchall()
        event["source_refs"] = [item[0] for item in sources]
        assertions = connection.execute(
            """
            SELECT assertion_payload
            FROM sinayxa.temporal_assertions
            WHERE event_id = %s AND inserted_at <= %s
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
    with connection.transaction():
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
