"""Atomic PostgreSQL persistence for Source & Evidence contract 0.2.1."""
from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Any
from .contract_package_validator import validate_contract_package

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "source-evidence-contract-0.2.1.schema.json"

# (package collection, SQL table, ordered SQL columns, JSONB columns)
MAPPINGS = (
("claims","claims","claim_id claim_version_id package_id claim_version proposition scope valid_time_start valid_time_end recorded_at supersedes_claim_version_id",""),
("claim_components","claim_components","claim_component_id claim_component_version_id package_id claim_id claim_version_id component_key proposition_fragment scope version recorded_at supersedes_component_version_id",""),
("sources","contract_sources","source_id package_id event_id registry_source_ref created_at recorded_at",""),
("source_versions","source_versions","source_version_id package_id source_id version_label version_sequence published_at first_detected_at first_publicly_observed_at original_timestamps retrieved_at canonical_reference content_reference content_hash hash_algorithm supersedes_source_version_id recorded_at artifact_source_ref","original_timestamps"),
("identity_assessments","identity_assessments","identity_assessment_id package_id source_id assessment_cutoff identity anonymous_to_public anonymous_to_publisher anonymous_to_sinayxa identity_verified_by_publisher identity_verified_by_sinayxa verification_evidence_refs limitations recorded_at",""),
("evaluation_units","evaluation_units","assessment_unit_id package_id claim_id claim_component_id source_id source_version_id access_path access_status assessment_cutoff methodology_version source_type source_subtype knowledge_basis institutional_character dissemination claim_version_id claim_component_version_id",""),
("evidence_items","contract_evidence_items","evidence_id package_id source_version_id evidence_kind information_nature factor_dimensions content_reference integrity_check authenticity_status access_status recorded_at artifact_evidence_ref","factor_dimensions integrity_check"),
("provenance_nodes","provenance_nodes","node_id package_id node_type entity_ref",""),
("provenance_edges","provenance_edges","edge_id package_id dependent_node_id origin_node_id relation_type claim_component_id evidence_refs recorded_at valid_from valid_to claim_component_version_id",""),
("factor_assessments","factor_assessments","factor_assessment_id package_id assessment_unit_id dimension status justification supporting_evidence_refs contrary_evidence_refs limitations assessed_at methodology_version human_review_status reviewed_at",""),
("independence_assessments","independence_assessments","independence_assessment_id package_id claim_id claim_component_id assessment_unit_ids status supporting_evidence_refs dependency_edge_refs rationale limitations assessment_cutoff methodology_version human_review_status reviewed_at claim_version_id claim_component_version_id independent_path_edge_refs unresolved_provenance_edge_refs",""),
("claim_assessments","claim_assessments","claim_assessment_id package_id claim_id claim_component_id evidentiary_status attribution_status supporting_evidence_refs contrary_evidence_refs independence_assessment_refs alternatives uncertainty limitations assessment_cutoff methodology_version human_review_status supersedes_assessment_id claim_version_id claim_component_version_id reviewed_at rationale supported_scope unsupported_scope corroboration_basis assessed_at",""),
("retention_records","retention_records","retention_id package_id subject_ref content_retained legal_basis_status purpose responsible_role review_at expires_at disposition previous_disposition authorization_reference recorded_at copy_scope_ids",""),
("audit_events","audit_events","audit_event_id package_id subject_ref action actor_role occurred_at reason retention_id from_disposition to_disposition copy_id from_copy_state to_copy_state",""),
("archive_attestations","archive_attestations","archive_attestation_id package_id evidence_id source_version_id captured_content_hash hash_algorithm archive_service capture_record_reference captured_at imported_at recorded_at integrity_result capture_record_verified content_authenticity content_truth verification_method verified_at verified_by_role",""),
("evidence_availability","evidence_availability","availability_id package_id evidence_id assessment_unit_id claim_id claim_component_id claim_version_id claim_component_version_id available_at availability_basis availability_reference recorded_at archive_attestation_id",""),
("claim_evidence_links","claim_evidence_links","link_id package_id claim_id claim_component_id evidence_id evidence_role scope_note limitations claim_version_id claim_component_version_id",""),
("retention_copy_records","retention_copy_records","copy_id package_id retention_id subject_ref copy_kind parent_copy_id state recorded_at verified_at verification_reference scheduled_disposition_at backup_expiration_policy_ref previous_state transition_event_ref",""),
("migration_records","contract_migration_records","migration_id package_id source_contract_version target_contract_version migrator_version executed_at input_sha256 output_sha256 rules_applied result loss_report source_snapshot_ref target_snapshot_ref",""),
("analysis_processes","analysis_processes","process_id package_id dataset_origin_id claim_component_version_id method_reference output_evidence_ref available_at assessment_cutoff recorded_at",""),
)

