-- SINAYXA Issue #2: local content-addressed source and evidence artifacts.
-- Bytes are explicitly supplied by the operator; this migration adds no fetcher.
CREATE TABLE IF NOT EXISTS sinayxa.source_artifacts (
    source_ref varchar(4000) PRIMARY KEY CHECK (length(btrim(source_ref)) > 0),
    source_uri text,
    title text,
    publisher text,
    media_type varchar(255) NOT NULL CHECK (length(btrim(media_type)) > 0),
    content_sha256 varchar(64) NOT NULL CHECK (content_sha256 ~ '^[a-f0-9]{64}$'),
    content_length bigint NOT NULL CHECK (content_length >= 0),
    content_bytes bytea NOT NULL,
    published_at timestamptz,
    license_ref varchar(256) NOT NULL CHECK (length(btrim(license_ref)) > 0),
    usage_status text NOT NULL CHECK (usage_status IN ('SYNTHETIC', 'AUTHORIZED')),
    authorization_ref varchar(128),
    captured_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(metadata) = 'object'),
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT source_artifacts_content_length_ck
        CHECK (octet_length(content_bytes)::bigint = content_length),
    CONSTRAINT source_artifacts_authorization_ck
        CHECK (usage_status <> 'AUTHORIZED' OR length(btrim(COALESCE(authorization_ref, ''))) > 0)
);

CREATE INDEX IF NOT EXISTS source_artifacts_sha256_idx
    ON sinayxa.source_artifacts (content_sha256);

CREATE TABLE IF NOT EXISTS sinayxa.evidence_artifacts (
    evidence_ref varchar(4000) PRIMARY KEY CHECK (length(btrim(evidence_ref)) > 0),
    source_ref varchar(4000)
        REFERENCES sinayxa.source_artifacts(source_ref) ON DELETE RESTRICT,
    evidence_type varchar(128) NOT NULL CHECK (length(btrim(evidence_type)) > 0),
    media_type varchar(255) NOT NULL CHECK (length(btrim(media_type)) > 0),
    content_sha256 varchar(64) NOT NULL CHECK (content_sha256 ~ '^[a-f0-9]{64}$'),
    content_length bigint NOT NULL CHECK (content_length >= 0),
    content_bytes bytea NOT NULL,
    extraction_method varchar(128) NOT NULL CHECK (length(btrim(extraction_method)) > 0),
    extraction_version varchar(128) NOT NULL CHECK (length(btrim(extraction_version)) > 0),
    location_hint text,
    license_ref varchar(256) NOT NULL CHECK (length(btrim(license_ref)) > 0),
    usage_status text NOT NULL CHECK (usage_status IN ('SYNTHETIC', 'AUTHORIZED')),
    authorization_ref varchar(128),
    captured_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(metadata) = 'object'),
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT evidence_artifacts_content_length_ck
        CHECK (octet_length(content_bytes)::bigint = content_length),
    CONSTRAINT evidence_artifacts_authorization_ck
        CHECK (usage_status <> 'AUTHORIZED' OR length(btrim(COALESCE(authorization_ref, ''))) > 0)
);

CREATE INDEX IF NOT EXISTS evidence_artifacts_sha256_idx
    ON sinayxa.evidence_artifacts (content_sha256);
CREATE INDEX IF NOT EXISTS evidence_artifacts_source_idx
    ON sinayxa.evidence_artifacts (source_ref, inserted_at);

DROP TRIGGER IF EXISTS source_artifacts_append_only ON sinayxa.source_artifacts;
CREATE TRIGGER source_artifacts_append_only
    BEFORE UPDATE OR DELETE ON sinayxa.source_artifacts
    FOR EACH ROW EXECUTE FUNCTION sinayxa.reject_registry_mutation();

DROP TRIGGER IF EXISTS evidence_artifacts_append_only ON sinayxa.evidence_artifacts;
CREATE TRIGGER evidence_artifacts_append_only
    BEFORE UPDATE OR DELETE ON sinayxa.evidence_artifacts
    FOR EACH ROW EXECUTE FUNCTION sinayxa.reject_registry_mutation();

INSERT INTO sinayxa.schema_migrations (migration_id)
VALUES ('issue-2-source-evidence-artifacts-0004')
ON CONFLICT (migration_id) DO NOTHING;
