[CmdletBinding()]
param(
    [Parameter()]
    [string]$FixturePath
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($FixturePath)) {
    $FixturePath = Join-Path $PSScriptRoot "..\..\tests\fixtures\methodology\intensity-horizons\t01-t20-synthetic-evidence-v1.3.0.json"
}

function Get-FixtureCase {
    param([string]$Id)
    $matchingCases = @($fixture.cases | Where-Object { $_.id -eq $Id })
    if ($matchingCases.Count -ne 1) {
        throw "Expected exactly one fixture case $Id; found $($matchingCases.Count)."
    }
    return $matchingCases[0]
}

function ConvertTo-DateTimeOffset {
    param([string]$Value)
    if ($Value -notmatch '(Z|[+-](0[0-9]|1[0-4]):[0-5][0-9])$') {
        throw "Timestamp must include an explicit UTC designator or numeric offset: $Value"
    }
    return [DateTimeOffset]::Parse(
        $Value,
        [Globalization.CultureInfo]::InvariantCulture,
        [Globalization.DateTimeStyles]::None
    )
}

function Assert-ExactCategory {
    param(
        [string[]]$Actual,
        [string[]]$Expected,
        [string]$CaseId
    )
    if (($Actual -join ',') -ne ($Expected -join ',')) {
        throw "$CaseId compatible_categories mismatch. Expected [$($Expected -join ',')], found [$($Actual -join ',')]."
    }
}

