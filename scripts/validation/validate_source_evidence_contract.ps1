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
        Test-Condition ($set.Add($id)) "$Label contains duplicate identifier '$id'."
    }
    return ,$set
}
function Test-Utc {
    param([object]$Value, [string]$Field)
    [void]$Field
    if ($null -eq $Value) { return $false }
    $text = [string]$Value
    $parsed = [DateTimeOffset]::MinValue
    $pattern = '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,7})?Z$'
    $styles = [Globalization.DateTimeStyles]::AssumeUniversal -bor [Globalization.DateTimeStyles]::AdjustToUniversal
    return ($text -cmatch $pattern -and [DateTimeOffset]::TryParse($text, [Globalization.CultureInfo]::InvariantCulture, $styles, [ref]$parsed) -and $parsed.Offset -eq [TimeSpan]::Zero)
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
            Test-Condition ($keyText -notin @('score','weight','probability','rank','real_name','email','phone','password','credential','identity_secret','private_identity')) "Forbidden field '$keyText' at $Path."
            Test-ForbiddenKey -Value $Value[$key] -Path ($Path + '.' + $keyText)
        }
    }
    elseif ($Value -is [System.Collections.IEnumerable] -and $Value -isnot [string]) {
        $index = 0
        foreach ($entry in $Value) {
            Test-ForbiddenKey -Value $entry -Path ($Path + '[' + $index + ']')
            $index++
        }
    }
}

Test-Condition (Test-Path -LiteralPath $FixturePath -PathType Leaf) "Fixture not found: $FixturePath"
$package = Get-Content -LiteralPath $FixturePath -Raw -Encoding utf8 | ConvertFrom-Json -AsHashtable -Depth 100 -DateKind String
Test-Condition ($package.contract_version -eq '0.2.0') 'contract_version must be 0.2.0.'
Test-Condition (-not [string]::IsNullOrWhiteSpace([string]$package.package_id)) 'package_id is required.'
Test-Condition (Test-Utc $package.created_at 'created_at') 'created_at must be an ISO 8601 UTC instant ending in Z.'

$collections = @(
    @{ Name='claims'; Id='claim_version_id' }, @{ Name='claim_components'; Id='claim_component_version_id' },
    @{ Name='sources'; Id='source_id' }, @{ Name='source_versions'; Id='source_version_id' },
    @{ Name='identity_assessments'; Id='identity_assessment_id' }, @{ Name='evaluation_units'; Id='assessment_unit_id' },
    @{ Name='evidence_items'; Id='evidence_id' }, @{ Name='evidence_availability'; Id='availability_id' }, @{ Name='claim_evidence_links'; Id='link_id' },
    @{ Name='provenance_nodes'; Id='node_id' }, @{ Name='provenance_edges'; Id='edge_id' },
    @{ Name='factor_assessments'; Id='factor_assessment_id' }, @{ Name='independence_assessments'; Id='independence_assessment_id' },
    @{ Name='claim_assessments'; Id='claim_assessment_id' }, @{ Name='retention_records'; Id='retention_id' },
    @{ Name='audit_events'; Id='audit_event_id' }
)
$sets = @{}
foreach ($collection in $collections) {
    Test-Condition ($package.Contains($collection.Name)) "Missing collection '$($collection.Name)'."
    $sets[$collection.Name] = Get-IdSet -Items @($package[$collection.Name]) -IdProperty $collection.Id -Label $collection.Name
}
$claimIds = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
foreach ($claim in $package.claims) { Test-Condition (-not [string]::IsNullOrWhiteSpace([string]$claim.claim_id)) 'Claim identity cannot be empty.'; [void]$claimIds.Add([string]$claim.claim_id) }
$claimVersionIds = $sets.claims
$componentIds = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
foreach ($component in $package.claim_components) { Test-Condition (-not [string]::IsNullOrWhiteSpace([string]$component.claim_component_id)) 'Claim component identity cannot be empty.'; [void]$componentIds.Add([string]$component.claim_component_id) }
$componentVersionIds = $sets.claim_components
$sourceIds = $sets.sources
$versionIds = $sets.source_versions
$unitIds = $sets.evaluation_units
$evidenceIds = $sets.evidence_items
$nodeIds = $sets.provenance_nodes
$edgeIds = $sets.provenance_edges

