[CmdletBinding()]
param(
    [Parameter()]
    [string]$FixturePath
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($FixturePath)) {
    $FixturePath = Join-Path $PSScriptRoot '..\..\tests\fixtures\methodology\evidence-standard\e01-e18-synthetic-conformance-v1.2.1.json'
}

function Assert-Condition {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

$resolved = (Resolve-Path -LiteralPath $FixturePath).Path
try { $fixture = Get-Content -LiteralPath $resolved -Raw -Encoding utf8 | ConvertFrom-Json -Depth 40 }
catch { throw "Fixture is not valid JSON: $($_.Exception.Message)" }

Assert-Condition ($fixture.schema_version -eq '1.2.1') 'Unsupported schema_version.'
Assert-Condition ($fixture.package_id -eq 'SINAYXA-EVIDENCE-E01-E18-SYNTHETIC-004') 'Unexpected package_id.'
Assert-Condition ($fixture.status -eq 'SYNTHETIC_TEST_FIXTURE_NOT_REAL_WORLD_EVIDENCE') 'Fixture must be explicitly synthetic.'
Assert-Condition ($fixture.source_standard -eq 'docs/news-and-events/evidence-standard-for-indicia-rumours-and-leaks.md') 'source_standard must point to the Issue #15 standard.'
Assert-Condition ($fixture.cases.Count -eq 18) "Expected 18 cases; found $($fixture.cases.Count)."

$allowedStates = @('NO_CORROBORADA','PARCIALMENTE_CORROBORADA','CORROBORADA','CONTRADICHA','REFUTADA','NO_RESUELTA')
$allowedNature = @('AFIRMACIÓN','INDICIO','RUMOR','POSIBLE_FILTRACIÓN','PUBLICACIÓN_OFICIAL','HECHO_OBSERVADO')
$allowedAuthenticity = @('NO_APLICA','NO_VERIFICADA','AUTENTICADA','DISPUTADA','AUTENTICIDAD_REFUTADA')
$allowedIdentity = @('IDENTIFICADA','ANÓNIMA_PARA_EL_PÚBLICO','ANÓNIMA_PARA_SINAYXA','SEUDÓNIMA','DESCONOCIDA')
$allowedIndependence = @('INDEPENDIENTE','DEPENDIENTE','DESCONOCIDA')
$allowedAccess = @('PÚBLICO_LEGÍTIMO','PRIVADO_AUTORIZADO','SOSPECHA_DE_ACCESO_NO_AUTORIZADO','NO_DETERMINADO')
$allowedSensitiveReview = @('NO_EVALUADA','POSIBLE_INFORMACIÓN_PRIVILEGIADA','REVISIÓN_LEGAL_REQUERIDA','REVISADA_CON_RESTRICCIONES','EXCLUIDA')
$expectedIds = @(1..18 | ForEach-Object { 'E{0:D2}' -f $_ })
$actualIds = @($fixture.cases | ForEach-Object { [string]$_.id })
Assert-Condition (($actualIds | Sort-Object -Unique).Count -eq 18) 'Case identifiers must be unique.'
Assert-Condition ((@($actualIds | Sort-Object) -join ',') -eq (@($expectedIds | Sort-Object) -join ',')) 'Fixture must contain exactly E01-E18.'

$requiredStatuses = @{
    E01 = 'CORROBORADA'
    E02 = 'NO_CORROBORADA'
    E03 = 'NO_CORROBORADA'
    E04 = 'PARCIALMENTE_CORROBORADA'
    E05 = 'NO_CORROBORADA'
    E06 = 'NO_CORROBORADA'
    E07 = 'PARCIALMENTE_CORROBORADA'
    E08 = 'NO_CORROBORADA'
    E09 = 'CONTRADICHA'
    E10 = 'NO_CORROBORADA'
    E11 = 'NO_CORROBORADA'
    E12 = 'REFUTADA'
    E13 = 'NO_RESUELTA'
    E14 = 'NO_CORROBORADA'
    E15 = 'PARCIALMENTE_CORROBORADA'
    E16 = 'NO_CORROBORADA'
    E17 = 'CONTRADICHA'
    E18 = 'NO_RESUELTA'
}
$caseById = @{}
foreach ($case in $fixture.cases) {
    $id = [string]$case.id
    $caseById[$id] = $case
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($case.scenario)) "${id}: scenario is required."
    Assert-Condition ($allowedNature -contains [string]$case.nature) "${id}: unsupported information nature."
    Assert-Condition ($null -ne $case.expected) "${id}: expected result is required."
    Assert-Condition ($requiredStatuses.ContainsKey($id)) "${id}: no standard case contract exists."
    Assert-Condition ($allowedStates -contains [string]$case.expected.evidentiary_status) "${id}: unsupported evidentiary status."
    Assert-Condition ($case.expected.evidentiary_status -eq $requiredStatuses[$id]) "${id}: evidentiary status does not match the corresponding Issue #15 case."
    Assert-Condition ($allowedAuthenticity -contains [string]$case.expected.document_authenticity) "${id}: unsupported document-authenticity value."
    Assert-Condition ($allowedIdentity -contains [string]$case.expected.source_identity) "${id}: unsupported source-identity value."
    Assert-Condition ($allowedIndependence -contains [string]$case.expected.independence_of_origin) "${id}: unsupported independence-of-origin value."
    Assert-Condition ($allowedAccess -contains [string]$case.expected.access_provenance) "${id}: unsupported access-provenance value."
    Assert-Condition ($allowedSensitiveReview -contains [string]$case.expected.sensitive_information_review) "${id}: unsupported sensitive-information review value."
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($case.expected.guardrail)) "${id}: guardrail is required."
    Assert-Condition ($case.invariants.price_is_corrobative -eq $false) "${id}: price must never be corroborative."
    Assert-Condition ($case.invariants.republishing_is_independent -eq $false) "${id}: republication must never imply independence."
    Assert-Condition ($case.invariants.retroactive_confirmation -eq $false) "${id}: historical state must not be rewritten retroactively."
    Assert-Condition ($case.invariants.unauthorized_acquisition -eq $false) "${id}: unauthorized acquisition must remain prohibited."
}