function Get-ElapsedDuration {
    param([string]$Start, [string]$End)
    $startInstant = ConvertTo-DateTimeOffset -Value $Start
    $endInstant = ConvertTo-DateTimeOffset -Value $End
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
$fixture = Get-Content -LiteralPath $resolvedPath -Raw -Encoding UTF8 | ConvertFrom-Json -DateKind String

if ($fixture.status -ne "SYNTHETIC_TEST_FIXTURE_NOT_REAL_WORLD_EVIDENCE") {
    throw "Fixture status is missing or does not identify the data as synthetic."
}

$allowedPackages = @{
    "SINAYXA-IH-T01-T19-SYNTHETIC-001" = "1.0.0"
    "SINAYXA-IH-T01-T19-SYNTHETIC-002" = "1.1.0"
    "SINAYXA-IH-T01-T19-SYNTHETIC-003" = "1.2.0"
    "SINAYXA-IH-T01-T20-SYNTHETIC-004" = "1.3.0"
}
if (-not $allowedPackages.ContainsKey([string]$fixture.package_id)) {
    throw "Unexpected package_id."
}
if ([string]$fixture.package_version -ne $allowedPackages[[string]$fixture.package_id]) {
    throw "Package ID/version mismatch."
}

$expectedCaseCount = if ($fixture.package_id -eq "SINAYXA-IH-T01-T20-SYNTHETIC-004") { 20 } else { 19 }
$expectedIds = 1..$expectedCaseCount | ForEach-Object { "T{0:D2}" -f $_ }
$actualIds = @($fixture.cases | ForEach-Object { $_.id })

if ($actualIds.Count -ne $expectedCaseCount) {
    throw "Expected exactly $expectedCaseCount cases; found $($actualIds.Count)."
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
if ($fixture.package_id -in @("SINAYXA-IH-T01-T19-SYNTHETIC-001", "SINAYXA-IH-T01-T19-SYNTHETIC-002")) {
    # Historical fixture versions retain their original two-human-evaluator
    # requirement; this check validates their historical, immutable contents.
    if ($t16.expected.process -notlike "BLOCKED*" -or
        $t16.expected.fixture_limit -notlike "A synthetic disagreement*") {
        throw "Historical T16 fixture content was unexpectedly changed."
    }
}
elseif ($fixture.package_id -in @("SINAYXA-IH-T01-T19-SYNTHETIC-003", "SINAYXA-IH-T01-T20-SYNTHETIC-004")) {
    if ($t16.expected.process -ne "ONE_HUMAN_PRIMARY_EVALUATION_WITH_AI_ASSISTED_ADVERSARIAL_REVIEW" -or
        $t16.expected.ai_review -notlike "*not a human evaluator*" -or
        $t16.expected.fixture_limit -notlike "*cannot establish inter-evaluator reliability*" -or
        $t16.expected.disagreement_handling -notlike "*never average*") {
        throw "T16 v1.2.0 must define the single-human process and prohibit false inter-evaluator claims."
    }
}

# Version 1.2.0 governance-contract checks. This validates the fixture declaration,
# not actual human/AI execution or methodological validity.
if ($fixture.package_id -in @("SINAYXA-IH-T01-T19-SYNTHETIC-003", "SINAYXA-IH-T01-T20-SYNTHETIC-004")) {
    if ($fixture.package_id -eq "SINAYXA-IH-T01-T19-SYNTHETIC-003" -and
        ($fixture.supersedes.package_id -ne "SINAYXA-IH-T01-T19-SYNTHETIC-002" -or
         $fixture.supersedes.package_version -ne "1.1.0" -or
         $fixture.supersedes.sha256 -ne "E685D6BB4459F5A580ABFAC11979D4FCABF385EE7856EC28C16541C2AD05948C")) {
        throw "v1.2.0 must identify the immutable v1.1.0 package it supersedes."
    }
    if ($t16.evidence.Count -lt 3 -or
        $t16.expected.human_primary_assessment -notlike "*before seeing any AI critique*" -or
        $t16.expected.ai_review -notlike "*not a human evaluator*" -or
        $t16.expected.separation -notlike "*isolated context*" -or
        $t16.expected.provenance -notlike "*NOT_AVAILABLE*" -or
        $t16.expected.fixture_limit -notlike "*cannot establish inter-evaluator reliability*") {
        throw "T16 v1.2.0 must preserve the single-human/AI-assistance boundaries and provenance requirements."
    }
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

# Version 1.2.0 semantic-input contract checks. These assertions validate the
# declared synthetic case contracts; they do not prove real-world impact or causality.
if ($fixture.package_id -eq "SINAYXA-IH-T01-T19-SYNTHETIC-003") {
    $t01 = Get-FixtureCase -Id "T01"
    if ($t01.expected.intensity -ne "I0" -or
        $t01.expected.direction -notlike "INDETERMINADA*" -or
        $t01.evidence.Count -lt 3 -or
        $t01.unit -notlike "*technical and operational functions only*" -or
        $t01.evidence[0].content -notlike "*complete reviewed architecture inventory*" -or
        $t01.expected.reason -notlike "*makes no I0 claim about token-market*") {
        throw "T01 v1.2.0 must bound I0 to the evidenced technical/operational unit and leave market direction unclaimed."
    }

    $t03 = Get-FixtureCase -Id "T03"
    if ($t03.expected.intensity -ne "I2" -or
        $t03.expected.direction -notlike "NEGATIVA*" -or
        $t03.evidence.Count -lt 4 -or
        $t03.expected.observed_effect -notlike "*uncredited*" -or
        $t03.expected.potential_effect -notlike "*not established*" -or
        $t03.evidence[3].content -notlike "*no evidence establishes that this segment or this deposit path is central to the exchange as a whole*") {
        throw "T03 v1.2.0 must preserve the bounded segment, observed effect, and unestablished future duration."
    }

    $t04 = Get-FixtureCase -Id "T04"
    if ($t04.expected.intensity -ne "I3" -or
        $t04.expected.direction -notlike "NEGATIVA*" -or
        $t04.evidence.Count -ne 5 -or
        $t04.evidence[0].content -notlike "*five named applications*" -or
        $t04.evidence[2].content -notlike "*suspended in the four dependent applications*" -or
        $t04.evidence[3].content -notlike "*withdrawals and user access remain available*" -or
        $t04.evidence[4].content -notlike "*inventory is complete*") {
        throw "T04 v1.2.0 must evidence the complete denominator, material suspension, and I4 boundary."
    }

    $t08 = Get-FixtureCase -Id "T08"
    if ($t08.evidence.Count -ne 5 -or
        $t08.expected.segment_A.intensity -ne "I2" -or
        $t08.expected.segment_A.direction -ne "NEGATIVA" -or
        $t08.expected.segment_B.intensity -ne "I2" -or
        $t08.expected.segment_B.direction -ne "POSITIVA" -or
        $t08.expected.aggregate -notlike "Do not assign an aggregate classification*") {
        throw "T08 v1.2.0 must preserve independent segment effects and prohibit an unsupported aggregate."
    }

    $t10 = Get-FixtureCase -Id "T10"
    if ($t10.expected.intensity_baseline -ne "NOT_ASSESSED" -or
        $t10.expected.mitigation -ne "UNVERIFIED" -or
        $t10.evidence.Count -ne 3 -or
        $t10.expected.rule -notlike "*does not supply or imply that baseline*") {
        throw "T10 v1.2.0 must remain mitigation-only and must not invent a baseline intensity."
    }
}

# Version 1.3.0 adds a dedicated past-milestone age contract. The age is
# descriptive chronology only; it must never be classified as a future horizon.
if ($fixture.package_id -eq "SINAYXA-IH-T01-T20-SYNTHETIC-004") {
    if ($fixture.supersedes.package_id -ne "SINAYXA-IH-T01-T19-SYNTHETIC-003" -or
        $fixture.supersedes.package_version -ne "1.2.0" -or
        $fixture.supersedes.sha256 -ne "5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB") {
        throw "v1.3.0 must identify the immutable v1.2.0 package it supersedes."
    }
    $t20 = Get-FixtureCase -Id "T20"
    $eventAt = ConvertTo-DateTimeOffset -Value $t20.evidence[0].occurred_at
    $cutoffAt = ConvertTo-DateTimeOffset -Value $t20.cutoff
    $ageSeconds = ($cutoffAt - $eventAt).TotalSeconds
    if ($ageSeconds -lt 0) {
        throw "T20 past-event chronology cannot be negative."
    }
    if ([Math]::Abs($ageSeconds - [double]$t20.expected.elapsed_since_event_seconds) -gt 0.001 -or
        $t20.expected.elapsed_since_event_seconds -ne 786600 -or
        $t20.expected.temporal_direction -ne "PAST_EVENT" -or
        $t20.expected.age_semantics -ne "DESCRIPTIVE_ONLY" -or
        $t20.expected.future_horizon -ne "NOT_APPLICABLE" -or
        $t20.expected.horizon_classification -ne "NOT_APPLICABLE_PAST_EVENT" -or
        $null -ne $t20.expected.horizon -or
        $null -ne $t20.expected.horizon_category) {
        throw "T20 must preserve past-event age as descriptive-only and prohibit future horizon classification."
    }
}

# Deterministic checks of the temporal test vectors.
# These validate arithmetic and fixture consistency, not human methodological judgments.
$t11 = Get-FixtureCase -Id "T11"
$t11Actual = @()
for ($index = 0; $index -lt $t11.evidence[0].targets.Count; $index++) {
    $seconds = Get-ElapsedDuration -Start $t11.evidence[0].reference -End $t11.evidence[0].targets[$index]
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
    $seconds = Get-ElapsedDuration -Start $t12.evidence[0].reference -End $t12.evidence[0].targets[$index]
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
$parsedDate = [datetime]::MinValue
if (-not [datetime]::TryParseExact(
        $dateOnly,
        "yyyy-MM-dd",
        [Globalization.CultureInfo]::InvariantCulture,
        [Globalization.DateTimeStyles]::None,
        [ref]$parsedDate
    ) -or
    $t13.expected.timestamp -ne "DATE_ONLY_PRESERVED" -or
    $t13.expected.horizon -ne "INDETERMINADO") {
    throw "T13 must preserve a valid calendar date only, without inventing a timestamp."
}

$t14 = Get-FixtureCase -Id "T14"
$milestoneNames = @($t14.evidence[0].milestones | ForEach-Object { $_.name })
$requiredMilestones = @("announcement", "approval", "effective", "implementation")
if ($milestoneNames.Count -ne 4 -or
    ($milestoneNames -join ",") -ne ($requiredMilestones -join ",") -or
    $t14.expected.treatment -ne "FOUR_SEPARATE_MILESTONES_AND_CLOCKS") {
    throw "T14 must preserve exactly announcement, approval, effective, and implementation as separate milestones."
}
foreach ($milestone in $t14.evidence[0].milestones) {
    $null = ConvertTo-DateTimeOffset -Value $milestone.at
}

$t15 = Get-FixtureCase -Id "T15"
$t15Start = ConvertTo-DateTimeOffset -Value $t15.evidence[0].earliest
$t15End = ConvertTo-DateTimeOffset -Value $t15.evidence[0].latest
$t15Reference = ConvertTo-DateTimeOffset -Value $t15.cutoff
$t15EarliestSeconds = ($t15Start - $t15Reference).TotalSeconds
$t15LatestSeconds = ($t15End - $t15Reference).TotalSeconds
Assert-ExactCategory -Actual @($t15.expected.compatible_categories) -Expected @("INMEDIATO", "CORTO") -CaseId "T15"
if ($t15EarliestSeconds -ge 86400 -or
    $t15LatestSeconds -le 86400 -or
    $t15.expected.horizon -ne "INDETERMINADO as a single category" -or
    [Math]::Abs($t15EarliestSeconds - 85800) -gt 0.001 -or
    [Math]::Abs($t15LatestSeconds - 87000) -gt 0.001) {
    throw "T15 interval must exactly preserve the 23 h 50 min–24 h 10 min boundary-crossing interval."
}

$t18 = Get-FixtureCase -Id "T18"
$t18Evidence = $t18.evidence[0]
if ($t18Evidence.timezone -ne "Europe/Madrid") {
    throw "T18 must declare the IANA timezone Europe/Madrid."
}
$t18Start = ConvertTo-DateTimeOffset -Value $t18Evidence.start
$t18End = ConvertTo-DateTimeOffset -Value $t18Evidence.end
$t18Seconds = ($t18End - $t18Start).TotalSeconds
# Windows PowerShell 5.1/.NET Framework uses Windows time-zone identifiers.
# This explicit mapping validates the IANA identifier against Windows zone rules.
try {
    $madridZone = [TimeZoneInfo]::FindSystemTimeZoneById("Romance Standard Time")
}
catch {
    throw "T18 cannot validate Europe/Madrid: Windows time zone 'Romance Standard Time' is unavailable."
}
$startMadrid = [TimeZoneInfo]::ConvertTime($t18Start, $madridZone)
$endMadrid = [TimeZoneInfo]::ConvertTime($t18End, $madridZone)
if ($startMadrid.Offset -ne $t18Start.Offset -or
    $endMadrid.Offset -ne $t18End.Offset -or
    [Math]::Abs($t18Seconds - [double]$t18Evidence.expected_elapsed_seconds) -gt 0.001 -or
    $t18.expected.horizon -ne "INMEDIATO" -or
    [double]$t18.expected.elapsed_seconds -ne 86400) {
    throw "T18 Europe/Madrid offset consistency or daylight-saving elapsed-time check failed."
}

$t19 = Get-FixtureCase -Id "T19"
$t19Reference = $t19.evidence[2].at
$t19SourceASeconds = Get-ElapsedDuration -Start $t19Reference -End $t19.evidence[0].at
$t19SourceBSeconds = Get-ElapsedDuration -Start $t19Reference -End $t19.evidence[1].at
Assert-ExactCategory -Actual @($t19.expected.compatible_categories) -Expected @("INMEDIATO", "CORTO") -CaseId "T19"
if ([Math]::Abs($t19SourceASeconds - 85800) -gt 0.001 -or
    [Math]::Abs($t19SourceBSeconds - 87000) -gt 0.001 -or
    $t19SourceASeconds -ge 86400 -or
    $t19SourceBSeconds -le 86400 -or
    $t19.expected.horizon -ne "INDETERMINADO as a single category" -or
    [Math]::Abs([double]$t19.evidence[2].elapsed_seconds[0] - 85800) -gt 0.001 -or
    [Math]::Abs([double]$t19.evidence[2].elapsed_seconds[1] - 87000) -gt 0.001) {
    throw "T19 contradictory timestamp interval or expected-category check failed."
}

$hash = (Get-FileHash -LiteralPath $resolvedPath -Algorithm SHA256).Hash

Write-Information "Fixture structure and semantic contract validation: PASS" -InformationAction Continue
Write-Information "Package: $($fixture.package_id) v$($fixture.package_version)" -InformationAction Continue
Write-Information "Cases: $($actualIds.Count)" -InformationAction Continue
$temporalChecks = "T11,T12,T13,T14,T15,T18,T19"
if ($fixture.package_id -eq "SINAYXA-IH-T01-T20-SYNTHETIC-004") { $temporalChecks += ",T20" }
Write-Information "Temporal fixture checks: PASS ($temporalChecks)" -InformationAction Continue
Write-Information "Semantic fixture checks: PASS (T01,T03,T04,T08,T10 where applicable)" -InformationAction Continue
if ($fixture.package_id -in @("SINAYXA-IH-T01-T19-SYNTHETIC-003", "SINAYXA-IH-T01-T20-SYNTHETIC-004")) {
    Write-Information "T16: SINGLE-HUMAN PROTOCOL DEFINED (not an execution result)" -InformationAction Continue
}
else {
    Write-Information "T16: BLOCKED (historical fixture requirement correctly preserved)" -InformationAction Continue
}
Write-Information "SHA256: $hash" -InformationAction Continue
Write-Information "Path: $resolvedPath" -InformationAction Continue