def _parent_first(rows: list[dict[str, Any]], parent_key: str, id_key: str) -> list[dict[str, Any]]:
    pending = list(rows)
    known = {r[id_key] for r in pending}
    emitted: set[str] = set()
    result: list[dict[str, Any]] = []
    while pending:
        ready = [r for r in pending if r.get(parent_key) is None or r.get(parent_key) not in known or r.get(parent_key) in emitted]
        if not ready:
            raise ValueError(f"cyclic or unresolved {parent_key} chain")
        for row in ready:
            result.append(row)
            emitted.add(row[id_key])
            pending.remove(row)
    return result

def _insert(cursor: Any, table: str, columns: list[str], rows: list[dict[str, Any]], package_id: str, json_columns: set[str]) -> int:
    from psycopg.types.json import Jsonb
    names = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    query = f"INSERT INTO sinayxa.{table} ({names}) VALUES ({placeholders})"
    for row in rows:
        values = []
        for name in columns:
            value = row.get(name)
            if name == "package_id":
                value = package_id
            if name in json_columns:
                value = Jsonb(value)
            values.append(value)
        cursor.execute(query, values)
    return len(rows)

def persist_contract_package(
    connection: Any,
    package: dict[str, Any],
    *,
    event_id: str,
    registry_source_refs: dict[str, str] | None = None,
    artifact_source_refs: dict[str, str] | None = None,
    artifact_evidence_refs: dict[str, str] | None = None,
    schema_path: Path | str = SCHEMA,
) -> dict[str, Any]:
    """Validate and atomically append one package; never copies artifact bytes."""
    validate_contract_package(package, schema_path)
    if not isinstance(event_id, str) or not event_id.strip():
        raise ValueError("event_id is required")
    package_id = package["package_id"]
    registry_source_refs = registry_source_refs or {}
    artifact_source_refs = artifact_source_refs or {}
    artifact_evidence_refs = artifact_evidence_refs or {}
    digest = hashlib.sha256(Path(schema_path).read_bytes()).hexdigest()
    counts: dict[str, int] = {}

    with connection.transaction():
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO sinayxa.contract_packages "
                "(package_id,event_id,contract_version,created_at,schema_sha256) "
                "VALUES (%s,%s,%s,%s,%s)",
                (package_id,event_id,package["contract_version"],package["created_at"],digest),
            )
            for collection, table, column_text, json_text in MAPPINGS:
                rows = [dict(r) for r in package[collection]]
                if collection == "claims":
                    rows = _parent_first(rows,"supersedes_claim_version_id","claim_version_id")
                elif collection == "claim_components":
                    rows = _parent_first(rows,"supersedes_component_version_id","claim_component_version_id")
                elif collection == "source_versions":
                    rows = _parent_first(rows,"supersedes_source_version_id","source_version_id")
                elif collection == "claim_assessments":
                    rows = _parent_first(rows,"supersedes_assessment_id","claim_assessment_id")
                elif collection == "retention_copy_records":
                    rows = _parent_first(rows,"parent_copy_id","copy_id")
                for row in rows:
                    if collection == "sources":
                        row.update(package_id=package_id,event_id=event_id,
                                   registry_source_ref=registry_source_refs.get(row["source_id"]))
                    elif collection == "source_versions":
                        row["artifact_source_ref"] = artifact_source_refs.get(row["source_version_id"])
                    elif collection == "evidence_items":
                        row["artifact_evidence_ref"] = artifact_evidence_refs.get(row["evidence_id"])
                columns = column_text.split()
                counts[collection] = _insert(cursor,table,columns,rows,package_id,set(json_text.split()))
    return {
        "package_id":package_id,
        "event_id":event_id,
        "contract_version":package["contract_version"],
        "schema_sha256":digest,
        "inserted_counts":counts,
        "total_entities":sum(counts.values()),
    }

def _contract_value(value: Any) -> Any:
    from datetime import date, datetime

    if isinstance(value, datetime):
        rendered = value.isoformat()
        if value.utcoffset() is not None and value.utcoffset().total_seconds() == 0:
            return rendered.removesuffix("+00:00") + "Z"
        return rendered
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, list):
        return [_contract_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _contract_value(item) for key, item in value.items()}
    return value