Assert-Condition ($caseById.E01.nature -eq 'PUBLICACIÓN_OFICIAL' -and $caseById.E01.expected.document_authenticity -eq 'AUTENTICADA') 'E01 must represent the authenticated official resolution.'
Assert-Condition ($caseById.E03.expected.independence_of_origin -eq 'DEPENDIENTE') 'E03 must represent the eight republications as one dependent origin.'
Assert-Condition ($caseById.E04.expected.independence_of_origin -eq 'INDEPENDIENTE' -and $caseById.E04.expected.source_identity -eq 'DESCONOCIDA' -and $caseById.E04.expected.evidentiary_status -eq 'PARCIALMENTE_CORROBORADA') 'E04 must preserve independent origin without inventing source identities and corroborate only date and entity.'
Assert-Condition ($caseById.E07.expected.document_authenticity -eq 'AUTENTICADA' -and $caseById.E07.expected.evidentiary_status -eq 'PARCIALMENTE_CORROBORADA') 'E07 must preserve the authenticated draft status without implying approval.'
Assert-Condition ($caseById.E08.expected.temporal_assessment.historical_status -eq 'NO_CORROBORADA' -and $caseById.E08.expected.temporal_assessment.post_announcement_status -eq 'CORROBORADA' -and $caseById.E08.expected.temporal_assessment.retroactive_rewrite -eq $false) 'E08 must preserve the pre-announcement state and record later corroboration separately.'
Assert-Condition ($caseById.E09.expected.evidentiary_status -eq 'CONTRADICHA' -and $caseById.E09.expected.document_authenticity -eq 'NO_VERIFICADA') 'E09 must preserve unresolved contradiction with an unauthenticated document.'
Assert-Condition ($caseById.E10.expected.evidentiary_status -eq 'NO_CORROBORADA') 'E10 must not treat silence or elapsed time as refutation.'
Assert-Condition ($caseById.E11.expected.evidentiary_status -eq 'NO_CORROBORADA') 'E11 must not use price movement as corroboration.'
Assert-Condition ($caseById.E12.expected.evidentiary_status -eq 'REFUTADA' -and $caseById.E12.expected.document_authenticity -eq 'AUTENTICIDAD_REFUTADA') 'E12 must mark the forged document and its dependent proposition as refuted.'
Assert-Condition ($caseById.E13.expected.access_provenance -eq 'SOSPECHA_DE_ACCESO_NO_AUTORIZADO' -and $caseById.E13.expected.sensitive_information_review -eq 'REVISIÓN_LEGAL_REQUERIDA') 'E13 must stop substantive review and require legal review.'
Assert-Condition ($caseById.E14.expected.source_identity -eq 'ANÓNIMA_PARA_EL_PÚBLICO' -and $caseById.E14.expected.evidentiary_status -eq 'NO_CORROBORADA') 'E14 must preserve the anonymous attribution without upgrading corroboration.'
Assert-Condition ($caseById.E15.expected.evidentiary_status -eq 'PARCIALMENTE_CORROBORADA') 'E15 must confirm filing only, not approval.'
Assert-Condition ($caseById.E16.expected.evidentiary_status -eq 'NO_CORROBORADA' -and $caseById.E16.expected.document_authenticity -eq 'NO_VERIFICADA' -and $caseById.E16.expected.access_provenance -eq 'NO_DETERMINADO' -and $caseById.E16.expected.guardrail.Contains('corroboración independiente')) 'E16 must not corroborate an unauthenticated proposal without independent evidence.'
Assert-Condition ($caseById.E17.expected.evidentiary_status -eq 'CONTRADICHA' -and $caseById.E17.expected.independence_of_origin -eq 'DESCONOCIDA') 'E17 must preserve incompatible anonymous versions without assuming independence.'
Assert-Condition ($caseById.E18.expected.evidentiary_status -eq 'NO_RESUELTA') 'E18 must not infer corroboration or refutation from a correction alone.'

[pscustomobject]@{
    Result = 'PASS'
    Package = $fixture.package_id
    Cases = $fixture.cases.Count
    StatesCovered = @($fixture.cases.expected.evidentiary_status | Sort-Object -Unique).Count
    DimensionsValidated = 6
    InvariantsChecked = 4
    Scope = 'Exact E01-E18 scenario alignment and synthetic structural conformance only; not empirical or legal validation.'
} | Format-List
