[CmdletBinding()]
param(
    [Parameter()]
    [string]$FixturePath
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($FixturePath)) {
    $FixturePath = Join-Path $PSScriptRoot "..\..\tests\fixtures\methodology\intensity-horizons\t01-t19-synthetic-evidence.json"
}

$resolvedPath = (Resolve-Path -LiteralPath $FixturePath).Path
$fixture = Get-Content -LiteralPath $resolvedPath -Raw -Encoding UTF8 | ConvertFrom-Json

if ($fixture.status -ne "SYNTHETIC_TEST_FIXTURE_NOT_REAL_WORLD_EVIDENCE") {
    throw "Fixture status is missing or does not identify the data as synthetic."
}

if ($fixture.package_id -ne "SINAYXA-IH-T01-T19-SYNTHETIC-001") {
    throw "Unexpected package_id."
}

$expectedIds = 1..19 | ForEach-Object { "T{0:D2}" -f $_ }
$actualIds = @($fixture.cases | ForEach-Object { $_.id })

if ($actualIds.Count -ne 19) {
    throw "Expected exactly 19 cases; found $($actualIds.Count)."
}

if (($actualIds | Select-Object -Unique).Count -ne 19) {
    throw "Duplicate case IDs detected."
}

for ($index = 0; $index -lt $expectedIds.Count; $index++) {
    if ($actualIds[$index] -ne $expectedIds[$index]) {
        throw "Case order/ID mismatch at position $($index + 1): expected $($expectedIds[$index]), found $($actualIds[$index])."
    }
}

foreach ($case in $fixture.cases) {
    if ([string]::IsNullOrWhiteSpace($case.unit) -or
        [string]::IsNullOrWhiteSpace($case.scenario) -or
        $null -eq $case.evidence -or
        $null -eq $case.expected) {
        throw "Case $($case.id) is missing a required fixture field."
    }
}

$t16 = $fixture.cases | Where-Object { $_.id -eq "T16" }
if ($t16.expected.process -notlike "BLOCKED*") {
    throw "T16 must remain blocked pending two real independent human evaluators."
}
if ($t16.expected.fixture_limit -notlike "A synthetic disagreement*") {
    throw "T16 must explicitly state that synthetic data cannot satisfy inter-evaluator validation."
}

$hash = (Get-FileHash -LiteralPath $resolvedPath -Algorithm SHA256).Hash

Write-Host "Fixture validation: PASS"
Write-Host "Package: $($fixture.package_id)"
Write-Host "Cases: $($actualIds.Count)"
Write-Host "T16: BLOCKED (correctly preserved)"
Write-Host "SHA256: $hash"
Write-Host "Path: $resolvedPath"
