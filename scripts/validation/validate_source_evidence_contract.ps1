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
            Test-Condition ($keyText -notin @('score','weight','probability','rank','real_name','email','phone','password','credential','identity_secret','private_identity')) "Forbidden field '$keyText' at $Path."
            Test-ForbiddenKey -Value $Value[$key] -Path "$Path.$keyText"
        }
    }
    elseif ($Value -is [System.Collections.IEnumerable] -and $Value -isnot [string]) {
        $index = 0
        foreach ($entry in $Value) { Test-ForbiddenKey -Value $entry -Path "$Path[$index]"; $index++ }
    }
}

Test-Condition (Test-Path -LiteralPath $FixturePath -PathType Leaf) "Fixture not found: $FixturePath"
$package = Get-Content -LiteralPath $FixturePath -Raw -Encoding utf8 | ConvertFrom-Json -AsHashtable -Depth 100
Test-Condition ($package.contract_version -eq '0.2.0') 'contract_version must be 0.2.0.'
Test-Condition (-not [string]::IsNullOrWhiteSpace([string]$package.package_id)) 'package_id is required.'
Test-Condition (Test-Utc $package.created_at 'created_at') 'created_at must be an ISO 8601 UTC instant ending in Z.'

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
    Test-Condition ($package.Contains($collection.Name)) "Missing collection '$($collection.Name)'."
    $items = @($package[$collection.Name])
    $sets[$collection.Name] = Get-IdSet -Items $items -IdProperty $collection.Id -Label $collection.Name
}
$claimIds = $sets.claims
$claimVersionIds = Get-IdSet -Items @($package.claims) -IdProperty 'claim_version_id' -Label 'claim versions'
$componentIds = $sets.claim_components
$componentVersionIds = Get-IdSet -Items @($package.claim_components) -IdProperty 'claim_component_version_id' -Label 'claim component versions'
$sourceIds = $sets.sources
$versionIds = $sets.source_versions
$unitIds = $sets.evaluation_units
$evidenceIds = $sets.evidence_items
$nodeIds = $sets.provenance_nodes
$edgeIds = $sets.provenance_edges

