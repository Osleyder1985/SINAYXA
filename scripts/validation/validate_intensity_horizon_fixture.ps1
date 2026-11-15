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

$allowedPackages = @{
    "SINAYXA-IH-T01-T19-SYNTHETIC-001" = "1.0.0"
    "SINAYXA-IH-T01-T19-SYNTHETIC-002" = "1.1.0"
}
if (-not $allowedPackages.ContainsKey([string]$fixture.package_id)) {
    throw "Unexpected package_id."
}
if ([string]$fixture.package_version -ne $allowedPackages[[string]$fixture.package_id]) {
    throw "Package ID/version mismatch."
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

# Version 1.1.0 semantic-input contract checks. These validate required fixture
# fields and scope declarations; they do not prove that the expected judgments
# are methodologically correct or constitute execution of the semantic cases.
if ($fixture.package_id -eq "SINAYXA-IH-T01-T19-SYNTHETIC-002") {
    if ($fixture.supersedes.package_id -ne "SINAYXA-IH-T01-T19-SYNTHETIC-001" -or
        $fixture.supersedes.package_version -ne "1.0.0" -or
        $fixture.supersedes.sha256 -ne "467F5B5236481C0EFDCAFF562DA3D4DFF27EF71C1FCB9D486E19072ABA902D22") {
        throw "v1.1.0 must identify the immutable v1.0.0 package it supersedes."
    }

    $t01 = Get-FixtureCase -Id "T01"
    if ($t01.expected.intensity -ne "I0" -or
        $t01.unit -notlike "*technical and operational functions only*" -or
        $t01.evidence.Count -lt 3 -or
        $t01.expected.reason -notlike "*makes no I0 claim about token-market*") {
        throw "T01 v1.1.0 must explicitly bound I0 to technical/operational functions."
    }

    $t03 = Get-FixtureCase -Id "T03"
    $t03EvidenceIds = @($t03.evidence | ForEach-Object { $_.id })
    if ($t03.expected.intensity -ne "I2" -or
        $t03EvidenceIds -notcontains "T03-E3" -or
        $t03.expected.observed_effect -notlike "*uncredited*" -or
        $t03.expected.potential_effect -notlike "*not established*") {
        throw "T03 v1.1.0 must include observed functional consequence and bounded potential effect."
    }

    $t04 = Get-FixtureCase -Id "T04"
    $t04EvidenceIds = @($t04.evidence | ForEach-Object { $_.id })
    if ($t04.expected.intensity -ne "I3" -or
        $t04EvidenceIds -notcontains "T04-E5" -or
        $t04.evidence[0].content -notlike "*five named applications*" -or
        $t04.evidence[3].content -notlike "*withdrawals and user access remain available*") {
        throw "T04 v1.1.0 must specify the dependency denominator, material function, and I4 boundary."
    }

    $t08 = Get-FixtureCase -Id "T08"
    if ($t08.evidence.Count -lt 5 -or
        $t08.expected.segment_A.intensity -ne "I2" -or
        $t08.expected.segment_B.intensity -ne "I2" -or
        $t08.expected.aggregate -notlike "Do not assign an aggregate classification*") {
        throw "T08 v1.1.0 must preserve independently evidenced segment classifications without an invented aggregate."
    }

    $t10 = Get-FixtureCase -Id "T10"
    if ($t10.expected.intensity_baseline -ne "NOT_ASSESSED" -or
        $t10.expected.mitigation -ne "UNVERIFIED") {
        throw "T10 v1.1.0 must remain a mitigation-only case without a baseline intensity."
    }
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
Write-Host "Package: $($fixture.package_id) v$($fixture.package_version)"
Write-Host "Cases: $($actualIds.Count)"
Write-Host "Temporal fixture checks: PASS (T11,T12,T13,T14,T15,T18,T19)"
Write-Host "T16: BLOCKED (correctly preserved)"
Write-Host "SHA256: $hash"
Write-Host "Path: $resolvedPath"
