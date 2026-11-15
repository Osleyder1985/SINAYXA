[CmdletBinding()]
param(
    [Parameter()]
    [string]$FixturePath = (Join-Path $PSScriptRoot '..\..\tests\fixtures\contracts\source-evidence-contract-v0.2.0.json')
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Test-Condition {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}
function Get-IdSet {
    param([object[]]$Items, [string]$IdProperty, [string]$Label)
    $set = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($item in $Items) {
        $id = [string]$item[$IdProperty]
        Test-Condition (-not [string]::IsNullOrWhiteSpace($id)) "$Label contains an empty identifier."
        Stop-IfFalse ($set.Add($id)) "$Label contains duplicate identifier '$id'."
    }
    return ,$set
}
function Test-Utc {
    param([object]$Value, [string]$Field)
    [void]$Field
    if ($null -eq $Value) { return $false }
    $text = [string]$Value
    $parsed = [DateTimeOffset]::MinValue
    return ($text -match 'Z$' -and [DateTimeOffset]::TryParse($text, [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::RoundtripKind, [ref]$parsed) -and $parsed.Offset -eq [TimeSpan]::Zero)
}
function Test-HasRef {
    param([System.Collections.Generic.HashSet[string]]$Set, [string]$Id)
    return (-not [string]::IsNullOrWhiteSpace($Id) -and $Set.Contains($Id))
}
function Test-ForbiddenKey {
    param([object]$Value, [string]$Path = '$')
    if ($Value -is [System.Collections.IDictionary]) {
        foreach ($key in $Value.Keys) {
            $keyText = [string]$key
            Stop-IfFalse ($keyText -notin @('score','weight','probability','rank','real_name','email','phone','password','credential','identity_secret','private_identity')) "Forbidden field '$keyText' at $Path."
            Test-ForbiddenKey -Value $Value[$key] -Path "$Path.$keyText"
        }
    }
    elseif ($Value -is [System.Collections.IEnumerable] -and $Value -isnot [string]) {
        $index = 0
        foreach ($entry in $Value) { Test-ForbiddenKeys -Value $entry -Path "$Path[$index]"; $index++ }
    }
}

Stop-IfFalse (Test-Path -LiteralPath $FixturePath -PathType Leaf) "Fixture not found: $FixturePath"
$package = Get-Content -LiteralPath $FixturePath -Raw -Encoding utf8 | ConvertFrom-Json -AsHashtable -Depth 100
Stop-IfFalse ($package.contract_version -eq '0.2.0') 'contract_version must be 0.2.0.'
Stop-IfFalse (-not [string]::IsNullOrWhiteSpace([string]$package.package_id)) 'package_id is required.'
Stop-IfFalse (Test-Utc $package.created_at 'created_at') 'created_at must be an ISO 8601 UTC instant ending in Z.'

$collections = @(
    @{ Name='claims'; Id='claim_id' }, @{ Name='claim_components'; Id='claim_component_id' },
    @{ Name='sources'; Id='source_id' }, @{ Name='source_versions'; Id='source_version_id' },
    @{ Name='identity_assessments'; Id='identity_assessment_id' }, @{ Name='evaluation_units'; Id='assessment_unit_id' },
    @{ Name='evidence_items'; Id='evidence_id' }, @{ Name='claim_evidence_links'; Id='link_id' },
    @{ Name='provenance_nodes'; Id='node_id' }, @{ Name='provenance_edges'; Id='edge_id' },
    @{ Name='factor_assessments'; Id='factor_assessment_id' }, @{ Name='independence_assessments'; Id='independence_assessment_id' },
    @{ Name='claim_assessments'; Id='claim_assessment_id' }, @{ Name='retention_records'; Id='retention_id' },
    @{ Name='audit_events'; Id='audit_event_id' }
)
$sets = @{}
foreach ($collection in $collections) {
    Stop-IfFalse ($package.Contains($collection.Name)) "Missing collection '$($collection.Name)'."
    $items = @($package[$collection.Name])
    $sets[$collection.Name] = Get-IdSet -Items $items -IdProperty $collection.Id -Label $collection.Name
}
$claimIds = $sets.claims
$componentIds = $sets.claim_components
$sourceIds = $sets.sources
$versionIds = $sets.source_versions
$unitIds = $sets.evaluation_units
$evidenceIds = $sets.evidence_items
$nodeIds = $sets.provenance_nodes
$edgeIds = $sets.provenance_edges

foreach ($component in $package.claim_components) {
    Stop-IfFalse (Test-HasRef $claimIds ([string]$component.claim_id)) "Component '$($component.claim_component_id)' references an unknown claim."
}
foreach ($version in $package.source_versions) {
    Stop-IfFalse (Test-HasRef $sourceIds ([string]$version.source_id)) "Source version '$($version.source_version_id)' references an unknown source."
    foreach ($field in @('published_at','first_detected_at','first_publicly_observed_at','retrieved_at','recorded_at')) {
        if ($null -ne $version[$field]) { Stop-IfFalse (Test-Utc $version[$field] $field) "Source version '$($version.source_version_id)' has invalid UTC $field." }
    }
    if ($null -ne $version.retrieved_at -and $null -ne $version.first_detected_at) {
        Stop-IfFalse ([DateTimeOffset]::Parse([string]$version.retrieved_at) -ge [DateTimeOffset]::Parse([string]$version.first_detected_at)) "Source version '$($version.source_version_id)' was retrieved before first detection."
    }
    if ($null -ne $version.supersedes_source_version_id) {
        Stop-IfFalse (Test-HasRef $versionIds ([string]$version.supersedes_source_version_id)) "Source version supersedes an unknown version."
        Stop-IfFalse ($version.supersedes_source_version_id -ne $version.source_version_id) 'A source version cannot supersede itself.'
    }
    if ($null -ne $version.content_hash) {
        Stop-IfFalse ([string]$version.content_hash -match '^[A-Fa-f0-9]{64}$') "Source version '$($version.source_version_id)' has an invalid SHA-256 digest."
        Stop-IfFalse ($version.hash_algorithm -eq 'SHA-256') "Source version '$($version.source_version_id)' hash algorithm must be SHA-256."
    }
}
foreach ($identity in $package.identity_assessments) {
    Stop-IfFalse (Test-HasRef $sourceIds ([string]$identity.source_id)) "Identity assessment references an unknown source."
    foreach ($reference in @($identity.verification_evidence_refs)) { Stop-IfFalse (Test-HasRef $evidenceIds ([string]$reference)) 'Identity assessment references unknown verification evidence.' }
    Stop-IfFalse (Test-Utc $identity.assessment_cutoff 'assessment_cutoff') 'Identity assessment cutoff must be UTC.'
    Stop-IfFalse (Test-Utc $identity.recorded_at 'recorded_at') 'Identity assessment recorded_at must be UTC.'
    if ($identity.identity_verified_by_sinayxa -eq $true) {
        Stop-IfFalse (@($identity.verification_evidence_refs).Count -gt 0) 'SINAYXA identity verification requires evidence references.'
    }
}
foreach ($unit in $package.evaluation_units) {
    Stop-IfFalse (Test-HasRef $claimIds ([string]$unit.claim_id)) "Evaluation unit references an unknown claim."
    Stop-IfFalse (Test-HasRef $componentIds ([string]$unit.claim_component_id)) "Evaluation unit references an unknown component."
    Stop-IfFalse (Test-HasRef $sourceIds ([string]$unit.source_id)) "Evaluation unit references an unknown source."
    Stop-IfFalse (Test-HasRef $versionIds ([string]$unit.source_version_id)) "Evaluation unit references an unknown source version."
    $component = @($package.claim_components | Where-Object { $_.claim_component_id -eq $unit.claim_component_id })[0]
    $version = @($package.source_versions | Where-Object { $_.source_version_id -eq $unit.source_version_id })[0]
    Stop-IfFalse ($component.claim_id -eq $unit.claim_id) 'Evaluation unit claim and component do not match.'
    Stop-IfFalse ($version.source_id -eq $unit.source_id) 'Evaluation unit source and source version do not match.'
    Stop-IfFalse (Test-Utc $unit.assessment_cutoff 'assessment_cutoff') 'Evaluation cutoff must be UTC.'
    Stop-IfFalse ($unit.access_status -in @('PÚBLICO_LEGÍTIMO','PRIVADO_AUTORIZADO','SOSPECHA_DE_ACCESO_NO_AUTORIZADO','NO_DETERMINADO')) 'Unsupported access status.'
    Stop-IfFalse ($unit.source_type -in @('PRIMARIA','SECUNDARIA','TERCIARIA','DESCONOCIDA')) 'Unsupported source type.'
}
foreach ($evidence in $package.evidence_items) {
    if ($null -ne $evidence.source_version_id) { Stop-IfFalse (Test-HasRef $versionIds ([string]$evidence.source_version_id)) "Evidence '$($evidence.evidence_id)' references an unknown source version." }
    Stop-IfFalse ($evidence.information_nature -in @('AFIRMACIÓN','INDICIO','RUMOR','POSIBLE_FILTRACIÓN','PUBLICACIÓN_OFICIAL','HECHO_OBSERVADO')) 'Unsupported information nature.'
    Stop-IfFalse ($evidence.authenticity_status -in @('NO_APLICA','NO_VERIFICADA','AUTENTICADA','DISPUTADA','AUTENTICIDAD_REFUTADA')) 'Unsupported authenticity status.'
    $integrity = $evidence.integrity_check
    Stop-IfFalse ($integrity.result -in @('MATCH','MISMATCH','NOT_CHECKED','UNAVAILABLE')) 'Unsupported integrity result.'
    if ($integrity.result -eq 'MATCH') {
        Stop-IfFalse ($null -ne $integrity.expected_digest -and $integrity.expected_digest -eq $integrity.observed_digest) 'Integrity MATCH requires equal expected and observed digests.'
    }
    if ($integrity.result -eq 'MISMATCH') {
        Stop-IfFalse ($null -ne $integrity.expected_digest -and $null -ne $integrity.observed_digest -and $integrity.expected_digest -ne $integrity.observed_digest) 'Integrity MISMATCH requires different known digests.'
    }
}
foreach ($link in $package.claim_evidence_links) {
    Stop-IfFalse (Test-HasRef $claimIds ([string]$link.claim_id)) 'Evidence link references an unknown claim.'
    Stop-IfFalse (Test-HasRef $componentIds ([string]$link.claim_component_id)) 'Evidence link references an unknown component.'
    Stop-IfFalse (Test-HasRef $evidenceIds ([string]$link.evidence_id)) 'Evidence link references an unknown evidence item.'
    $component = @($package.claim_components | Where-Object { $_.claim_component_id -eq $link.claim_component_id })[0]
    Stop-IfFalse ($component.claim_id -eq $link.claim_id) 'Evidence link claim and component do not match.'
}
foreach ($edge in $package.provenance_edges) {
    Stop-IfFalse (Test-HasRef $nodeIds ([string]$edge.dependent_node_id)) 'Provenance edge has an unknown dependent node.'
    Stop-IfFalse (Test-HasRef $nodeIds ([string]$edge.origin_node_id)) 'Provenance edge has an unknown origin node.'
    Stop-IfFalse (Test-HasRef $componentIds ([string]$edge.claim_component_id)) 'Provenance edge has an unknown claim component.'
    Stop-IfFalse ($edge.dependent_node_id -ne $edge.origin_node_id) 'A provenance edge cannot point to itself.'
    if ($edge.relation_type -eq 'ORIGEN_NO_DETERMINADO') {
        $origin = @($package.provenance_nodes | Where-Object { $_.node_id -eq $edge.origin_node_id })[0]
        Stop-IfFalse ($origin.node_type -eq 'UNKNOWN_ORIGIN') 'ORIGEN_NO_DETERMINADO must point to an UNKNOWN_ORIGIN node.'
    }
    if ($null -ne $edge.recorded_at) { Stop-IfFalse (Test-Utc $edge.recorded_at 'recorded_at') 'Provenance edge recorded_at must be UTC.' }
    if ($null -ne $edge.valid_from -and $null -ne $edge.valid_to) {
        Stop-IfFalse ((Test-Utc $edge.valid_from 'valid_from') -and (Test-Utc $edge.valid_to 'valid_to')) 'Provenance validity timestamps must be UTC.'
        Stop-IfFalse ([DateTimeOffset]::Parse([string]$edge.valid_to) -ge [DateTimeOffset]::Parse([string]$edge.valid_from)) 'Provenance edge valid_to precedes valid_from.'
    }
}
foreach ($factor in $package.factor_assessments) {
    Stop-IfFalse (Test-HasRef $unitIds ([string]$factor.assessment_unit_id)) 'Factor assessment references an unknown evaluation unit.'
    Stop-IfFalse ($factor.dimension -in @('RELATION_WITH_FACT','ACCESS_AND_PROXIMITY','SUBJECT_COMPETENCE','TRANSPARENCY_TRACEABILITY','RELEVANT_ACCURACY_HISTORY','CORRECTIONS_ACCOUNTABILITY','INCENTIVES_CONFLICTS','INTERNAL_CONSISTENCY','CONTRARY_EVIDENCE','TEMPORAL_ADEQUACY')) 'Unsupported factor dimension.'
    Stop-IfFalse ($factor.status -in @('SUSTENTADA','LIMITADA','DESFAVORABLE','DESCONOCIDA','NO_APLICA')) 'Factor status must use the approved #16 descriptive vocabulary.'
    Stop-IfFalse (-not [string]::IsNullOrWhiteSpace([string]$factor.justification)) 'Factor assessment requires a justification.'
    foreach ($reference in @($factor.supporting_evidence_refs) + @($factor.contrary_evidence_refs)) {
        Stop-IfFalse (Test-HasRef $evidenceIds ([string]$reference)) 'Factor assessment references unknown evidence.'
    }
}
foreach ($assessment in $package.independence_assessments) {
    Stop-IfFalse (Test-HasRef $claimIds ([string]$assessment.claim_id)) 'Independence assessment references an unknown claim.'
    Stop-IfFalse (Test-HasRef $componentIds ([string]$assessment.claim_component_id)) 'Independence assessment references an unknown component.'
    Stop-IfFalse (@($assessment.assessment_unit_ids).Count -ge 2) 'Independence assessment requires at least two evaluation units.'
    foreach ($unitId in $assessment.assessment_unit_ids) { Stop-IfFalse (Test-HasRef $unitIds ([string]$unitId)) 'Independence assessment references an unknown evaluation unit.' }
    $units = @($package.evaluation_units | Where-Object { $_.assessment_unit_id -in $assessment.assessment_unit_ids })
    Stop-IfFalse (@($units | Where-Object { $_.claim_id -ne $assessment.claim_id -or $_.claim_component_id -ne $assessment.claim_component_id }).Count -eq 0) 'Independence assessment mixes claims or components.'
    foreach ($reference in @($assessment.supporting_evidence_refs)) { Stop-IfFalse (Test-HasRef $evidenceIds ([string]$reference)) 'Independence assessment references unknown evidence.' }
    foreach ($reference in @($assessment.dependency_edge_refs)) { Stop-IfFalse (Test-HasRef $edgeIds ([string]$reference)) 'Independence assessment references an unknown provenance edge.' }
    if ($assessment.status -eq 'INDEPENDIENTE') {
        Stop-IfFalse (@($assessment.supporting_evidence_refs).Count -gt 0) 'INDEPENDIENTE requires positive supporting evidence.'
    }
    if ($assessment.human_review_status -eq 'REVIEWED') { Stop-IfFalse (Test-Utc $assessment.reviewed_at 'reviewed_at') 'A reviewed independence assessment requires a UTC reviewed_at.' }
    if ($assessment.human_review_status -eq 'PENDING') { Stop-IfFalse ($null -eq $assessment.reviewed_at) 'A pending independence assessment cannot carry reviewed_at.' }
    if ($assessment.status -eq 'DEPENDIENTE') {
        Stop-IfFalse (@($assessment.dependency_edge_refs).Count -gt 0) 'DEPENDIENTE requires an evidenced dependency edge.'
    }
    Stop-IfFalse ($assessment.status -in @('INDEPENDIENTE','DEPENDIENTE','DESCONOCIDA')) 'Unsupported independence status.'
}
foreach ($assessment in $package.claim_assessments) {
    Stop-IfFalse (Test-HasRef $claimIds ([string]$assessment.claim_id)) 'Claim assessment references an unknown claim.'
    Stop-IfFalse (Test-HasRef $componentIds ([string]$assessment.claim_component_id)) 'Claim assessment references an unknown component.'
    $component = @($package.claim_components | Where-Object { $_.claim_component_id -eq $assessment.claim_component_id })[0]
    Stop-IfFalse ($component.claim_id -eq $assessment.claim_id) 'Claim assessment claim and component do not match.'
    Stop-IfFalse ($assessment.evidentiary_status -in @('NO_CORROBORADA','PARCIALMENTE_CORROBORADA','CORROBORADA','CONTRADICHA','REFUTADA','NO_RESUELTA')) 'Unsupported #15 evidentiary status.'
    Stop-IfFalse ($assessment.attribution_status -in @('ATRIBUIDA','NO_ATRIBUIDA','NO_DETERMINADA')) 'Unsupported attribution status.'
    foreach ($reference in @($assessment.supporting_evidence_refs) + @($assessment.contrary_evidence_refs)) { Stop-IfFalse (Test-HasRef $evidenceIds ([string]$reference)) 'Claim assessment references unknown evidence.' }
    foreach ($reference in @($assessment.independence_assessment_refs)) {
        Stop-IfFalse (Test-HasRef $sets.independence_assessments ([string]$reference)) 'Claim assessment references unknown independence assessment.'
        $independence = @($package.independence_assessments | Where-Object { $_.independence_assessment_id -eq $reference })[0]
        Stop-IfFalse ($independence.claim_id -eq $assessment.claim_id -and $independence.claim_component_id -eq $assessment.claim_component_id) 'Claim assessment references independence evidence for a different claim component.'
    }
    $linkedSupport = @($package.claim_evidence_links | Where-Object { $_.claim_component_id -eq $assessment.claim_component_id -and $_.evidence_role -eq 'SUPPORTING' } | ForEach-Object { $_.evidence_id })
    $linkedContrary = @($package.claim_evidence_links | Where-Object { $_.claim_component_id -eq $assessment.claim_component_id -and $_.evidence_role -eq 'CONTRARY' } | ForEach-Object { $_.evidence_id })
    foreach ($reference in @($assessment.supporting_evidence_refs)) { Stop-IfFalse ($reference -in $linkedSupport) 'Supporting evidence reference has no SUPPORTING claim-evidence link for this component.' }
    foreach ($reference in @($assessment.contrary_evidence_refs)) { Stop-IfFalse ($reference -in $linkedContrary) 'Contrary evidence reference has no CONTRARY claim-evidence link for this component.' }
    if ($assessment.evidentiary_status -eq 'CONTRADICHA') { Stop-IfFalse (@($assessment.supporting_evidence_refs).Count -gt 0 -and @($assessment.contrary_evidence_refs).Count -gt 0) 'CONTRADICHA requires traceable evidence on both sides.' }
    if ($assessment.evidentiary_status -eq 'REFUTADA') { Stop-IfFalse (@($assessment.contrary_evidence_refs).Count -gt 0) 'REFUTADA requires direct, relevant contrary evidence.' }
    if ($assessment.evidentiary_status -eq 'CORROBORADA') { Stop-IfFalse (@($assessment.supporting_evidence_refs).Count -gt 0) 'CORROBORADA requires supporting evidence.' }
    Stop-IfFalse (Test-Utc $assessment.assessment_cutoff 'assessment_cutoff') 'Claim assessment cutoff must be UTC.'
    if ($null -ne $assessment.supersedes_assessment_id) {
        Stop-IfFalse (Test-HasRef $sets.claim_assessments ([string]$assessment.supersedes_assessment_id)) 'Claim assessment supersedes an unknown assessment.'
        Stop-IfFalse ($assessment.supersedes_assessment_id -ne $assessment.claim_assessment_id) 'Claim assessment cannot supersede itself.'
    }
}
foreach ($record in $package.retention_records) {
    Stop-IfFalse (Test-Utc $record.review_at 'review_at') 'Retention review_at must be UTC.'
    Stop-IfFalse (Test-Utc $record.recorded_at 'recorded_at') 'Retention recorded_at must be UTC.'
    if ($record.content_retained -eq $true) {
        Stop-IfFalse ($record.legal_basis_status -eq 'VERIFIED') 'Retained content requires a verified legal/access basis.'
        Stop-IfFalse ($null -ne $record.expires_at -and (Test-Utc $record.expires_at 'expires_at')) 'Retained content requires a reviewable UTC expiry.'
    }
    else {
        Stop-IfFalse ($record.disposition -in @('REFERENCE_ONLY','DELETED','RESTRICTED')) 'Content not retained must not be marked RETAIN.'
    }
}
foreach ($event in $package.audit_events) {
    Stop-IfFalse (Test-Utc $event.occurred_at 'occurred_at') 'Audit event occurred_at must be UTC.'
}
Test-ForbiddenKeys -Value $package
[pscustomobject]@{
    Result = 'PASS'
    ContractVersion = $package.contract_version
    Claims = @($package.claims).Count
    Components = @($package.claim_components).Count
    Sources = @($package.sources).Count
    EvaluationUnits = @($package.evaluation_units).Count
    EvidenceItems = @($package.evidence_items).Count
    ProvenanceEdges = @($package.provenance_edges).Count
    SyntheticOnly = $true
    Scope = 'Structural and cross-reference conformance; not empirical truth, legal advice, or authorization to capture.'
} | Format-List
