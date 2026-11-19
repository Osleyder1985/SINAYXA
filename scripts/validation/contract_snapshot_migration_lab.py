"""Persisted, synthetic 0.2.0 -> 0.2.1 contract migration laboratory.

Loads the canonical migrator and validator from a separately checked-out,
pinned PR #85 commit. No migration logic is copied into SINAYXA main.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import platform
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HISTORICAL_COLLECTIONS = (
    "claims", "claim_components", "sources", "source_versions",
    "identity_assessments", "evaluation_units", "evidence_items",
    "evidence_availability", "claim_evidence_links", "provenance_nodes",
    "provenance_edges", "factor_assessments", "independence_assessments",
    "claim_assessments", "retention_records", "audit_events",
)
PLAN = {
    "migration_id": "migration-020-021-local-lab-issue-138",
    "executed_at": "2026-11-19T00:00:00Z",
    "source_snapshot_ref": "sinayxa-lab://issue-138/source-0.2.0",
    "target_snapshot_ref": "sinayxa-lab://issue-138/target-0.2.1",
}


class MigrationLabError(RuntimeError):
    """Raised when persisted migration evidence is incomplete or inconsistent."""


class InjectedFailure(MigrationLabError):
    """Controlled failure used to verify that staged output is not published."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def load_contract_modules(contract_source: Path):
    validation_dir = (contract_source / "scripts" / "validation").resolve(strict=True)
    if str(validation_dir) not in sys.path:
        sys.path.insert(0, str(validation_dir))
    migrator = importlib.import_module("migrate_source_evidence_contract_0_2_0_to_0_2_1")
    validator = importlib.import_module("validate_source_evidence_contract_0_2_1")
    return migrator, validator


def execute_persisted_migration(
    root: Path,
    contract_source: Path,
    *,
    inject_failure_before_publish: bool = False,
) -> dict[str, Any]:
    if root.exists() and any(root.iterdir()):
        raise MigrationLabError("migration root must be empty; refusing to overwrite prior evidence")
    root.mkdir(parents=True, exist_ok=True)
    migrator, validator = load_contract_modules(contract_source)

    source_path = contract_source / "tests" / "fixtures" / "contracts" / "source-evidence-contract-v0.2.0.json"
    source_schema_path = contract_source / "schemas" / "source-evidence-contract-0.2.0.schema.json"
    target_schema_path = contract_source / "schemas" / "source-evidence-contract-0.2.1.schema.json"
    for required in (source_path, source_schema_path, target_schema_path):
        if not required.is_file():
            raise MigrationLabError(f"pinned contract source is incomplete: {required.name}")

    source_bytes = source_path.read_bytes()
    source = json.loads(source_bytes)
    source_schema = json.loads(source_schema_path.read_text(encoding="utf-8"))
    target_schema = json.loads(target_schema_path.read_text(encoding="utf-8"))

    source_dir = root / "source"
    source_dir.mkdir()
    persisted_source = source_dir / "source-0.2.0.json"
    persisted_source.write_bytes(source_bytes)
    source_file_digest = sha256(persisted_source.read_bytes())

    migrated, snapshots = migrator.migrate_package(
        source, source_schema, target_schema, **PLAN
    )
    validator.validate_package(migrated, source_schema, target_schema, snapshots)

    target_snapshot = snapshots[PLAN["target_snapshot_ref"]]
    target_snapshot_bytes = canonical_json(target_snapshot)
    final_package_bytes = canonical_json(migrated)
    target_snapshot_digest = sha256(target_snapshot_bytes)
    final_package_digest = sha256(final_package_bytes)

    baseline = {
        collection: {
            "count": len(source[collection]),
            "ids": sorted(
                str(item.get(next((key for key in item if key.endswith("_id")), "")))
                for item in source[collection]
            ),
        }
        for collection in HISTORICAL_COLLECTIONS
    }
    output_counts = {
        collection: len(migrated[collection]) for collection in HISTORICAL_COLLECTIONS
    }
    if any(baseline[name]["count"] != output_counts[name] for name in HISTORICAL_COLLECTIONS):
        raise MigrationLabError("historical collection cardinality changed")

    stage = root / ".target.staging"
    published = root / "target"
    if published.exists():
        raise MigrationLabError("target snapshot already published; duplicate migration is forbidden")
    stage.mkdir()
    (stage / "target-snapshot-0.2.1.json").write_bytes(target_snapshot_bytes)
    (stage / "migrated-package-0.2.1.json").write_bytes(final_package_bytes)
    manifest = {
        "schema_version": "1.0.0",
        "classification": "LAB_SYNTHETIC_LOCAL",
        "migration_id": PLAN["migration_id"],
        "source_contract_commit": os.environ.get("SINAYXA_CONTRACT_SOURCE_COMMIT", "UNPINNED"),
        "source_snapshot_ref": PLAN["source_snapshot_ref"],
        "target_snapshot_ref": PLAN["target_snapshot_ref"],
        "input_file_sha256": source_file_digest,
        "input_canonical_sha256": migrated["migration_records"][0]["input_sha256"],
        "target_snapshot_file_sha256": target_snapshot_digest,
        "output_package_file_sha256": final_package_digest,
        "output_canonical_sha256": migrated["migration_records"][0]["output_sha256"],
        "historical_collection_counts_before": {key: value["count"] for key, value in baseline.items()},
        "historical_collection_counts_after": output_counts,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "result": "PASS",
    }
    (stage / "migration-evidence.json").write_bytes(canonical_json(manifest))

    if inject_failure_before_publish:
        shutil.rmtree(stage)
        raise InjectedFailure("injected failure before atomic target publication")

    # Stage and destination are siblings on one filesystem; rename is atomic.
    os.replace(stage, published)
    if not (published / "migrated-package-0.2.1.json").is_file():
        raise MigrationLabError("published target package is missing")
    if (root / ".target.staging").exists():
        raise MigrationLabError("staging directory remains after publication")
    return {
        "manifest": manifest,
        "source_path": persisted_source,
        "published_path": published,
        "final_package_bytes": final_package_bytes,
        "target_snapshot_bytes": target_snapshot_bytes,
    }