def load_contract_package(connection: Any, package_id: str) -> dict[str, Any]:
    """Reconstruct and validate a persisted 0.2.1 package by its package ID.

    Registry-only columns (event binding, artifact references and inserted_at)
    are deliberately excluded from the contract representation.
    """
    result: dict[str, Any] = {}
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT package_id, contract_version, created_at
            FROM sinayxa.contract_packages
            WHERE package_id = %s
            """,
            (package_id,),
        )
        root = cursor.fetchone()
        if root is None:
            raise KeyError(f"contract package not found: {package_id}")
        result.update(
            package_id=root[0],
            contract_version=root[1],
            created_at=_contract_value(root[2]),
        )

        for collection, table, column_text, _json_text in MAPPINGS:
            columns = column_text.split()
            excluded = {"package_id", "event_id", "registry_source_ref",
                        "artifact_source_ref", "artifact_evidence_ref"}
            selected = [column for column in columns if column not in excluded]
            query_columns = ", ".join(selected)
            cursor.execute(
                f"SELECT {query_columns} FROM sinayxa.{table} "
                f"WHERE package_id = %s ORDER BY inserted_at",
                (package_id,),
            )
            names = [description.name for description in cursor.description]
            omit_null = {
                ("audit_events", "retention_id"),
                ("independence_assessments", "unresolved_provenance_edge_refs"),
            }
            result[collection] = []
            for row in cursor.fetchall():
                item = {}
                for name, value in zip(names, row, strict=True):
                    if value is None and (collection, name) in omit_null:
                        continue
                    item[name] = _contract_value(value)
                result[collection].append(item)

    return validate_contract_package(result)


def load_claim_assessments_as_of(
    connection: Any,
    package_id: str,
    as_of: Any,
) -> dict[str, Any]:
    """Return assessments demonstrably recorded and evidence-available by an aware cutoff.

    The database insertion timestamp is the system-recorded time; contract
    assessment_cutoff/assessed_at are separate analytical times. Evidence is
    included only when its availability record and any referenced archive
    verification were also recorded and effective by the requested cutoff.
    """
    from datetime import datetime, timezone

    if isinstance(as_of, str):
        try:
            as_of = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("as_of must be an ISO-8601 timestamp with timezone") from exc
    if not isinstance(as_of, datetime) or as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("as_of must be a timezone-aware datetime")
    cutoff = as_of.astimezone(timezone.utc)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM sinayxa.contract_packages WHERE package_id = %s",
            (package_id,),
        )
        if cursor.fetchone() is None:
            raise KeyError(f"contract package not found: {package_id}")

        assessment_columns = [
            column for column in dict((table, columns) for collection, table, columns, _ in MAPPINGS)
            .get("claim_assessments", "").split()
            if column not in {"package_id"}
        ]
        cursor.execute(
            f"SELECT {', '.join(assessment_columns)} FROM sinayxa.claim_assessments "
            "WHERE package_id = %s AND assessment_cutoff <= %s "
            "AND assessed_at IS NOT NULL AND assessed_at <= %s "
            "AND inserted_at <= %s "
            "AND (reviewed_at IS NULL OR reviewed_at <= %s) "
            "ORDER BY assessment_cutoff, assessed_at, inserted_at, claim_assessment_id",
            (package_id, cutoff, cutoff, cutoff, cutoff),
        )
        names = [description.name for description in cursor.description]
        candidates = [
            {name: _contract_value(value) for name, value in zip(names, row, strict=True)}
            for row in cursor.fetchall()
        ]

        evidence_refs = sorted({
            ref
            for assessment in candidates
            for ref in (
                assessment.get("supporting_evidence_refs", [])
                + assessment.get("contrary_evidence_refs", [])
            )
        })
        available: set[str] = set()
        if evidence_refs:
            cursor.execute(
                """
                SELECT DISTINCT ea.evidence_id
                FROM sinayxa.evidence_availability AS ea
                LEFT JOIN sinayxa.archive_attestations AS aa
                  ON aa.archive_attestation_id = ea.archive_attestation_id
                WHERE ea.package_id = %s
                  AND ea.evidence_id = ANY(%s)
                  AND ea.available_at <= %s
                  AND ea.recorded_at <= %s
                  AND ea.inserted_at <= %s
                  AND (
                    ea.archive_attestation_id IS NULL
                    OR (
                      aa.verified_at IS NOT NULL
                      AND aa.verified_at <= %s
                      AND aa.recorded_at <= %s
                      AND aa.inserted_at <= %s
                    )
                  )
                """,
                (package_id, evidence_refs, cutoff, cutoff, cutoff, cutoff, cutoff, cutoff),
            )
            available = {row[0] for row in cursor.fetchall()}

    eligible = []
    for assessment in candidates:
        required = set(
            assessment.get("supporting_evidence_refs", [])
            + assessment.get("contrary_evidence_refs", [])
        )
        if required.issubset(available):
            eligible.append(assessment)

    return {
        "package_id": package_id,
        "as_of": _contract_value(cutoff),
        "time_semantics": {
            "assessment_cutoff": "analytical evidence cutoff",
            "assessed_at": "assessment execution time",
            "inserted_at": "database system-recorded time",
            "evidence_available_at": "recorded evidence availability time",
            "archive_verified_at": "archive verification time when an attestation is linked",
        },
        "assessments": eligible,
    }
