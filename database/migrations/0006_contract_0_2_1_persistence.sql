-- SINAYXA Issue #153: typed persistence for source-evidence contract 0.2.1.
-- Additive migration over the existing Issue #2 registry. No ingestion or capture.
-- JSONB is limited to contract-defined nested structures/arrays; entity identity,
-- versioning, timestamps and relationships are represented by typed columns/FKs.

CREATE TABLE sinayxa.contract_packages (
    package_id varchar(160) PRIMARY KEY CHECK (package_id ~ '^[A-Za-z0-9][A-Za-z0-9._:-]*$'),
    event_id varchar(128) NOT NULL REFERENCES sinayxa.events(event_id) ON DELETE RESTRICT,
    contract_version text NOT NULL CHECK (contract_version = '0.2.1'),
    created_at timestamptz NOT NULL,
    schema_sha256 varchar(64) NOT NULL CHECK (schema_sha256 ~ '^[a-f0-9]{64}$'),
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE sinayxa.claims (
    claim_id varchar(160) NOT NULL,
    claim_version_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    claim_version integer NOT NULL CHECK (claim_version > 0),
    proposition text NOT NULL CHECK (length(btrim(proposition)) > 0),
    scope text NOT NULL CHECK (length(btrim(scope)) > 0),
    valid_time_start timestamptz,
    valid_time_end timestamptz,
    recorded_at timestamptz NOT NULL,
    supersedes_claim_version_id varchar(160),
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (claim_id, claim_version_id),
    UNIQUE (claim_id, claim_version),
    FOREIGN KEY (claim_id, supersedes_claim_version_id)
        REFERENCES sinayxa.claims(claim_id, claim_version_id) ON DELETE RESTRICT,
    CHECK (supersedes_claim_version_id IS NULL OR supersedes_claim_version_id <> claim_version_id)
);

CREATE TABLE sinayxa.claim_components (
    claim_component_id varchar(160) NOT NULL,
    claim_component_version_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    claim_id varchar(160) NOT NULL,
    claim_version_id varchar(160) NOT NULL,
    component_key text NOT NULL CHECK (component_key IN ('entity','date','amount','approval','execution','intent','whole_claim','other')),
    proposition_fragment text NOT NULL CHECK (length(btrim(proposition_fragment)) > 0),
    scope text NOT NULL CHECK (length(btrim(scope)) > 0),
    version integer NOT NULL CHECK (version > 0),
    recorded_at timestamptz NOT NULL,
    supersedes_component_version_id varchar(160),
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (claim_component_id, claim_component_version_id),
    UNIQUE (claim_component_id, version),
    FOREIGN KEY (claim_id, claim_version_id)
        REFERENCES sinayxa.claims(claim_id, claim_version_id) ON DELETE RESTRICT,
    FOREIGN KEY (claim_component_id, supersedes_component_version_id)
        REFERENCES sinayxa.claim_components(claim_component_id, claim_component_version_id) ON DELETE RESTRICT,
    CHECK (supersedes_component_version_id IS NULL OR supersedes_component_version_id <> claim_component_version_id)
);

CREATE TABLE sinayxa.contract_sources (
    source_id varchar(160) PRIMARY KEY CHECK (source_id ~ '^src_[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'),
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    event_id varchar(128) NOT NULL REFERENCES sinayxa.events(event_id) ON DELETE RESTRICT,
    registry_source_ref varchar(4000),
    created_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL,
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    FOREIGN KEY (event_id, registry_source_ref) REFERENCES sinayxa.event_sources(event_id, source_ref) ON DELETE RESTRICT
);

CREATE TABLE sinayxa.source_versions (
    source_version_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    source_id varchar(160) NOT NULL REFERENCES sinayxa.contract_sources(source_id) ON DELETE RESTRICT,
    version_label text NOT NULL CHECK (length(btrim(version_label)) > 0),
    version_sequence integer NOT NULL CHECK (version_sequence > 0),
    published_at timestamptz,
    first_detected_at timestamptz,
    first_publicly_observed_at timestamptz,
    original_timestamps jsonb NOT NULL CHECK (jsonb_typeof(original_timestamps) = 'array'),
    retrieved_at timestamptz,
    canonical_reference text,
    content_reference text,
    content_hash text,
    hash_algorithm text CHECK (hash_algorithm IS NULL OR hash_algorithm = 'SHA-256'),
    supersedes_source_version_id varchar(160),
    recorded_at timestamptz NOT NULL,
    artifact_source_ref varchar(4000) REFERENCES sinayxa.source_artifacts(source_ref) ON DELETE RESTRICT,
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (source_id, version_sequence),
    UNIQUE (source_id, source_version_id),
    FOREIGN KEY (source_id, supersedes_source_version_id)
        REFERENCES sinayxa.source_versions(source_id, source_version_id) ON DELETE RESTRICT,
    CHECK (content_hash IS NULL OR length(btrim(content_hash)) > 0)
);

CREATE TABLE sinayxa.identity_assessments (
    identity_assessment_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    source_id varchar(160) NOT NULL REFERENCES sinayxa.contract_sources(source_id) ON DELETE RESTRICT,
    assessment_cutoff timestamptz NOT NULL,
    identity text NOT NULL CHECK (identity IN ('IDENTIFICADA','ANÓNIMA_PARA_EL_PÚBLICO','ANÓNIMA_PARA_SINAYXA','SEUDÓNIMA','DESCONOCIDA')),
    anonymous_to_public boolean NOT NULL,
    anonymous_to_publisher boolean NOT NULL,
    anonymous_to_sinayxa boolean NOT NULL,
    identity_verified_by_publisher boolean NOT NULL,
    identity_verified_by_sinayxa boolean NOT NULL,
    verification_evidence_refs text[] NOT NULL DEFAULT '{}',
    limitations text[] NOT NULL DEFAULT '{}',
    recorded_at timestamptz NOT NULL,
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE sinayxa.evaluation_units (
    assessment_unit_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    claim_id varchar(160) NOT NULL,
    claim_component_id varchar(160) NOT NULL,
    source_id varchar(160) NOT NULL,
    source_version_id varchar(160) NOT NULL,
    access_path text NOT NULL CHECK (length(btrim(access_path)) > 0),
    access_status text NOT NULL CHECK (access_status IN ('PÚBLICO_LEGÍTIMO','PRIVADO_AUTORIZADO','SOSPECHA_DE_ACCESO_NO_AUTORIZADO','NO_DETERMINADO')),
    assessment_cutoff timestamptz NOT NULL,
    methodology_version text NOT NULL CHECK (length(btrim(methodology_version)) > 0),
    source_type text NOT NULL CHECK (source_type IN ('PRIMARIA','SECUNDARIA','TERCIARIA','DESCONOCIDA')),
    source_subtype text NOT NULL CHECK (source_subtype IN ('REGISTRO_ORIGINAL','TESTIMONIO_PRIMERA_MANO','INVESTIGACION_SECUNDARIA','ANALISIS_TECNICO','COMENTARIO','COMPILACION','REPRODUCCION')),
    knowledge_basis text NOT NULL CHECK (knowledge_basis IN ('OBSERVACIÓN_DIRECTA','REGISTRO_ORIGINAL','ACCESO_DIRECTO_DECLARADO','TESTIMONIO_DE_TERCEROS','DOCUMENTO_DE_TERCEROS','ANÁLISIS_REPRODUCIBLE','OPINIÓN_O_INTERPRETACIÓN','REPRODUCCIÓN_SIN_VERIFICACIÓN_PROPIA','DESCONOCIDA')),
    institutional_character text NOT NULL CHECK (institutional_character IN ('OFICIAL','NO_INSTITUCIONAL','DESCONOCIDO')),
    dissemination text NOT NULL CHECK (dissemination IN ('ORIGINAL','SINDICADA','REPUBLICADA','TRADUCIDA','RESUMIDA','ANÁLISIS_PROPIO','COMPILACIÓN','DESCONOCIDA')),
    claim_version_id varchar(160) NOT NULL,
    claim_component_version_id varchar(160) NOT NULL,
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    FOREIGN KEY (claim_id, claim_version_id) REFERENCES sinayxa.claims(claim_id, claim_version_id) ON DELETE RESTRICT,
    FOREIGN KEY (claim_component_id, claim_component_version_id) REFERENCES sinayxa.claim_components(claim_component_id, claim_component_version_id) ON DELETE RESTRICT,
    FOREIGN KEY (source_id, source_version_id) REFERENCES sinayxa.source_versions(source_id, source_version_id) ON DELETE RESTRICT
);

CREATE TABLE sinayxa.contract_evidence_items (
    evidence_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    source_version_id varchar(160) REFERENCES sinayxa.source_versions(source_version_id) ON DELETE RESTRICT,
    evidence_kind text NOT NULL CHECK (evidence_kind IN ('DOCUMENTO','REGISTRO','DECLARACIÓN','OBSERVACIÓN','DATASET','ANÁLISIS','OTRO')),
    information_nature text NOT NULL CHECK (information_nature IN ('AFIRMACIÓN','INDICIO','RUMOR','POSIBLE_FILTRACIÓN','PUBLICACIÓN_OFICIAL','HECHO_OBSERVADO')),
    factor_dimensions jsonb NOT NULL CHECK (jsonb_typeof(factor_dimensions) = 'array'),
    content_reference text,
    integrity_check jsonb NOT NULL CHECK (jsonb_typeof(integrity_check) = 'object'),
    authenticity_status text NOT NULL CHECK (authenticity_status IN ('NO_APLICA','NO_VERIFICADA','AUTENTICADA','DISPUTADA','AUTENTICIDAD_REFUTADA')),
    access_status text NOT NULL CHECK (access_status IN ('PÚBLICO_LEGÍTIMO','PRIVADO_AUTORIZADO','SOSPECHA_DE_ACCESO_NO_AUTORIZADO','NO_DETERMINADO')),
    recorded_at timestamptz NOT NULL,
    artifact_evidence_ref varchar(4000) REFERENCES sinayxa.evidence_artifacts(evidence_ref) ON DELETE RESTRICT,
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE sinayxa.evidence_availability (
    availability_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    evidence_id varchar(160) NOT NULL REFERENCES sinayxa.contract_evidence_items(evidence_id) ON DELETE RESTRICT,
    assessment_unit_id varchar(160) NOT NULL REFERENCES sinayxa.evaluation_units(assessment_unit_id) ON DELETE RESTRICT,
    claim_id varchar(160) NOT NULL,
    claim_component_id varchar(160) NOT NULL,
    claim_version_id varchar(160) NOT NULL,
    claim_component_version_id varchar(160) NOT NULL,
    available_at timestamptz,
    availability_basis text NOT NULL CHECK (availability_basis IN ('SINAYXA_OBSERVATION','INDEPENDENT_ARCHIVE','SOURCE_STATED','UNKNOWN')),
    availability_reference text,
    recorded_at timestamptz NOT NULL,
    archive_attestation_id varchar(160),
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    FOREIGN KEY (claim_id, claim_version_id) REFERENCES sinayxa.claims(claim_id, claim_version_id) ON DELETE RESTRICT,
    FOREIGN KEY (claim_component_id, claim_component_version_id) REFERENCES sinayxa.claim_components(claim_component_id, claim_component_version_id) ON DELETE RESTRICT
);

CREATE TABLE sinayxa.claim_evidence_links (
    link_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    claim_id varchar(160) NOT NULL,
    claim_component_id varchar(160) NOT NULL,
    evidence_id varchar(160) NOT NULL REFERENCES sinayxa.contract_evidence_items(evidence_id) ON DELETE RESTRICT,
    evidence_role text NOT NULL CHECK (evidence_role IN ('SUPPORTING','CONTRARY','CONTEXTUAL')),
    scope_note text NOT NULL CHECK (length(btrim(scope_note)) > 0),
    limitations text[] NOT NULL DEFAULT '{}',
    claim_version_id varchar(160) NOT NULL,
    claim_component_version_id varchar(160) NOT NULL,
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    FOREIGN KEY (claim_id, claim_version_id) REFERENCES sinayxa.claims(claim_id, claim_version_id) ON DELETE RESTRICT,
    FOREIGN KEY (claim_component_id, claim_component_version_id) REFERENCES sinayxa.claim_components(claim_component_id, claim_component_version_id) ON DELETE RESTRICT
);

CREATE TABLE sinayxa.provenance_nodes (
    node_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    node_type text NOT NULL CHECK (node_type IN ('SOURCE_VERSION','EVIDENCE_ITEM','DOCUMENT','DATASET','INTERMEDIARY','INFORMANT','UNKNOWN_ORIGIN')),
    entity_ref text,
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE sinayxa.provenance_edges (
    edge_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    dependent_node_id varchar(160) NOT NULL REFERENCES sinayxa.provenance_nodes(node_id) ON DELETE RESTRICT,
    origin_node_id varchar(160) NOT NULL REFERENCES sinayxa.provenance_nodes(node_id) ON DELETE RESTRICT,
    relation_type text NOT NULL CHECK (relation_type IN ('ORIGEN_DIRECTO','CITA_DE','SINDICADA_DE','DERIVADA_DE','DOCUMENTO_COMÚN','CONTACTO_COMÚN','ORIGEN_NO_DETERMINADO','ANÁLISIS_SEPARADO_SOBRE_DATOS_COMUNES')),
    claim_component_id varchar(160) NOT NULL,
    evidence_refs text[] NOT NULL DEFAULT '{}',
    recorded_at timestamptz NOT NULL,
    valid_from timestamptz,
    valid_to timestamptz,
    claim_component_version_id varchar(160) NOT NULL,
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    FOREIGN KEY (claim_component_id, claim_component_version_id) REFERENCES sinayxa.claim_components(claim_component_id, claim_component_version_id) ON DELETE RESTRICT
);

CREATE TABLE sinayxa.factor_assessments (
    factor_assessment_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    assessment_unit_id varchar(160) NOT NULL REFERENCES sinayxa.evaluation_units(assessment_unit_id) ON DELETE RESTRICT,
    dimension text NOT NULL CHECK (dimension IN ('RELATION_WITH_FACT','ACCESS_AND_PROXIMITY','SUBJECT_COMPETENCE','TRANSPARENCY_TRACEABILITY','RELEVANT_ACCURACY_HISTORY','CORRECTIONS_ACCOUNTABILITY','INCENTIVES_CONFLICTS','INTERNAL_CONSISTENCY','CONTRARY_EVIDENCE','TEMPORAL_ADEQUACY')),
    status text NOT NULL CHECK (status IN ('SUSTENTADA','LIMITADA','DESFAVORABLE','DESCONOCIDA','NO_APLICA')),
    justification text NOT NULL CHECK (length(btrim(justification)) > 0),
    supporting_evidence_refs text[] NOT NULL DEFAULT '{}',
    contrary_evidence_refs text[] NOT NULL DEFAULT '{}',
    limitations text[] NOT NULL DEFAULT '{}',
    assessed_at timestamptz NOT NULL,
    methodology_version text NOT NULL CHECK (length(btrim(methodology_version)) > 0),
    human_review_status text NOT NULL CHECK (human_review_status IN ('PENDING','REVIEWED','REJECTED')),
    reviewed_at timestamptz,
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE sinayxa.independence_assessments (
    independence_assessment_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    claim_id varchar(160) NOT NULL,
    claim_component_id varchar(160) NOT NULL,
    assessment_unit_ids text[] NOT NULL DEFAULT '{}',
    status text NOT NULL CHECK (status IN ('INDEPENDIENTE','DEPENDIENTE','DESCONOCIDA')),
    supporting_evidence_refs text[] NOT NULL DEFAULT '{}',
    dependency_edge_refs text[] NOT NULL DEFAULT '{}',
    rationale text NOT NULL CHECK (length(btrim(rationale)) > 0),
    limitations text[] NOT NULL DEFAULT '{}',
    assessment_cutoff timestamptz NOT NULL,
    methodology_version text NOT NULL CHECK (length(btrim(methodology_version)) > 0),
    human_review_status text NOT NULL CHECK (human_review_status IN ('PENDING','REVIEWED','REJECTED')),
    reviewed_at timestamptz,
    claim_version_id varchar(160) NOT NULL,
    claim_component_version_id varchar(160) NOT NULL,
    independent_path_edge_refs text[] NOT NULL DEFAULT '{}',
    unresolved_provenance_edge_refs text[],
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    FOREIGN KEY (claim_id, claim_version_id) REFERENCES sinayxa.claims(claim_id, claim_version_id) ON DELETE RESTRICT,
    FOREIGN KEY (claim_component_id, claim_component_version_id) REFERENCES sinayxa.claim_components(claim_component_id, claim_component_version_id) ON DELETE RESTRICT
);

CREATE TABLE sinayxa.claim_assessments (
    claim_assessment_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    claim_id varchar(160) NOT NULL,
    claim_component_id varchar(160) NOT NULL,
    evidentiary_status text NOT NULL CHECK (evidentiary_status IN ('NO_CORROBORADA','PARCIALMENTE_CORROBORADA','CORROBORADA','CONTRADICHA','REFUTADA','NO_RESUELTA')),
    attribution_status text NOT NULL CHECK (attribution_status IN ('ATRIBUIDA','NO_ATRIBUIDA','NO_DETERMINADA')),
    supporting_evidence_refs text[] NOT NULL DEFAULT '{}',
    contrary_evidence_refs text[] NOT NULL DEFAULT '{}',
    independence_assessment_refs text[] NOT NULL DEFAULT '{}',
    alternatives text[] NOT NULL DEFAULT '{}',
    uncertainty text NOT NULL CHECK (length(btrim(uncertainty)) > 0),
    limitations text[] NOT NULL DEFAULT '{}',
    assessment_cutoff timestamptz NOT NULL,
    methodology_version text NOT NULL CHECK (length(btrim(methodology_version)) > 0),
    human_review_status text NOT NULL CHECK (human_review_status IN ('PENDING','REVIEWED','REJECTED')),
    supersedes_assessment_id varchar(160) REFERENCES sinayxa.claim_assessments(claim_assessment_id) ON DELETE RESTRICT,
    claim_version_id varchar(160) NOT NULL,
    claim_component_version_id varchar(160) NOT NULL,
    reviewed_at timestamptz,
    rationale text NOT NULL CHECK (length(btrim(rationale)) > 0),
    supported_scope text,
    unsupported_scope text,
    corroboration_basis text NOT NULL CHECK (corroboration_basis IN ('EVIDENCIA_PRIMARIA_DIRECTA','CORROBORACION_INDEPENDIENTE','AMBAS','NO_APLICA')),
    assessed_at timestamptz,
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    FOREIGN KEY (claim_id, claim_version_id) REFERENCES sinayxa.claims(claim_id, claim_version_id) ON DELETE RESTRICT,
    FOREIGN KEY (claim_component_id, claim_component_version_id) REFERENCES sinayxa.claim_components(claim_component_id, claim_component_version_id) ON DELETE RESTRICT
);

CREATE TABLE sinayxa.retention_records (
    retention_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    subject_ref varchar(160) NOT NULL,
    content_retained boolean NOT NULL,
    legal_basis_status text NOT NULL CHECK (legal_basis_status IN ('VERIFIED','PENDING_REVIEW','NOT_ESTABLISHED','NOT_REQUIRED')),
    purpose text NOT NULL CHECK (length(btrim(purpose)) > 0),
    responsible_role text NOT NULL CHECK (length(btrim(responsible_role)) > 0),
    review_at timestamptz NOT NULL,
    expires_at timestamptz,
    disposition text NOT NULL CHECK (disposition IN ('RETAIN','REFERENCE_ONLY','DELETE_PENDING','DELETED','RESTRICTED')),
    previous_disposition text CHECK (previous_disposition IS NULL OR previous_disposition IN ('RETAIN','REFERENCE_ONLY','DELETE_PENDING','DELETED','RESTRICTED')),
    authorization_reference text,
    recorded_at timestamptz NOT NULL,
    copy_scope_ids text[] NOT NULL DEFAULT '{}',
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE sinayxa.audit_events (
    audit_event_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    subject_ref varchar(160) NOT NULL,
    action text NOT NULL CHECK (action IN ('CREATED','UPDATED','SUPERSEDED','RETENTION_SET','REFERENCE_ONLY','RESTRICTED','RETENTION_REVIEWED','DELETION_REQUESTED','DELETED','ACCESS_DENIED','COPY_DISCOVERED','COPY_DELETION_REQUESTED','COPY_DELETED')),
    actor_role text NOT NULL CHECK (length(btrim(actor_role)) > 0),
    occurred_at timestamptz NOT NULL,
    reason text NOT NULL CHECK (length(btrim(reason)) > 0),
    retention_id varchar(160) REFERENCES sinayxa.retention_records(retention_id) ON DELETE RESTRICT,
    from_disposition text CHECK (from_disposition IS NULL OR from_disposition IN ('RETAIN','REFERENCE_ONLY','DELETE_PENDING','DELETED','RESTRICTED')),
    to_disposition text CHECK (to_disposition IS NULL OR to_disposition IN ('RETAIN','REFERENCE_ONLY','DELETE_PENDING','DELETED','RESTRICTED')),
    copy_id varchar(160),
    from_copy_state text CHECK (from_copy_state IS NULL OR from_copy_state IN ('PRESENT','DELETE_PENDING','DELETED')),
    to_copy_state text CHECK (to_copy_state IS NULL OR to_copy_state IN ('PRESENT','DELETE_PENDING','DELETED')),
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE sinayxa.archive_attestations (
    archive_attestation_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    evidence_id varchar(160) NOT NULL REFERENCES sinayxa.contract_evidence_items(evidence_id) ON DELETE RESTRICT,
    source_version_id varchar(160) NOT NULL REFERENCES sinayxa.source_versions(source_version_id) ON DELETE RESTRICT,
    captured_content_hash text NOT NULL,
    hash_algorithm text NOT NULL CHECK (hash_algorithm = 'SHA-256'),
    archive_service text NOT NULL CHECK (length(btrim(archive_service)) > 0),
    capture_record_reference text NOT NULL CHECK (length(btrim(capture_record_reference)) > 0),
    captured_at timestamptz NOT NULL,
    imported_at timestamptz,
    recorded_at timestamptz NOT NULL,
    integrity_result text NOT NULL CHECK (integrity_result IN ('MATCH','MISMATCH','NOT_CHECKED','UNAVAILABLE')),
    capture_record_verified boolean NOT NULL,
    content_authenticity text NOT NULL CHECK (content_authenticity IN ('UNKNOWN','NOT_ASSESSED')),
    content_truth text NOT NULL CHECK (content_truth IN ('UNKNOWN','NOT_ASSESSED')),
    verification_method text CHECK (verification_method IS NULL OR verification_method IN ('ARCHIVE_API_RETRIEVAL','SIGNATURE_OR_DIGEST_CHECK','INDEPENDENT_RECORD_REVIEW','OTHER')),
    verified_at timestamptz,
    verified_by_role text,
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

ALTER TABLE sinayxa.evidence_availability
    ADD CONSTRAINT evidence_availability_archive_fk
    FOREIGN KEY (archive_attestation_id)
    REFERENCES sinayxa.archive_attestations(archive_attestation_id) ON DELETE RESTRICT;

CREATE TABLE sinayxa.retention_copy_records (
    copy_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    retention_id varchar(160) NOT NULL REFERENCES sinayxa.retention_records(retention_id) ON DELETE RESTRICT,
    subject_ref varchar(160) NOT NULL,
    copy_kind text NOT NULL CHECK (copy_kind IN ('PRIMARY','REPLICA','CACHE','EXPORT','TEMPORARY','DERIVATIVE','BACKUP')),
    parent_copy_id varchar(160) REFERENCES sinayxa.retention_copy_records(copy_id) ON DELETE RESTRICT,
    state text NOT NULL CHECK (state IN ('PRESENT','DELETE_PENDING','DELETED')),
    recorded_at timestamptz NOT NULL,
    verified_at timestamptz,
    verification_reference text,
    scheduled_disposition_at timestamptz,
    backup_expiration_policy_ref text,
    previous_state text CHECK (previous_state IS NULL OR previous_state IN ('PRESENT','DELETE_PENDING','DELETED')),
    transition_event_ref varchar(160) NOT NULL REFERENCES sinayxa.audit_events(audit_event_id) ON DELETE RESTRICT,
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE sinayxa.contract_migration_records (
    migration_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    source_contract_version text NOT NULL CHECK (length(btrim(source_contract_version)) > 0),
    target_contract_version text NOT NULL CHECK (length(btrim(target_contract_version)) > 0),
    migrator_version text NOT NULL CHECK (length(btrim(migrator_version)) > 0),
    executed_at timestamptz NOT NULL,
    input_sha256 text NOT NULL CHECK (input_sha256 ~ '^[a-f0-9]{64}$'),
    output_sha256 text NOT NULL CHECK (output_sha256 ~ '^[a-f0-9]{64}$'),
    rules_applied text[] NOT NULL DEFAULT '{}',
    result text NOT NULL CHECK (result IN ('PASS','REJECTED')),
    loss_report text[] NOT NULL DEFAULT '{}',
    source_snapshot_ref text NOT NULL CHECK (length(btrim(source_snapshot_ref)) > 0),
    target_snapshot_ref text NOT NULL CHECK (length(btrim(target_snapshot_ref)) > 0),
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE sinayxa.analysis_processes (
    process_id varchar(160) PRIMARY KEY,
    package_id varchar(160) NOT NULL REFERENCES sinayxa.contract_packages(package_id) ON DELETE RESTRICT,
    dataset_origin_id text NOT NULL CHECK (length(btrim(dataset_origin_id)) > 0),
    claim_component_version_id varchar(160) NOT NULL REFERENCES sinayxa.claim_components(claim_component_version_id) ON DELETE RESTRICT,
    method_reference text NOT NULL CHECK (length(btrim(method_reference)) > 0),
    output_evidence_ref varchar(160) NOT NULL REFERENCES sinayxa.contract_evidence_items(evidence_id) ON DELETE RESTRICT,
    available_at timestamptz NOT NULL,
    assessment_cutoff timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL,
    inserted_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

-- Indexes support exact-version and knowledge-cutoff retrieval.
CREATE INDEX contract_packages_event_idx ON sinayxa.contract_packages (event_id, inserted_at, package_id);
CREATE INDEX contract_sources_event_idx ON sinayxa.contract_sources (event_id, inserted_at, source_id);
CREATE INDEX claims_asof_idx ON sinayxa.claims (claim_id, inserted_at, claim_version);
CREATE INDEX claim_components_asof_idx ON sinayxa.claim_components (claim_id, claim_component_id, inserted_at, version);
CREATE INDEX source_versions_asof_idx ON sinayxa.source_versions (source_id, inserted_at, version_sequence);
CREATE INDEX evaluation_units_cutoff_idx ON sinayxa.evaluation_units (claim_id, claim_component_id, assessment_cutoff);
CREATE INDEX evidence_availability_asof_idx ON sinayxa.evidence_availability (claim_id, claim_component_id, inserted_at, available_at);
CREATE INDEX claim_assessments_asof_idx ON sinayxa.claim_assessments (claim_id, claim_component_id, inserted_at, assessment_cutoff);
CREATE INDEX provenance_edges_component_idx ON sinayxa.provenance_edges (claim_component_id, claim_component_version_id, inserted_at);

-- All contract records are append-only. Corrections are new versions/records.
DO $$
DECLARE
    table_name text;
BEGIN
    FOREACH table_name IN ARRAY ARRAY[
        'contract_packages','claims','claim_components','contract_sources','source_versions',
        'identity_assessments','evaluation_units','contract_evidence_items','evidence_availability',
        'claim_evidence_links','provenance_nodes','provenance_edges','factor_assessments',
        'independence_assessments','claim_assessments','retention_records','audit_events',
        'archive_attestations','retention_copy_records','contract_migration_records','analysis_processes'
    ]
    LOOP
        EXECUTE format('CREATE TRIGGER %I_append_only BEFORE UPDATE OR DELETE ON sinayxa.%I FOR EACH ROW EXECUTE FUNCTION sinayxa.reject_registry_mutation()', table_name, table_name);
        EXECUTE format('CREATE TRIGGER %I_no_truncate BEFORE TRUNCATE ON sinayxa.%I FOR EACH STATEMENT EXECUTE FUNCTION sinayxa.reject_registry_mutation()', table_name, table_name);
    END LOOP;
END;
$$;

INSERT INTO sinayxa.schema_migrations (migration_id)
VALUES ('issue-153-contract-0.2.1-persistence-0006')
ON CONFLICT (migration_id) DO NOTHING;