foreach ($source in $package.sources) {
    Test-Condition ([string]$source.source_id -match '^src_[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}
    if ($null -ne $claim.supersedes_claim_version_id) {
        Test-Condition (Test-HasRef $claimVersionIds ([string]$claim.supersedes_claim_version_id)) "Claim version '$($claim.claim_version_id)' supersedes an unknown claim version."
        $priorClaim = @($package.claims | Where-Object { $_.claim_version_id -eq $claim.supersedes_claim_version_id })[0]
        Test-Condition ($priorClaim.claim_id -eq $claim.claim_id -and $priorClaim.claim_version -lt $claim.claim_version) 'Claim version supersession must reference an earlier version of the same claim.'
    }
}
foreach ($component in $package.claim_components) {
    Test-Condition (Test-HasRef $claimIds ([string]$component.claim_id)) "Component '$($component.claim_component_id)' references an unknown claim."
    Test-Condition (Test-HasRef $claimVersionIds ([string]$component.claim_version_id)) "Component '$($component.claim_component_id)' references an unknown claim version."
    $claimVersion = @($package.claims | Where-Object { $_.claim_version_id -eq $component.claim_version_id })[0]
    Test-Condition ($claimVersion.claim_id -eq $component.claim_id) 'Component and claim version identities do not match.'
    if ($null -ne $component.supersedes_component_version_id) {
        Test-Condition (Test-HasRef $componentVersionIds ([string]$component.supersedes_component_version_id)) 'Component supersedes an unknown component version.'
        $priorComponent = @($package.claim_components | Where-Object { $_.claim_component_version_id -eq $component.supersedes_component_version_id })[0]
        Test-Condition ($priorComponent.claim_component_id -eq $component.claim_component_id -and $priorComponent.version -lt $component.version) 'Component supersession must reference an earlier version of the same component.'
    }
}
foreach ($version in $package.source_versions) {
    Test-Condition (Test-HasRef $sourceIds ([string]$version.source_id)) "Source version '$($version.source_version_id)' references an unknown source."
    foreach ($field in @('published_at','first_detected_at','first_publicly_observed_at','retrieved_at','recorded_at')) {
        if ($null -ne $version[$field]) { Test-Condition (Test-Utc $version[$field] $field) "Source version '$($version.source_version_id)' has invalid UTC $field." }
    }
    if ($null -ne $version.retrieved_at -and $null -ne $version.first_detected_at) {
        Test-Condition ([DateTimeOffset]::Parse([string]$version.retrieved_at) -ge [DateTimeOffset]::Parse([string]$version.first_detected_at)) "Source version '$($version.source_version_id)' was retrieved before first detection."
    }
    if ($null -ne $version.supersedes_source_version_id) {
        Test-Condition (Test-HasRef $versionIds ([string]$version.supersedes_source_version_id)) "Source version supersedes an unknown version."
        Test-Condition ($version.supersedes_source_version_id -ne $version.source_version_id) 'A source version cannot supersede itself.'
    }
    if ($null -ne $version.content_hash) {
        Test-Condition ([string]$version.content_hash -match '^[A-Fa-f0-9]{64}$') "Source version '$($version.source_version_id)' has an invalid SHA-256 digest."
        Test-Condition ($version.hash_algorithm -eq 'SHA-256') "Source version '$($version.source_version_id)' hash algorithm must be SHA-256."
    }
}
foreach ($identity in $package.identity_assessments) {
    Test-Condition (Test-HasRef $sourceIds ([string]$identity.source_id)) "Identity assessment references an unknown source."
    foreach ($reference in @($identity.verification_evidence_refs)) { Test-Condition (Test-HasRef $evidenceIds ([string]$reference)) 'Identity assessment references unknown verification evidence.' }
    Test-Condition (Test-Utc $identity.assessment_cutoff 'assessment_cutoff') 'Identity assessment cutoff must be UTC.'
    Test-Condition (Test-Utc $identity.recorded_at 'recorded_at') 'Identity assessment recorded_at must be UTC.'
    if ($identity.identity -eq 'ANÓNIMA_PARA_EL_PÚBLICO') {
        Test-Condition ($identity.anonymous_to_public -eq $true) 'ANÓNIMA_PARA_EL_PÚBLICO requires anonymous_to_public=true.'
    }
    if ($identity.identity -eq 'ANÓNIMA_PARA_SINAYXA') {
        Test-Condition ($identity.anonymous_to_sinayxa -eq $true) 'ANÓNIMA_PARA_SINAYXA requires anonymous_to_sinayxa=true.'
    }
    if ($identity.identity_verified_by_sinayxa -eq $true) {
        Test-Condition ($identity.anonymous_to_sinayxa -eq $false) 'SINAYXA cannot verify an identity recorded as anonymous to SINAYXA.'
        Test-Condition (@($identity.verification_evidence_refs).Count -gt 0) 'SINAYXA identity verification requires evidence references.'
    }
}
foreach ($unit in $package.evaluation_units) {
    Test-Condition (Test-HasRef $claimIds ([string]$unit.claim_id)) "Evaluation unit references an unknown claim."
    Test-Condition (Test-HasRef $componentIds ([string]$unit.claim_component_id)) "Evaluation unit references an unknown component."
    Test-Condition (Test-HasRef $claimVersionIds ([string]$unit.claim_version_id)) 'Evaluation unit references an unknown claim version.'
    Test-Condition (Test-HasRef $componentVersionIds ([string]$unit.claim_component_version_id)) 'Evaluation unit references an unknown component version.'
    Test-Condition (Test-HasRef $sourceIds ([string]$unit.source_id)) "Evaluation unit references an unknown source."
    Test-Condition (Test-HasRef $versionIds ([string]$unit.source_version_id)) "Evaluation unit references an unknown source version."
    $component = @($package.claim_components | Where-Object { $_.claim_component_id -eq $unit.claim_component_id })[0]
    $version = @($package.source_versions | Where-Object { $_.source_version_id -eq $unit.source_version_id })[0]
    Test-Condition ($component.claim_id -eq $unit.claim_id) 'Evaluation unit claim and component do not match.'
    Test-Condition ($component.claim_version_id -eq $unit.claim_version_id -and $component.claim_component_version_id -eq $unit.claim_component_version_id) 'Evaluation unit is not bound to the exact claim/component versions.'
    Test-Condition ($version.source_id -eq $unit.source_id) 'Evaluation unit source and source version do not match.'
    Test-Condition (Test-Utc $unit.assessment_cutoff 'assessment_cutoff') 'Evaluation cutoff must be UTC.'
    Test-Condition ($unit.access_status -in @('PÚBLICO_LEGÍTIMO','PRIVADO_AUTORIZADO','SOSPECHA_DE_ACCESO_NO_AUTORIZADO','NO_DETERMINADO')) 'Unsupported access status.'
    Test-Condition ($unit.source_type -in @('PRIMARIA','SECUNDARIA','TERCIARIA','DESCONOCIDA')) 'Unsupported source type.'
}
foreach ($evidence in $package.evidence_items) {
    if ($null -ne $evidence.source_version_id) { Test-Condition (Test-HasRef $versionIds ([string]$evidence.source_version_id)) "Evidence '$($evidence.evidence_id)' references an unknown source version." }
    Test-Condition ($evidence.information_nature -in @('AFIRMACIÓN','INDICIO','RUMOR','POSIBLE_FILTRACIÓN','PUBLICACIÓN_OFICIAL','HECHO_OBSERVADO')) 'Unsupported information nature.'
    Test-Condition ($evidence.authenticity_status -in @('NO_APLICA','NO_VERIFICADA','AUTENTICADA','DISPUTADA','AUTENTICIDAD_REFUTADA')) 'Unsupported authenticity status.'
    $integrity = $evidence.integrity_check
    Test-Condition ($integrity.result -in @('MATCH','MISMATCH','NOT_CHECKED','UNAVAILABLE')) 'Unsupported integrity result.'
    if ($integrity.result -eq 'MATCH') {
        Test-Condition ($null -ne $integrity.expected_digest -and $integrity.expected_digest -eq $integrity.observed_digest) 'Integrity MATCH requires equal expected and observed digests.'
    }
    if ($integrity.result -eq 'MISMATCH') {
        Test-Condition ($null -ne $integrity.expected_digest -and $null -ne $integrity.observed_digest -and $integrity.expected_digest -ne $integrity.observed_digest) 'Integrity MISMATCH requires different known digests.'
    }
}
foreach ($link in $package.claim_evidence_links) {
    Test-Condition (Test-HasRef $claimIds ([string]$link.claim_id)) 'Evidence link references an unknown claim.'
    Test-Condition (Test-HasRef $componentIds ([string]$link.claim_component_id)) 'Evidence link references an unknown component.'
    Test-Condition (Test-HasRef $claimVersionIds ([string]$link.claim_version_id)) 'Evidence link references an unknown claim version.'
    Test-Condition (Test-HasRef $componentVersionIds ([string]$link.claim_component_version_id)) 'Evidence link references an unknown component version.'
    Test-Condition (Test-HasRef $evidenceIds ([string]$link.evidence_id)) 'Evidence link references an unknown evidence item.'
    $component = @($package.claim_components | Where-Object { $_.claim_component_id -eq $link.claim_component_id })[0]
    Test-Condition ($component.claim_id -eq $link.claim_id) 'Evidence link claim and component do not match.'
    Test-Condition ($component.claim_version_id -eq $link.claim_version_id -and $component.claim_component_version_id -eq $link.claim_component_version_id) 'Evidence link does not match the exact claim/component versions.'
}
foreach ($node in $package.provenance_nodes) {
    if ($node.node_type -eq 'SOURCE_VERSION') {
        Test-Condition (Test-HasRef $versionIds ([string]$node.entity_ref)) 'SOURCE_VERSION provenance node must reference an existing source version.'
    }
    if ($node.node_type -eq 'EVIDENCE_ITEM') {
        Test-Condition (Test-HasRef $evidenceIds ([string]$node.entity_ref)) 'EVIDENCE_ITEM provenance node must reference an existing evidence item.'
    }
    if ($node.node_type -eq 'UNKNOWN_ORIGIN') {
        Test-Condition ($null -eq $node.entity_ref) 'UNKNOWN_ORIGIN must not contain an entity reference or identity.'
    }
}
foreach ($edge in $package.provenance_edges) {
    Test-Condition (Test-HasRef $nodeIds ([string]$edge.dependent_node_id)) 'Provenance edge has an unknown dependent node.'
    Test-Condition (Test-HasRef $nodeIds ([string]$edge.origin_node_id)) 'Provenance edge has an unknown origin node.'
    Test-Condition (Test-HasRef $componentIds ([string]$edge.claim_component_id)) 'Provenance edge has an unknown claim component.'
    Test-Condition (Test-HasRef $componentVersionIds ([string]$edge.claim_component_version_id)) 'Provenance edge has an unknown component version.'
    foreach ($reference in @($edge.evidence_refs)) { Test-Condition (Test-HasRef $evidenceIds ([string]$reference)) 'Provenance edge references unknown supporting evidence.' }
    $edgeComponent = @($package.claim_components | Where-Object { $_.claim_component_version_id -eq $edge.claim_component_version_id })[0]
    Test-Condition ($edgeComponent.claim_component_id -eq $edge.claim_component_id) 'Provenance edge component version does not match its component.'
    Test-Condition ($edge.dependent_node_id -ne $edge.origin_node_id) 'A provenance edge cannot point to itself.'
    if ($edge.relation_type -eq 'ORIGEN_NO_DETERMINADO') {
        $origin = @($package.provenance_nodes | Where-Object { $_.node_id -eq $edge.origin_node_id })[0]
        Test-Condition ($origin.node_type -eq 'UNKNOWN_ORIGIN') 'ORIGEN_NO_DETERMINADO must point to an UNKNOWN_ORIGIN node.'
    }
    if ($null -ne $edge.recorded_at) { Test-Condition (Test-Utc $edge.recorded_at 'recorded_at') 'Provenance edge recorded_at must be UTC.' }
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
foreach ($nodeId in $inDegree.Keys) {
    if ($inDegree[$nodeId] -eq 0) { $queue.Enqueue([string]$nodeId) }
}
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
    Test-Condition ($factor.status -in @('SUSTENTADA','LIMITADA','DESFAVORABLE','DESCONOCIDA','NO_APLICA')) 'Factor status must use the approved #16 descriptive vocabulary.'
    Test-Condition (-not [string]::IsNullOrWhiteSpace([string]$factor.justification)) 'Factor assessment requires a justification.'
    foreach ($reference in @($factor.supporting_evidence_refs) + @($factor.contrary_evidence_refs)) {
        Test-Condition (Test-HasRef $evidenceIds ([string]$reference)) 'Factor assessment references unknown evidence.'
    }
    if ($factor.human_review_status -eq 'REVIEWED') { Test-Condition (Test-Utc $factor.reviewed_at 'reviewed_at') 'A reviewed factor assessment requires UTC reviewed_at.' }
    if ($factor.human_review_status -eq 'PENDING') { Test-Condition ($null -eq $factor.reviewed_at) 'A pending factor assessment cannot carry reviewed_at.' }
}
$expectedFactorDimensions = @(
    'RELATION_WITH_FACT','ACCESS_AND_PROXIMITY','SUBJECT_COMPETENCE','TRANSPARENCY_TRACEABILITY',
    'RELEVANT_ACCURACY_HISTORY','CORRECTIONS_ACCOUNTABILITY','INCENTIVES_CONFLICTS',
    'INTERNAL_CONSISTENCY','CONTRARY_EVIDENCE','TEMPORAL_ADEQUACY'
)
foreach ($unit in $package.evaluation_units) {
    $unitFactors = @($package.factor_assessments | Where-Object { $_.assessment_unit_id -eq $unit.assessment_unit_id })
    Test-Condition ($unitFactors.Count -eq $expectedFactorDimensions.Count) "Evaluation unit '$($unit.assessment_unit_id)' must contain exactly ten factor assessments."
    $actualDimensions = @($unitFactors.dimension | Sort-Object -Unique)
    $missingDimensions = @($expectedFactorDimensions | Where-Object { $_ -notin $actualDimensions })
    $unexpectedDimensions = @($actualDimensions | Where-Object { $_ -notin $expectedFactorDimensions })
    Test-Condition ($missingDimensions.Count -eq 0 -and $unexpectedDimensions.Count -eq 0) "Evaluation unit '$($unit.assessment_unit_id)' does not implement the exact #16 factor catalogue."
}

foreach ($assessment in $package.independence_assessments) {
    Test-Condition (Test-HasRef $claimIds ([string]$assessment.claim_id)) 'Independence assessment references an unknown claim.'
    Test-Condition (Test-HasRef $componentIds ([string]$assessment.claim_component_id)) 'Independence assessment references an unknown component.'
    Test-Condition (Test-HasRef $claimVersionIds ([string]$assessment.claim_version_id)) 'Independence assessment references an unknown claim version.'
    Test-Condition (Test-HasRef $componentVersionIds ([string]$assessment.claim_component_version_id)) 'Independence assessment references an unknown component version.'
    Test-Condition (@($assessment.assessment_unit_ids).Count -ge 2) 'Independence assessment requires at least two evaluation units.'
    foreach ($unitId in $assessment.assessment_unit_ids) { Test-Condition (Test-HasRef $unitIds ([string]$unitId)) 'Independence assessment references an unknown evaluation unit.' }
    $units = @($package.evaluation_units | Where-Object { $_.assessment_unit_id -in $assessment.assessment_unit_ids })
    Test-Condition (@($units | Where-Object { $_.claim_id -ne $assessment.claim_id -or $_.claim_component_id -ne $assessment.claim_component_id -or $_.claim_version_id -ne $assessment.claim_version_id -or $_.claim_component_version_id -ne $assessment.claim_component_version_id }).Count -eq 0) 'Independence assessment mixes claims or component versions.'
    foreach ($reference in @($assessment.supporting_evidence_refs)) { Test-Condition (Test-HasRef $evidenceIds ([string]$reference)) 'Independence assessment references unknown evidence.' }
    foreach ($reference in @($assessment.dependency_edge_refs)) { Test-Condition (Test-HasRef $edgeIds ([string]$reference)) 'Independence assessment references an unknown provenance edge.' }
    if ($assessment.status -eq 'INDEPENDIENTE') {
        Test-Condition (@($assessment.supporting_evidence_refs).Count -gt 0) 'INDEPENDIENTE requires positive supporting evidence.'
    }
    if ($assessment.human_review_status -eq 'REVIEWED') { Test-Condition (Test-Utc $assessment.reviewed_at 'reviewed_at') 'A reviewed independence assessment requires a UTC reviewed_at.' }
    if ($assessment.human_review_status -eq 'PENDING') { Test-Condition ($null -eq $assessment.reviewed_at) 'A pending independence assessment cannot carry reviewed_at.' }
    if ($assessment.status -eq 'DEPENDIENTE') {
        Test-Condition (@($assessment.dependency_edge_refs).Count -gt 0) 'DEPENDIENTE requires an evidenced dependency edge.'
    }
    if ($assessment.status -in @('INDEPENDIENTE','DEPENDIENTE')) { Test-Condition ($assessment.human_review_status -eq 'REVIEWED') 'A positive independence/dependence conclusion requires human review.' }
    Test-Condition ($assessment.status -in @('INDEPENDIENTE','DEPENDIENTE','DESCONOCIDA')) 'Unsupported independence status.'
}
foreach ($assessment in $package.claim_assessments) {
    Test-Condition (Test-HasRef $claimIds ([string]$assessment.claim_id)) 'Claim assessment references an unknown claim.'
    Test-Condition (Test-HasRef $componentIds ([string]$assessment.claim_component_id)) 'Claim assessment references an unknown component.'
    Test-Condition (Test-HasRef $claimVersionIds ([string]$assessment.claim_version_id)) 'Claim assessment references an unknown claim version.'
    Test-Condition (Test-HasRef $componentVersionIds ([string]$assessment.claim_component_version_id)) 'Claim assessment references an unknown component version.'
    $component = @($package.claim_components | Where-Object { $_.claim_component_id -eq $assessment.claim_component_id })[0]
    Test-Condition ($component.claim_id -eq $assessment.claim_id) 'Claim assessment claim and component do not match.'
    Test-Condition ($component.claim_version_id -eq $assessment.claim_version_id -and $component.claim_component_version_id -eq $assessment.claim_component_version_id) 'Claim assessment is not bound to the exact claim/component versions.'
    Test-Condition ($assessment.evidentiary_status -in @('NO_CORROBORADA','PARCIALMENTE_CORROBORADA','CORROBORADA','CONTRADICHA','REFUTADA','NO_RESUELTA')) 'Unsupported #15 evidentiary status.'
    Test-Condition ($assessment.attribution_status -in @('ATRIBUIDA','NO_ATRIBUIDA','NO_DETERMINADA')) 'Unsupported attribution status.'
    foreach ($reference in @($assessment.supporting_evidence_refs) + @($assessment.contrary_evidence_refs)) { Test-Condition (Test-HasRef $evidenceIds ([string]$reference)) 'Claim assessment references unknown evidence.' }
    foreach ($reference in @($assessment.independence_assessment_refs)) {
        Test-Condition (Test-HasRef $sets.independence_assessments ([string]$reference)) 'Claim assessment references unknown independence assessment.'
        $independence = @($package.independence_assessments | Where-Object { $_.independence_assessment_id -eq $reference })[0]
        Test-Condition ($independence.claim_id -eq $assessment.claim_id -and $independence.claim_component_id -eq $assessment.claim_component_id -and $independence.claim_version_id -eq $assessment.claim_version_id -and $independence.claim_component_version_id -eq $assessment.claim_component_version_id) 'Claim assessment references independence evidence for a different claim/component version.'
    }
    $linkedSupport = @($package.claim_evidence_links | Where-Object { $_.claim_id -eq $assessment.claim_id -and $_.claim_component_id -eq $assessment.claim_component_id -and $_.claim_version_id -eq $assessment.claim_version_id -and $_.claim_component_version_id -eq $assessment.claim_component_version_id -and $_.evidence_role -eq 'SUPPORTING' } | ForEach-Object { $_.evidence_id })
    $linkedContrary = @($package.claim_evidence_links | Where-Object { $_.claim_id -eq $assessment.claim_id -and $_.claim_component_id -eq $assessment.claim_component_id -and $_.claim_version_id -eq $assessment.claim_version_id -and $_.claim_component_version_id -eq $assessment.claim_component_version_id -and $_.evidence_role -eq 'CONTRARY' } | ForEach-Object { $_.evidence_id })
    foreach ($reference in @($assessment.supporting_evidence_refs)) { Test-Condition ($reference -in $linkedSupport) 'Supporting evidence reference has no SUPPORTING claim-evidence link for this component.' }
    foreach ($reference in @($assessment.contrary_evidence_refs)) { Test-Condition ($reference -in $linkedContrary) 'Contrary evidence reference has no CONTRARY claim-evidence link for this component.' }
    if ($assessment.evidentiary_status -eq 'CORROBORADA') {
        $supportingUnits = @()
        foreach ($evidenceId in @($assessment.supporting_evidence_refs)) {
            $evidenceItem = @($package.evidence_items | Where-Object { $_.evidence_id -eq $evidenceId })[0]
            if ($null -ne $evidenceItem.source_version_id) {
                $supportingUnits += @($package.evaluation_units | Where-Object {
                    $_.source_version_id -eq $evidenceItem.source_version_id -and
                    $_.claim_id -eq $assessment.claim_id -and
                    $_.claim_component_id -eq $assessment.claim_component_id -and
                    $_.claim_version_id -eq $assessment.claim_version_id -and
                    $_.claim_component_version_id -eq $assessment.claim_component_version_id
                })
            }
        }
        Test-Condition ($supportingUnits.Count -gt 0) 'CORROBORADA requires supporting evidence mapped to an evaluation unit for the exact component version.'
        $secondaryUnits = @($supportingUnits | Where-Object { $_.source_type -in @('SECUNDARIA','TERCIARIA','DESCONOCIDA') })
        if ($secondaryUnits.Count -gt 0) {
            $reviewedIndependent = @($package.independence_assessments | Where-Object {
                $_.independence_assessment_id -in $assessment.independence_assessment_refs -and
                $_.status -eq 'INDEPENDIENTE' -and $_.human_review_status -eq 'REVIEWED'
            })
            $covered = $false
            foreach ($independenceRecord in $reviewedIndependent) {
                $allCovered = @($secondaryUnits | Where-Object { $_.assessment_unit_id -notin $independenceRecord.assessment_unit_ids }).Count -eq 0
                if ($allCovered) { $covered = $true; break }
            }
            Test-Condition $covered 'Secondary/tertiary corroboration requires a reviewed INDEPENDIENTE assessment covering every supporting source unit for this component version.'
        }
    }
    if ($assessment.evidentiary_status -eq 'CONTRADICHA') { Test-Condition (@($assessment.supporting_evidence_refs).Count -gt 0 -and @($assessment.contrary_evidence_refs).Count -gt 0) 'CONTRADICHA requires traceable evidence on both sides.' }
    if ($assessment.evidentiary_status -eq 'REFUTADA') { Test-Condition (@($assessment.contrary_evidence_refs).Count -gt 0) 'REFUTADA requires direct, relevant contrary evidence.' }
    if ($assessment.evidentiary_status -eq 'CORROBORADA') { Test-Condition (@($assessment.supporting_evidence_refs).Count -gt 0) 'CORROBORADA requires supporting evidence.' }
    Test-Condition (Test-Utc $assessment.assessment_cutoff 'assessment_cutoff') 'Claim assessment cutoff must be UTC.'
    if ($null -ne $assessment.supersedes_assessment_id) {
        Test-Condition (Test-HasRef $sets.claim_assessments ([string]$assessment.supersedes_assessment_id)) 'Claim assessment supersedes an unknown assessment.'
        Test-Condition ($assessment.supersedes_assessment_id -ne $assessment.claim_assessment_id) 'Claim assessment cannot supersede itself.'
        $priorAssessment = @($package.claim_assessments | Where-Object { $_.claim_assessment_id -eq $assessment.supersedes_assessment_id })[0]
        Test-Condition ($priorAssessment.claim_id -eq $assessment.claim_id -and $priorAssessment.claim_component_id -eq $assessment.claim_component_id) 'Claim assessment supersession must remain within the same claim component.'
        Test-Condition ([DateTimeOffset]::Parse([string]$priorAssessment.assessment_cutoff) -lt [DateTimeOffset]::Parse([string]$assessment.assessment_cutoff)) 'A superseding claim assessment must have a later assessment cutoff.'
    }
    if ($assessment.human_review_status -eq 'REVIEWED') { Test-Condition (Test-Utc $assessment.reviewed_at 'reviewed_at') 'A reviewed claim assessment requires UTC reviewed_at.' }
    if ($assessment.human_review_status -eq 'PENDING') { Test-Condition ($null -eq $assessment.reviewed_at) 'A pending claim assessment cannot carry reviewed_at.' }
    if ($assessment.evidentiary_status -in @('CORROBORADA','PARCIALMENTE_CORROBORADA','CONTRADICHA','REFUTADA')) {
        Test-Condition ($assessment.human_review_status -eq 'REVIEWED') 'A conclusive probative state requires human review.'
    }
}
foreach ($record in $package.retention_records) {
    Test-Condition ((Test-HasRef $claimIds ([string]$record.subject_ref)) -or (Test-HasRef $claimVersionIds ([string]$record.subject_ref)) -or (Test-HasRef $componentIds ([string]$record.subject_ref)) -or (Test-HasRef $componentVersionIds ([string]$record.subject_ref)) -or (Test-HasRef $sourceIds ([string]$record.subject_ref)) -or (Test-HasRef $versionIds ([string]$record.subject_ref)) -or (Test-HasRef $evidenceIds ([string]$record.subject_ref))) 'Retention record references an unknown subject.'
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
    Test-Condition ((Test-HasRef $claimIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $claimVersionIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $componentIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $componentVersionIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sourceIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $versionIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $evidenceIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sets.claim_assessments ([string]$auditEvent.subject_ref))) 'Audit event references an unknown subject.'
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
    EvidenceItems = @($package.evidence_items).Count
    ProvenanceEdges = @($package.provenance_edges).Count
    CycleReviewRequired = $cyclesDetected
    SyntheticOnly = $true
    Scope = 'Structural and cross-reference conformance; not empirical truth, legal advice, or authorization to capture.'
} | Format-List
) 'Source identifiers must be opaque UUIDs with the src_ prefix.'
}
foreach ($claim in $package.claims) {
    if ($null -ne $claim.supersedes_claim_version_id) {
        Test-Condition (Test-HasRef $claimVersionIds ([string]$claim.supersedes_claim_version_id)) "Claim version '$($claim.claim_version_id)' supersedes an unknown claim version."
        $priorClaim = @($package.claims | Where-Object { $_.claim_version_id -eq $claim.supersedes_claim_version_id })[0]
        Test-Condition ($priorClaim.claim_id -eq $claim.claim_id -and $priorClaim.claim_version -lt $claim.claim_version) 'Claim version supersession must reference an earlier version of the same claim.'
    }
}
foreach ($component in $package.claim_components) {
    Test-Condition (Test-HasRef $claimIds ([string]$component.claim_id)) "Component '$($component.claim_component_id)' references an unknown claim."
    Test-Condition (Test-HasRef $claimVersionIds ([string]$component.claim_version_id)) "Component '$($component.claim_component_id)' references an unknown claim version."
    $claimVersion = @($package.claims | Where-Object { $_.claim_version_id -eq $component.claim_version_id })[0]
    Test-Condition ($claimVersion.claim_id -eq $component.claim_id) 'Component and claim version identities do not match.'
    if ($null -ne $component.supersedes_component_version_id) {
        Test-Condition (Test-HasRef $componentVersionIds ([string]$component.supersedes_component_version_id)) 'Component supersedes an unknown component version.'
        $priorComponent = @($package.claim_components | Where-Object { $_.claim_component_version_id -eq $component.supersedes_component_version_id })[0]
        Test-Condition ($priorComponent.claim_component_id -eq $component.claim_component_id -and $priorComponent.version -lt $component.version) 'Component supersession must reference an earlier version of the same component.'
    }
}
foreach ($version in $package.source_versions) {
    Test-Condition (Test-HasRef $sourceIds ([string]$version.source_id)) "Source version '$($version.source_version_id)' references an unknown source."
    foreach ($field in @('published_at','first_detected_at','first_publicly_observed_at','retrieved_at','recorded_at')) {
        if ($null -ne $version[$field]) { Test-Condition (Test-Utc $version[$field] $field) "Source version '$($version.source_version_id)' has invalid UTC $field." }
    }
    if ($null -ne $version.retrieved_at -and $null -ne $version.first_detected_at) {
        Test-Condition ([DateTimeOffset]::Parse([string]$version.retrieved_at) -ge [DateTimeOffset]::Parse([string]$version.first_detected_at)) "Source version '$($version.source_version_id)' was retrieved before first detection."
    }
    if ($null -ne $version.supersedes_source_version_id) {
        Test-Condition (Test-HasRef $versionIds ([string]$version.supersedes_source_version_id)) "Source version supersedes an unknown version."
        Test-Condition ($version.supersedes_source_version_id -ne $version.source_version_id) 'A source version cannot supersede itself.'
    }
    if ($null -ne $version.content_hash) {
        Test-Condition ([string]$version.content_hash -match '^[A-Fa-f0-9]{64}$') "Source version '$($version.source_version_id)' has an invalid SHA-256 digest."
        Test-Condition ($version.hash_algorithm -eq 'SHA-256') "Source version '$($version.source_version_id)' hash algorithm must be SHA-256."
    }
}
foreach ($identity in $package.identity_assessments) {
    Test-Condition (Test-HasRef $sourceIds ([string]$identity.source_id)) "Identity assessment references an unknown source."
    foreach ($reference in @($identity.verification_evidence_refs)) { Test-Condition (Test-HasRef $evidenceIds ([string]$reference)) 'Identity assessment references unknown verification evidence.' }
    Test-Condition (Test-Utc $identity.assessment_cutoff 'assessment_cutoff') 'Identity assessment cutoff must be UTC.'
    Test-Condition (Test-Utc $identity.recorded_at 'recorded_at') 'Identity assessment recorded_at must be UTC.'
    if ($identity.identity -eq 'ANÓNIMA_PARA_EL_PÚBLICO') {
        Test-Condition ($identity.anonymous_to_public -eq $true) 'ANÓNIMA_PARA_EL_PÚBLICO requires anonymous_to_public=true.'
    }
    if ($identity.identity -eq 'ANÓNIMA_PARA_SINAYXA') {
        Test-Condition ($identity.anonymous_to_sinayxa -eq $true) 'ANÓNIMA_PARA_SINAYXA requires anonymous_to_sinayxa=true.'
    }
    if ($identity.identity_verified_by_sinayxa -eq $true) {
        Test-Condition ($identity.anonymous_to_sinayxa -eq $false) 'SINAYXA cannot verify an identity recorded as anonymous to SINAYXA.'
        Test-Condition (@($identity.verification_evidence_refs).Count -gt 0) 'SINAYXA identity verification requires evidence references.'
    }
}
foreach ($unit in $package.evaluation_units) {
    Test-Condition (Test-HasRef $claimIds ([string]$unit.claim_id)) "Evaluation unit references an unknown claim."
    Test-Condition (Test-HasRef $componentIds ([string]$unit.claim_component_id)) "Evaluation unit references an unknown component."
    Test-Condition (Test-HasRef $claimVersionIds ([string]$unit.claim_version_id)) 'Evaluation unit references an unknown claim version.'
    Test-Condition (Test-HasRef $componentVersionIds ([string]$unit.claim_component_version_id)) 'Evaluation unit references an unknown component version.'
    Test-Condition (Test-HasRef $sourceIds ([string]$unit.source_id)) "Evaluation unit references an unknown source."
    Test-Condition (Test-HasRef $versionIds ([string]$unit.source_version_id)) "Evaluation unit references an unknown source version."
    $component = @($package.claim_components | Where-Object { $_.claim_component_id -eq $unit.claim_component_id })[0]
    $version = @($package.source_versions | Where-Object { $_.source_version_id -eq $unit.source_version_id })[0]
    Test-Condition ($component.claim_id -eq $unit.claim_id) 'Evaluation unit claim and component do not match.'
    Test-Condition ($component.claim_version_id -eq $unit.claim_version_id -and $component.claim_component_version_id -eq $unit.claim_component_version_id) 'Evaluation unit is not bound to the exact claim/component versions.'
    Test-Condition ($version.source_id -eq $unit.source_id) 'Evaluation unit source and source version do not match.'
    Test-Condition (Test-Utc $unit.assessment_cutoff 'assessment_cutoff') 'Evaluation cutoff must be UTC.'
    Test-Condition ($unit.access_status -in @('PÚBLICO_LEGÍTIMO','PRIVADO_AUTORIZADO','SOSPECHA_DE_ACCESO_NO_AUTORIZADO','NO_DETERMINADO')) 'Unsupported access status.'
    Test-Condition ($unit.source_type -in @('PRIMARIA','SECUNDARIA','TERCIARIA','DESCONOCIDA')) 'Unsupported source type.'
}
foreach ($evidence in $package.evidence_items) {
    if ($null -ne $evidence.source_version_id) { Test-Condition (Test-HasRef $versionIds ([string]$evidence.source_version_id)) "Evidence '$($evidence.evidence_id)' references an unknown source version." }
    Test-Condition ($evidence.information_nature -in @('AFIRMACIÓN','INDICIO','RUMOR','POSIBLE_FILTRACIÓN','PUBLICACIÓN_OFICIAL','HECHO_OBSERVADO')) 'Unsupported information nature.'
    Test-Condition ($evidence.authenticity_status -in @('NO_APLICA','NO_VERIFICADA','AUTENTICADA','DISPUTADA','AUTENTICIDAD_REFUTADA')) 'Unsupported authenticity status.'
    $integrity = $evidence.integrity_check
    Test-Condition ($integrity.result -in @('MATCH','MISMATCH','NOT_CHECKED','UNAVAILABLE')) 'Unsupported integrity result.'
    if ($integrity.result -eq 'MATCH') {
        Test-Condition ($null -ne $integrity.expected_digest -and $integrity.expected_digest -eq $integrity.observed_digest) 'Integrity MATCH requires equal expected and observed digests.'
    }
    if ($integrity.result -eq 'MISMATCH') {
        Test-Condition ($null -ne $integrity.expected_digest -and $null -ne $integrity.observed_digest -and $integrity.expected_digest -ne $integrity.observed_digest) 'Integrity MISMATCH requires different known digests.'
    }
}
foreach ($link in $package.claim_evidence_links) {
    Test-Condition (Test-HasRef $claimIds ([string]$link.claim_id)) 'Evidence link references an unknown claim.'
    Test-Condition (Test-HasRef $componentIds ([string]$link.claim_component_id)) 'Evidence link references an unknown component.'
    Test-Condition (Test-HasRef $claimVersionIds ([string]$link.claim_version_id)) 'Evidence link references an unknown claim version.'
    Test-Condition (Test-HasRef $componentVersionIds ([string]$link.claim_component_version_id)) 'Evidence link references an unknown component version.'
    Test-Condition (Test-HasRef $evidenceIds ([string]$link.evidence_id)) 'Evidence link references an unknown evidence item.'
    $component = @($package.claim_components | Where-Object { $_.claim_component_id -eq $link.claim_component_id })[0]
    Test-Condition ($component.claim_id -eq $link.claim_id) 'Evidence link claim and component do not match.'
    Test-Condition ($component.claim_version_id -eq $link.claim_version_id -and $component.claim_component_version_id -eq $link.claim_component_version_id) 'Evidence link does not match the exact claim/component versions.'
}
foreach ($node in $package.provenance_nodes) {
    if ($node.node_type -eq 'SOURCE_VERSION') {
        Test-Condition (Test-HasRef $versionIds ([string]$node.entity_ref)) 'SOURCE_VERSION provenance node must reference an existing source version.'
    }
    if ($node.node_type -eq 'EVIDENCE_ITEM') {
        Test-Condition (Test-HasRef $evidenceIds ([string]$node.entity_ref)) 'EVIDENCE_ITEM provenance node must reference an existing evidence item.'
    }
    if ($node.node_type -eq 'UNKNOWN_ORIGIN') {
        Test-Condition ($null -eq $node.entity_ref) 'UNKNOWN_ORIGIN must not contain an entity reference or identity.'
    }
}
foreach ($edge in $package.provenance_edges) {
    Test-Condition (Test-HasRef $nodeIds ([string]$edge.dependent_node_id)) 'Provenance edge has an unknown dependent node.'
    Test-Condition (Test-HasRef $nodeIds ([string]$edge.origin_node_id)) 'Provenance edge has an unknown origin node.'
    Test-Condition (Test-HasRef $componentIds ([string]$edge.claim_component_id)) 'Provenance edge has an unknown claim component.'
    Test-Condition (Test-HasRef $componentVersionIds ([string]$edge.claim_component_version_id)) 'Provenance edge has an unknown component version.'
    foreach ($reference in @($edge.evidence_refs)) { Test-Condition (Test-HasRef $evidenceIds ([string]$reference)) 'Provenance edge references unknown supporting evidence.' }
    $edgeComponent = @($package.claim_components | Where-Object { $_.claim_component_version_id -eq $edge.claim_component_version_id })[0]
    Test-Condition ($edgeComponent.claim_component_id -eq $edge.claim_component_id) 'Provenance edge component version does not match its component.'
    Test-Condition ($edge.dependent_node_id -ne $edge.origin_node_id) 'A provenance edge cannot point to itself.'
    if ($edge.relation_type -eq 'ORIGEN_NO_DETERMINADO') {
        $origin = @($package.provenance_nodes | Where-Object { $_.node_id -eq $edge.origin_node_id })[0]
        Test-Condition ($origin.node_type -eq 'UNKNOWN_ORIGIN') 'ORIGEN_NO_DETERMINADO must point to an UNKNOWN_ORIGIN node.'
    }
    if ($null -ne $edge.recorded_at) { Test-Condition (Test-Utc $edge.recorded_at 'recorded_at') 'Provenance edge recorded_at must be UTC.' }
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
foreach ($nodeId in $inDegree.Keys) {
    if ($inDegree[$nodeId] -eq 0) { $queue.Enqueue([string]$nodeId) }
}
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
    Test-Condition ($factor.status -in @('SUSTENTADA','LIMITADA','DESFAVORABLE','DESCONOCIDA','NO_APLICA')) 'Factor status must use the approved #16 descriptive vocabulary.'
    Test-Condition (-not [string]::IsNullOrWhiteSpace([string]$factor.justification)) 'Factor assessment requires a justification.'
    foreach ($reference in @($factor.supporting_evidence_refs) + @($factor.contrary_evidence_refs)) {
        Test-Condition (Test-HasRef $evidenceIds ([string]$reference)) 'Factor assessment references unknown evidence.'
    }
    if ($factor.human_review_status -eq 'REVIEWED') { Test-Condition (Test-Utc $factor.reviewed_at 'reviewed_at') 'A reviewed factor assessment requires UTC reviewed_at.' }
    if ($factor.human_review_status -eq 'PENDING') { Test-Condition ($null -eq $factor.reviewed_at) 'A pending factor assessment cannot carry reviewed_at.' }
}
$expectedFactorDimensions = @(
    'RELATION_WITH_FACT','ACCESS_AND_PROXIMITY','SUBJECT_COMPETENCE','TRANSPARENCY_TRACEABILITY',
    'RELEVANT_ACCURACY_HISTORY','CORRECTIONS_ACCOUNTABILITY','INCENTIVES_CONFLICTS',
    'INTERNAL_CONSISTENCY','CONTRARY_EVIDENCE','TEMPORAL_ADEQUACY'
)
foreach ($unit in $package.evaluation_units) {
    $unitFactors = @($package.factor_assessments | Where-Object { $_.assessment_unit_id -eq $unit.assessment_unit_id })
    Test-Condition ($unitFactors.Count -eq $expectedFactorDimensions.Count) "Evaluation unit '$($unit.assessment_unit_id)' must contain exactly ten factor assessments."
    $actualDimensions = @($unitFactors.dimension | Sort-Object -Unique)
    $missingDimensions = @($expectedFactorDimensions | Where-Object { $_ -notin $actualDimensions })
    $unexpectedDimensions = @($actualDimensions | Where-Object { $_ -notin $expectedFactorDimensions })
    Test-Condition ($missingDimensions.Count -eq 0 -and $unexpectedDimensions.Count -eq 0) "Evaluation unit '$($unit.assessment_unit_id)' does not implement the exact #16 factor catalogue."
}