foreach ($source in $package.sources) {
    Test-Condition ([string]$source.source_id -cmatch '^src_[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$') 'Source identifiers must be opaque UUIDs with the src_ prefix.'
}
foreach ($claim in $package.claims) {
    $duplicateClaimVersion = @($package.claims | Where-Object { $_.claim_id -eq $claim.claim_id -and $_.claim_version -eq $claim.claim_version -and $_.claim_version_id -ne $claim.claim_version_id })
    Test-Condition ($duplicateClaimVersion.Count -eq 0) 'Claim version numbers must be unique within the same claim.'
    if ($null -ne $claim.supersedes_claim_version_id) {
        Test-Condition (Test-HasRef $claimVersionIds ([string]$claim.supersedes_claim_version_id)) 'Claim version supersedes an unknown claim version.'
        $prior = @($package.claims | Where-Object { $_.claim_version_id -eq $claim.supersedes_claim_version_id })[0]
        Test-Condition ($prior.claim_id -eq $claim.claim_id -and $prior.claim_version -lt $claim.claim_version) 'Claim supersession must reference an earlier version of the same claim.'
    }
}
foreach ($component in $package.claim_components) {
    Test-Condition (Test-HasRef $claimIds ([string]$component.claim_id)) 'Component references an unknown claim.'
    Test-Condition (Test-HasRef $claimVersionIds ([string]$component.claim_version_id)) 'Component references an unknown claim version.'
    $claimVersion = @($package.claims | Where-Object { $_.claim_version_id -eq $component.claim_version_id })[0]
    Test-Condition ($claimVersion.claim_id -eq $component.claim_id) 'Component and claim version identities do not match.'
    $duplicateComponentVersion = @($package.claim_components | Where-Object { $_.claim_component_id -eq $component.claim_component_id -and $_.version -eq $component.version -and $_.claim_component_version_id -ne $component.claim_component_version_id })
    Test-Condition ($duplicateComponentVersion.Count -eq 0) 'Component version numbers must be unique within the same component.'
    if ($null -ne $component.supersedes_component_version_id) {
        Test-Condition (Test-HasRef $componentVersionIds ([string]$component.supersedes_component_version_id)) 'Component supersedes an unknown component version.'
        $prior = @($package.claim_components | Where-Object { $_.claim_component_version_id -eq $component.supersedes_component_version_id })[0]
        Test-Condition ($prior.claim_component_id -eq $component.claim_component_id -and $prior.version -lt $component.version) 'Component supersession must reference an earlier version of the same component.'
    }
}
$sourceVersionSequences = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
foreach ($version in $package.source_versions) {
    Test-Condition (Test-HasRef $sourceIds ([string]$version.source_id)) 'Source version references an unknown source.'
    Test-Condition ([int]$version.version_sequence -ge 1) 'Source version sequence must be a positive integer.'
    $successors = @($package.source_versions | Where-Object { $_.supersedes_source_version_id -eq $version.source_version_id })
    Test-Condition ($successors.Count -le 1) 'A source version cannot have multiple competing direct successors; represent distinct sources/variants explicitly.'
    $duplicateSourceSequence = @($package.source_versions | Where-Object { $_.source_id -eq $version.source_id -and $_.version_sequence -eq $version.version_sequence -and $_.source_version_id -ne $version.source_version_id })
    Test-Condition ($duplicateSourceSequence.Count -eq 0) 'Source version sequence must be unique within the same source.'
    $sequenceKey = ([string]$version.source_id) + '|' + ([string][int]$version.version_sequence)
    Test-Condition ($sourceVersionSequences.Add($sequenceKey)) 'Source version sequence must be unique within the same source.'
    foreach ($field in @('published_at','first_detected_at','first_publicly_observed_at','retrieved_at','recorded_at')) {
        if ($null -ne $version[$field]) { Test-Condition (Test-Utc $version[$field] $field) "Source version has invalid UTC $field." }
    }
    if ($null -ne $version.retrieved_at -and $null -ne $version.first_detected_at) {
        Test-Condition ([DateTimeOffset]::Parse([string]$version.retrieved_at) -ge [DateTimeOffset]::Parse([string]$version.first_detected_at)) 'Source version was retrieved before first detection.'
    }
    if ($null -ne $version.supersedes_source_version_id) {
        Test-Condition (Test-HasRef $versionIds ([string]$version.supersedes_source_version_id)) 'Source version supersedes an unknown version.'
        $prior = @($package.source_versions | Where-Object { $_.source_version_id -eq $version.supersedes_source_version_id })[0]
        Test-Condition ($prior.source_id -eq $version.source_id -and $prior.source_version_id -ne $version.source_version_id) 'Source version supersession must reference another version of the same source.'
        Test-Condition ([int]$prior.version_sequence -lt [int]$version.version_sequence) 'Source version must supersede a strictly earlier version of the same source.'
    }
    foreach ($observation in @($version.original_timestamps)) {
        $value = [string]$observation.original_value
        $pattern = switch ($observation.precision) {
            'YEAR' { '^\d{4}$' }
            'MONTH' { '^\d{4}-\d{2}$' }
            'DAY' { '^\d{4}-\d{2}-\d{2}$' }
            'HOUR' { '^\d{4}-\d{2}-\d{2}T\d{2}(?:Z|[+-]\d{2}:\d{2})?$' }
            'MINUTE' { '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})?$' }
            'SECOND' { '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})?$' }
            'MILLISECOND' { '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,3}(?:Z|[+-]\d{2}:\d{2})?$' }
            'UNKNOWN' { '^.+$' }
            default { '' }
        }
        Test-Condition (-not [string]::IsNullOrWhiteSpace($pattern) -and $value -cmatch $pattern) 'Original timestamp value does not match its declared precision; do not invent finer precision.'
    }
    if ($null -ne $version.content_hash) {
        Test-Condition ([string]$version.content_hash -cmatch '^[A-Fa-f0-9]{64}$') 'Source version has an invalid SHA-256 digest.'
        Test-Condition ($version.hash_algorithm -eq 'SHA-256') 'Source version hash algorithm must be SHA-256.'
    }
    else {
        Test-Condition ($null -eq $version.hash_algorithm) 'Source version cannot declare a hash algorithm without a content hash.'
    }
}
foreach ($identity in $package.identity_assessments) {
    Test-Condition (Test-HasRef $sourceIds ([string]$identity.source_id)) 'Identity assessment references an unknown source.'
    Test-Condition (Test-Utc $identity.assessment_cutoff 'assessment_cutoff') 'Identity assessment cutoff must be UTC.'
    Test-Condition (Test-Utc $identity.recorded_at 'recorded_at') 'Identity assessment recorded_at must be UTC.'
    foreach ($reference in @($identity.verification_evidence_refs)) { Test-Condition (Test-HasRef $evidenceIds ([string]$reference)) 'Identity assessment references unknown evidence.' }
    if ($identity.identity -eq 'ANÓNIMA_PARA_EL_PÚBLICO') { Test-Condition ($identity.anonymous_to_public -eq $true) 'ANÓNIMA_PARA_EL_PÚBLICO requires anonymous_to_public=true.' }
    if ($identity.identity -eq 'ANÓNIMA_PARA_SINAYXA') { Test-Condition ($identity.anonymous_to_sinayxa -eq $true) 'ANÓNIMA_PARA_SINAYXA requires anonymous_to_sinayxa=true.' }
    if ($identity.identity_verified_by_sinayxa -eq $true) {
        Test-Condition ($identity.anonymous_to_sinayxa -eq $false) 'SINAYXA cannot verify an identity recorded as anonymous to SINAYXA.'
        Test-Condition (@($identity.verification_evidence_refs).Count -gt 0) 'SINAYXA identity verification requires evidence references.'
    }
}
foreach ($unit in $package.evaluation_units) {
    Test-Condition (Test-HasRef $claimIds ([string]$unit.claim_id)) 'Evaluation unit references an unknown claim.'
    Test-Condition (Test-HasRef $componentIds ([string]$unit.claim_component_id)) 'Evaluation unit references an unknown component.'
    Test-Condition (Test-HasRef $claimVersionIds ([string]$unit.claim_version_id)) 'Evaluation unit references an unknown claim version.'
    Test-Condition (Test-HasRef $componentVersionIds ([string]$unit.claim_component_version_id)) 'Evaluation unit references an unknown component version.'
    Test-Condition (Test-HasRef $sourceIds ([string]$unit.source_id)) 'Evaluation unit references an unknown source.'
    Test-Condition (Test-HasRef $versionIds ([string]$unit.source_version_id)) 'Evaluation unit references an unknown source version.'
    $component = @($package.claim_components | Where-Object { $_.claim_component_id -eq $unit.claim_component_id })[0]
    $version = @($package.source_versions | Where-Object { $_.source_version_id -eq $unit.source_version_id })[0]
    Test-Condition ($component.claim_id -eq $unit.claim_id) 'Evaluation unit claim and component do not match.'
    Test-Condition ($component.claim_version_id -eq $unit.claim_version_id -and $component.claim_component_version_id -eq $unit.claim_component_version_id) 'Evaluation unit is not bound to exact claim/component versions.'
    Test-Condition ($version.source_id -eq $unit.source_id) 'Evaluation unit source and source version do not match.'
    Test-Condition (Test-Utc $unit.assessment_cutoff 'assessment_cutoff') 'Evaluation cutoff must be UTC.'
    Test-Condition ($unit.access_status -in @('PÚBLICO_LEGÍTIMO','PRIVADO_AUTORIZADO','SOSPECHA_DE_ACCESO_NO_AUTORIZADO','NO_DETERMINADO')) 'Unsupported access status.'
    Test-Condition ($unit.source_type -in @('PRIMARIA','SECUNDARIA','TERCIARIA','DESCONOCIDA')) 'Unsupported source type.'
}
foreach ($evidence in $package.evidence_items) {
    if ($null -ne $evidence.source_version_id) { Test-Condition (Test-HasRef $versionIds ([string]$evidence.source_version_id)) 'Evidence references an unknown source version.' }
    Test-Condition ($evidence.information_nature -in @('AFIRMACIÓN','INDICIO','RUMOR','POSIBLE_FILTRACIÓN','PUBLICACIÓN_OFICIAL','HECHO_OBSERVADO')) 'Unsupported information nature.'
    Test-Condition ($evidence.authenticity_status -in @('NO_APLICA','NO_VERIFICADA','AUTENTICADA','DISPUTADA','AUTENTICIDAD_REFUTADA')) 'Unsupported authenticity status.'
    $integrity = $evidence.integrity_check
    Test-Condition ($integrity.result -in @('MATCH','MISMATCH','NOT_CHECKED','UNAVAILABLE')) 'Unsupported integrity result.'
    if ($integrity.result -eq 'MATCH') { Test-Condition ($null -ne $integrity.expected_digest -and $integrity.expected_digest -eq $integrity.observed_digest) 'Integrity MATCH requires equal known digests.' }
    if ($integrity.result -eq 'MISMATCH') { Test-Condition ($null -ne $integrity.expected_digest -and $null -ne $integrity.observed_digest -and $integrity.expected_digest -ne $integrity.observed_digest) 'Integrity MISMATCH requires different known digests.' }
    if ($integrity.algorithm -eq 'SHA-256') {
        Test-Condition ([string]$integrity.expected_digest -cmatch '^[A-Fa-f0-9]{64}$' -and [string]$integrity.observed_digest -cmatch '^[A-Fa-f0-9]{64}$') 'SHA-256 integrity checks require two valid digests.'
        Test-Condition ($integrity.result -in @('MATCH','MISMATCH')) 'SHA-256 integrity check must be MATCH or MISMATCH.'
    }
    else {
        Test-Condition ($null -eq $integrity.expected_digest -and $null -eq $integrity.observed_digest) 'Digest values cannot be retained without a supported hash algorithm.'
    }
}
foreach ($availability in $package.evidence_availability) {
    Test-Condition (Test-HasRef $evidenceIds ([string]$availability.evidence_id)) 'Evidence availability references unknown evidence.'
    Test-Condition (Test-HasRef $unitIds ([string]$availability.assessment_unit_id)) 'Evidence availability references an unknown evaluation unit.'
    $unit = @($package.evaluation_units | Where-Object { $_.assessment_unit_id -eq $availability.assessment_unit_id })[0]
    $evidence = @($package.evidence_items | Where-Object { $_.evidence_id -eq $availability.evidence_id })[0]
    Test-Condition ($null -ne $evidence.source_version_id -and $evidence.source_version_id -eq $unit.source_version_id) 'Evidence availability must match the exact source version in its evaluation unit.'
    Test-Condition ($availability.claim_id -eq $unit.claim_id -and $availability.claim_component_id -eq $unit.claim_component_id -and $availability.claim_version_id -eq $unit.claim_version_id -and $availability.claim_component_version_id -eq $unit.claim_component_version_id) 'Evidence availability must match the exact claim/component version of its evaluation unit.'
    $blockedRetention = @($package.retention_records | Where-Object { $_.subject_ref -eq $availability.evidence_id -and $_.disposition -in @('DELETE_PENDING','DELETED') -and (Test-Utc $_.recorded_at 'recorded_at') -and [DateTimeOffset]::Parse([string]$_.recorded_at) -le [DateTimeOffset]::Parse([string]$unit.assessment_cutoff) })
    Test-Condition ($blockedRetention.Count -eq 0) 'Evidence under DELETE_PENDING or DELETED disposition cannot be used for an assessment at or after that transition.'
    Test-Condition (Test-Utc $availability.recorded_at 'recorded_at') 'Evidence availability recorded_at must be UTC.'
    if ($null -eq $availability.available_at) {
        Test-Condition ($availability.availability_basis -eq 'UNKNOWN' -and $null -eq $availability.availability_reference) 'Unknown availability requires UNKNOWN basis and no availability reference.'
    }
    else {
        Test-Condition (Test-Utc $availability.available_at 'available_at') 'Evidence available_at must be UTC.'
        Test-Condition ($availability.availability_basis -in @('SINAYXA_OBSERVATION','INDEPENDENT_ARCHIVE','SOURCE_STATED')) 'Known availability requires an explicit supported basis.'
        Test-Condition (-not [string]::IsNullOrWhiteSpace([string]$availability.availability_reference)) 'Known availability requires a traceable reference.'
        Test-Condition ([DateTimeOffset]::Parse([string]$availability.available_at) -le [DateTimeOffset]::Parse([string]$unit.assessment_cutoff)) 'Evidence was not available by the evaluation cutoff.'
    }
}
foreach ($link in $package.claim_evidence_links) {
    Test-Condition (Test-HasRef $claimIds ([string]$link.claim_id)) 'Evidence link references an unknown claim.'
    Test-Condition (Test-HasRef $componentIds ([string]$link.claim_component_id)) 'Evidence link references an unknown component.'
    Test-Condition (Test-HasRef $claimVersionIds ([string]$link.claim_version_id)) 'Evidence link references an unknown claim version.'
    Test-Condition (Test-HasRef $componentVersionIds ([string]$link.claim_component_version_id)) 'Evidence link references an unknown component version.'
    Test-Condition (Test-HasRef $evidenceIds ([string]$link.evidence_id)) 'Evidence link references an unknown evidence item.'
    $component = @($package.claim_components | Where-Object { $_.claim_component_id -eq $link.claim_component_id })[0]
    Test-Condition ($component.claim_id -eq $link.claim_id -and $component.claim_version_id -eq $link.claim_version_id -and $component.claim_component_version_id -eq $link.claim_component_version_id) 'Evidence link does not match the exact claim/component versions.'
}
foreach ($node in $package.provenance_nodes) {
    if ($node.node_type -eq 'SOURCE_VERSION') { Test-Condition (Test-HasRef $versionIds ([string]$node.entity_ref)) 'SOURCE_VERSION node must reference an existing source version.' }
    if ($node.node_type -eq 'EVIDENCE_ITEM') { Test-Condition (Test-HasRef $evidenceIds ([string]$node.entity_ref)) 'EVIDENCE_ITEM node must reference an existing evidence item.' }
    if ($node.node_type -eq 'UNKNOWN_ORIGIN') { Test-Condition ($null -eq $node.entity_ref) 'UNKNOWN_ORIGIN must not contain an entity reference or identity.' }
}
foreach ($edge in $package.provenance_edges) {
    Test-Condition (Test-HasRef $nodeIds ([string]$edge.dependent_node_id)) 'Provenance edge has an unknown dependent node.'
    Test-Condition (Test-HasRef $nodeIds ([string]$edge.origin_node_id)) 'Provenance edge has an unknown origin node.'
    Test-Condition (Test-HasRef $componentIds ([string]$edge.claim_component_id)) 'Provenance edge has an unknown component.'
    Test-Condition (Test-HasRef $componentVersionIds ([string]$edge.claim_component_version_id)) 'Provenance edge has an unknown component version.'
    $component = @($package.claim_components | Where-Object { $_.claim_component_version_id -eq $edge.claim_component_version_id })[0]
    Test-Condition ($component.claim_component_id -eq $edge.claim_component_id) 'Provenance edge component version does not match its component.'
    foreach ($reference in @($edge.evidence_refs)) { Test-Condition (Test-HasRef $evidenceIds ([string]$reference)) 'Provenance edge references unknown evidence.' }
    Test-Condition ($edge.dependent_node_id -ne $edge.origin_node_id) 'A provenance edge cannot point to itself.'
    if ($edge.relation_type -eq 'ORIGEN_NO_DETERMINADO') {
        $origin = @($package.provenance_nodes | Where-Object { $_.node_id -eq $edge.origin_node_id })[0]
        Test-Condition ($origin.node_type -eq 'UNKNOWN_ORIGIN') 'ORIGEN_NO_DETERMINADO must point to UNKNOWN_ORIGIN.'
    }
    Test-Condition (Test-Utc $edge.recorded_at 'recorded_at') 'Provenance edge recorded_at must be UTC.'
    if ($null -ne $edge.valid_from -and $null -ne $edge.valid_to) {
        Test-Condition ((Test-Utc $edge.valid_from 'valid_from') -and (Test-Utc $edge.valid_to 'valid_to')) 'Provenance validity timestamps must be UTC.'
        Test-Condition ([DateTimeOffset]::Parse([string]$edge.valid_to) -ge [DateTimeOffset]::Parse([string]$edge.valid_from)) 'Provenance edge valid_to precedes valid_from.'
    }
}
$adjacency = @{}
$inDegree = @{}
foreach ($node in $package.provenance_nodes) {
    $adjacency[[string]$node.node_id] = [System.Collections.Generic.List[string]]::new()
    $inDegree[[string]$node.node_id] = 0
}
foreach ($edge in $package.provenance_edges) {
    $dependent = [string]$edge.dependent_node_id
    $origin = [string]$edge.origin_node_id
    $adjacency[$dependent].Add($origin)
    $inDegree[$origin]++
}
$queue = [System.Collections.Generic.Queue[string]]::new()
foreach ($nodeId in $inDegree.Keys) { if ($inDegree[$nodeId] -eq 0) { $queue.Enqueue([string]$nodeId) } }
$processedNodes = 0
while ($queue.Count -gt 0) {
    $current = $queue.Dequeue()
    $processedNodes++
    foreach ($nextNode in $adjacency[$current]) {
        $inDegree[$nextNode]--
        if ($inDegree[$nextNode] -eq 0) { $queue.Enqueue($nextNode) }
    }
}
$cyclesDetected = ($processedNodes -lt $package.provenance_nodes.Count)

