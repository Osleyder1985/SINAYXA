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
        @{ Name='Shared dataset counted as two origins'; Apply={ param($x) $x.cases[15].expected.independent_data_origins = 2 } },
        @{ Name='Disputed amount falsely corroborated'; Apply={ param($x) $x.cases[13].expected.corroboration_count_increment = 1 } },
        @{ Name='Malformed provenance edge'; Apply={ param($x) $x.cases[0].provenance_edges[0].to = '' } },
        @{ Name='Filing falsely treated as approval'; Apply={ param($x) $x.cases[2].expected.scope_not_confirmed = @() } },
        @{ Name='Interpretation falsely treated as execution'; Apply={ param($x) $x.cases[4].expected.supports_execution = $true } },
        @{ Name='Rectification erases prior version'; Apply={ param($x) $x.cases[5].expected.version_history.preserve_prior_versions = $false } },
        @{ Name='Official denial falsely refutes claim'; Apply={ param($x) $x.cases[9].expected.claim_refuted = $true } },
        @{ Name='Past source errors invalidate authenticated document'; Apply={ param($x) $x.cases[10].expected.past_errors_automatically_invalidate_document = $true } },
        @{ Name='Prestige treated as evidence'; Apply={ param($x) $x.cases[11].expected.prestige_used_as_evidence = $true } },
        @{ Name='Editorial anonymity verification transferred'; Apply={ param($x) $x.cases[14].expected.editor_identity_verification_transferred = $true } },
        @{ Name='Shared employer automatically implies dependency'; Apply={ param($x) $x.cases[8].expected.shared_employer_does_not_imply_dependency = $false } },
        @{ Name='Unsupported institutional character'; Apply={ param($x) $x.cases[2].institutional_character = 'UNOFFICIAL' } },
        @{ Name='Unsupported independence state'; Apply={ param($x) $x.cases[0].independence = 'UNVERIFIED' } },
        @{ Name='Missing source version'; Apply={ param($x) $x.cases[0].evaluation_units[0].source_version = '' } },
        @{ Name='Mismatched evaluation component'; Apply={ param($x) $x.cases[0].evaluation_units[0].claim_component_id = 'different-component' } },
        @{ Name='Missing provenance node evaluation'; Apply={ param($x) $x.cases[0].evaluation_units = @($x.cases[0].evaluation_units | Where-Object { $_.source_id -ne 'agency-wire' }) } },
        @{ Name='Unreferenced independence evidence source'; Apply={ param($x) $x.cases[3].independence_evidence[0].source_ids = @('not-a-source') } },
        @{ Name='Automated decision bypasses human review'; Apply={ param($x) $x.cases[0].assessment_record.human_review_required = $false } },
        @{ Name='Assessment decision differs from independence'; Apply={ param($x) $x.cases[0].assessment_record.decision_state = 'INDEPENDIENTE' } },
        @{ Name='Assessment omits limitations'; Apply={ param($x) $x.cases[0].assessment_record.limitations = @() } },
        @{ Name='Assessment cites no supporting evidence'; Apply={ param($x) $x.cases[0].assessment_record.supporting_evidence_refs = @() } },
        @{ Name='Unsupported source subtype'; Apply={ param($x) $x.cases[0].source_subtype = 'UNCLASSIFIED' } },
        @{ Name='SINAYXA anonymity status falsely cleared'; Apply={ param($x) $x.cases[14].identity_visibility.anonymous_to_sinayxa = $false } },
        @{ Name='Publisher identity verification transferred to SINAYXA'; Apply={ param($x) $x.cases[14].identity_visibility.identity_verified_by_sinayxa = $true } },
        @{ Name='Assessment cites nonexistent contrary evidence'; Apply={ param($x) $x.cases[13].assessment_record.contrary_evidence_refs = @('synthetic-fixture://missing-contrary') } },
        @{ Name='Missing qualitative factor'; Apply={ param($x) $x.cases[0].factor_assessments = @($x.cases[0].factor_assessments | Select-Object -Skip 1) } },
        @{ Name='Unsupported qualitative factor status'; Apply={ param($x) $x.cases[0].factor_assessments[0].status = 'HIGH_CONFIDENCE' } },
        @{ Name='Factor without justification'; Apply={ param($x) $x.cases[0].factor_assessments[0].justification = '' } },
        @{ Name='Factor references nonexistent evidence'; Apply={ param($x) $x.cases[0].factor_assessments[0].evidence_refs = @('synthetic-fixture://missing-factor-evidence') } },
        @{ Name='Factor status contradicts evidence basis'; Apply={ param($x) $x.cases[0].factor_assessments[0].status = 'SUSTENTADA' } },
        @{ Name='Numeric credibility score injected'; Apply={ param($x) $x.cases[0].factor_assessments[0] | Add-Member -NotePropertyName score -NotePropertyValue 0.95 } },
        @{ Name='Issue 15 probative state CONTRADICHA used as factor'; Apply={ param($x) $x.cases[0].factor_assessments[0].status = 'CONTRADICHA' } },
        @{ Name='Issue 15 probative state CORROBORADA used as factor'; Apply={ param($x) $x.cases[0].factor_assessments[0].status = 'CORROBORADA' } }
    )
    foreach ($mutation in $mutations) {
        $copy = $base | ConvertTo-Json -Depth 50 | ConvertFrom-Json -Depth 50
        & $mutation.Apply $copy
        $copy | ConvertTo-Json -Depth 50 | Set-Content -LiteralPath $temp -Encoding utf8
        $rejected = $false
        try { & $validator -FixturePath $temp | Out-Null } catch { $rejected = $true }
        if (-not $rejected) { throw "Mutation was not rejected: $($mutation.Name)" }
    }
    [pscustomobject]@{ Result='PASS'; BaselineFixture=1; BaselineScenarios=16; NegativeMutations=$mutations.Count; TotalChecks=($mutations.Count + 1); Scope='Validator rejection behavior; synthetic only.' } | Format-List
}
finally {
    if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force }
}
