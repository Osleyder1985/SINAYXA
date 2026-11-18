CREATE SCHEMA sinayxa_control;

CREATE TABLE sinayxa_control.bootstrap_state (
    singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
    bootstrap_version integer NOT NULL,
    bootstrap_sha256 char(64) NOT NULL,
    installed_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE sinayxa_control.migration_integrity (
    migration_id text PRIMARY KEY,
    version integer NOT NULL UNIQUE CHECK (version > 0),
    sha256 char(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    source_revision text NOT NULL CHECK (source_revision ~ '^([0-9a-f]{40}|[0-9a-f]{64})$'),
    applied_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    runner_version text NOT NULL
);

CREATE TABLE sinayxa_control.legacy_adoption_attestations (
    attestation_id text PRIMARY KEY,
    status text NOT NULL CHECK (status = 'LEGACY_ADOPTED_CATALOG_MATCH'),
    verifier_version text NOT NULL,
    algorithm_version text NOT NULL,
    computed_fingerprint char(64) NOT NULL,
    expected_fingerprint char(64) NOT NULL,
    payload jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
