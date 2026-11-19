"""Synthetic, local-only retention copy inventory and reconciliation lab.

This module deliberately proves only deletion from five directories created by
one temporary test run. It does not claim physical erasure or external-copy
coverage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

COPY_KINDS = {"PRIMARY", "LOGICAL_REPLICA", "CACHE", "EXPORT", "BACKUP"}
REPORT_VERSION = "1.0.0"


class RetentionLabError(ValueError):
    """Raised when inventory or deletion evidence is incomplete or unsafe."""


def _safe_child(root: Path, relative: str) -> Path:
    base = root.resolve(strict=True)
    normalized = relative.replace("\\", "/")
    parts = normalized.split("/")
    if normalized.startswith("/") or any(part in {"", ".", ".."} for part in parts):
        raise RetentionLabError("copy path contains an unsafe component")
    candidate = base.joinpath(*parts).resolve(strict=False)
    if candidate == base or base not in candidate.parents:
        raise RetentionLabError("copy path escapes the isolated laboratory root")
    current = base
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise RetentionLabError("symbolic links are not allowed in managed copy paths")
    return candidate


def validate_inventory(root: Path, inventory: list[dict[str, Any]]) -> dict[str, Path]:
    if not root.is_dir():
        raise RetentionLabError("isolated laboratory root does not exist")
    if not isinstance(inventory, list) or not inventory:
        raise RetentionLabError("copy inventory must be a non-empty list")
    resolved: dict[str, Path] = {}
    kinds: set[str] = set()
    for item in inventory:
        if not isinstance(item, dict):
            raise RetentionLabError("inventory entry must be an object")
        copy_id = item.get("copy_id")
        kind = item.get("kind")
        object_id = item.get("object_id")
        relative_path = item.get("relative_path")
        if not all(isinstance(value, str) and value.strip() for value in
                   (copy_id, kind, object_id, relative_path)):
            raise RetentionLabError("inventory entry has missing identifiers or path")
        if object_id in {".", ".."} or "/" in object_id or "\\" in object_id:
            raise RetentionLabError("object_id must be a single safe path component")
        if copy_id in resolved:
            raise RetentionLabError("duplicate copy_id in inventory")
        if kind not in COPY_KINDS:
            raise RetentionLabError("unknown managed copy kind")
        if kind in kinds:
            raise RetentionLabError("duplicate managed copy kind")
        if item.get("state") != "PRESENT":
            raise RetentionLabError("initial copy state must be PRESENT")
        path = _safe_child(root, relative_path)
        if not path.is_dir():
            raise RetentionLabError("managed copy location must be an existing directory")
        resolved[copy_id] = path
        kinds.add(kind)
    if kinds != COPY_KINDS:
        raise RetentionLabError("inventory must cover all five managed copy kinds")
    return resolved


def assert_read_allowed(deletion_state: str) -> None:
    if deletion_state != "ACTIVE":
        raise RetentionLabError("read/evaluation blocked while deletion is pending or complete")


def reconcile_deletion(
    root: Path,
    inventory: list[dict[str, Any]],
    ledger: dict[str, Any] | None,
) -> dict[str, Any]:
    locations = validate_inventory(root, inventory)
    if not isinstance(ledger, dict):
        raise RetentionLabError("deletion ledger missing or malformed")
    if ledger.get("synthetic") is not True or ledger.get("status") != "DELETE_PENDING":
        raise RetentionLabError("deletion ledger is not a synthetic DELETE_PENDING request")
    object_id = ledger.get("object_id")
    copy_ids = ledger.get("copy_ids")
    inventory_object_ids = {item["object_id"] for item in inventory}
    if not isinstance(object_id, str) or not object_id or inventory_object_ids != {object_id}:
        raise RetentionLabError("deletion ledger object_id does not match the complete inventory")
    if not isinstance(copy_ids, list) or any(not isinstance(value, str) for value in copy_ids) or len(copy_ids) != len(set(copy_ids)):
        raise RetentionLabError("deletion ledger copy_ids are malformed or duplicated")
    expected_ids = set(locations)
    if set(copy_ids) != expected_ids:
        raise RetentionLabError("deletion ledger does not cover the complete copy inventory")

    removed: list[dict[str, str]] = []
    remaining: list[str] = []
    for copy_id, location in locations.items():
        target = _safe_child(root, f"{inventory[[x['copy_id'] for x in inventory].index(copy_id)]['relative_path']}/{object_id}.json")
        if target.exists():
            if not target.is_file():
                raise RetentionLabError("managed object is not a regular file")
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            target.unlink()
            removed.append({"copy_id": copy_id, "sha256_before_delete": digest})
        if target.exists():
            remaining.append(copy_id)
    if remaining:
        raise RetentionLabError("one or more managed copies remain after reconciliation")
    return {
        "status": "DELETED",
        "object_id": object_id,
        "removed": removed,
        "remaining_copy_ids": remaining,
        "idempotent": True,
    }


def run_lab() -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    checks: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="sinayxa-issue-137-") as isolated:
        root = Path(isolated)
        object_id = "SYN-OBJECT-137"
        payload = json.dumps(
            {"object_id": object_id, "synthetic": True, "value": "retention-lab"},
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        inventory = []
        for index, kind in enumerate(sorted(COPY_KINDS)):
            relative = f"copies/{kind.lower()}"
            location = root / relative
            location.mkdir(parents=True)
            (location / f"{object_id}.json").write_bytes(payload)
            (location / "unaffected.json").write_text('{"preserve":true}', encoding="utf-8")
            inventory.append({
                "copy_id": f"COPY-{index + 1}",
                "kind": kind,
                "object_id": object_id,
                "relative_path": relative,
                "state": "PRESENT",
            })
        try:
            validate_inventory(root, inventory)
            checks["five_copy_inventory"] = "PASS"
        except RetentionLabError:
            checks["five_copy_inventory"] = "FAIL"
            raise
        try:
            assert_read_allowed("DELETE_PENDING")
            checks["delete_pending_read_gate"] = "FAIL"
        except RetentionLabError:
            checks["delete_pending_read_gate"] = "PASS"
        ledger = {
            "request_id": "SYN-DELETE-137",
            "object_id": object_id,
            "copy_ids": [entry["copy_id"] for entry in inventory],
            "status": "DELETE_PENDING",
            "synthetic": True,
        }
        result = reconcile_deletion(root, inventory, ledger)
        checks["all_five_copies_reconciled"] = (
            "PASS" if result["status"] == "DELETED" and len(result["removed"]) == 5 else "FAIL"
        )
        second = reconcile_deletion(root, inventory, ledger)
        checks["idempotent_repeat"] = (
            "PASS" if second["status"] == "DELETED" and not second["removed"] else "FAIL"
        )
        unaffected = all(
            (root / entry["relative_path"] / "unaffected.json").read_text(encoding="utf-8")
            == '{"preserve":true}'
            for entry in inventory
        )
        checks["unaffected_objects_preserved"] = "PASS" if unaffected else "FAIL"
        if "FAIL" in checks.values():
            raise RetentionLabError("one or more laboratory checks failed")
    cleanup_verified = not Path(isolated).exists()
    checks["temporary_root_cleanup"] = "PASS" if cleanup_verified else "FAIL"
    return {
        "schema_version": REPORT_VERSION,
        "source_commit": os.environ.get("GITHUB_SHA", "LOCAL_UNPINNED"),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "classification": "LAB_SYNTHETIC_LOCAL",
        "started_at_utc": started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all(value == "PASS" for value in checks.values()) else "FAIL",
        "checks": checks,
        "cleanup": "PASS" if cleanup_verified else "FAIL",
        "cleanup_scope": "single temporary directory created by this run",
        "network_used": False,
        "external_services_used": False,
        "production_data_used": False,
        "limits": [
            "All five copies are directories on one local host and may share physical media.",
            "No secure physical erasure, WORM/Object Lock, external replicas, provider snapshots, or production backups were tested.",
            "A PASS covers only the synthetic locations created and controlled by this run.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="write JSON report to this path")
    args = parser.parse_args()
    report = run_lab()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
