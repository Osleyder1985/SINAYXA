# Contract 0.2.1 persistence mapping

**Status:** migration 0006, the JSON Schema/cross-entity validator, atomic PostgreSQL persistence adapter and package read-back serializer are implemented on the Issue #153 branch. PostgreSQL integration tests exercise fixture persistence and read-back. Knowledge-time/as-of query semantics remain open and are not claimed by this document.

## Integration boundary

Each contract_packages row is bound to one existing sinayxa.events.event_id. Contract source identities can be linked to an existing sinayxa.event_sources row through the explicit (event_id, registry_source_ref) pair. This reuses the existing event registry; it does not create a parallel event catalog.

Existing content-addressed bytes remain in source_artifacts and evidence_artifacts. The new contract records hold optional foreign-key references (artifact_source_ref, artifact_evidence_ref) to those rows. They do not duplicate artifact bytes. The new artifact-reference columns are persistence bindings, not additions to the 0.2.1 JSON contract.

## Entity-to-table mapping

| Contract 0.2.1 entity | Typed persistence | Relationship / notes |
| --- | --- | --- |
| Package root | contract_packages | Contract version, schema digest, event binding and DB insertion time |
| Claim | claims | Version ID, sequence, supersession and valid-time bounds |
| Claim component | claim_components | Component version tied to exact claim version |
| Source | contract_sources | UUID source identity, package/event binding and optional existing registry source reference |
| Source version | source_versions | Independent publication, first-detected, first-publicly-observed, retrieval and recorded timestamps; original timestamp observations retained as a schema-defined JSON array |
| Identity assessment | identity_assessments | Explicit booleans, identity category, evidence references and limitations |
| Evaluation unit | evaluation_units | Exact claim/component/source/source-version foreign keys and cutoff/methodology attributes |
| Evidence item | contract_evidence_items | Evidence kind, information nature, authenticity/access status; optional FK to existing evidence bytes |
| Evidence availability | evidence_availability | Claim/component/version/evaluation/evidence relationships and distinct availability/recorded times; optional archive-attestation FK |
| Claim-evidence link | claim_evidence_links | Typed SUPPORTING / CONTRARY / CONTEXTUAL relation to exact claim/component versions |
| Provenance node | provenance_nodes | Typed node kind and entity reference |
| Provenance edge | provenance_edges | Typed origin/dependency relation, exact component version, evidence references and valid-time bounds |
| Factor assessment | factor_assessments | Per-evaluation-unit factor dimension, status, rationale and human-review fields |
| Independence assessment | independence_assessments | Claim/component version, independence state, path/dependency references and human-review fields |
| Claim assessment | claim_assessments | Evidentiary and attribution states, alternatives, uncertainty, scope and human-review fields |
| Retention record | retention_records | Legal-basis state, purpose, responsible role, review/expiry and disposition |
| Audit event | audit_events | Typed action, actor role, occurred time, reason and state transition attributes |
| Archive attestation | archive_attestations | Evidence/source-version FKs, captured hash, archive record, integrity and verification claims |
| Retention copy record | retention_copy_records | Copy state/kind, parent copy, retention record and transition audit event |
| Migration record | contract_migration_records | Source/target versions, migrator, input/output digests, rules, result and loss report |
| Analysis process | analysis_processes | Dataset origin, exact component version, method, output evidence and separate availability/cutoff/recorded times |

## Representation rules

- Entity identity, version identity and relationships are relational columns with primary/foreign/unique constraints.
- Enumerated states are constrained by SQL CHECK clauses.
- SQL arrays represent contract reference/string arrays. JSONB is limited to contract-defined nested structures: source_versions.original_timestamps, contract_evidence_items.factor_dimensions, and contract_evidence_items.integrity_check. These structures still require validation against the exact JSON Schema before persistence; JSONB is not used as a substitute for an entity model.
- recorded_at preserves the contract-supplied timestamp. inserted_at is assigned by PostgreSQL and represents when the registry learned the row. Historical/as-of queries must use inserted_at as the knowledge-time boundary and must not substitute one timestamp for another.
- Publication, first detection, first public observation, retrieval, availability, assessment cutoff, capture, import, verification and database insertion timestamps remain distinct.
- Rows are append-only; corrections require new versioned rows or assessment records. UPDATE, DELETE and TRUNCATE are guarded on all new contract tables.
- Artifact reference FKs point to existing byte records. No second copy of the same source/evidence bytes is introduced.

## Not established by migration 0006

The current branch now implements the JSON Schema package validator, cross-entity reference checks, atomic package persistence and package reconstruction from PostgreSQL. The read-back path validates the reconstructed contract before returning it. It does not yet implement a knowledge-time/as-of query API. That requires an explicit policy for database insertion timestamps versus transaction commit/visibility time; inserted_at alone must not be represented as an exact commit-time observation. Real operational deletion/backup reconciliation, physical WORM/Object Lock, source collection, crawling, scraping and automatic credibility/causality scoring remain outside this implementation.

The migration is additive and applies only through the existing fresh-database migration runner. It does not adopt or alter legacy databases.
