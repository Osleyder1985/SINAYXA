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
