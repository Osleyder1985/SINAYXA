"""Adversarial tests for the Issue #137 synthetic retention copy lab."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validation.retention_copy_reconciliation_lab import (
    COPY_KINDS,
    RetentionLabError,
    assert_read_allowed,
    reconcile_deletion,
    run_lab,
    validate_inventory,
)


class RetentionCopyReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.object_id = "SYN-OBJECT"
        self.inventory = []
        for index, kind in enumerate(sorted(COPY_KINDS)):
            relative = f"copies/{kind.lower()}"
            location = self.root / relative
            location.mkdir(parents=True)
            (location / f"{self.object_id}.json").write_text('{"synthetic":true}', encoding="utf-8")
            self.inventory.append({
                "copy_id": f"COPY-{index}",
                "kind": kind,
                "object_id": self.object_id,
                "relative_path": relative,
                "state": "PRESENT",
            })
        self.ledger = {
            "request_id": "SYN-DELETE",
            "object_id": self.object_id,
            "copy_ids": [entry["copy_id"] for entry in self.inventory],
            "status": "DELETE_PENDING",
            "synthetic": True,
        }

    def test_inventory_covers_all_five_copy_kinds(self) -> None:
        self.assertEqual(5, len(validate_inventory(self.root, self.inventory)))

    def test_inventory_rejects_duplicate_copy_id(self) -> None:
        duplicate = [*self.inventory, dict(self.inventory[0], kind="PRIMARY")]
        with self.assertRaisesRegex(RetentionLabError, "duplicate copy_id"):
            validate_inventory(self.root, duplicate)

    def test_inventory_rejects_unknown_copy_kind(self) -> None:
        invalid = [dict(item) for item in self.inventory]
        invalid[0]["kind"] = "REMOTE_SNAPSHOT"
        with self.assertRaisesRegex(RetentionLabError, "unknown"):
            validate_inventory(self.root, invalid)

    def test_inventory_rejects_missing_copy_kind(self) -> None:
        with self.assertRaisesRegex(RetentionLabError, "all five"):
            validate_inventory(self.root, self.inventory[:-1])

    def test_inventory_rejects_path_traversal(self) -> None:
        invalid = [dict(item) for item in self.inventory]
        invalid[0]["relative_path"] = "../../outside"
        with self.assertRaisesRegex(RetentionLabError, "escapes"):
            validate_inventory(self.root, invalid)

    def test_inventory_rejects_symlink_location(self) -> None:
        invalid = [dict(item) for item in self.inventory]
        location = self.root / invalid[0]["relative_path"]
        location.rmdir()
        outside = self.root / "outside"
        outside.mkdir()
        location.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(RetentionLabError, "symbolic links"):
            validate_inventory(self.root, invalid)

    def test_delete_pending_blocks_reads(self) -> None:
        with self.assertRaisesRegex(RetentionLabError, "blocked"):
            assert_read_allowed("DELETE_PENDING")

    def test_missing_ledger_fails_closed(self) -> None:
        with self.assertRaisesRegex(RetentionLabError, "missing or malformed"):
            reconcile_deletion(self.root, self.inventory, None)

    def test_incomplete_or_unknown_ledger_fails_closed(self) -> None:
        invalid = dict(self.ledger, copy_ids=self.ledger["copy_ids"][:-1])
        with self.assertRaisesRegex(RetentionLabError, "complete copy inventory"):
            reconcile_deletion(self.root, self.inventory, invalid)
        invalid = dict(self.ledger, copy_ids=["UNKNOWN-COPY"])
        with self.assertRaisesRegex(RetentionLabError, "complete copy inventory"):
            reconcile_deletion(self.root, self.inventory, invalid)

    def test_ledger_object_must_match_inventory(self) -> None:
        invalid = dict(self.ledger, object_id="SYN-OTHER-OBJECT")
        with self.assertRaisesRegex(RetentionLabError, "does not match"):
            reconcile_deletion(self.root, self.inventory, invalid)

    def test_reconciliation_removes_all_managed_copies_and_is_idempotent(self) -> None:
        first = reconcile_deletion(self.root, self.inventory, self.ledger)
        self.assertEqual("DELETED", first["status"])
        self.assertEqual(5, len(first["removed"]))
        second = reconcile_deletion(self.root, self.inventory, self.ledger)
        self.assertEqual("DELETED", second["status"])
        self.assertEqual([], second["removed"])

    def test_reconciliation_preserves_unaffected_objects(self) -> None:
        for item in self.inventory:
            (self.root / item["relative_path"] / "unaffected.json").write_text(
                '{"keep":true}', encoding="utf-8"
            )
        reconcile_deletion(self.root, self.inventory, self.ledger)
        for item in self.inventory:
            self.assertEqual(
                '{"keep":true}',
                (self.root / item["relative_path"] / "unaffected.json").read_text(encoding="utf-8"),
            )

    def test_lab_report_is_synthetic_and_scoped(self) -> None:
        report = run_lab()
        self.assertEqual("PASS", report["status"])
        self.assertTrue(all(value == "PASS" for value in report["checks"].values()))
        self.assertFalse(report["network_used"])
        self.assertFalse(report["external_services_used"])
        self.assertFalse(report["production_data_used"])
        self.assertEqual("PASS", report["cleanup"])


if __name__ == "__main__":
    unittest.main()
