 [CmdletBinding()]
param([Parameter()][string]$FixturePath)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($FixturePath)) {
    $FixturePath = Join-Path $PSScriptRoot '..\..\tests\fixtures\methodology\source-independence\s01-s16-synthetic-conformance-v1.0.0.json'
}
function Assert-Condition {
    param([bool]$Condition,[string]$Message)
    if (-not $Condition) { throw $Message }
}
$resolved = (Resolve-Path -LiteralPath $FixturePath).Path
try { $fixture = Get-Content -LiteralPath $resolved -Raw -Encoding utf8 | ConvertFrom-Json -Depth 50 }
catch { throw "Fixture is not valid JSON: $($_.Exception.Message)" }
Assert-Condition ($fixture.schema_version -eq '1.0.0') 'Unsupported schema_version.'
Assert-Condition ($fixture.package_id -eq 'SINAYXA-SOURCE-INDEPENDENCE-S01-S16-001') 'Unexpected package_id.'
Assert-Condition ($fixture.status -eq 'SYNTHETIC_TEST_FIXTURE_NOT_REAL_WORLD_EVIDENCE') 'Fixture must be explicitly synthetic.'
Assert-Condition ($fixture.cases.Count -eq 16) "Expected 16 cases; found $($fixture.cases.Count)."
$expectedIds = @(1..16 | ForEach-Object { 'S{0:D2}' -f $_ })
$ids = @($fixture.cases | ForEach-Object { [string]$_.id })
Assert-Condition (($ids | Sort-Object -Unique).Count -eq 16) 'Case identifiers must be unique.'
Assert-Condition ((@($ids | Sort-Object) -join ',') -eq (@($expectedIds | Sort-Object) -join ',')) 'Fixture must contain exactly S01-S16.'
$allowedIndependence = @('INDEPENDIENTE','DEPENDIENTE','DESCONOCIDA')
$allowedInstitutional = @('OFICIAL','NO_INSTITUCIONAL','DESCONOCIDO')
foreach ($case in $fixture.cases) {
    $id = [string]$case.id
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($case.scenario)) "${id}: scenario is required."
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($case.claim_component_id)) "${id}: claim_component_id is required."
    Assert-Condition ($fixture.allowed.source_type -contains [string]$case.source_type) "${id}: invalid source_type."
    Assert-Condition ($fixture.allowed.knowledge_basis -contains [string]$case.knowledge_basis) "${id}: invalid knowledge_basis."
    Assert-Condition ($fixture.allowed.identity -contains [string]$case.identity) "${id}: invalid identity."
    Assert-Condition ($allowedInstitutional -contains [string]$case.institutional_character) "${id}: invalid institutional_character."
    Assert-Condition ($fixture.allowed.dissemination -contains [string]$case.dissemination) "${id}: invalid dissemination."
    Assert-Condition ($allowedIndependence -contains [string]$case.independence) "${id}: invalid independence."
    Assert-Condition ($null -ne $case.provenance_edges) "${id}: provenance_edges must be present, even when empty."
    foreach ($edge in $case.provenance_edges) {
        Assert-Condition (-not [string]::IsNullOrWhiteSpace($edge.from)) "${id}: provenance edge requires from."
        Assert-Condition (-not [string]::IsNullOrWhiteSpace($edge.relation)) "${id}: provenance edge requires relation."
        Assert-Condition (-not [string]::IsNullOrWhiteSpace($edge.to)) "${id}: provenance edge requires to."
    }
    Assert-Condition ($case.expected.PSObject.Properties.Name -contains 'independent_origins') "${id}: expected.independent_origins must be explicit, including null."
    Assert-Condition ($case.expected.PSObject.Properties.Name -contains 'corroboration_count_increment') "${id}: expected.corroboration_count_increment must be explicit, including null."
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($case.expected.guardrail)) "${id}: expected.guardrail is required."
    if ($case.independence -eq 'INDEPENDIENTE') {
        Assert-Condition ($case.independence_basis.Count -gt 0) "${id}: INDEPENDIENTE requires positive, component-specific evidence."
        Assert-Condition ($case.provenance_edges.Count -gt 0) "${id}: INDEPENDIENTE requires traceable provenance edges."
    }
    if ($case.independence -eq 'DEPENDIENTE') {
        Assert-Condition ($case.provenance_edges.Count -gt 0) "${id}: DEPENDIENTE requires an evidenced dependency edge."
    }
    if ($case.independence -ne 'INDEPENDIENTE') {
        Assert-Condition ($case.expected.corroboration_count_increment -ne 1) "${id}: only INDEPENDIENTE with positive evidence may increment independent corroboration."
    }
}
$byId = @{}
foreach ($case in $fixture.cases) { $byId[[string]$case.id] = $case }

