[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$validator = Join-Path $PSScriptRoot 'validate_evidence_standard_fixture.ps1'
$fixture = Join-Path $PSScriptRoot '..\..\tests\fixtures\methodology\evidence-standard\e01-e18-synthetic-conformance-v1.1.0.json'
$fixture = (Resolve-Path -LiteralPath $fixture).Path
$temp = Join-Path ([IO.Path]::GetTempPath()) ('sinayxa-evidence-tests-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $temp | Out-Null

function Invoke-ExpectedFailure {
    param([string]$Name, [object]$Data, [string]$ExpectedMessage)
    $path = Join-Path $temp ($Name + '.json')
    $Data | ConvertTo-Json -Depth 40 | Set-Content -LiteralPath $path -Encoding utf8
    $failed = $false
    try { & $validator -FixturePath $path *> $null }
    catch {
        if ($_.Exception.Message -like "*$ExpectedMessage*") { $failed = $true }
        else { throw "$Name failed for an unexpected reason: $($_.Exception.Message)" }
    }
    if (-not $failed) { throw "Negative test '$Name' was not rejected with expected message '$ExpectedMessage'." }
    Write-Information "Negative test $Name: PASS" -InformationAction Continue
}

function Copy-Fixture {
    return (Get-Content -LiteralPath $fixture -Raw -Encoding utf8 | ConvertFrom-Json -Depth 40)
}

try {
    & $validator -FixturePath $fixture
    Write-Information 'Positive fixture validation: PASS' -InformationAction Continue

    $mut = Copy-Fixture; $mut.cases = @($mut.cases | Select-Object -SkipLast 1)
    Invoke-ExpectedFailure 'missing-case' $mut 'Expected 18 cases'

    $mut = Copy-Fixture; $mut.cases[1].id = 'E01'
    Invoke-ExpectedFailure 'duplicate-case-id' $mut 'unique'

    $mut = Copy-Fixture; $mut.cases[0].expected.evidentiary_status = 'PROBABLE'
    Invoke-ExpectedFailure 'unsupported-status' $mut 'unsupported evidentiary status'

    $mut = Copy-Fixture; $mut.cases[0].nature = 'UNCLASSIFIED'
    Invoke-ExpectedFailure 'unsupported-nature' $mut 'unsupported information nature'

    $mut = Copy-Fixture; $mut.cases[0].expected.source_identity = 'ANÓNIMA_PARA_EL_PÚBLICO'; $mut.cases[0].expected.document_authenticity = 'ANÓNIMA_PARA_EL_PÚBLICO'
    Invoke-ExpectedFailure 'source-identity-not-authenticity' $mut 'unsupported document-authenticity'

    $mut = Copy-Fixture; $mut.cases[3].expected.independence_of_origin = 'UNVERIFIED'
    Invoke-ExpectedFailure 'invalid-independence-state' $mut 'unsupported independence-of-origin'

    $mut = Copy-Fixture; $mut.cases[14].expected.access_provenance = 'PÚBLICO_LEGÍTIMO'
    Invoke-ExpectedFailure 'erase-suspicious-access' $mut 'E15 must preserve'

    $mut = Copy-Fixture; $mut.cases[14].expected.sensitive_information_review = 'NO_EVALUADA'
    Invoke-ExpectedFailure 'erase-legal-review' $mut 'E15 must preserve'

    $mut = Copy-Fixture; $mut.cases[2].invariants.republishing_is_independent = $true
    Invoke-ExpectedFailure 'republication-as-independent' $mut 'republication must never imply independence'

    $mut = Copy-Fixture; $mut.cases[12].invariants.retroactive_confirmation = $true
    Invoke-ExpectedFailure 'retroactive-confirmation' $mut 'historical state must not be rewritten'

    $mut = Copy-Fixture; $mut.cases[13].invariants.price_is_corrobative = $true
    Invoke-ExpectedFailure 'price-as-proof' $mut 'price must never be corroborative'

    $mut = Copy-Fixture; $mut.cases[14].invariants.unauthorized_acquisition = $true
    Invoke-ExpectedFailure 'unauthorized-acquisition' $mut 'unauthorized acquisition must remain prohibited'

    $mut = Copy-Fixture; $mut.cases[6].expected.evidentiary_status = 'CORROBORADA'
    Invoke-ExpectedFailure 'partial-to-full-overclaim' $mut 'E07: status does not match'

    Write-Information 'Evidence-standard fixture tests: PASS (1 positive + 12 negative mutations).' -InformationAction Continue
}
finally {
    Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue
}
