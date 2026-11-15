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
    if ($null -ne $component.supersedes_component_version_id) {
        Test-Condition (Test-HasRef $componentVersionIds ([string]$component.supersedes_component_version_id)) 'Component supersedes an unknown component version.'
        $prior = @($package.claim_components | Where-Object { $_.claim_component_version_id -eq $component.supersedes_component_version_id })[0]
        Test-Condition ($prior.claim_component_id -eq $component.claim_component_id -and $prior.version -lt $component.version) 'Component supersession must reference an earlier version of the same component.'
    }
}
foreach ($version in $package.source_versions) {
    Test-Condition (Test-HasRef $sourceIds ([string]$version.source_id)) 'Source version references an unknown source.'
    Test-Condition ([int]$version.version_sequence -ge 1) 'Source version sequence must be a positive integer.'
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
        $availableForUnit = @($package.evidence_availability | Where-Object { $_.evidence_id -eq $reference -and $_.assessment_unit_id -eq $factor.assessment_unit_id -and $null -ne $_.available_at })
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
    Test-Condition (@($units | Where-Object { $_.claim_id -ne $assessment.claim_id -or $_.claim_component_id -ne $assessment.claim_component_id -or $_.claim_version_id -ne $assessment.claim_version_id -or $_.claim_component_version_id -ne $assessment.claim_component_version_id }).Count -eq 0) 'Independence assessment mixes claims or component versions.'
    foreach ($reference in @($assessment.supporting_evidence_refs)) { Test-Condition (Test-HasRef $evidenceIds ([string]$reference)) 'Independence assessment references unknown evidence.' }
    foreach ($reference in @($assessment.dependency_edge_refs)) { Test-Condition (Test-HasRef $edgeIds ([string]$reference)) 'Independence assessment references an unknown provenance edge.' }
    Test-Condition ($assessment.status -in @('INDEPENDIENTE','DEPENDIENTE','DESCONOCIDA')) 'Unsupported independence status.'
    if ($assessment.status -eq 'INDEPENDIENTE') {
        Test-Condition (@($assessment.supporting_evidence_refs).Count -gt 0) 'INDEPENDIENTE requires positive evidence.'
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
        Test-Condition (@($assessment.dependency_edge_refs).Count -eq 0) 'INDEPENDIENTE cannot simultaneously declare material dependency edges.'
    }
    if ($assessment.status -eq 'DEPENDIENTE') {
        Test-Condition (@($assessment.dependency_edge_refs).Count -gt 0) 'DEPENDIENTE requires an evidenced dependency edge.'
        foreach ($edgeId in @($assessment.dependency_edge_refs)) {
            $dependencyEdge = @($package.provenance_edges | Where-Object { $_.edge_id -eq $edgeId })[0]
            Test-Condition ($dependencyEdge.claim_component_id -eq $assessment.claim_component_id -and $dependencyEdge.claim_component_version_id -eq $assessment.claim_component_version_id) 'Dependency edge must apply to the exact assessed component version.'
            Test-Condition ($dependencyEdge.relation_type -ne 'ORIGEN_NO_DETERMINADO' -and @($dependencyEdge.evidence_refs).Count -gt 0) 'DEPENDIENTE requires a material, evidenced dependency relation; unknown origin alone is insufficient.'
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
            $_.available_at -and [DateTimeOffset]::Parse([string]$_.available_at) -le [DateTimeOffset]::Parse([string]$assessment.assessment_cutoff)
        })
        Test-Condition ($availableForAssessment.Count -gt 0) 'Claim assessment uses evidence without a matching availability observation at or before its cutoff.'
    }
    if ($assessment.evidentiary_status -eq 'CORROBORADA') {
        Test-Condition (@($assessment.supporting_evidence_refs).Count -gt 0) 'CORROBORADA requires supporting evidence.'
        $supportingUnits = @()
        foreach ($evidenceId in @($assessment.supporting_evidence_refs)) {
            $item = @($package.evidence_items | Where-Object { $_.evidence_id -eq $evidenceId })[0]
            if ($null -ne $item.source_version_id) {
                $supportingUnits += @($package.evaluation_units | Where-Object { $_.source_version_id -eq $item.source_version_id -and $_.claim_id -eq $assessment.claim_id -and $_.claim_component_id -eq $assessment.claim_component_id -and $_.claim_version_id -eq $assessment.claim_version_id -and $_.claim_component_version_id -eq $assessment.claim_component_version_id })
            }
        }
        Test-Condition ($supportingUnits.Count -gt 0) 'CORROBORADA requires supporting evidence mapped to an evaluation unit for the exact component version.'
        $secondaryUnits = @($supportingUnits | Where-Object { $_.source_type -in @('SECUNDARIA','TERCIARIA','DESCONOCIDA') })
        if ($secondaryUnits.Count -gt 0) {
            $reviewedIndependent = @($package.independence_assessments | Where-Object { $_.independence_assessment_id -in $assessment.independence_assessment_refs -and $_.status -eq 'INDEPENDIENTE' -and $_.human_review_status -eq 'REVIEWED' })
            $covered = $false
            foreach ($independenceRecord in $reviewedIndependent) {
                if (@($secondaryUnits | Where-Object { $_.assessment_unit_id -notin $independenceRecord.assessment_unit_ids }).Count -eq 0) { $covered = $true; break }
            }
            Test-Condition $covered 'Secondary/tertiary corroboration requires reviewed INDEPENDIENTE covering all supporting source units for this component version.'
        }
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
    if ($record.content_retained -eq $true) {
        Test-Condition ($record.legal_basis_status -eq 'VERIFIED') 'Retained content requires a verified legal/access basis.'
        Test-Condition ($null -ne $record.expires_at -and (Test-Utc $record.expires_at 'expires_at')) 'Retained content requires a reviewable UTC expiry.'
    }
    else {
        Test-Condition ($record.disposition -in @('REFERENCE_ONLY','DELETED','RESTRICTED')) 'Content not retained must not be marked RETAIN.'
    }
}
foreach ($auditEvent in $package.audit_events) {
    $known = (Test-HasRef $claimIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $claimVersionIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $componentIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $componentVersionIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sourceIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $versionIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $evidenceIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sets.claim_assessments ([string]$auditEvent.subject_ref))
    Test-Condition $known 'Audit event references an unknown subject.'
    Test-Condition (Test-Utc $auditEvent.occurred_at 'occurred_at') 'Audit event occurred_at must be UTC.'
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
