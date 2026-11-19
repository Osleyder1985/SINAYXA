# Issue #138 — persisted contract snapshot migration laboratory

## Purpose and source of truth

This laboratory executes the canonical 0.2.0 → 0.2.1 migrator from PR #85. It does not copy or reimplement migration rules. CI checks out the exact PR #85 commit `6335771309d55e3cc948ba28b008310c3b1b4d4c` into `contract-source/` and imports its migrator, schemas, validator and fixture.

Only the synthetic fixture `source-evidence-contract-v0.2.0.json` is used. No production data, credentials, cloud storage or paid service is involved.

## Local execution

1. Check out the repository and PR #85 source at the pinned commit into a sibling directory named `contract-source`.
2. Install `requirements-contract-validation.txt`.
3. Run:

```bash
python -m unittest tests.validation.test_contract_snapshot_migration_lab -v
python -m scripts.validation.contract_snapshot_migration_lab --contract-source ./contract-source --report ./artifacts/contract-migration-lab/report.json
```

The lab persists the exact source fixture, calls the PR #85 migrator, validates the output through the PR #85 semantic validator, persists both the referenced target snapshot and final migrated package, then atomically renames a staged directory into the published target location.

## Failure and recovery checks

- Injects a failure after staging output but before publication.
- Verifies no final target is visible and the source snapshot remains unchanged.
- Retries in the same isolated run and publishes successfully.
- Rejects a second migration into an already populated root.
- Runs the same plan in a second isolated root and compares exact output bytes.

## Evidence

The JSON report includes exact source commits, Python runtime, UTC timestamps, byte-level SHA-256 values, canonical migrator hashes, source/target snapshot references, historical collection counts, individual control results and cleanup status.

## Limits

This validates persisted snapshots and atomic directory publication on one local filesystem only. It does not prove production migration, cross-device atomicity, external storage durability, provider backup behavior or production database rollback. Area E in #89 remains open until an environment representative of the actual target is authorized and validated.