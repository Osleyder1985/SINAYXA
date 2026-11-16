"""Pure, deterministic migration from synthetic contract 0.2.0 to 0.2.1."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from contract_0_2_1_extensions import canonical_migration_payload_sha256


MIGRATOR_VERSION = "0.2.1"
RULES_APPLIED = [
    "MIG-02-CLAIM-ASSESSED-AT-UNKNOWN",
    "MIG-08-CONTRACT-VERSION-ONLY",
    "MIG-NEW-COLLECTIONS-EMPTY",
    "MIG-PRESERVE-HISTORICAL-VALUES",
]


def migrate_package(
    source: dict[str, Any],
    source_schema: dict[str, Any],
    target_schema: dict[str, Any],
    *,
    migration_id: str,
    executed_at: str,
    source_snapshot_ref: str,
    target_snapshot_ref: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Return a migrated package and its resolvable immutable snapshot map.

    The execution timestamp and references are explicit plan inputs. Repeating
    the same source and plan therefore yields byte-for-byte equivalent objects.
    """
    if source.get("contract_version") != "0.2.0":
        raise ValueError("migrator accepts only contract_version 0.2.0")
    if not all((migration_id, executed_at, source_snapshot_ref, target_snapshot_ref)):
        raise ValueError("migration identity, UTC execution time and snapshot refs are required")
    source_errors = list(
        Draft202012Validator(source_schema, format_checker=FormatChecker()).iter_errors(source)
    )
    if source_errors:
        raise ValueError("source package fails 0.2.0 schema: " + "; ".join(e.message for e in source_errors))

    migrated = deepcopy(source)
    migrated["contract_version"] = "0.2.1"

    # The 0.2.0 source has no claim-assessment execution timestamp. Do not
    # substitute cutoff, record, package or migration timestamps.
    for assessment in migrated["claim_assessments"]:
        assessment["assessed_at"] = None

    for availability in migrated["evidence_availability"]:
        availability["archive_attestation_id"] = None

    for retention in migrated["retention_records"]:
        retention["copy_scope_ids"] = []

    for event in migrated["audit_events"]:
        event["copy_id"] = None
        event["from_copy_state"] = None
        event["to_copy_state"] = None

    migrated["archive_attestations"] = []
    migrated["retention_copy_records"] = []
    migrated["migration_records"] = []
    migrated["analysis_processes"] = []

    target_errors = list(
        Draft202012Validator(target_schema, format_checker=FormatChecker()).iter_errors(migrated)
    )
    if target_errors:
        raise ValueError("migrated package fails 0.2.1 schema: " + "; ".join(e.message for e in target_errors))

    source_snapshot = deepcopy(source)
    target_snapshot = deepcopy(migrated)
    manifest = {
        "migration_id": migration_id,
        "source_contract_version": "0.2.0",
        "target_contract_version": "0.2.1",
        "migrator_version": MIGRATOR_VERSION,
        "executed_at": executed_at,
        "input_sha256": canonical_migration_payload_sha256(source_snapshot),
        "output_sha256": canonical_migration_payload_sha256(target_snapshot),
        "rules_applied": list(RULES_APPLIED),
        "result": "PASS",
        "loss_report": [],
        "source_snapshot_ref": source_snapshot_ref,
        "target_snapshot_ref": target_snapshot_ref,
    }
    migrated["migration_records"] = [manifest]
    snapshots = {
        source_snapshot_ref: source_snapshot,
        target_snapshot_ref: target_snapshot,
    }
    return migrated, snapshots
