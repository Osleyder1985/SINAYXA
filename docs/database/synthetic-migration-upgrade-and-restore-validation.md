# Synthetic migration upgrade and logical restore validation

**Status:** Executed in the local PostgreSQL 18.7 CI laboratory  
**Issue:** #121  
**Test:** `MigrationRunnerIntegrationTests.test_synthetic_historical_snapshots_upgrade_and_preserve_invariants`  
**Scope:** Synthetic data only; no production database or external provider

## Upgrade experiment

The test starts by asserting the explicit **pre-0001** snapshot: the disposable database has neither the application schema nor the migration control-plane schema. It then constructs five inventory-consistent migration prefixes:

1. After `0001_event_registry.sql`: one synthetic event, its source link, and two temporal assertions.
2. After `0002_temporal_conflicts.sql`: a conflict linked to both assertions and a decision linked to that conflict.
3. After `0003_temporal_assessments_manifests.sql`: an assessment linked to the assertions and decision, plus a reproducibility manifest.
4. After `0004_source_evidence_artifacts.sql`: source and evidence artifacts with exact bytes, lengths, and SHA-256 digests.
5. After `0005_append_only_truncate_guard.sql`: the final schema and append-only truncate guards.

At each boundary the runner receives a manifest containing exactly the SQL files present in that synthetic snapshot. The full manifest is then applied as the roll-forward target. The test verifies that earlier migrations are not replayed and that identifiers, relationships, values, cardinalities, and artifact bytes remain unchanged.

## Logical data backup and restore experiment

After the final upgrade, the test exports all rows from the nine application data tables using PostgreSQL binary `COPY` streams, ordered deterministically by the first two columns. It writes each stream to a disposable backup file and records its SHA-256 digest.

The test then:

1. Creates a second disposable PostgreSQL database.
2. Recreates its schema and migration ledgers by applying the approved migration manifest.
3. Restores the nine application-table data streams in foreign-key dependency order.
4. Exports the restored tables using the same binary `COPY` format and deterministic ordering.
5. Compares the SHA-256 digest of every restored table stream with its backup stream.

The test passed on PostgreSQL 18.7 in CI. This demonstrates exact logical row-stream restoration for the synthetic records covered by the test.

## Migration failure and retry semantics

A separate integration test commits migration 0001, forces migration 0002 to fail, and verifies that migration 0002's DDL and integrity-ledger row are absent while migration 0001 remains committed. It then corrects the still-unapplied migration 0002 artifact, updates its SHA-256 **and** its synthetic `source_revision`, and retries. The corrected migration is applied once and the ledger records the corrected provenance. This does not weaken drift protection: changing bytes for an already-applied migration remains a fail-closed error.

## Explicit limitations

This is **not** a physical backup, a full-cluster backup, or a `pg_dump` archive test. The schema is recreated from the migration manifest; the application data tables are restored from binary `COPY` streams. The control-plane schema and its integrity ledger are freshly bootstrapped on the target, not copied from the source.

The experiment does not prove:

- recovery of production data or an existing deployed installation;
- point-in-time recovery, WAL replay, or disaster recovery;
- restoration of roles, grants, server configuration, extensions, or external object storage;
- recovery of data not represented in the synthetic fixture;
- legacy database adoption or proof of historical SQL execution.

Do not describe this test as a production backup/recovery certification. A separate, version-pinned `pg_dump`/`pg_restore` or physical-backup exercise, including control-plane policy and environment prerequisites, remains a distinct validation task if full database recovery is required.