foreach ($factor in $package.factor_assessments) {
    Test-Condition (Test-HasRef $unitIds ([string]$factor.assessment_unit_id)) 'Factor assessment references an unknown evaluation unit.'
    Test-Condition ($factor.dimension -in @('RELATION_WITH_FACT','ACCESS_AND_PROXIMITY','SUBJECT_COMPETENCE','TRANSPARENCY_TRACEABILITY','RELEVANT_ACCURACY_HISTORY','CORRECTIONS_ACCOUNTABILITY','INCENTIVES_CONFLICTS','INTERNAL_CONSISTENCY','CONTRARY_EVIDENCE','TEMPORAL_ADEQUACY')) 'Unsupported factor dimension.'
    Test-Condition ($factor.status -in @('SUSTENTADA','LIMITADA','DESFAVORABLE','DESCONOCIDA','NO_APLICA')) 'Factor status must use the approved #16 vocabulary.'
    Test-Condition (-not [string]::IsNullOrWhiteSpace([string]$factor.justification)) 'Factor assessment requires justification.'
    foreach ($reference in @($factor.supporting_evidence_refs) + @($factor.contrary_evidence_refs)) {
        Test-Condition (Test-HasRef $evidenceIds ([string]$reference)) 'Factor assessment references unknown evidence.'
        $factorEvidence = @($package.evidence_items | Where-Object { $_.evidence_id -eq $reference })[0]
        Test-Condition ($factor.dimension -in @($factorEvidence.factor_dimensions)) 'Factor evidence is not explicitly scoped to the assessed dimension.'
        $availableForUnit = @($package.evidence_availability | Where-Object { $_.evidence_id -eq $reference -and $_.assessment_unit_id -eq $factor.assessment_unit_id -and $null -ne $_.available_at -and $_.availability_basis -in @('SINAYXA_OBSERVATION','INDEPENDENT_ARCHIVE') })
        Test-Condition ($availableForUnit.Count -gt 0) 'Factor evidence must have a known availability observation for its exact evaluation unit.'
    }
    if ($factor.human_review_status -eq 'REVIEWED') { Test-Condition (Test-Utc $factor.reviewed_at 'reviewed_at') 'Reviewed factor assessment requires UTC reviewed_at.' }
    if ($factor.human_review_status -eq 'PENDING') { Test-Condition ($null -eq $factor.reviewed_at) 'Pending factor assessment cannot carry reviewed_at.' }
}
$expectedDimensions = @('RELATION_WITH_FACT','ACCESS_AND_PROXIMITY','SUBJECT_COMPETENCE','TRANSPARENCY_TRACEABILITY','RELEVANT_ACCURACY_HISTORY','CORRECTIONS_ACCOUNTABILITY','INCENTIVES_CONFLICTS','INTERNAL_CONSISTENCY','CONTRARY_EVIDENCE','TEMPORAL_ADEQUACY')
foreach ($unit in $package.evaluation_units) {
    $unitFactors = @($package.factor_assessments | Where-Object { $_.assessment_unit_id -eq $unit.assessment_unit_id })
    Test-Condition ($unitFactors.Count -eq 10) "Evaluation unit '$($unit.assessment_unit_id)' must contain exactly ten factor assessments."
    $actual = @($unitFactors.dimension | Sort-Object -Unique)
    $missing = @($expectedDimensions | Where-Object { $_ -notin $actual })
    $unexpected = @($actual | Where-Object { $_ -notin $expectedDimensions })
    Test-Condition ($missing.Count -eq 0 -and $unexpected.Count -eq 0) "Evaluation unit '$($unit.assessment_unit_id)' does not implement the exact #16 factor catalogue."
}
foreach ($assessment in $package.independence_assessments) {
    Test-Condition (Test-HasRef $claimIds ([string]$assessment.claim_id)) 'Independence assessment references an unknown claim.'
    Test-Condition (Test-HasRef $componentIds ([string]$assessment.claim_component_id)) 'Independence assessment references an unknown component.'
    Test-Condition (Test-HasRef $claimVersionIds ([string]$assessment.claim_version_id)) 'Independence assessment references an unknown claim version.'
    Test-Condition (Test-HasRef $componentVersionIds ([string]$assessment.claim_component_version_id)) 'Independence assessment references an unknown component version.'
    Test-Condition (@($assessment.assessment_unit_ids).Count -ge 2) 'Independence assessment requires at least two units.'
    Test-Condition (@($assessment.assessment_unit_ids | Sort-Object -Unique).Count -eq @($assessment.assessment_unit_ids).Count) 'Independence assessment cannot repeat an evaluation unit.'
    foreach ($unitId in $assessment.assessment_unit_ids) { Test-Condition (Test-HasRef $unitIds ([string]$unitId)) 'Independence assessment references an unknown unit.' }
    $units = @($package.evaluation_units | Where-Object { $_.assessment_unit_id -in $assessment.assessment_unit_ids })
    Test-Condition (Test-Utc $assessment.assessment_cutoff 'assessment_cutoff') 'Independence assessment cutoff must be UTC.'
    Test-Condition (@($units | Where-Object { $_.assessment_cutoff -ne $assessment.assessment_cutoff }).Count -eq 0) 'Independence assessment units must share the exact assessment cutoff.'
    Test-Condition (@($units | Where-Object { $_.claim_id -ne $assessment.claim_id -or $_.claim_component_id -ne $assessment.claim_component_id -or $_.claim_version_id -ne $assessment.claim_version_id -or $_.claim_component_version_id -ne $assessment.claim_component_version_id }).Count -eq 0) 'Independence assessment mixes claims or component versions.'
    foreach ($reference in @($assessment.supporting_evidence_refs)) { Test-Condition (Test-HasRef $evidenceIds ([string]$reference)) 'Independence assessment references unknown evidence.' }
    foreach ($reference in @($assessment.dependency_edge_refs)) { Test-Condition (Test-HasRef $edgeIds ([string]$reference)) 'Independence assessment references an unknown provenance edge.' }
    foreach ($reference in @($assessment.independent_path_edge_refs)) { Test-Condition (Test-HasRef $edgeIds ([string]$reference)) 'Independence assessment references an unknown independent provenance path edge.' }
    Test-Condition (@($assessment.independent_path_edge_refs | Sort-Object -Unique).Count -eq @($assessment.independent_path_edge_refs).Count) 'Independent path edge references cannot be duplicated.'
    Test-Condition (@($assessment.dependency_edge_refs | Sort-Object -Unique).Count -eq @($assessment.dependency_edge_refs).Count) 'Dependency edge references cannot be duplicated.'
    Test-Condition ($assessment.status -in @('INDEPENDIENTE','DEPENDIENTE','DESCONOCIDA')) 'Unsupported independence status.'
    if ($assessment.status -eq 'INDEPENDIENTE') {
        Test-Condition (@($assessment.supporting_evidence_refs).Count -gt 0) 'INDEPENDIENTE requires positive evidence.'
        Test-Condition (@($assessment.independent_path_edge_refs).Count -ge 2) 'INDEPENDIENTE requires at least two explicit provenance paths.'
        $distinctSourceIds = @($units.source_id | Sort-Object -Unique)
        Test-Condition ($distinctSourceIds.Count -ge 2) 'INDEPENDIENTE requires at least two distinct source identities, not merely two versions of one source.'
        $evidenceSourceIds = @()
        foreach ($evidenceId in @($assessment.supporting_evidence_refs)) {
            $evidenceItem = @($package.evidence_items | Where-Object { $_.evidence_id -eq $evidenceId })[0]
            if ($null -ne $evidenceItem.source_version_id) {
                $evidenceVersion = @($package.source_versions | Where-Object { $_.source_version_id -eq $evidenceItem.source_version_id })[0]
                if ($null -ne $evidenceVersion) { $evidenceSourceIds += [string]$evidenceVersion.source_id }
            }
        }
        Test-Condition (@($evidenceSourceIds | Sort-Object -Unique).Count -ge 2) 'INDEPENDIENTE evidence must positively cover at least two distinct source identities.'
        Test-Condition (@($evidenceSourceIds | Where-Object { $_ -notin $distinctSourceIds }).Count -eq 0) 'INDEPENDIENTE evidence cannot originate outside the evaluated source set.'
        Test-Condition (@($distinctSourceIds | Where-Object { $_ -notin $evidenceSourceIds }).Count -eq 0) 'INDEPENDIENTE evidence must cover every evaluated source identity.'
        foreach ($evidenceId in @($assessment.supporting_evidence_refs)) {
            $item = @($package.evidence_items | Where-Object { $_.evidence_id -eq $evidenceId })[0]
            $unitForEvidence = @($units | Where-Object { $_.source_version_id -eq $item.source_version_id })[0]
            Test-Condition ($null -ne $unitForEvidence) 'INDEPENDIENTE evidence must bind to the exact source version evaluated.'
            $available = @($package.evidence_availability | Where-Object { $_.evidence_id -eq $evidenceId -and $_.assessment_unit_id -eq $unitForEvidence.assessment_unit_id -and $_.availability_basis -in @('SINAYXA_OBSERVATION','INDEPENDENT_ARCHIVE') -and $null -ne $_.available_at -and [DateTimeOffset]::Parse([string]$_.available_at) -le [DateTimeOffset]::Parse([string]$assessment.assessment_cutoff) })
            Test-Condition ($available.Count -gt 0) 'INDEPENDIENTE evidence must be available by the cutoff through the exact evaluated source version.'
        }
        $coveredSourceVersions = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
        $distinctOriginNodes = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
        $distinctOriginRefs = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
        foreach ($pathEdgeId in @($assessment.independent_path_edge_refs)) {
            $pathEdge = @($package.provenance_edges | Where-Object { $_.edge_id -eq $pathEdgeId })[0]
            Test-Condition ($pathEdge.claim_component_id -eq $assessment.claim_component_id -and $pathEdge.claim_component_version_id -eq $assessment.claim_component_version_id) 'Independent path edge must apply to the exact assessed component version.'
            Test-Condition ($pathEdge.relation_type -eq 'ORIGEN_DIRECTO' -and @($pathEdge.evidence_refs).Count -gt 0) 'Independent path must be a directly evidenced origin path.'
            $dependentNode = @($package.provenance_nodes | Where-Object { $_.node_id -eq $pathEdge.dependent_node_id })[0]
            $originNode = @($package.provenance_nodes | Where-Object { $_.node_id -eq $pathEdge.origin_node_id })[0]
            Test-Condition ($dependentNode.node_type -eq 'SOURCE_VERSION' -and $dependentNode.entity_ref -in @($units.source_version_id)) 'Independent path must begin at an exact evaluated source version.'
            Test-Condition ($originNode.node_type -eq 'EVIDENCE_ITEM' -and $originNode.entity_ref -in @($pathEdge.evidence_refs) -and $originNode.node_id -ne $dependentNode.node_id) 'Independent path must terminate at a distinct, evidence-identified origin item, not an unknown or unanchored node.'
            Test-Condition (@($package.provenance_edges | Where-Object { $_.dependent_node_id -eq $originNode.node_id }).Count -eq 0) 'Independent path origin must be a separately evidenced terminal origin, not an unresolved shared intermediary.'
            Test-Condition ($distinctOriginNodes.Add([string]$originNode.node_id)) 'Independent source paths must terminate at distinct origin nodes.'
            $originIdentity = if ([string]::IsNullOrWhiteSpace([string]$originNode.entity_ref)) { [string]$originNode.node_id } else { [string]$originNode.entity_ref }
            Test-Condition ($distinctOriginRefs.Add($originIdentity)) 'Independent source paths cannot resolve to the same underlying origin identity.'
            [void]$coveredSourceVersions.Add([string]$dependentNode.entity_ref)
            foreach ($pathEvidenceId in @($pathEdge.evidence_refs)) {
                Test-Condition ($pathEvidenceId -in $assessment.supporting_evidence_refs) 'Independent path evidence must be included in the assessment supporting evidence.'
                $pathEvidence = @($package.evidence_items | Where-Object { $_.evidence_id -eq $pathEvidenceId })[0]
                Test-Condition ($pathEvidence.source_version_id -eq $dependentNode.entity_ref) 'Independent path evidence must originate from the exact source version represented by its path.'
                $pathUnit = @($units | Where-Object { $_.source_version_id -eq $dependentNode.entity_ref })[0]
                $pathAvailability = @($package.evidence_availability | Where-Object { $_.evidence_id -eq $pathEvidenceId -and $_.assessment_unit_id -eq $pathUnit.assessment_unit_id -and $_.availability_basis -in @('SINAYXA_OBSERVATION','INDEPENDENT_ARCHIVE') -and $null -ne $_.available_at -and [DateTimeOffset]::Parse([string]$_.available_at) -le [DateTimeOffset]::Parse([string]$assessment.assessment_cutoff) })
                Test-Condition ($pathAvailability.Count -gt 0) 'Independent path evidence must be available by the exact assessment cutoff.'
            }
        }
        Test-Condition (@($units | Where-Object { $_.source_version_id -notin $coveredSourceVersions }).Count -eq 0) 'Independent paths must cover every evaluated source version.'
        Test-Condition (@($assessment.dependency_edge_refs).Count -eq 0) 'INDEPENDIENTE cannot simultaneously declare material dependency edges.'
    }
    if ($assessment.status -eq 'DEPENDIENTE') {
        Test-Condition (@($assessment.dependency_edge_refs).Count -gt 0) 'DEPENDIENTE requires an evidenced dependency edge.'
        Test-Condition (@($assessment.independent_path_edge_refs).Count -eq 0) 'DEPENDIENTE cannot simultaneously declare independent origin paths.'
        foreach ($edgeId in @($assessment.dependency_edge_refs)) {
            $dependencyEdge = @($package.provenance_edges | Where-Object { $_.edge_id -eq $edgeId })[0]
            Test-Condition ($dependencyEdge.claim_component_id -eq $assessment.claim_component_id -and $dependencyEdge.claim_component_version_id -eq $assessment.claim_component_version_id) 'Dependency edge must apply to the exact assessed component version.'
            Test-Condition ($dependencyEdge.relation_type -in @('CITA_DE','SINDICADA_DE','DERIVADA_DE','DOCUMENTO_COMÚN','CONTACTO_COMÚN','ANÁLISIS_SEPARADO_SOBRE_DATOS_COMUNES') -and @($dependencyEdge.evidence_refs).Count -gt 0) 'DEPENDIENTE requires a material, evidenced dependency relation; direct or unknown origin alone is insufficient.'
            $dependentNode = @($package.provenance_nodes | Where-Object { $_.node_id -eq $dependencyEdge.dependent_node_id })[0]
            $originNode = @($package.provenance_nodes | Where-Object { $_.node_id -eq $dependencyEdge.origin_node_id })[0]
            Test-Condition ($dependentNode.node_type -eq 'SOURCE_VERSION' -and $originNode.node_type -eq 'SOURCE_VERSION') 'DEPENDIENTE edge must connect two concrete source-version nodes, not UNKNOWN_ORIGIN.'
            Test-Condition ($dependentNode.entity_ref -in @($units.source_version_id) -and $originNode.entity_ref -in @($units.source_version_id) -and $dependentNode.entity_ref -ne $originNode.entity_ref) 'DEPENDIENTE edge must connect two distinct source versions included in the same independence assessment.'
            $dependentVersion = @($package.source_versions | Where-Object { $_.source_version_id -eq $dependentNode.entity_ref })[0]
            $originVersion = @($package.source_versions | Where-Object { $_.source_version_id -eq $originNode.entity_ref })[0]
            Test-Condition ($dependentVersion.source_id -ne $originVersion.source_id) 'DEPENDIENTE edge must connect two distinct source identities, not two versions of one source.'
            foreach ($evidenceId in @($dependencyEdge.evidence_refs)) {
                $edgeEvidence = @($package.evidence_items | Where-Object { $_.evidence_id -eq $evidenceId })[0]
                Test-Condition ($edgeEvidence.source_version_id -in @($units.source_version_id)) 'Dependency edge evidence must originate from one of the exact evaluated source versions.'
                $edgeUnit = @($units | Where-Object { $_.source_version_id -eq $edgeEvidence.source_version_id })[0]
                $edgeEvidenceAvailable = @($package.evidence_availability | Where-Object { $_.evidence_id -eq $evidenceId -and $_.assessment_unit_id -eq $edgeUnit.assessment_unit_id -and $_.availability_basis -in @('SINAYXA_OBSERVATION','INDEPENDENT_ARCHIVE') -and $null -ne $_.available_at -and [DateTimeOffset]::Parse([string]$_.available_at) -le [DateTimeOffset]::Parse([string]$assessment.assessment_cutoff) })
                Test-Condition ($edgeEvidenceAvailable.Count -gt 0) 'Dependency edge evidence must be available by the exact assessment cutoff.'
            }
        }
    }
    if ($assessment.status -in @('INDEPENDIENTE','DEPENDIENTE')) { Test-Condition ($assessment.human_review_status -eq 'REVIEWED') 'Positive independence/dependence requires human review.' }
    if ($assessment.human_review_status -eq 'REVIEWED') { Test-Condition (Test-Utc $assessment.reviewed_at 'reviewed_at') 'Reviewed independence assessment requires UTC reviewed_at.' }
    if ($assessment.human_review_status -eq 'PENDING') { Test-Condition ($null -eq $assessment.reviewed_at) 'Pending independence assessment cannot carry reviewed_at.' }
}
foreach ($assessment in $package.claim_assessments) {
    Test-Condition (Test-HasRef $claimIds ([string]$assessment.claim_id)) 'Claim assessment references an unknown claim.'
    Test-Condition (Test-HasRef $componentIds ([string]$assessment.claim_component_id)) 'Claim assessment references an unknown component.'
    Test-Condition (Test-HasRef $claimVersionIds ([string]$assessment.claim_version_id)) 'Claim assessment references an unknown claim version.'
    Test-Condition (Test-HasRef $componentVersionIds ([string]$assessment.claim_component_version_id)) 'Claim assessment references an unknown component version.'
    $component = @($package.claim_components | Where-Object { $_.claim_component_id -eq $assessment.claim_component_id })[0]
    Test-Condition ($component.claim_id -eq $assessment.claim_id -and $component.claim_version_id -eq $assessment.claim_version_id -and $component.claim_component_version_id -eq $assessment.claim_component_version_id) 'Claim assessment is not bound to the exact claim/component versions.'
    Test-Condition ($assessment.evidentiary_status -in @('NO_CORROBORADA','PARCIALMENTE_CORROBORADA','CORROBORADA','CONTRADICHA','REFUTADA','NO_RESUELTA')) 'Unsupported #15 evidentiary status.'
    Test-Condition ($assessment.attribution_status -in @('ATRIBUIDA','NO_ATRIBUIDA','NO_DETERMINADA')) 'Unsupported attribution status.'
    foreach ($reference in @($assessment.supporting_evidence_refs) + @($assessment.contrary_evidence_refs)) { Test-Condition (Test-HasRef $evidenceIds ([string]$reference)) 'Claim assessment references unknown evidence.' }
    foreach ($reference in @($assessment.independence_assessment_refs)) {
        Test-Condition (Test-HasRef $sets.independence_assessments ([string]$reference)) 'Claim assessment references unknown independence assessment.'
        $independence = @($package.independence_assessments | Where-Object { $_.independence_assessment_id -eq $reference })[0]
        Test-Condition ($independence.claim_id -eq $assessment.claim_id -and $independence.claim_component_id -eq $assessment.claim_component_id -and $independence.claim_version_id -eq $assessment.claim_version_id -and $independence.claim_component_version_id -eq $assessment.claim_component_version_id) 'Claim assessment references independence evidence for another component version.'
    }
    $linkedSupport = @($package.claim_evidence_links | Where-Object { $_.claim_id -eq $assessment.claim_id -and $_.claim_component_id -eq $assessment.claim_component_id -and $_.claim_version_id -eq $assessment.claim_version_id -and $_.claim_component_version_id -eq $assessment.claim_component_version_id -and $_.evidence_role -eq 'SUPPORTING' } | ForEach-Object { $_.evidence_id })
    $linkedContrary = @($package.claim_evidence_links | Where-Object { $_.claim_id -eq $assessment.claim_id -and $_.claim_component_id -eq $assessment.claim_component_id -and $_.claim_version_id -eq $assessment.claim_version_id -and $_.claim_component_version_id -eq $assessment.claim_component_version_id -and $_.evidence_role -eq 'CONTRARY' } | ForEach-Object { $_.evidence_id })
    foreach ($reference in @($assessment.supporting_evidence_refs)) { Test-Condition ($reference -in $linkedSupport) 'Supporting evidence has no SUPPORTING link for this exact component version.' }
    foreach ($reference in @($assessment.contrary_evidence_refs)) { Test-Condition ($reference -in $linkedContrary) 'Contrary evidence has no CONTRARY link for this exact component version.' }
    foreach ($reference in @($assessment.supporting_evidence_refs) + @($assessment.contrary_evidence_refs)) {
        $availableForAssessment = @($package.evidence_availability | Where-Object {
            $_.evidence_id -eq $reference -and $_.claim_id -eq $assessment.claim_id -and $_.claim_component_id -eq $assessment.claim_component_id -and
            $_.claim_version_id -eq $assessment.claim_version_id -and $_.claim_component_version_id -eq $assessment.claim_component_version_id -and
            $_.available_at -and $_.availability_basis -in @('SINAYXA_OBSERVATION','INDEPENDENT_ARCHIVE') -and
            [DateTimeOffset]::Parse([string]$_.available_at) -le [DateTimeOffset]::Parse([string]$assessment.assessment_cutoff)
        })
        Test-Condition ($availableForAssessment.Count -gt 0) 'Claim assessment uses evidence without a matching availability observation at or before its cutoff.'
    }
    if ($assessment.evidentiary_status -eq 'CORROBORADA') {
        Test-Condition (@($assessment.supporting_evidence_refs).Count -gt 0) 'CORROBORADA requires supporting evidence.'
        $supportingUnits = @()
        $primaryDirectEvidenceFound = $false
        foreach ($evidenceId in @($assessment.supporting_evidence_refs)) {
            $item = @($package.evidence_items | Where-Object { $_.evidence_id -eq $evidenceId })[0]
            if ($null -ne $item.source_version_id) {
                $matchingUnits = @($package.evaluation_units | Where-Object { $_.source_version_id -eq $item.source_version_id -and $_.claim_id -eq $assessment.claim_id -and $_.claim_component_id -eq $assessment.claim_component_id -and $_.claim_version_id -eq $assessment.claim_version_id -and $_.claim_component_version_id -eq $assessment.claim_component_version_id })
                $supportingUnits += $matchingUnits
                foreach ($unit in $matchingUnits) {
                    if ($unit.source_type -eq 'PRIMARIA') {
                        $directLinks = @($package.claim_evidence_links | Where-Object {
                            $_.evidence_id -eq $evidenceId -and $_.claim_id -eq $assessment.claim_id -and $_.claim_component_id -eq $assessment.claim_component_id -and
                            $_.claim_version_id -eq $assessment.claim_version_id -and $_.claim_component_version_id -eq $assessment.claim_component_version_id -and
                            $_.evidence_role -eq 'SUPPORTING' -and -not [string]::IsNullOrWhiteSpace([string]$_.scope_note)
                        })
                        if ($unit.knowledge_basis -in @('OBSERVACIÓN_DIRECTA','REGISTRO_ORIGINAL') -and $item.authenticity_status -eq 'AUTENTICADA' -and $item.access_status -in @('PÚBLICO_LEGÍTIMO','PRIVADO_AUTORIZADO') -and $directLinks.Count -gt 0) {
                            $primaryDirectEvidenceFound = $true
                        }
                    }
                }
            }
        }
        $supportingUnits = @($supportingUnits | Sort-Object -Property assessment_unit_id -Unique)
        Test-Condition ($supportingUnits.Count -gt 0) 'CORROBORADA evidence must map to at least one exact supporting evaluation unit.'
        $hasNonPrimarySupportingUnit = @($supportingUnits | Where-Object { $_.source_type -ne 'PRIMARIA' }).Count -gt 0
        if ($hasNonPrimarySupportingUnit) {
            Test-Condition ($assessment.corroboration_basis -in @('CORROBORACION_INDEPENDIENTE','AMBAS')) 'Any non-primary supporting source requires the independent-corroboration basis.'
        }
        if ($assessment.corroboration_basis -eq 'EVIDENCIA_PRIMARIA_DIRECTA') {
            Test-Condition (-not $hasNonPrimarySupportingUnit) 'Primary-direct corroboration cannot silently include non-primary supporting sources.'
        }
        if ($assessment.corroboration_basis -in @('EVIDENCIA_PRIMARIA_DIRECTA','AMBAS')) {
            Test-Condition $primaryDirectEvidenceFound 'Primary corroboration requires authenticated, legitimately accessed primary evidence directly linked to the exact component scope.'
        }
        if ($assessment.corroboration_basis -in @('CORROBORACION_INDEPENDIENTE','AMBAS')) {
            Test-Condition ($supportingUnits.Count -ge 2) 'Independent corroboration requires at least two supporting source units.'
            $distinctSupportingSourceIds = @($supportingUnits.source_id | Sort-Object -Unique)
            Test-Condition ($distinctSupportingSourceIds.Count -ge 2) 'Independent corroboration requires at least two distinct source identities; multiple versions of one source are not corroboration.'
            $reviewedIndependent = @($package.independence_assessments | Where-Object { $_.independence_assessment_id -in $assessment.independence_assessment_refs -and $_.status -eq 'INDEPENDIENTE' -and $_.human_review_status -eq 'REVIEWED' })
            $covered = $false
            foreach ($independenceRecord in $reviewedIndependent) {
                if (@($supportingUnits | Where-Object { $_.assessment_unit_id -notin $independenceRecord.assessment_unit_ids }).Count -eq 0) { $covered = $true; break }
            }
            Test-Condition $covered 'Independent corroboration requires reviewed INDEPENDIENTE covering every supporting source unit.'
        }
        Test-Condition ($assessment.corroboration_basis -in @('EVIDENCIA_PRIMARIA_DIRECTA','CORROBORACION_INDEPENDIENTE','AMBAS')) 'CORROBORADA requires an explicit primary or independent corroboration basis.'
    }
    else {
        Test-Condition ($assessment.corroboration_basis -eq 'NO_APLICA') 'Non-CORROBORADA assessments must use NO_APLICA corroboration basis.'
    }
    if ($assessment.evidentiary_status -eq 'CONTRADICHA') { Test-Condition (@($assessment.supporting_evidence_refs).Count -gt 0 -and @($assessment.contrary_evidence_refs).Count -gt 0) 'CONTRADICHA requires traceable evidence on both sides.' }
    if ($assessment.evidentiary_status -eq 'REFUTADA') { Test-Condition (@($assessment.contrary_evidence_refs).Count -gt 0) 'REFUTADA requires direct, relevant contrary evidence.' }
    if ($null -ne $assessment.supersedes_assessment_id) {
        Test-Condition (Test-HasRef $sets.claim_assessments ([string]$assessment.supersedes_assessment_id)) 'Claim assessment supersedes an unknown assessment.'
        Test-Condition ($assessment.supersedes_assessment_id -ne $assessment.claim_assessment_id) 'Claim assessment cannot supersede itself.'
        $prior = @($package.claim_assessments | Where-Object { $_.claim_assessment_id -eq $assessment.supersedes_assessment_id })[0]
        Test-Condition ($prior.claim_id -eq $assessment.claim_id -and $prior.claim_component_id -eq $assessment.claim_component_id) 'Claim assessment supersession must remain within the same component.'
        Test-Condition ([DateTimeOffset]::Parse([string]$prior.assessment_cutoff) -lt [DateTimeOffset]::Parse([string]$assessment.assessment_cutoff)) 'Superseding assessment must have a later cutoff.'
    }
    if ($assessment.human_review_status -eq 'REVIEWED') { Test-Condition (Test-Utc $assessment.reviewed_at 'reviewed_at') 'Reviewed claim assessment requires UTC reviewed_at.' }
    if ($assessment.human_review_status -eq 'PENDING') { Test-Condition ($null -eq $assessment.reviewed_at) 'Pending claim assessment cannot carry reviewed_at.' }
    if ($assessment.evidentiary_status -in @('CORROBORADA','PARCIALMENTE_CORROBORADA','CONTRADICHA','REFUTADA')) { Test-Condition ($assessment.human_review_status -eq 'REVIEWED') 'Conclusive probative state requires human review.' }
}
foreach ($record in $package.retention_records) {
    $known = (Test-HasRef $claimIds ([string]$record.subject_ref)) -or (Test-HasRef $claimVersionIds ([string]$record.subject_ref)) -or (Test-HasRef $componentIds ([string]$record.subject_ref)) -or (Test-HasRef $componentVersionIds ([string]$record.subject_ref)) -or (Test-HasRef $sourceIds ([string]$record.subject_ref)) -or (Test-HasRef $versionIds ([string]$record.subject_ref)) -or (Test-HasRef $evidenceIds ([string]$record.subject_ref))
    Test-Condition $known 'Retention record references an unknown subject.'
    Test-Condition (Test-Utc $record.review_at 'review_at') 'Retention review_at must be UTC.'
    Test-Condition (Test-Utc $record.recorded_at 'recorded_at') 'Retention recorded_at must be UTC.'
    $previous = $record.previous_disposition
    if ($null -eq $previous) {
        $allowedNext = @('RETAIN','REFERENCE_ONLY','RESTRICTED')
    }
    else {
        $allowedNext = switch ($previous) {
            'RETAIN' { @('RESTRICTED','DELETE_PENDING','DELETED','REFERENCE_ONLY') }
            'RESTRICTED' { @('RETAIN','DELETE_PENDING','DELETED','REFERENCE_ONLY') }
            'REFERENCE_ONLY' { @('RETAIN','RESTRICTED','DELETED') }
            'DELETE_PENDING' { @('DELETED','REFERENCE_ONLY') }
            'DELETED' { @() }
            default { @() }
        }
    }
    Test-Condition ($record.disposition -in $allowedNext) 'Invalid retention disposition transition.'
    if ($record.content_retained -eq $true) {
        Test-Condition ($record.disposition -in @('RETAIN','DELETE_PENDING','RESTRICTED')) 'Retained content has an incompatible disposition.'
    }
    else {
        Test-Condition ($record.disposition -in @('REFERENCE_ONLY','DELETED','RESTRICTED')) 'Content not retained has an incompatible disposition.'
    }
    if ($record.disposition -in @('RETAIN','RESTRICTED') -and $record.content_retained -eq $true) {
        Test-Condition ($record.legal_basis_status -eq 'VERIFIED') 'Retained content requires a verified legal/access basis.'
        Test-Condition ($null -ne $record.expires_at -and (Test-Utc $record.expires_at 'expires_at')) 'Retained content requires a reviewable UTC expiry.'
        Test-Condition ([DateTimeOffset]::Parse([string]$record.expires_at) -gt [DateTimeOffset]::Parse([string]$record.recorded_at)) 'Retained content expiry must be later than its retention record.'
        Test-Condition ([DateTimeOffset]::Parse([string]$record.review_at) -le [DateTimeOffset]::Parse([string]$record.expires_at)) 'Retention review must occur no later than expiry.'
    }
    if ($record.disposition -eq 'RETAIN') {
        Test-Condition ($record.content_retained -eq $true -and $record.legal_basis_status -eq 'VERIFIED') 'RETAIN requires retained content and verified legal/access basis.'
        Test-Condition (-not [string]::IsNullOrWhiteSpace([string]$record.authorization_reference)) 'RETAIN requires a traceable authorization decision.'
    }
    if ($record.disposition -eq 'REFERENCE_ONLY') {
        Test-Condition ($record.content_retained -eq $false) 'REFERENCE_ONLY cannot retain content.'
    }
    if ($record.disposition -eq 'DELETE_PENDING') {
        Test-Condition ($record.content_retained -eq $true) 'DELETE_PENDING requires the retained copy to remain explicitly tracked until deletion is confirmed.'
        Test-Condition ($previous -in @('RETAIN','RESTRICTED')) 'DELETE_PENDING must follow a retained or restricted state.'
        Test-Condition ($null -ne $record.expires_at -and (Test-Utc $record.expires_at 'expires_at')) 'DELETE_PENDING requires a recorded expiry/deletion deadline.'
    }
    if ($record.disposition -eq 'DELETED') {
        Test-Condition ($record.content_retained -eq $false) 'DELETED disposition cannot retain content.'
        Test-Condition ($previous -in @('RETAIN','RESTRICTED','DELETE_PENDING')) 'DELETED must follow a state in which content was retained or pending deletion.'
    }
    if ($null -ne $previous -and $previous -eq 'DELETED') { Test-Condition $false 'DELETED is terminal; a new retention decision must use a new evidence subject.' }
    $expectedAction = switch ($record.disposition) {
        'RETAIN' { 'RETENTION_SET' }
        'REFERENCE_ONLY' { 'REFERENCE_ONLY' }
        'RESTRICTED' { 'RESTRICTED' }
        'DELETE_PENDING' { 'DELETION_REQUESTED' }
        'DELETED' { 'DELETED' }
    }
    $transitionEvents = @($package.audit_events | Where-Object {
        $_.retention_id -eq $record.retention_id -and $_.subject_ref -eq $record.subject_ref -and
        $_.from_disposition -eq $record.previous_disposition -and $_.to_disposition -eq $record.disposition -and
        $_.action -eq $expectedAction -and (Test-Utc $_.occurred_at 'occurred_at') -and
        [DateTimeOffset]::Parse([string]$_.occurred_at) -ge [DateTimeOffset]::Parse([string]$record.recorded_at)
    })
    Test-Condition ($transitionEvents.Count -eq 1) 'Every retention disposition transition requires exactly one matching audit event.'
    $priorDeletionEvents = @($package.audit_events | Where-Object { $_.subject_ref -eq $record.subject_ref -and $_.to_disposition -eq 'DELETED' -and $_.retention_id -ne $record.retention_id -and (Test-Utc $_.occurred_at 'occurred_at') -and [DateTimeOffset]::Parse([string]$_.occurred_at) -lt [DateTimeOffset]::Parse([string]$record.recorded_at) })
    Test-Condition ($priorDeletionEvents.Count -eq 0) 'A deleted evidence subject cannot be retained again; a newly authorized copy requires a new evidence subject.'
}
foreach ($auditEvent in $package.audit_events) {
    $known = (Test-HasRef $claimIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $claimVersionIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $componentIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $componentVersionIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sourceIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $versionIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $evidenceIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sets.claim_assessments ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sets.identity_assessments ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sets.evaluation_units ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sets.claim_evidence_links ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sets.provenance_nodes ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sets.provenance_edges ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sets.factor_assessments ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sets.independence_assessments ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sets.retention_records ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sets.evidence_availability ([string]$auditEvent.subject_ref))
    Test-Condition $known 'Audit event references an unknown subject.'
    Test-Condition (Test-Utc $auditEvent.occurred_at 'occurred_at') 'Audit event occurred_at must be UTC.'
    if ($null -ne $auditEvent.retention_id) {
        Test-Condition (Test-HasRef $sets.retention_records ([string]$auditEvent.retention_id)) 'Retention audit event references an unknown retention record.'
        $retention = @($package.retention_records | Where-Object { $_.retention_id -eq $auditEvent.retention_id })[0]
        Test-Condition ($retention.subject_ref -eq $auditEvent.subject_ref -and $retention.previous_disposition -eq $auditEvent.from_disposition -and $retention.disposition -eq $auditEvent.to_disposition) 'Retention audit event does not match its retention transition.'
    }
    elseif ($null -ne $auditEvent.from_disposition -or $null -ne $auditEvent.to_disposition) { Test-Condition $false 'Retention transition audit fields require retention_id.' }
}
Test-ForbiddenKey -Value $package
[pscustomobject]@{
    Result = 'PASS'
    ContractVersion = $package.contract_version
    Claims = @($package.claims).Count
    Components = @($package.claim_components).Count
    Sources = @($package.sources).Count
    EvaluationUnits = @($package.evaluation_units).Count
    FactorAssessments = @($package.factor_assessments).Count
    EvidenceItems = @($package.evidence_items).Count
    ProvenanceEdges = @($package.provenance_edges).Count
    CycleReviewRequired = $cyclesDetected
    SyntheticOnly = $true
    Scope = 'Structural and cross-reference conformance; not empirical truth, legal advice, or authorization to capture.'
} | Format-List
