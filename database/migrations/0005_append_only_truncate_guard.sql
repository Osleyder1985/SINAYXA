-- SINAYXA Issue #2: block TRUNCATE on every append-only registry table.
CREATE OR REPLACE FUNCTION sinayxa.reject_registry_truncate()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'SINAYXA registry is append-only: TRUNCATE is forbidden on %.%',
        TG_TABLE_SCHEMA, TG_TABLE_NAME
        USING ERRCODE = '55000';
END;
$$;

DROP TRIGGER IF EXISTS events_no_truncate ON sinayxa.events;
CREATE TRIGGER events_no_truncate
    BEFORE TRUNCATE ON sinayxa.events
    FOR EACH STATEMENT EXECUTE FUNCTION sinayxa.reject_registry_truncate();

DROP TRIGGER IF EXISTS event_sources_no_truncate ON sinayxa.event_sources;
CREATE TRIGGER event_sources_no_truncate
    BEFORE TRUNCATE ON sinayxa.event_sources
    FOR EACH STATEMENT EXECUTE FUNCTION sinayxa.reject_registry_truncate();

DROP TRIGGER IF EXISTS temporal_assertions_no_truncate ON sinayxa.temporal_assertions;
CREATE TRIGGER temporal_assertions_no_truncate
    BEFORE TRUNCATE ON sinayxa.temporal_assertions
    FOR EACH STATEMENT EXECUTE FUNCTION sinayxa.reject_registry_truncate();

DROP TRIGGER IF EXISTS temporal_conflicts_no_truncate ON sinayxa.temporal_conflicts;
CREATE TRIGGER temporal_conflicts_no_truncate
    BEFORE TRUNCATE ON sinayxa.temporal_conflicts
    FOR EACH STATEMENT EXECUTE FUNCTION sinayxa.reject_registry_truncate();

DROP TRIGGER IF EXISTS conflict_decisions_no_truncate ON sinayxa.conflict_decisions;
CREATE TRIGGER conflict_decisions_no_truncate
    BEFORE TRUNCATE ON sinayxa.conflict_decisions
    FOR EACH STATEMENT EXECUTE FUNCTION sinayxa.reject_registry_truncate();

DROP TRIGGER IF EXISTS temporal_assessments_no_truncate ON sinayxa.temporal_assessments;
CREATE TRIGGER temporal_assessments_no_truncate
    BEFORE TRUNCATE ON sinayxa.temporal_assessments
    FOR EACH STATEMENT EXECUTE FUNCTION sinayxa.reject_registry_truncate();

DROP TRIGGER IF EXISTS reproducibility_manifests_no_truncate ON sinayxa.reproducibility_manifests;
CREATE TRIGGER reproducibility_manifests_no_truncate
    BEFORE TRUNCATE ON sinayxa.reproducibility_manifests
    FOR EACH STATEMENT EXECUTE FUNCTION sinayxa.reject_registry_truncate();

DROP TRIGGER IF EXISTS source_artifacts_no_truncate ON sinayxa.source_artifacts;
CREATE TRIGGER source_artifacts_no_truncate
    BEFORE TRUNCATE ON sinayxa.source_artifacts
    FOR EACH STATEMENT EXECUTE FUNCTION sinayxa.reject_registry_truncate();

DROP TRIGGER IF EXISTS evidence_artifacts_no_truncate ON sinayxa.evidence_artifacts;
CREATE TRIGGER evidence_artifacts_no_truncate
    BEFORE TRUNCATE ON sinayxa.evidence_artifacts
    FOR EACH STATEMENT EXECUTE FUNCTION sinayxa.reject_registry_truncate();

INSERT INTO sinayxa.schema_migrations (migration_id)
VALUES ('issue-2-append-only-truncate-guard-0005')
ON CONFLICT (migration_id) DO NOTHING;
