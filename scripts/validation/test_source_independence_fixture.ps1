 [CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$validator = Join-Path $PSScriptRoot 'validate_source_independence_fixture.ps1'
$fixture = Join-Path $PSScriptRoot '..\..\tests\fixtures\methodology\source-independence\s01-s16-synthetic-conformance-v1.0.0.json'
& $validator -FixturePath $fixture

$base = Get-Content -LiteralPath $fixture -Raw -Encoding utf8 | ConvertFrom-Json -Depth 50
$temp = Join-Path ([System.IO.Path]::GetTempPath()) ("sinayxa-source-independence-" + [guid]::NewGuid().ToString('N') + '.json')
try {
    $mutations = @(
        @{ Name='Independent without positive evidence'; Apply={ param($x) $x.cases[3].independence_basis = @() } },
        @{ Name='Unknown independence upgraded to corroboration'; Apply={ param($x) $x.cases[6].expected.corroboration_count_increment = 1 } },
        @{ Name='Missing case identifier'; Apply={ param($x) $x.cases[0].id = 'S99' } },
        @{ Name='Syndication falsely independent'; Apply={ param($x) $x.cases[0].independence = 'INDEPENDIENTE' } },
        @{ Name='Cycle no longer detected'; Apply={ param($x) $x.cases[12].expected.cycle_detected = $false } },
        @{ Name='Shared dataset counted as two origins'; Apply={ param($x) $x.cases[15].expected.independent_data_origins = 2 } }
    )
    foreach ($mutation in $mutations) {
        $copy = $base | ConvertTo-Json -Depth 50 | ConvertFrom-Json -Depth 50
        & $mutation.Apply $copy
        $copy | ConvertTo-Json -Depth 50 | Set-Content -LiteralPath $temp -Encoding utf8
        $rejected = $false
        try { & $validator -FixturePath $temp | Out-Null } catch { $rejected = $true }
        if (-not $rejected) { throw "Mutation was not rejected: $($mutation.Name)" }
    }
    [pscustomobject]@{ Result='PASS'; PositiveCases=1; NegativeMutations=$mutations.Count; TotalChecks=($mutations.Count + 1); Scope='Validator rejection behavior; synthetic only.' } | Format-List
}
finally {
    if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force }
}
