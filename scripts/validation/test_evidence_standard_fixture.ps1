[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$validator = Join-Path $PSScriptRoot 'validate_evidence_standard_fixture.ps1'
$fixture = Join-Path $PSScriptRoot '..\..\tests\fixtures\methodology\evidence-standard\e01-e18-synthetic-conformance-v1.2.2.json'
$fixture = (Resolve-Path -LiteralPath $fixture).Path
$temp = Join-Path ([IO.Path]::GetTempPath()) ('sinayxa-evidence-tests-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $temp | Out-Null

function Invoke-ExpectedFailure {
    param([string]$Name, [object]$Data, [string]$ExpectedMessage)
    $path = Join-Path $temp ($Name + '.json')
    $Data | ConvertTo-Json -Depth 50 | Set-Content -LiteralPath $path -Encoding utf8
    $failed = $false
    try { & $validator -FixturePath $path *> $null }
    catch {
        if ($_.Exception.Message -like "*$ExpectedMessage*") { $failed = $true }
        else { throw "$Name failed for an unexpected reason: $($_.Exception.Message)" }
    }
    if (-not $failed) { throw "Negative test '$Name' was not rejected with expected message '$ExpectedMessage'." }
    Write-Information "Negative test ${Name}: PASS" -InformationAction Continue
}

function Copy-Fixture {
    return (Get-Content -LiteralPath $fixture -Raw -Encoding utf8 | ConvertFrom-Json -Depth 50)
}

try {
    & $validator -FixturePath $fixture
    Write-Information 'Positive fixture validation: PASS' -InformationAction Continue

    $mut = Copy-Fixture; $mut.cases = @($mut.cases | Select-Object -SkipLast 1)
    Invoke-ExpectedFailure -Name 'missing-case' -Data $mut -ExpectedMessage 'Expected 18 cases'

    $mut = Copy-Fixture; $mut.cases[1].id = 'E01'
    Invoke-ExpectedFailure -Name 'duplicate-case-id' -Data $mut -ExpectedMessage 'unique'

    $mut = Copy-Fixture; $mut.cases[0].expected.attribution_status = 'UNATTRIBUTED'
    Invoke-ExpectedFailure -Name 'invalid-attribution-status' -Data $mut -ExpectedMessage 'unsupported attribution-status'

    $mut = Copy-Fixture; $mut.cases[0].expected.evidentiary_status = 'PROBABLE'
    Invoke-ExpectedFailure -Name 'unsupported-status' -Data $mut -ExpectedMessage 'unsupported evidentiary status'

    $mut = Copy-Fixture; $mut.cases[0].nature = 'UNCLASSIFIED'
    Invoke-ExpectedFailure -Name 'unsupported-nature' -Data $mut -ExpectedMessage 'unsupported information nature'

    $mut = Copy-Fixture; $mut.cases[0].expected.document_authenticity = 'ANÓNIMA_PARA_EL_PÚBLICO'
    Invoke-ExpectedFailure -Name 'source-identity-not-authenticity' -Data $mut -ExpectedMessage 'unsupported document-authenticity'

    $mut = Copy-Fixture; $mut.cases[4].expected.source_identity = 'ANONYMOUS'
    Invoke-ExpectedFailure -Name 'invalid-source-identity' -Data $mut -ExpectedMessage 'unsupported source-identity value'

    $mut = Copy-Fixture; $mut.cases[3].expected.independence_of_origin = 'UNVERIFIED'
    Invoke-ExpectedFailure -Name 'invalid-independence-state' -Data $mut -ExpectedMessage 'unsupported independence-of-origin'

    $mut = Copy-Fixture; $mut.cases[12].expected.access_provenance = 'UNAUTHORIZED'
    Invoke-ExpectedFailure -Name 'invalid-access-provenance' -Data $mut -ExpectedMessage 'unsupported access-provenance value'

    $mut = Copy-Fixture; $mut.cases[12].expected.sensitive_information_review = 'LEGAL_REVIEW'
    Invoke-ExpectedFailure -Name 'invalid-sensitive-review-state' -Data $mut -ExpectedMessage 'unsupported sensitive-information review value'

    $mut = Copy-Fixture; $mut.cases[12].expected.access_provenance = 'PÚBLICO_LEGÍTIMO'
    Invoke-ExpectedFailure -Name 'erase-suspicious-access' -Data $mut -ExpectedMessage 'E13 must stop substantive review'

    $mut = Copy-Fixture; $mut.cases[12].expected.sensitive_information_review = 'NO_EVALUADA'
    Invoke-ExpectedFailure -Name 'erase-legal-review' -Data $mut -ExpectedMessage 'E13 must stop substantive review'

    $mut = Copy-Fixture; $mut.cases[2].invariants.republishing_is_independent = $true
    Invoke-ExpectedFailure -Name 'republication-as-independent' -Data $mut -ExpectedMessage 'republication must never imply independence'

    $mut = Copy-Fixture; $mut.cases[7].invariants.retroactive_confirmation = $true
    Invoke-ExpectedFailure -Name 'retroactive-confirmation' -Data $mut -ExpectedMessage 'historical state must not be rewritten'

    $mut = Copy-Fixture; $mut.cases[10].invariants.price_is_corrobative = $true
    Invoke-ExpectedFailure -Name 'price-as-proof' -Data $mut -ExpectedMessage 'price must never be corroborative'

    $mut = Copy-Fixture; $mut.cases[12].invariants.unauthorized_acquisition = $true
    Invoke-ExpectedFailure -Name 'unauthorized-acquisition' -Data $mut -ExpectedMessage 'unauthorized acquisition must remain prohibited'

    $mut = Copy-Fixture; $mut.cases[3].expected.source_identity = 'IDENTIFICADA'
    Invoke-ExpectedFailure -Name 'invent-source-identity' -Data $mut -ExpectedMessage 'E04 must preserve independent origin'

    $mut = Copy-Fixture; $mut.cases[8].expected.evidentiary_status = 'CONTRADICHA'
    Invoke-ExpectedFailure -Name 'unauthenticated-document-as-contradiction' -Data $mut -ExpectedMessage 'E09: evidentiary status does not match'

    $mut = Copy-Fixture; $mut.cases[16].expected.evidentiary_status = 'CONTRADICHA'
    Invoke-ExpectedFailure -Name 'anonymous-reports-as-contradiction' -Data $mut -ExpectedMessage 'E17: evidentiary status does not match'

    $mut = Copy-Fixture; $mut.cases[15].expected.document_authenticity = 'AUTENTICADA'
    Invoke-ExpectedFailure -Name 'invent-document-authenticity' -Data $mut -ExpectedMessage 'E16 must not corroborate an unauthenticated proposal'

    $mut = Copy-Fixture; $mut.cases[15].expected.evidentiary_status = 'PARCIALMENTE_CORROBORADA'
    Invoke-ExpectedFailure -Name 'unauthenticated-proposal-overclaim' -Data $mut -ExpectedMessage 'E16: evidentiary status does not match'

    $mut = Copy-Fixture; $mut.cases[14].expected.evidentiary_status = 'CORROBORADA'
    Invoke-ExpectedFailure -Name 'filing-to-approval-overclaim' -Data $mut -ExpectedMessage 'E15: evidentiary status does not match'

    $mut = Copy-Fixture; $mut.cases[7].expected.temporal_assessment.historical_status = 'CORROBORADA'
    Invoke-ExpectedFailure -Name 'retroactive-historical-upgrade' -Data $mut -ExpectedMessage 'E08 must preserve the pre-announcement state'

    $mut = Copy-Fixture; $mut.cases[11].expected.document_authenticity = 'AUTENTICADA'
    Invoke-ExpectedFailure -Name 'forged-document-not-refuted' -Data $mut -ExpectedMessage 'E12 must mark the forged document'

    $mut = Copy-Fixture; $mut.cases[0].nature = 'RUMOR'
    Invoke-ExpectedFailure -Name 'official-resolution-misclassified' -Data $mut -ExpectedMessage 'E01 must represent the authenticated official resolution'

    $mut = Copy-Fixture; $mut.cases[16].expected.evidentiary_status = 'CONTRADICHA'
    Invoke-ExpectedFailure -Name 'incompatible-versions-not-contradicted' -Data $mut -ExpectedMessage 'E17: evidentiary status does not match'

    Write-Information 'Evidence-standard fixture tests: PASS (1 positive + 26 negative mutations).' -InformationAction Continue
}
finally {
    Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue
}
