[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$validator = Join-Path $PSScriptRoot 'validate_evidence_standard_fixture.ps1'
$fixture = Join-Path $PSScriptRoot '..\..\tests\fixtures\methodology\evidence-standard\e01-e18-synthetic-conformance-v1.0.0.json'
$fixture = (Resolve-Path -LiteralPath $fixture).Path
$temp = Join-Path ([IO.Path]::GetTempPath()) ('sinayxa-evidence-tests-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $temp | Out-Null

function Invoke-ExpectedFailure {
    param([string]$Name, [object]$Data)
    $path = Join-Path $temp ($Name + '.json')
    $Data | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $path -Encoding utf8
    & $validator -FixturePath $path *> $null
    if ($LASTEXITCODE -eq 0) { throw "Negative test '$Name' unexpectedly passed." }
}

try {
    & $validator -FixturePath $fixture
    if ($LASTEXITCODE -ne 0) { throw 'Positive fixture validation failed.' }
    $base = Get-Content -LiteralPath $fixture -Raw -Encoding utf8 | ConvertFrom-Json -Depth 30

    $mut = $base | ConvertTo-Json -Depth 30 | ConvertFrom-Json -Depth 30
    $mut.cases = @($mut.cases | Select-Object -SkipLast 1)
    Invoke-ExpectedFailure 'missing-case' $mut

    $mut = $base | ConvertTo-Json -Depth 30 | ConvertFrom-Json -Depth 30
    $mut.cases[1].id = 'E01'
    Invoke-ExpectedFailure 'duplicate-case-id' $mut

    $mut = $base | ConvertTo-Json -Depth 30 | ConvertFrom-Json -Depth 30
    $mut.cases[0].expected.evidentiary_status = 'PROBABLE'
    Invoke-ExpectedFailure 'unsupported-status' $mut

    $mut = $base | ConvertTo-Json -Depth 30 | ConvertFrom-Json -Depth 30
    $mut.cases[0].invariants.price_is_corrobative = $true
    Invoke-ExpectedFailure 'price-as-proof' $mut

    $mut = $base | ConvertTo-Json -Depth 30 | ConvertFrom-Json -Depth 30
    $mut.cases[2].invariants.republishing_is_independent = $true
    Invoke-ExpectedFailure 'republication-as-independent' $mut

    $mut = $base | ConvertTo-Json -Depth 30 | ConvertFrom-Json -Depth 30
    $mut.cases[12].invariants.retroactive_confirmation = $true
    Invoke-ExpectedFailure 'retroactive-confirmation' $mut

    $mut = $base | ConvertTo-Json -Depth 30 | ConvertFrom-Json -Depth 30
    $mut.cases[14].invariants.unauthorized_acquisition = $true
    Invoke-ExpectedFailure 'unauthorized-acquisition' $mut

    $mut = $base | ConvertTo-Json -Depth 30 | ConvertFrom-Json -Depth 30
    $mut.cases[6].expected.evidentiary_status = 'CORROBORADA'
    Invoke-ExpectedFailure 'partial-to-full-overclaim' $mut

    'Evidence-standard fixture tests: PASS (1 positive + 8 negative mutations).'
}
finally {
    Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue
}
