-- SINAYXA Issue #2: immutable temporal assessments and reproducibility manifests.
-- Only explicit operator-requested assessments are recorded; no automatic analysis runs.
CREATE TABLE IF NOT EXISTS sinayxa.temporal_assessments (
    assessment_id varchar(128) PRIMARY KEY,
    event_id varchar(128) NOT NULL
        REFERENCES sinayxa.events(event_id) ON DELETE RESTRICT,
    assessment_cutoff timestamptz NOT NULL,
    assertion_refs text[] NOT NULL,
    conflict_decision_refs text[] NOT NULL DEFAULT '{}',
    derived_temporal_state text NOT NULL CHECK (
        derived_temporal_state IN ('PAST', 'ONGOING', 'FUTURE', 'UNDETERMINED')
    ),
    rules_version varchar(128) NOT NULL,
    software_version varchar(128) NOT NULL,
    recorded_at timestamptz NOT NULL,
    assessment_payload jsonb NOT NULL CHECK (jsonb_typeof(assessment_payload) = 'object'),
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX IF NOT EXISTS temporal_assessments_event_recorded_idx
    ON sinayxa.temporal_assessments (event_id, inserted_at, assessment_id);

CREATE TABLE IF NOT EXISTS sinayxa.reproducibility_manifests (
    manifest_id varchar(128) PRIMARY KEY,
    assessment_id varchar(128) NOT NULL
        REFERENCES sinayxa.temporal_assessments(assessment_id) ON DELETE RESTRICT,
    assessment_cutoff timestamptz NOT NULL,
    contract_version varchar(32) NOT NULL CHECK (contract_version = '1.0.0'),
    schema_sha256 varchar(64) NOT NULL CHECK (schema_sha256 ~ '^[a-f0-9]{64}$'),
    assertion_versions jsonb NOT NULL CHECK (jsonb_typeof(assertion_versions) = 'array'),
    excluded_assertions jsonb NOT NULL CHECK (jsonb_typeof(excluded_assertions) = 'array'),
    evidence_refs text[] NOT NULL DEFAULT '{}',
    conflict_decision_refs text[] NOT NULL DEFAULT '{}',
    rules_version varchar(128) NOT NULL,
    rules_sha256 varchar(64) NOT NULL CHECK (rules_sha256 ~ '^[a-f0-9]{64}$'),
    tzdb_version varchar(128) NOT NULL,
    software_version varchar(128) NOT NULL,
    result_sha256 varchar(64) NOT NULL CHECK (result_sha256 ~ '^[a-f0-9]{64}$'),
    canonicalization varchar(16) NOT NULL CHECK (canonicalization = 'RFC8785'),
    reproducibility_status text NOT NULL CHECK (
        reproducibility_status IN ('REPRODUCIBLE', 'PARTIALLY_REPRODUCIBLE', 'NOT_REPRODUCIBLE')
    ),
    missing_components text[] NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL,
    manifest_payload jsonb NOT NULL CHECK (jsonb_typeof(manifest_payload) = 'object'),
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX IF NOT EXISTS reproducibility_manifests_assessment_recorded_idx
    ON sinayxa.reproducibility_manifests (assessment_id, inserted_at, manifest_id);

DROP TRIGGER IF EXISTS temporal_assessments_append_only ON sinayxa.temporal_assessments;
CREATE TRIGGER temporal_assessments_append_only
    BEFORE UPDATE OR DELETE ON sinayxa.temporal_assessments
    FOR EACH ROW EXECUTE FUNCTION sinayxa.reject_registry_mutation();

DROP TRIGGER IF EXISTS reproducibility_manifests_append_only ON sinayxa.reproducibility_manifests;
CREATE TRIGGER reproducibility_manifests_append_only
    BEFORE UPDATE OR DELETE ON sinayxa.reproducibility_manifests
    FOR EACH ROW EXECUTE FUNCTION sinayxa.reject_registry_mutation();

INSERT INTO sinayxa.schema_migrations (migration_id)
VALUES ('issue-2-temporal-assessments-manifests-0003')
ON CONFLICT (migration_id) DO NOTHING;