foreach ($assessment in $package.independence_assessments) {
    Test-Condition (Test-HasRef $claimIds ([string]$assessment.claim_id)) 'Independence assessment references an unknown claim.'
    Test-Condition (Test-HasRef $componentIds ([string]$assessment.claim_component_id)) 'Independence assessment references an unknown component.'
    Test-Condition (Test-HasRef $claimVersionIds ([string]$assessment.claim_version_id)) 'Independence assessment references an unknown claim version.'
    Test-Condition (Test-HasRef $componentVersionIds ([string]$assessment.claim_component_version_id)) 'Independence assessment references an unknown component version.'
    Test-Condition (@($assessment.assessment_unit_ids).Count -ge 2) 'Independence assessment requires at least two evaluation units.'
    foreach ($unitId in $assessment.assessment_unit_ids) { Test-Condition (Test-HasRef $unitIds ([string]$unitId)) 'Independence assessment references an unknown evaluation unit.' }
    $units = @($package.evaluation_units | Where-Object { $_.assessment_unit_id -in $assessment.assessment_unit_ids })
    Test-Condition (@($units | Where-Object { $_.claim_id -ne $assessment.claim_id -or $_.claim_component_id -ne $assessment.claim_component_id -or $_.claim_version_id -ne $assessment.claim_version_id -or $_.claim_component_version_id -ne $assessment.claim_component_version_id }).Count -eq 0) 'Independence assessment mixes claims or component versions.'
    foreach ($reference in @($assessment.supporting_evidence_refs)) { Test-Condition (Test-HasRef $evidenceIds ([string]$reference)) 'Independence assessment references unknown evidence.' }
    foreach ($reference in @($assessment.dependency_edge_refs)) { Test-Condition (Test-HasRef $edgeIds ([string]$reference)) 'Independence assessment references an unknown provenance edge.' }
    if ($assessment.status -eq 'INDEPENDIENTE') {
        Test-Condition (@($assessment.supporting_evidence_refs).Count -gt 0) 'INDEPENDIENTE requires positive supporting evidence.'
    }
    if ($assessment.human_review_status -eq 'REVIEWED') { Test-Condition (Test-Utc $assessment.reviewed_at 'reviewed_at') 'A reviewed independence assessment requires a UTC reviewed_at.' }
    if ($assessment.human_review_status -eq 'PENDING') { Test-Condition ($null -eq $assessment.reviewed_at) 'A pending independence assessment cannot carry reviewed_at.' }
    if ($assessment.status -eq 'DEPENDIENTE') {
        Test-Condition (@($assessment.dependency_edge_refs).Count -gt 0) 'DEPENDIENTE requires an evidenced dependency edge.'
    }
    if ($assessment.status -in @('INDEPENDIENTE','DEPENDIENTE')) { Test-Condition ($assessment.human_review_status -eq 'REVIEWED') 'A positive independence/dependence conclusion requires human review.' }
    Test-Condition ($assessment.status -in @('INDEPENDIENTE','DEPENDIENTE','DESCONOCIDA')) 'Unsupported independence status.'
}
foreach ($assessment in $package.claim_assessments) {
    Test-Condition (Test-HasRef $claimIds ([string]$assessment.claim_id)) 'Claim assessment references an unknown claim.'
    Test-Condition (Test-HasRef $componentIds ([string]$assessment.claim_component_id)) 'Claim assessment references an unknown component.'
    Test-Condition (Test-HasRef $claimVersionIds ([string]$assessment.claim_version_id)) 'Claim assessment references an unknown claim version.'
    Test-Condition (Test-HasRef $componentVersionIds ([string]$assessment.claim_component_version_id)) 'Claim assessment references an unknown component version.'
    $component = @($package.claim_components | Where-Object { $_.claim_component_id -eq $assessment.claim_component_id })[0]
    Test-Condition ($component.claim_id -eq $assessment.claim_id) 'Claim assessment claim and component do not match.'
    Test-Condition ($component.claim_version_id -eq $assessment.claim_version_id -and $component.claim_component_version_id -eq $assessment.claim_component_version_id) 'Claim assessment is not bound to the exact claim/component versions.'
    Test-Condition ($assessment.evidentiary_status -in @('NO_CORROBORADA','PARCIALMENTE_CORROBORADA','CORROBORADA','CONTRADICHA','REFUTADA','NO_RESUELTA')) 'Unsupported #15 evidentiary status.'
    Test-Condition ($assessment.attribution_status -in @('ATRIBUIDA','NO_ATRIBUIDA','NO_DETERMINADA')) 'Unsupported attribution status.'
    foreach ($reference in @($assessment.supporting_evidence_refs) + @($assessment.contrary_evidence_refs)) { Test-Condition (Test-HasRef $evidenceIds ([string]$reference)) 'Claim assessment references unknown evidence.' }
    foreach ($reference in @($assessment.independence_assessment_refs)) {
        Test-Condition (Test-HasRef $sets.independence_assessments ([string]$reference)) 'Claim assessment references unknown independence assessment.'
        $independence = @($package.independence_assessments | Where-Object { $_.independence_assessment_id -eq $reference })[0]
        Test-Condition ($independence.claim_id -eq $assessment.claim_id -and $independence.claim_component_id -eq $assessment.claim_component_id -and $independence.claim_version_id -eq $assessment.claim_version_id -and $independence.claim_component_version_id -eq $assessment.claim_component_version_id) 'Claim assessment references independence evidence for a different claim/component version.'
    }
    $linkedSupport = @($package.claim_evidence_links | Where-Object { $_.claim_id -eq $assessment.claim_id -and $_.claim_component_id -eq $assessment.claim_component_id -and $_.claim_version_id -eq $assessment.claim_version_id -and $_.claim_component_version_id -eq $assessment.claim_component_version_id -and $_.evidence_role -eq 'SUPPORTING' } | ForEach-Object { $_.evidence_id })
    $linkedContrary = @($package.claim_evidence_links | Where-Object { $_.claim_id -eq $assessment.claim_id -and $_.claim_component_id -eq $assessment.claim_component_id -and $_.claim_version_id -eq $assessment.claim_version_id -and $_.claim_component_version_id -eq $assessment.claim_component_version_id -and $_.evidence_role -eq 'CONTRARY' } | ForEach-Object { $_.evidence_id })
    foreach ($reference in @($assessment.supporting_evidence_refs)) { Test-Condition ($reference -in $linkedSupport) 'Supporting evidence reference has no SUPPORTING claim-evidence link for this component.' }
    foreach ($reference in @($assessment.contrary_evidence_refs)) { Test-Condition ($reference -in $linkedContrary) 'Contrary evidence reference has no CONTRARY claim-evidence link for this component.' }
    if ($assessment.evidentiary_status -eq 'CORROBORADA') {
        $supportingUnits = @()
        foreach ($evidenceId in @($assessment.supporting_evidence_refs)) {
            $evidenceItem = @($package.evidence_items | Where-Object { $_.evidence_id -eq $evidenceId })[0]
            if ($null -ne $evidenceItem.source_version_id) {
                $supportingUnits += @($package.evaluation_units | Where-Object {
                    $_.source_version_id -eq $evidenceItem.source_version_id -and
                    $_.claim_id -eq $assessment.claim_id -and
                    $_.claim_component_id -eq $assessment.claim_component_id -and
                    $_.claim_version_id -eq $assessment.claim_version_id -and
                    $_.claim_component_version_id -eq $assessment.claim_component_version_id
                })
            }
        }
        Test-Condition ($supportingUnits.Count -gt 0) 'CORROBORADA requires supporting evidence mapped to an evaluation unit for the exact component version.'
        $secondaryUnits = @($supportingUnits | Where-Object { $_.source_type -in @('SECUNDARIA','TERCIARIA','DESCONOCIDA') })
        if ($secondaryUnits.Count -gt 0) {
            $reviewedIndependent = @($package.independence_assessments | Where-Object {
                $_.independence_assessment_id -in $assessment.independence_assessment_refs -and
                $_.status -eq 'INDEPENDIENTE' -and $_.human_review_status -eq 'REVIEWED'
            })
            $covered = $false
            foreach ($independenceRecord in $reviewedIndependent) {
                $allCovered = @($secondaryUnits | Where-Object { $_.assessment_unit_id -notin $independenceRecord.assessment_unit_ids }).Count -eq 0
                if ($allCovered) { $covered = $true; break }
            }
            Test-Condition $covered 'Secondary/tertiary corroboration requires a reviewed INDEPENDIENTE assessment covering every supporting source unit for this component version.'
        }
    }
    if ($assessment.evidentiary_status -eq 'CONTRADICHA') { Test-Condition (@($assessment.supporting_evidence_refs).Count -gt 0 -and @($assessment.contrary_evidence_refs).Count -gt 0) 'CONTRADICHA requires traceable evidence on both sides.' }
    if ($assessment.evidentiary_status -eq 'REFUTADA') { Test-Condition (@($assessment.contrary_evidence_refs).Count -gt 0) 'REFUTADA requires direct, relevant contrary evidence.' }
    if ($assessment.evidentiary_status -eq 'CORROBORADA') { Test-Condition (@($assessment.supporting_evidence_refs).Count -gt 0) 'CORROBORADA requires supporting evidence.' }
    Test-Condition (Test-Utc $assessment.assessment_cutoff 'assessment_cutoff') 'Claim assessment cutoff must be UTC.'
    if ($null -ne $assessment.supersedes_assessment_id) {
        Test-Condition (Test-HasRef $sets.claim_assessments ([string]$assessment.supersedes_assessment_id)) 'Claim assessment supersedes an unknown assessment.'
        Test-Condition ($assessment.supersedes_assessment_id -ne $assessment.claim_assessment_id) 'Claim assessment cannot supersede itself.'
        $priorAssessment = @($package.claim_assessments | Where-Object { $_.claim_assessment_id -eq $assessment.supersedes_assessment_id })[0]
        Test-Condition ($priorAssessment.claim_id -eq $assessment.claim_id -and $priorAssessment.claim_component_id -eq $assessment.claim_component_id) 'Claim assessment supersession must remain within the same claim component.'
        Test-Condition ([DateTimeOffset]::Parse([string]$priorAssessment.assessment_cutoff) -lt [DateTimeOffset]::Parse([string]$assessment.assessment_cutoff)) 'A superseding claim assessment must have a later assessment cutoff.'
    }
    if ($assessment.human_review_status -eq 'REVIEWED') { Test-Condition (Test-Utc $assessment.reviewed_at 'reviewed_at') 'A reviewed claim assessment requires UTC reviewed_at.' }
    if ($assessment.human_review_status -eq 'PENDING') { Test-Condition ($null -eq $assessment.reviewed_at) 'A pending claim assessment cannot carry reviewed_at.' }
    if ($assessment.evidentiary_status -in @('CORROBORADA','PARCIALMENTE_CORROBORADA','CONTRADICHA','REFUTADA')) {
        Test-Condition ($assessment.human_review_status -eq 'REVIEWED') 'A conclusive probative state requires human review.'
    }
}
foreach ($record in $package.retention_records) {
    Test-Condition ((Test-HasRef $claimIds ([string]$record.subject_ref)) -or (Test-HasRef $claimVersionIds ([string]$record.subject_ref)) -or (Test-HasRef $componentIds ([string]$record.subject_ref)) -or (Test-HasRef $componentVersionIds ([string]$record.subject_ref)) -or (Test-HasRef $sourceIds ([string]$record.subject_ref)) -or (Test-HasRef $versionIds ([string]$record.subject_ref)) -or (Test-HasRef $evidenceIds ([string]$record.subject_ref))) 'Retention record references an unknown subject.'
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
    Test-Condition ((Test-HasRef $claimIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $claimVersionIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $componentIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $componentVersionIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sourceIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $versionIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $evidenceIds ([string]$auditEvent.subject_ref)) -or (Test-HasRef $sets.claim_assessments ([string]$auditEvent.subject_ref))) 'Audit event references an unknown subject.'
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
    EvidenceItems = @($package.evidence_items).Count
    ProvenanceEdges = @($package.provenance_edges).Count
    CycleReviewRequired = $cyclesDetected
    SyntheticOnly = $true
    Scope = 'Structural and cross-reference conformance; not empirical truth, legal advice, or authorization to capture.'
} | Format-List
