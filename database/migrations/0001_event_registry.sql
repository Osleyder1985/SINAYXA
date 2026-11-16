-- SINAYXA Issue #2: local, append-only event registry (PostgreSQL 18+).
-- This migration stores only explicitly submitted records. It performs no capture.
CREATE SCHEMA IF NOT EXISTS sinayxa;

CREATE TABLE IF NOT EXISTS sinayxa.schema_migrations (
    migration_id text PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT transaction_timestamp()
);

CREATE TABLE IF NOT EXISTS sinayxa.events (
    event_id varchar(128) PRIMARY KEY,
    description varchar(4000) NOT NULL CHECK (length(btrim(description)) > 0),
    affected_asset_refs text[] NOT NULL DEFAULT '{}',
    source_refs text[] NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL,
    contract_version text NOT NULL CHECK (contract_version = '1.0.0'),
    event_payload jsonb NOT NULL,
    inserted_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    CONSTRAINT events_payload_is_object CHECK (jsonb_typeof(event_payload) = 'object')
);

CREATE TABLE IF NOT EXISTS sinayxa.event_sources (
    event_id varchar(128) NOT NULL REFERENCES sinayxa.events(event_id) ON DELETE RESTRICT,
    source_ref varchar(4000) NOT NULL CHECK (length(btrim(source_ref)) > 0),
    inserted_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (event_id, source_ref)
);

CREATE TABLE IF NOT EXISTS sinayxa.temporal_assertions (
    temporal_assertion_id varchar(128) PRIMARY KEY,
    event_id varchar(128) NOT NULL,
    version integer NOT NULL CHECK (version > 0),
    temporal_role text NOT NULL CHECK (temporal_role IN ('ACTUAL', 'SCHEDULED', 'ESTIMATED', 'UNKNOWN')),
    precision text NOT NULL CHECK (precision IN ('YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND', 'RANGE', 'UNKNOWN')),
    interval_start jsonb NOT NULL,
    interval_end jsonb NOT NULL,
    approximation boolean NOT NULL,
    original_value text,
    original_timezone text,
    original_offset text,
    normalized_start_utc timestamptz,
    normalized_end_utc timestamptz,
    source_ref varchar(4000),
    evidence_ref varchar(4000),
    retrieved_at timestamptz,
    recorded_at timestamptz NOT NULL,
    supersedes_assertion_id varchar(4000),
    published_at timestamptz,
    first_observed_at timestamptz,
    assertion_payload jsonb NOT NULL,
    inserted_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    CONSTRAINT temporal_assertions_event_fk
        FOREIGN KEY (event_id) REFERENCES sinayxa.events(event_id) ON DELETE RESTRICT,
    CONSTRAINT temporal_assertions_version_uq UNIQUE (event_id, version),
    CONSTRAINT temporal_assertions_event_id_uq UNIQUE (event_id, temporal_assertion_id),
    CONSTRAINT temporal_assertions_supersedes_fk
        FOREIGN KEY (event_id, supersedes_assertion_id)
        REFERENCES sinayxa.temporal_assertions(event_id, temporal_assertion_id)
        ON DELETE RESTRICT,
    CONSTRAINT temporal_assertions_payload_is_object
        CHECK (jsonb_typeof(assertion_payload) = 'object')
);

CREATE INDEX IF NOT EXISTS temporal_assertions_event_recorded_idx
    ON sinayxa.temporal_assertions (event_id, recorded_at, version);

CREATE OR REPLACE FUNCTION sinayxa.reject_registry_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'SINAYXA event registry is append-only: % is forbidden on %.%',
        TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME
        USING ERRCODE = '55000';
END;
$$;

DROP TRIGGER IF EXISTS events_append_only ON sinayxa.events;
CREATE TRIGGER events_append_only
    BEFORE UPDATE OR DELETE ON sinayxa.events
    FOR EACH ROW EXECUTE FUNCTION sinayxa.reject_registry_mutation();

DROP TRIGGER IF EXISTS temporal_assertions_append_only ON sinayxa.temporal_assertions;
CREATE TRIGGER temporal_assertions_append_only
    BEFORE UPDATE OR DELETE ON sinayxa.temporal_assertions
    FOR EACH ROW EXECUTE FUNCTION sinayxa.reject_registry_mutation();

INSERT INTO sinayxa.schema_migrations (migration_id)
VALUES ('issue-2-event-registry-0001')
ON CONFLICT (migration_id) DO NOTHING;
