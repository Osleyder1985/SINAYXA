-- SINAYXA Issue #2: append-only temporal conflict and decision records.
-- Records are explicitly submitted; no automatic source ingestion is performed.
CREATE TABLE IF NOT EXISTS sinayxa.temporal_conflicts (
    conflict_id varchar(128) PRIMARY KEY,
    event_id varchar(128) NOT NULL
        REFERENCES sinayxa.events(event_id) ON DELETE RESTRICT,
    assertion_refs text[] NOT NULL CHECK (cardinality(assertion_refs) >= 2),
    disputed_component text NOT NULL CHECK (
        disputed_component IN ('START', 'END', 'INTERVAL', 'DURATION', 'DATE', 'TIMEZONE', 'OTHER')
    ),
    classification text NOT NULL CHECK (
        classification IN (
            'DIRECT_CONTRADICTION', 'PRECISION_DIFFERENCE', 'TIMEZONE_DIFFERENCE',
            'SCHEDULE_CHANGE', 'SCOPE_DIFFERENCE', 'UNCLASSIFIED'
        )
    ),
    status text NOT NULL CHECK (
        status IN ('OPEN', 'UNDER_REVIEW', 'RESOLVED', 'REOPENED', 'CLOSED_NO_CONFLICT')
    ),
    recorded_at timestamptz NOT NULL,
    conflict_payload jsonb NOT NULL CHECK (jsonb_typeof(conflict_payload) = 'object'),
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX IF NOT EXISTS temporal_conflicts_event_recorded_idx
    ON sinayxa.temporal_conflicts (event_id, inserted_at, conflict_id);

CREATE TABLE IF NOT EXISTS sinayxa.conflict_decisions (
    decision_id varchar(128) PRIMARY KEY,
    conflict_id varchar(128) NOT NULL
        REFERENCES sinayxa.temporal_conflicts(conflict_id) ON DELETE RESTRICT,
    from_status text NOT NULL CHECK (
        from_status IN ('OPEN', 'UNDER_REVIEW', 'RESOLVED', 'REOPENED', 'CLOSED_NO_CONFLICT')
    ),
    to_status text NOT NULL CHECK (
        to_status IN ('OPEN', 'UNDER_REVIEW', 'RESOLVED', 'REOPENED', 'CLOSED_NO_CONFLICT')
    ),
    assertion_refs text[] NOT NULL CHECK (cardinality(assertion_refs) >= 1),
    supporting_evidence_refs text[] NOT NULL DEFAULT '{}',
    contrary_evidence_refs text[] NOT NULL DEFAULT '{}',
    scope text NOT NULL,
    rationale text NOT NULL,
    limitations text NOT NULL,
    actor_ref varchar(128) NOT NULL,
    decided_at timestamptz NOT NULL,
    assessment_cutoff timestamptz NOT NULL,
    rules_version varchar(128) NOT NULL,
    supersedes_decision_id varchar(128),
    decision_payload jsonb NOT NULL CHECK (jsonb_typeof(decision_payload) = 'object'),
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT conflict_decisions_conflict_time_uq UNIQUE (conflict_id, decided_at),
    CONSTRAINT conflict_decisions_conflict_id_uq UNIQUE (conflict_id, decision_id),
    CONSTRAINT conflict_decisions_supersedes_fk
        FOREIGN KEY (conflict_id, supersedes_decision_id)
        REFERENCES sinayxa.conflict_decisions(conflict_id, decision_id)
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS conflict_decisions_conflict_recorded_idx
    ON sinayxa.conflict_decisions (conflict_id, inserted_at, decided_at);

DROP TRIGGER IF EXISTS temporal_conflicts_append_only ON sinayxa.temporal_conflicts;
CREATE TRIGGER temporal_conflicts_append_only
    BEFORE UPDATE OR DELETE ON sinayxa.temporal_conflicts
    FOR EACH ROW EXECUTE FUNCTION sinayxa.reject_registry_mutation();

DROP TRIGGER IF EXISTS conflict_decisions_append_only ON sinayxa.conflict_decisions;
CREATE TRIGGER conflict_decisions_append_only
    BEFORE UPDATE OR DELETE ON sinayxa.conflict_decisions
    FOR EACH ROW EXECUTE FUNCTION sinayxa.reject_registry_mutation();

-- Use wall-clock insertion timestamps, not transaction start timestamps.
-- This preserves correct registry knowledge-time ordering after long transactions.
ALTER TABLE sinayxa.events
    ALTER COLUMN inserted_at SET DEFAULT clock_timestamp();
ALTER TABLE sinayxa.event_sources
    ALTER COLUMN recorded_at SET DEFAULT clock_timestamp(),
    ALTER COLUMN inserted_at SET DEFAULT clock_timestamp();
ALTER TABLE sinayxa.temporal_assertions
    ALTER COLUMN inserted_at SET DEFAULT clock_timestamp();
ALTER TABLE sinayxa.temporal_conflicts
    ALTER COLUMN inserted_at SET DEFAULT clock_timestamp();
ALTER TABLE sinayxa.conflict_decisions
    ALTER COLUMN inserted_at SET DEFAULT clock_timestamp();

INSERT INTO sinayxa.schema_migrations (migration_id)
VALUES ('issue-2-temporal-conflicts-0002')
ON CONFLICT (migration_id) DO NOTHING;
