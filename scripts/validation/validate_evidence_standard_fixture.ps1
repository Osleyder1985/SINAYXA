[CmdletBinding()]
param(
    [Parameter()]
    [string]$FixturePath
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($FixturePath)) {
    $FixturePath = Join-Path $PSScriptRoot '..\..\tests\fixtures\methodology\evidence-standard\e01-e18-synthetic-conformance-v1.0.0.json'
}

function Assert-Condition {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

$resolved = (Resolve-Path -LiteralPath $FixturePath).Path
try { $fixture = Get-Content -LiteralPath $resolved -Raw -Encoding utf8 | ConvertFrom-Json -Depth 20 }
catch { throw "Fixture is not valid JSON: $($_.Exception.Message)" }

Assert-Condition ($fixture.schema_version -eq '1.0.0') 'Unsupported schema_version.'
Assert-Condition ($fixture.package_id -eq 'SINAYXA-EVIDENCE-E01-E18-SYNTHETIC-001') 'Unexpected package_id.'
Assert-Condition ($fixture.status -eq 'SYNTHETIC_TEST_FIXTURE_NOT_REAL_WORLD_EVIDENCE') 'Fixture must be explicitly synthetic.'
Assert-Condition ($fixture.source_standard -eq 'docs/news-and-events/evidence-standard-for-indicia-rumours-and-leaks.md') 'source_standard must point to the Issue #15 standard.'
Assert-Condition ($fixture.cases.Count -eq 18) "Expected 18 cases; found $($fixture.cases.Count)."

$allowed = @('NO_CORROBORADA','PARCIALMENTE_CORROBORADA','CORROBORADA','CONTRADICHA','REFUTADA','NO_RESUELTA')
$expectedIds = @(1..18 | ForEach-Object { 'E{0:D2}' -f $_ })
$actualIds = @($fixture.cases | ForEach-Object { [string]$_.id })
Assert-Condition (($actualIds | Sort-Object -Unique).Count -eq 18) 'Case identifiers must be unique.'
$actualSorted = (@($actualIds | Sort-Object) -join ',')
$expectedSorted = (@($expectedIds | Sort-Object) -join ',')
Assert-Condition ($actualSorted -eq $expectedSorted) 'Fixture must contain exactly E01-E18.'

foreach ($case in $fixture.cases) {
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($case.scenario)) "$($case.id): scenario is required."
    Assert-Condition ($null -ne $case.expected) "$($case.id): expected result is required."
    Assert-Condition ($allowed -contains [string]$case.expected.evidentiary_status) "$($case.id): unsupported evidentiary status."
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($case.expected.guardrail)) "$($case.id): guardrail is required."
    Assert-Condition ($case.invariants.price_is_corrobative -eq $false) "$($case.id): price must never be corroborative."
    Assert-Condition ($case.invariants.republishing_is_independent -eq $false) "$($case.id): republication must never imply independence."
    Assert-Condition ($case.invariants.retroactive_confirmation -eq $false) "$($case.id): historical state must not be rewritten retroactively."
    Assert-Condition ($case.invariants.unauthorized_acquisition -eq $false) "$($case.id): unauthorized acquisition must remain prohibited."
}

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
    Assert-Condition ($item.Count -eq 1) "$id: required coverage case missing."
    Assert-Condition ($item[0].expected.evidentiary_status -eq $requiredCoverage[$id]) "$id: status does not match its required conformance contract."
}

[pscustomobject]@{
    Result = 'PASS'
    Package = $fixture.package_id
    Cases = $fixture.cases.Count
    StatesCovered = @($fixture.cases.expected.evidentiary_status | Sort-Object -Unique).Count
    InvariantsChecked = 4
    Scope = 'Synthetic structural conformance only; not empirical or legal validation.'
} | Format-List