def run_lab(contract_source: Path) -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    checks: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="sinayxa-issue-138-") as temporary:
        root = Path(temporary)
        first = root / "first"
        first.mkdir()
        # First execute an injected interruption; source must remain byte-identical
        # and no final target may become visible.
        source_fixture = contract_source / "tests" / "fixtures" / "contracts" / "source-evidence-contract-v0.2.0.json"
        original_digest = sha256(source_fixture.read_bytes())
        try:
            execute_persisted_migration(first, contract_source, inject_failure_before_publish=True)
            checks["failure_injection"] = "FAIL"
        except InjectedFailure:
            checks["failure_injection"] = "PASS"
        checks["no_partial_target_published"] = (
            "PASS" if not (first / "target").exists() and not (first / ".target.staging").exists() else "FAIL"
        )
        checks["source_preserved_after_failure"] = (
            "PASS" if sha256(source_fixture.read_bytes()) == original_digest
            and (first / "source" / "source-0.2.0.json").is_file() else "FAIL"
        )

        successful = execute_persisted_migration(first, contract_source)
        checks["persisted_source_and_target"] = (
            "PASS" if successful["source_path"].is_file()
            and (successful["published_path"] / "migrated-package-0.2.1.json").is_file()
            and (successful["published_path"] / "target-snapshot-0.2.1.json").is_file()
            else "FAIL"
        )
        checks["atomic_publication_no_staging"] = (
            "PASS" if not (first / ".target.staging").exists() else "FAIL"
        )
        checks["historical_collection_counts_preserved"] = (
            "PASS" if successful["manifest"]["historical_collection_counts_before"]
            == successful["manifest"]["historical_collection_counts_after"] else "FAIL"
        )
        try:
            execute_persisted_migration(first, contract_source)
            checks["duplicate_migration_rejected"] = "FAIL"
        except MigrationLabError:
            checks["duplicate_migration_rejected"] = "PASS"

        second_root = root / "repeat"
        second_root.mkdir()
        repeated = execute_persisted_migration(second_root, contract_source)
        checks["deterministic_persisted_output"] = (
            "PASS" if successful["final_package_bytes"] == repeated["final_package_bytes"]
            and successful["target_snapshot_bytes"] == repeated["target_snapshot_bytes"]
            else "FAIL"
        )
        checks["input_output_hashes_present"] = (
            "PASS" if all(len(successful["manifest"][key]) == 64 for key in (
                "input_file_sha256", "input_canonical_sha256",
                "target_snapshot_file_sha256", "output_package_file_sha256",
                "output_canonical_sha256",
            )) else "FAIL"
        )
        final_manifest = successful["manifest"]
        if "FAIL" in checks.values():
            raise MigrationLabError("one or more migration laboratory checks failed")

    cleanup = not Path(temporary).exists()
    checks["temporary_root_cleanup"] = "PASS" if cleanup else "FAIL"
    return {
        "schema_version": "1.0.0",
        "classification": "LAB_SYNTHETIC_LOCAL",
        "source_commit": os.environ.get("GITHUB_SHA", "LOCAL_UNPINNED"),
        "contract_source_commit": os.environ.get("SINAYXA_CONTRACT_SOURCE_COMMIT", "UNPINNED"),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "started_at_utc": started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all(value == "PASS" for value in checks.values()) else "FAIL",
        "checks": checks,
        "migration_evidence": final_manifest,
        "cleanup": "PASS" if cleanup else "FAIL",
        "network_used_by_lab": False,
        "production_data_used": False,
        "external_services_used": False,
        "limits": [
            "Uses the exact PR #85 migrator and schemas from a separately checked-out commit.",
            "Validates persisted snapshots and atomic publication only on local temporary filesystem.",
            "Does not prove production migration, external storage durability, cross-device atomicity, or rollback of a production database.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract-source", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = run_lab(args.contract_source.resolve(strict=True))
    rendered = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
