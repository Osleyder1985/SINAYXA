[CmdletBinding()]
param(
    [Parameter()]
    [string]$FixturePath
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($FixturePath)) {
    $FixturePath = Join-Path $PSScriptRoot '..\..\tests\fixtures\methodology\evidence-standard\e01-e18-synthetic-conformance-v1.1.0.json'
}

function Assert-Condition {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

$resolved = (Resolve-Path -LiteralPath $FixturePath).Path
try { $fixture = Get-Content -LiteralPath $resolved -Raw -Encoding utf8 | ConvertFrom-Json -Depth 30 }
catch { throw "Fixture is not valid JSON: $($_.Exception.Message)" }

Assert-Condition ($fixture.schema_version -eq '1.1.0') 'Unsupported schema_version.'
Assert-Condition ($fixture.package_id -eq 'SINAYXA-EVIDENCE-E01-E18-SYNTHETIC-002') 'Unexpected package_id.'
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
$actualSorted = (@($actualIds | Sort-Object) -join ',')
$expectedSorted = (@($expectedIds | Sort-Object) -join ',')
Assert-Condition ($actualSorted -eq $expectedSorted) 'Fixture must contain exactly E01-E18.'

foreach ($case in $fixture.cases) {
    $id = [string]$case.id
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($case.scenario)) "${id}: scenario is required."
    Assert-Condition ($allowedNature -contains [string]$case.nature) "${id}: unsupported information nature."
    Assert-Condition ($null -ne $case.expected) "${id}: expected result is required."
    Assert-Condition ($allowedStates -contains [string]$case.expected.evidentiary_status) "${id}: unsupported evidentiary status."
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

$caseById = @{}
foreach ($case in $fixture.cases) { $caseById[[string]$case.id] = $case }
Assert-Condition ($caseById.E01.expected.source_identity -eq 'ANÓNIMA_PARA_EL_PÚBLICO' -and $caseById.E01.expected.document_authenticity -eq 'NO_APLICA') 'E01 must keep source anonymity separate from document authenticity.'
Assert-Condition ($caseById.E03.expected.independence_of_origin -eq 'DEPENDIENTE' -and $caseById.E03.expected.document_authenticity -eq 'NO_APLICA') 'E03 must represent republication as dependent origin, not document authenticity.'
Assert-Condition ($caseById.E04.expected.independence_of_origin -eq 'DEPENDIENTE' -and $caseById.E04.expected.document_authenticity -eq 'NO_APLICA') 'E04 must represent common-source dependence in its own dimension.'
Assert-Condition ($caseById.E15.expected.access_provenance -eq 'SOSPECHA_DE_ACCESO_NO_AUTORIZADO' -and $caseById.E15.expected.sensitive_information_review -eq 'REVISIÓN_LEGAL_REQUERIDA') 'E15 must preserve the access concern and legal-review safeguard.'

$requiredCoverage = @{
    E03 = 'NO_CORROBORADA'
    E05 = 'NO_CORROBORADA'
    E07 = 'PARCIALMENTE_CORROBORADA'
    E09 = 'CORROBORADA'
    E10 = 'CONTRADICHA'
    E11 = 'REFUTADA'
    E12 = 'NO_RESUELTA'
    E14 = 'NO_CORROBORADA'
    E15 = 'NO_RESUELTA'
    E18 = 'NO_RESUELTA'
}
foreach ($id in $requiredCoverage.Keys) {
    $item = @($fixture.cases | Where-Object id -eq $id)
    Assert-Condition ($item.Count -eq 1) "${id}: required coverage case missing."
    Assert-Condition ($item[0].expected.evidentiary_status -eq $requiredCoverage[$id]) "${id}: status does not match its required conformance contract."
}

[pscustomobject]@{
    Result = 'PASS'
    Package = $fixture.package_id
    Cases = $fixture.cases.Count
    StatesCovered = @($fixture.cases.expected.evidentiary_status | Sort-Object -Unique).Count
    DimensionsValidated = 6
    InvariantsChecked = 4
    Scope = 'Synthetic structural and dimension-separation conformance only; not empirical or legal validation.'
} | Format-List
