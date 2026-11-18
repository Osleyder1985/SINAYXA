# PostgreSQL migration integrity and legacy adoption design

**Status:** Proposed; implementation not yet authorized by a reviewed test plan  
**Issue:** [#121](https://github.com/Osleyder1985/SINAYXA/issues/121)  
**Scope:** Local PostgreSQL 18.7 validation laboratory only

## 1. Purpose

Replace the current unconditional SQL replay in `initialize_database()` with a deterministic, fail-closed migration runner that:

- applies only migrations not recorded as applied;
- verifies the exact bytes of every newly managed migration using SHA-256;
- refuses to run when an already-applied migration's current bytes differ from its recorded digest;
- serializes concurrent initializers;
- preserves per-migration transactional atomicity;
- distinguishes historical installations whose old ledger has no content digest from installations verifiable from first bootstrap.

This design does not authorize production migrations, external database services, provider selection, destructive rollback, or changes to append-only business data.

## 2. Current-state facts

The current initializer reads every `database/migrations/*.sql` file in lexical order and executes each file in its own transaction. It does not consult the ledger before execution.

The current `sinayxa.schema_migrations` table stores only:

- `migration_id text PRIMARY KEY`
- `applied_at timestamptz NOT NULL`

The five existing migration files insert their IDs with `ON CONFLICT DO NOTHING`. The existing integration test reruns initialization and checks five IDs and 18 triggers. It does not prove content integrity, historical upgrades, concurrency, or recovery across committed migrations.

## 3. Required architecture

### 3.1 Immutable migration manifest

Introduce a reviewed manifest for every migration with:

- monotonically increasing integer version;
- stable migration ID;
- repository-relative SQL path;
- expected SHA-256 of the exact UTF-8 file bytes;
- introducing commit/release identifier once known;
- transactional execution mode (transactional only in the first implementation).

The runner must reject duplicate versions, duplicate IDs, path traversal, missing files, malformed digests, and non-increasing versions before opening a database transaction.

The manifest is the approved inventory. It must not silently learn or rewrite a digest from the current working tree. Updating a historical SQL file and its digest together must still be detected against the database's recorded digest.

### 3.2 Separate integrity ledger

Do not pretend the legacy `schema_migrations` rows contain historical hashes. Add a separate integrity/attestation ledger with at least:

- migration ID and version;
- SHA-256 of exact SQL bytes;
- source revision;
- applied timestamp;
- runner version.

For a new database, each migration's DDL, legacy-compatible ID row (if retained), and integrity-ledger row must commit in the same transaction.

For an existing database with old IDs and no digests, classify those rows as `LEGACY_UNVERIFIED`. Never fill in the current SQL digest and label it as the historical executed digest.

### 3.3 Legacy adoption is a separate operation

A legacy database may be adopted only through an explicit, read-only preflight followed by a separately recorded adoption attestation. The attestation must include:

- exact verifier version and source commit;
- normalized catalog fingerprint algorithm/version;
- computed fingerprint;
- expected approved baseline fingerprint;
- verification timestamp and result;
- list of legacy migration IDs found.

The fingerprint must be derived from a deterministic, documented set of PostgreSQL catalog objects: schemas, relations, columns and types, constraints, indexes, functions, triggers, and relevant defaults. Volatile OIDs, physical storage details, row estimates, and timestamps must be excluded. The expected baseline must be produced by a clean database built from the approved migration set and independently reviewed.

If the catalog cannot be normalized, differs from the approved baseline, contains unexpected objects, or lacks required objects, adoption fails closed. The adoption attestation must say that it verifies present catalog equivalence only; it does not prove which historical SQL bytes were executed.


### 3.3.1 Catalog fingerprint contract v1

The first fingerprint implementation is deliberately scoped to the application schema `sinayxa` on PostgreSQL 18.7. It is a schema-equivalence check, not a data-integrity check and not proof of historical SQL execution. The fingerprint algorithm must have an explicit version (for example, `sinayxa-catalog-v1`) and must fail closed when it encounters a catalog feature that the version does not understand.

**Objects and semantic properties included**

- **Schema:** qualified name, owner role, schema ACL, and explicitly granted privileges.
- **Relations:** every relation in `sinayxa`, including relation kind, persistence, partitioning metadata, row-security flags, replica-identity mode, owner, and ACL. The known baseline includes the ten current tables: the nine business tables plus `schema_migrations`.
- **Columns:** ordinal position, name, fully qualified type identity, type modifier, collation, nullability, identity/generated attributes, and normalized default expression.
- **Constraints:** name, type, ordered local and referenced column names, referenced relation, deferrability, initially-deferred state, validation state, and normalized definition. This includes PK, FK, UNIQUE, CHECK, and exclusion constraints.
- **Indexes:** name, owning relation, access method, uniqueness, primary/exclusion flags, validity/readiness, ordered key and included columns, expressions, predicate, and normalized definition.
- **Sequences:** name, type, increment, minimum, maximum, start, cache, cycle flag, owner, and ownership/dependency relation. Current sequence values are data state and are excluded from the catalog fingerprint; they require separate migration/restore invariants.
- **Functions:** qualified name and identity argument types, return type, language, normalized definition, volatility, strictness, security-definer flag, leakproof flag, parallel-safety, cost, configuration (including function-level `search_path`), owner, and ACL. Function bodies are semantic inputs and must not be omitted.
- **Triggers:** name, owning relation, timing, event set, row-versus-statement orientation, condition, enabled state, and referenced function identity. The normalized definition must distinguish the row-level UPDATE/DELETE guards from statement-level TRUNCATE guards.
- **Types:** domains, enums, composites, and other user-defined types in the managed schema, including their constraints, labels, attributes, and base-type identity.
- **Views and materialized views:** definition, output columns, owner, ACL, and relevant refresh/population metadata.
- **Security and extension metadata:** RLS policies and their command/role/USING/WITH CHECK expressions; extension name, version, and schema; object ownership, explicit ACLs, and default privileges relevant to `sinayxa`.

The expected baseline must explicitly enumerate the current schema objects and their semantic properties. Any additional object in the managed schema that is not represented by the fingerprint algorithm is an unsupported catalog object and causes adoption to fail; it must not be silently ignored. Missing expected objects also cause failure. The initial baseline must account for the two current PL/pgSQL functions (`reject_registry_mutation()` and `reject_registry_truncate()`) and all row-level and statement-level triggers created by migrations 0001–0005.

**Canonicalization and digest**

Catalog queries may use OIDs internally to join PostgreSQL catalogs, but OIDs must never appear in the serialized fingerprint. Resolve references to stable qualified names and ordered column names. Normalize each object into a typed JSON record; sort records by object type, qualified name, and stable identity. Serialize with UTF-8 JSON, lexicographically sorted object keys, no insignificant whitespace, and a documented null/boolean/number representation. Compute SHA-256 over those exact serialized bytes. The attestation stores the algorithm version, PostgreSQL server version, record count, and final digest, plus the normalized record-set artifact or its separately retained digest-addressed artifact.

Role names in owners and ACLs are semantically relevant. Do not discard ACLs or silently remap owners to make two schemas compare equal. If the expected roles are absent or differ, the verifier must return an explicit unsupported-environment/mismatch result. System schemas and volatile physical/statistical fields (OIDs, relfilenodes, relation sizes, row estimates, planner statistics, transaction IDs, and timestamps) are excluded. Excluding these fields must not exclude logical schema properties listed above.

**Separation from data validation**

A matching catalog fingerprint does not prove that table contents, sequence positions, append-only history, or artifact bytes match. Adoption and restore tests must separately compare the approved logical-data invariants: row counts and primary-key sets per table, FK consistency, payload values, temporal ordering, sequence state where used, and content lengths/SHA-256 for source and evidence artifacts. These checks remain synthetic in this laboratory and do not prove production recovery.

No automatic schema repair or DDL is allowed during adoption.

### 3.4 Runner transaction and locking protocol

For each migration:

1. Acquire a transaction-scoped PostgreSQL advisory lock using a documented, stable key for this migration system.
2. Read the integrity ledger while holding the lock.
3. If the migration ID exists with the same version and SHA-256, skip it.
4. If the ID exists with a different version or SHA-256, abort with a dedicated drift error before executing SQL.
5. If the ID is absent but the version is already occupied by another ID, abort.
6. Execute the SQL with the same connection and transaction.
7. Insert the migration integrity row and any compatibility row in that same transaction.
8. Commit; transaction exit releases the advisory lock.

The runner must also detect unknown ledger entries, gaps/ordering violations, and manifest/database disagreement. It must not treat a missing integrity row for a legacy ID as a new migration.

The first implementation supports transactional SQL only. Non-transactional migrations require a separate explicit design and are out of scope.

### 3.5 Recovery model

Do not generate or run automatic `down` migrations against append-only registry tables.

- Failure inside one migration: its DDL and ledger write roll back together.
- Failure after earlier migrations committed: those earlier migrations remain applied; a retry verifies and skips them, then resumes at the first unapplied migration.
- Recovery from data loss or an invalid catalog: restore a verified backup into an isolated target, validate it, then perform an approved roll-forward. Do not claim recovery until restore tests prove it.

A backup is not considered verified merely because a backup command returned success. The lab must restore it to a clean isolated PostgreSQL instance and compare logical invariants and artifact digests.

## 4. Legacy transition states

Use explicit machine-readable states:

- `FRESH_VERIFIED`: all migrations applied by the new runner with matching digests.
- `LEGACY_UNVERIFIED`: old migration IDs exist but historical SQL digests do not.
- `LEGACY_ADOPTED_CATALOG_MATCH`: a separate adoption attestation confirms current catalog equivalence; historical SQL execution remains unproven.
- `DRIFT_DETECTED`: an applied migration ID/version/digest or catalog invariant conflicts with the approved manifest.
- `INCOMPLETE`: one or more approved migrations are not yet applied.

Never collapse `LEGACY_ADOPTED_CATALOG_MATCH` into `FRESH_VERIFIED`.

## 5. Test matrix and evidence requirements

### Test cases

- **Empty PostgreSQL 18.7 database:** apply all migrations once; verify ledger rows and catalog fingerprint.
- **Second initialization:** do not replay SQL; verify execution spy and unchanged applied rows.
- **Same ID and same digest:** skip the migration and return an explicit skip result.
- **Same ID with changed bytes:** fail before SQL; verify drift exception and absence of sentinel DDL.
- **Same version with a different ID:** fail closed with a version-collision error.
- **New migration:** execute only the pending migration; verify per-migration execution log.
- **SQL fails midway:** both DDL and ledger row are absent after rollback.
- **Failure after an earlier commit:** retain the earlier applied row; retry resumes at the next migration.
- **Two concurrent initializers:** verify exactly-once application using parallel connections and catalog/ledger checks.
- **Legacy IDs without hashes:** remain unverified until adoption; do not backfill synthetic digests.
- **Legacy catalog exact match:** produce a separate adoption attestation with fingerprint and verifier provenance.
- **Legacy catalog mismatch:** refuse adoption without DDL; compare catalog state before and after.
- **Backup restore:** restore logical state to an isolated instance and verify invariants and artifact digests.

Tests must use unique disposable schemas or databases and synthetic records. No production or external provider is involved.

## 6. Upgrade fixtures

Create versioned synthetic snapshots for each historical migration boundary:

- before migration 0001;
- after 0001;
- after 0002;
- after 0003;
- after 0004;
- after 0005.

Each fixture must include representative synthetic records where the schema permits them. Upgrade assertions must preserve primary keys, foreign keys, row counts, payload values, temporal ordering, append-only triggers, and source/evidence byte lengths and SHA-256 digests.

The fixtures are test inputs, not claims about real customer databases.

## 7. Implementation sequence

1. Freeze and hash the five current SQL files; review the manifest against the exact main commit.
2. Implement pure manifest validation and digest verification tests without a database.
3. Implement the new ledger and runner for fresh databases only.
4. Add failure, retry, drift, version collision, and concurrency integration tests.
5. Implement legacy catalog fingerprinting and read-only preflight.
6. Implement explicit legacy adoption attestation only after an independently reviewed clean-baseline fingerprint exists.
7. Add historical upgrade fixtures and backup restore test.
8. Update documentation and Issue #89 evidence; keep Issue #121 open until every criterion has evidence.

## 8. Non-goals and safeguards

- No production database access or migration.
- No provider selection or external resources.
- No automatic destructive rollback.
- No deletion or rewriting of append-only event, assertion, conflict, assessment, manifest, source, or evidence records.
- No claims of WORM, superuser resistance, offsite backup, or production readiness from PostgreSQL triggers or synthetic tests.
- No automatic blessing of historical SQL hashes.
- No modification to the five existing SQL files until the migration manifest and legacy transition tests are reviewed.

## 9. Acceptance decision

The design is acceptable for implementation only when the migration manifest, normalized catalog fingerprint contract, and legacy adoption semantics are reviewed together. CI success alone is not sufficient evidence for historical adoption or recovery.
