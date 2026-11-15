[CmdletBinding()]
param(
    [Parameter()]
    [string]$FixturePath
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($FixturePath)) {
    $FixturePath = Join-Path $PSScriptRoot "..\..\tests\fixtures\methodology\intensity-horizons\t01-t19-synthetic-evidence.json"
}

function Get-FixtureCase {
    param([string]$Id)
    $matches = @($fixture.cases | Where-Object { $_.id -eq $Id })
    if ($matches.Count -ne 1) {
        throw "Expected exactly one fixture case $Id; found $($matches.Count)."
    }
    return $matches[0]
}

function ConvertTo-UtcOffset {
    param([string]$Value)
    return [DateTimeOffset]::Parse($Value, [Globalization.CultureInfo]::InvariantCulture).ToUniversalTime()
}

function Get-ElapsedSeconds {
    param([string]$Start, [string]$End)
    $startInstant = ConvertTo-UtcOffset -Value $Start
    $endInstant = ConvertTo-UtcOffset -Value $End
    return ($endInstant - $startInstant).TotalSeconds
}

function Get-ProposedHorizon {
    param([double]$ElapsedSeconds)
    if ($ElapsedSeconds -lt 0) {
        throw "Elapsed duration cannot be negative."
    }
    if ($ElapsedSeconds -le 86400) { return "INMEDIATO" }
    if ($ElapsedSeconds -le 604800) { return "CORTO" }
    if ($ElapsedSeconds -le 7776000) { return "MEDIO" }
    return "LARGO"
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

$t16 = Get-FixtureCase -Id "T16"
if ($t16.expected.process -notlike "BLOCKED*") {
    throw "T16 must remain blocked pending two real independent human evaluators."
}
if ($t16.expected.fixture_limit -notlike "A synthetic disagreement*") {
    throw "T16 must explicitly state that synthetic data cannot satisfy inter-evaluator validation."
}

# Deterministic checks of the temporal test vectors.
# These validate arithmetic and fixture consistency, not human methodological judgments.
$t11 = Get-FixtureCase -Id "T11"
$t11Actual = @()
for ($index = 0; $index -lt $t11.evidence[0].targets.Count; $index++) {
    $seconds = Get-ElapsedSeconds -Start $t11.evidence[0].reference -End $t11.evidence[0].targets[$index]
    if ([Math]::Abs($seconds - [double]$t11.evidence[0].elapsed_seconds[$index]) -gt 0.001) {
        throw "T11 elapsed-seconds mismatch at vector $($index + 1)."
    }
    $t11Actual += Get-ProposedHorizon -ElapsedSeconds $seconds
}
if (($t11Actual -join ",") -ne ($t11.expected.horizons -join ",")) {
    throw "T11 horizon boundary results do not match the expected vector."
}

$t12 = Get-FixtureCase -Id "T12"
$t12Actual = @()
for ($index = 0; $index -lt $t12.evidence[0].targets.Count; $index++) {
    $seconds = Get-ElapsedSeconds -Start $t12.evidence[0].reference -End $t12.evidence[0].targets[$index]
    if ([Math]::Abs($seconds - [double]$t12.evidence[0].elapsed_seconds[$index]) -gt 0.001) {
        throw "T12 elapsed-seconds mismatch at vector $($index + 1)."
    }
    $t12Actual += Get-ProposedHorizon -ElapsedSeconds $seconds
}
if (($t12Actual -join ",") -ne ($t12.expected.horizons -join ",")) {
    throw "T12 horizon boundary results do not match the expected vector."
}

$t13 = Get-FixtureCase -Id "T13"
$dateOnly = [string]$t13.evidence[0].date_only
if ($dateOnly -notmatch '^\d{4}-\d{2}-\d{2}$' -or
    $t13.expected.timestamp -ne "DATE_ONLY_PRESERVED" -or
    $t13.expected.horizon -ne "INDETERMINADO") {
    throw "T13 must preserve a date-only value without inventing a timestamp."
}

$t14 = Get-FixtureCase -Id "T14"
$milestoneNames = @($t14.evidence[0].milestones | ForEach-Object { $_.name })
if ($milestoneNames.Count -ne 4 -or
    ($milestoneNames | Select-Object -Unique).Count -ne 4 -or
    $t14.expected.treatment -ne "FOUR_SEPARATE_MILESTONES_AND_CLOCKS") {
    throw "T14 must preserve four distinct milestones and clocks."
}

$t15 = Get-FixtureCase -Id "T15"
$t15Start = ConvertTo-UtcOffset -Value $t15.evidence[0].earliest
$t15End = ConvertTo-UtcOffset -Value $t15.evidence[0].latest
$t15Reference = ConvertTo-UtcOffset -Value $t15.cutoff
$t15EarliestSeconds = ($t15Start - $t15Reference).TotalSeconds
$t15LatestSeconds = ($t15End - $t15Reference).TotalSeconds
if ($t15EarliestSeconds -ge 86400 -or
    $t15LatestSeconds -le 86400 -or
    $t15.expected.horizon -notlike "INDETERMINADO*") {
    throw "T15 interval must straddle the 24-hour boundary and remain indeterminate."
}

$t18 = Get-FixtureCase -Id "T18"
$t18Seconds = Get-ElapsedSeconds -Start $t18.evidence[0].start -End $t18.evidence[0].end
if ([Math]::Abs($t18Seconds - [double]$t18.evidence[0].expected_elapsed_seconds) -gt 0.001 -or
    $t18.expected.horizon -ne "INMEDIATO") {
    throw "T18 daylight-saving elapsed-time check failed."
}

$t19 = Get-FixtureCase -Id "T19"
$t19Reference = $t19.evidence[2].at
$t19SourceASeconds = Get-ElapsedSeconds -Start $t19Reference -End $t19.evidence[0].at
$t19SourceBSeconds = Get-ElapsedSeconds -Start $t19Reference -End $t19.evidence[1].at
if ([Math]::Abs($t19SourceASeconds - 85800) -gt 0.001 -or
    [Math]::Abs($t19SourceBSeconds - 87000) -gt 0.001 -or
    $t19SourceASeconds -ge 86400 -or
    $t19SourceBSeconds -le 86400 -or
    $t19.expected.horizon -notlike "INDETERMINADO*") {
    throw "T19 contradictory timestamp interval check failed."
}

$hash = (Get-FileHash -LiteralPath $resolvedPath -Algorithm SHA256).Hash

Write-Host "Fixture structure validation: PASS"
Write-Host "Package: $($fixture.package_id)"
Write-Host "Cases: $($actualIds.Count)"
Write-Host "Temporal fixture checks: PASS (T11,T12,T13,T14,T15,T18,T19)"
Write-Host "T16: BLOCKED (correctly preserved)"
Write-Host "SHA256: $hash"
Write-Host "Path: $resolvedPath"
