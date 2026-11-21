# Issue #137 — Synthetic retention copy reconciliation laboratory

## Purpose

This dependency-free laboratory exercises inventory and deletion reconciliation for exactly five synthetic copy classes:

- `PRIMARY`
- `LOGICAL_REPLICA`
- `CACHE`
- `EXPORT`
- `BACKUP`

It is an additional filesystem-level test. The PostgreSQL backup/restore gate and post-backup deletion-ledger reconciliation remain covered separately by Issue #113 / PR #115. This laboratory does not replace those database tests.

## Execution environments

The GitHub Actions workflow executes this laboratory on an ephemeral GitHub-hosted Ubuntu runner. Its temporary filesystem is local to that runner; it is not the user's workstation or a persistent self-hosted machine. Reports distinguish `GITHUB_HOSTED_RUNNER` from `USER_LOCAL_HOST`.

## Run locally

Requirements: Python 3.12 or newer. No third-party Python package, Docker daemon, network access, database, cloud account, license, or paid service is required.

From the repository root:

```bash
python -m unittest tests.validation.test_retention_copy_reconciliation_lab -v
python -m scripts.validation.retention_copy_reconciliation_lab --report artifacts/retention-copy-lab/retention-copy-lab-report.json
```

The runner creates a unique temporary directory, writes only deterministic synthetic JSON objects, validates the inventory, blocks reads in `DELETE_PENDING`, reconciles all five copies, repeats reconciliation to test idempotency, verifies unrelated files remain unchanged, and confirms the temporary directory is absent after cleanup.

## Evidence

The JSON report records:

- source branch commit (`SINAYXA_SOURCE_COMMIT`, supplied from the PR head in CI);
- workflow commit (`GITHUB_SHA`, which may be GitHub's synthetic PR merge commit);
- Python version and platform;
- UTC start/completion timestamps;
- per-control PASS/FAIL states;
- per-copy SHA-256 digests captured immediately before deletion;
- confirmation of idempotent repeat and temporary-root cleanup;
- explicit synthetic-only and no-network/no-external-service declarations.

A local run is marked `LOCAL_UNPINNED` unless `SINAYXA_SOURCE_COMMIT` is explicitly supplied; run it from a clean checkout and record `git rev-parse HEAD` alongside the report. The CI artifact is retained for 14 days. A CI PASS is evidence from the ephemeral GitHub-hosted runner only; reproduce on the user's local machine separately before describing it as a user-local validation.

## Safety and interpretation

All copy locations are directories on one local host and may share the same physical disk. The laboratory proves only that the exact files created by this run were removed from those managed directories. It does not prove secure media erasure, independence of physical media, deletion from unmanaged caches or exports, external/provider backup deletion, snapshot reconciliation, WORM/Object Lock, or production behavior.

The PostgreSQL restore gate from #113 remains a separate synthetic database test: a restored database is not made available to its consumer until the deletion ledger is validated and reconciled. Neither laboratory is evidence of production data deletion.

## Acceptance boundary

Issue #137 may be considered implemented only after the complete CI run passes on the reviewed PR HEAD and its artifact is inspected. Area C in #89 remains partially verified until external copies, production inventories, backup providers, physical erasure claims, and operational controls are independently evidenced.

## Receipt and retry boundary

A missing object is not treated as deleted merely because its path is absent. Reconciliation requires a SHA-256 deletion receipt for every already-missing copy; a copy that exists despite a prior receipt is rejected. The unit tests cover fail-closed behavior for unreceipted missing copies and retry of a partial deletion when matching receipts are supplied.

The current laboratory passes receipts between calls in memory and records them in the report. It does **not** yet simulate a durable receipt journal surviving process termination between filesystem unlink and receipt persistence. That crash-consistency property remains unverified and must not be inferred from the idempotency test.