# Scenario-specific expected outcomes: guardrails are executable, not prose-only.
Assert-Condition ($byId.S01.expected.publication_count -eq 6 -and $byId.S01.expected.independent_origins -eq 1) 'S01 must count six publications as one origin.'
Assert-Condition ($byId.S02.expected.shared_origin_count -eq 1 -and $byId.S02.expected.identity_scope -eq 'ANÓNIMA_PARA_EL_PÚBLICO') 'S02 must preserve the shared anonymous origin and its identity scope.'
Assert-Condition (($byId.S03.expected.scope_confirmed -join ',') -eq 'filing' -and ($byId.S03.expected.scope_not_confirmed -join ',') -eq 'approval' -and $byId.S03.expected.evidence_effect -eq 'RECORDS_FILING_ONLY') 'S03 must not turn a filing into an approval.'
Assert-Condition ($byId.S04.independence -eq 'INDEPENDIENTE' -and $byId.S04.expected.independent_origins -eq 2 -and $byId.S04.expected.corroboration_count_increment -eq 1) 'S04 must require and record two separately traced origins.'
Assert-Condition ($byId.S05.expected.supports_contract_interpretation -eq $true -and $byId.S05.expected.supports_execution -eq $false) 'S05 must separate contract interpretation from execution.'
Assert-Condition ($byId.S06.expected.version_history.preserve_prior_versions -eq $true -and $byId.S06.expected.version_history.other_components_automatically_invalidated -eq $false -and ($byId.S06.expected.version_history.corrected_components -join ',') -eq 'amount') 'S06 must preserve versions and limit correction to the affected component.'
Assert-Condition ($byId.S07.expected.access_claim_verified -eq $false -and $byId.S07.independence -eq 'DESCONOCIDA') 'S07 must not treat declared access as verified.'
Assert-Condition ($byId.S08.expected.shared_document_origin -eq $true -and $byId.S08.independence -eq 'DEPENDIENTE') 'S08 must preserve common-document dependency.'
Assert-Condition ($byId.S09.expected.shared_employer_does_not_imply_dependency -eq $true -and $byId.S09.expected.independent_origins -eq 2) 'S09 must not infer dependency from shared employer.'
Assert-Condition ($byId.S10.expected.declaration_recorded -eq $true -and $byId.S10.expected.underlying_evidence_available -eq $false -and $byId.S10.expected.probative_effect -eq 'ATTRIBUTED_DENIAL_ONLY' -and $byId.S10.expected.claim_refuted -eq $false) 'S10 must record an unsupported official denial without treating it as refutation.'
Assert-Condition ($byId.S11.expected.document_authenticity -eq 'AUTHENTICATED' -and $byId.S11.expected.source_track_record_separate -eq $true -and $byId.S11.expected.past_errors_automatically_invalidate_document -eq $false) 'S11 must assess document authenticity separately from source history.'
Assert-Condition ($byId.S12.expected.prestige_used_as_evidence -eq $false -and $byId.S12.knowledge_basis -eq 'DESCONOCIDA') 'S12 must not use prestige as evidence.'
Assert-Condition ($byId.S13.expected.cycle_detected -eq $true -and $byId.S13.independence -eq 'DEPENDIENTE') 'S13 must detect circular citation dependency.'
Assert-Condition (($byId.S14.expected.corroborated_components -join ',') -eq 'entity,date' -and ($byId.S14.expected.unresolved_components -join ',') -eq 'amount' -and $byId.S14.expected.corroboration_count_increment -eq 0) 'S14 must not corroborate the disputed amount.'
Assert-Condition ($byId.S15.expected.editor_identity_verification_transferred -eq $false -and $byId.S15.independence -eq 'DESCONOCIDA') 'S15 must not transfer editorial identity verification to SINAYXA.'
Assert-Condition ($byId.S16.expected.independent_analytical_processes -eq 2 -and $byId.S16.expected.independent_data_origins -eq 1) 'S16 must separate independent analytical processes from shared data origin.'
Assert-Condition ($byId.S01.independence -eq 'DEPENDIENTE' -and $byId.S01.expected.independent_origins -eq 1) 'S01 must collapse six syndications to one origin.'
Assert-Condition ($byId.S02.independence -eq 'DEPENDIENTE' -and $byId.S02.identity -eq 'ANÓNIMA_PARA_EL_PÚBLICO') 'S02 must preserve common anonymous spokesperson dependency.'
Assert-Condition ($byId.S03.source_type -eq 'PRIMARIA' -and $byId.S03.institutional_character -eq 'OFICIAL') 'S03 must separate primary type from institutional character.'
Assert-Condition ($byId.S07.knowledge_basis -eq 'ACCESO_DIRECTO_DECLARADO' -and $byId.S07.independence -eq 'DESCONOCIDA') 'S07 must not treat declared access as verified independence.'
Assert-Condition ($byId.S04.expected.independent_origins -eq 2) 'S04 must represent both separately traced source paths.'
Assert-Condition ($byId.S09.independence -eq 'INDEPENDIENTE' -and $byId.S09.independence_basis.Count -gt 0) 'S09 must require evidence despite shared employer.'
Assert-Condition ($byId.S13.independence -eq 'DEPENDIENTE' -and $byId.S13.expected.cycle_detected -eq $true) 'S13 must detect citation cycles.'
Assert-Condition ($byId.S16.expected.independent_analytical_processes -eq 2 -and $byId.S16.expected.independent_data_origins -eq 1 -and $byId.S16.expected.corroboration_count_increment -eq 0) 'S16 must separate analytical replication from data-origin independence.'
Assert-Condition ($byId.S14.independence -eq 'INDEPENDIENTE' -and $byId.S14.claim_component_id -eq 'amount' -and $byId.S14.expected.corroboration_count_increment -eq 0) 'S14 must leave the disputed amount uncorroborated.'
Assert-Condition (($byId.S14.expected.corroborated_components -join ',') -eq 'entity,date' -and ($byId.S14.expected.unresolved_components -join ',') -eq 'amount') 'S14 must scope corroboration to entity/date and leave amount unresolved.'
Assert-Condition ($byId.S15.independence -eq 'DESCONOCIDA' -and $byId.S15.identity -eq 'ANÓNIMA_PARA_SINAYXA') 'S15 must not transfer editor identity verification to SINAYXA.'
[pscustomobject]@{
    Result = 'PASS'
    Package = $fixture.package_id
    Cases = $fixture.cases.Count
    IndependenceStates = @($fixture.cases.independence | Sort-Object -Unique).Count
    PositiveIndependenceEvidenceCases = @($fixture.cases | Where-Object { $_.independence -eq 'INDEPENDIENTE' }).Count
    Scope = 'Synthetic structural conformance only; no empirical truth or credibility scoring.'
} | Format-List
