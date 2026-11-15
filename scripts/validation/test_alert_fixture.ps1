[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$validator = Join-Path $PSScriptRoot 'validate_alert_fixture.ps1'
$fixturePath = Join-Path $PSScriptRoot '..\..\tests\fixtures\methodology\alerts\a01-a15-synthetic-conformance-v1.0.0.json'
$fixturePath = (Resolve-Path -LiteralPath $fixturePath).Path
$tempDirectory = Join-Path ([IO.Path]::GetTempPath()) ('sinayxa-alert-tests-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempDirectory | Out-Null
function Copy-Fixture {
    return (Get-Content -LiteralPath $fixturePath -Raw -Encoding UTF8 | ConvertFrom-Json -Depth 50)
}
function Invoke-ExpectedFailure {
    param([string]$Name, [object]$Data, [string]$ExpectedMessage)
    $path = Join-Path $tempDirectory ($Name + '.json')
    $Data | ConvertTo-Json -Depth 50 | Set-Content -LiteralPath $path -Encoding UTF8
    $failed = $false
    try { & $validator -FixturePath $path *> $null }
    catch {
        if ($_.Exception.Message -like "*$ExpectedMessage*") { $failed = $true }
        else { throw "$Name failed for an unexpected reason: $($_.Exception.Message)" }
    }
    if (-not $failed) { throw "$Name was not rejected with expected message '$ExpectedMessage'." }
    Write-Information ("Negative test " + $Name + ': PASS') -InformationAction Continue
}
try {
    & $validator -FixturePath $fixturePath
    Write-Information 'Positive fixture validation: PASS' -InformationAction Continue
    $mut = Copy-Fixture; $mut.cases = @($mut.cases | Select-Object -SkipLast 1)
    Invoke-ExpectedFailure -Name 'missing-case' -Data $mut -ExpectedMessage 'Expected exactly 15'
    $mut = Copy-Fixture; $mut.cases[1].id = 'A01'
    Invoke-ExpectedFailure -Name 'duplicate-id' -Data $mut -ExpectedMessage 'Duplicate alert case IDs'
    $mut = Copy-Fixture; $mut.cases[3].expected.evidentiary_status = 'CORROBORADA'
    Invoke-ExpectedFailure -Name 'rumour-upgrade' -Data $mut -ExpectedMessage 'A04 must keep the rumour uncorroborated'
    $mut = Copy-Fixture; $mut.cases[3].expected.visible_label = 'CONFIRMADA'
    Invoke-ExpectedFailure -Name 'rumour-label-hidden' -Data $mut -ExpectedMessage 'A04 must keep the rumour uncorroborated'
    $mut = Copy-Fixture; $mut.cases[3].input.affected_scope = $null
    Invoke-ExpectedFailure -Name 'rumour-scope-omitted' -Data $mut -ExpectedMessage 'A04 must identify the affected scope'
    $mut = Copy-Fixture; $mut.cases[1].input.independent_origins_proven = $true
    Invoke-ExpectedFailure -Name 'syndication-as-independent' -Data $mut -ExpectedMessage 'A02 must not count syndicated republications'
    $mut = Copy-Fixture; $mut.cases[2].expected.evidence_scope = 'ALL_CLAIMS_AND_CONSEQUENCES'
    Invoke-ExpectedFailure -Name 'official-act-overclaim' -Data $mut -ExpectedMessage 'A03 must corroborate only the official act'
    $mut = Copy-Fixture; $mut.cases[4].expected.history = 'RETAIN_DENIAL_ONLY'
    Invoke-ExpectedFailure -Name 'erase-rumour-history' -Data $mut -ExpectedMessage 'A05 must retain both the rumour and denial'
    $mut = Copy-Fixture; $mut.cases[6].expected.evidentiary_status = 'CORROBORADA'
    Invoke-ExpectedFailure -Name 'price-as-proof' -Data $mut -ExpectedMessage 'A07 must not use price movement'
    $mut = Copy-Fixture; $mut.cases[7].input.same_real_world_event = $true
    Invoke-ExpectedFailure -Name 'merge-distinct-events' -Data $mut -ExpectedMessage 'A08 must preserve distinct event identities'
    $mut = Copy-Fixture; $mut.cases[8].expected.history = 'DISCARD_PREVIOUS_VERSION'
    Invoke-ExpectedFailure -Name 'discard-prior-version' -Data $mut -ExpectedMessage 'A09 must preserve the previous version'
    $mut = Copy-Fixture; $mut.cases[10].expected.severity = 'REASSESS_WITH_REASON'
    Invoke-ExpectedFailure -Name 'urgency-inflates-severity' -Data $mut -ExpectedMessage 'A11 may change urgency only'
    $mut = Copy-Fixture; $mut.cases[11].expected.urgency = 'LARGO'
    Invoke-ExpectedFailure -Name 'past-age-as-future-horizon' -Data $mut -ExpectedMessage 'A12: unsupported urgency expectation.'
    $mut = Copy-Fixture; $mut.cases[12].input.evidence_lines_individually_sufficient = $true
    Invoke-ExpectedFailure -Name 'claim-collapse' -Data $mut -ExpectedMessage 'A13 must preserve separate claims'
    $mut = Copy-Fixture; $mut.cases[13].expected.independence_of_origin = 'INDEPENDIENTE'
    Invoke-ExpectedFailure -Name 'unknown-as-independent' -Data $mut -ExpectedMessage 'A14 must not upgrade corroboration'
    $mut = Copy-Fixture; $mut.cases[14].expected.audit_fields = @('reason')
    Invoke-ExpectedFailure -Name 'non-auditable-suppression' -Data $mut -ExpectedMessage 'A15 must preserve an auditable suppression record'
    $mut = Copy-Fixture; $mut.cases[0].invariants.suppression_deletes_history = $true
    Invoke-ExpectedFailure -Name 'global-history-deletion' -Data $mut -ExpectedMessage 'A01: invariant suppression_deletes_history must remain false'
    $mut = Copy-Fixture; $mut.scope = 'This fixture approves the methodology.'
    Invoke-ExpectedFailure -Name 'approval-boundary-removed' -Data $mut -ExpectedMessage 'Fixture scope must preserve the pending-approval boundary.'
    $missing = Join-Path $tempDirectory 'missing.json'
    $missingRejected = $false
    try { & $validator -FixturePath $missing *> $null } catch { $missingRejected = $true }
    if (-not $missingRejected) { throw 'Validator accepted a missing fixture file.' }
    Write-Information 'Robustness test missing-file: PASS' -InformationAction Continue
    $corrupt = Join-Path $tempDirectory 'corrupt.json'
    Set-Content -LiteralPath $corrupt -Value '{"cases":' -Encoding UTF8
    $corruptRejected = $false
    try { & $validator -FixturePath $corrupt *> $null } catch { $corruptRejected = $true }
    if (-not $corruptRejected) { throw 'Validator accepted malformed JSON.' }
    Write-Information 'Robustness test malformed-json: PASS' -InformationAction Continue
    Write-Information 'Alert fixture tests: PASS (1 positive + 17 negative mutations + 2 robustness checks).' -InformationAction Continue
}
finally {
    if (Test-Path -LiteralPath $tempDirectory) { Remove-Item -LiteralPath $tempDirectory -Recurse -Force }
}
