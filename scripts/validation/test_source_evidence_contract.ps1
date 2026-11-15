[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$validator = Join-Path $PSScriptRoot 'validate_source_evidence_contract.ps1'
$fixture = Join-Path $PSScriptRoot '..\..\tests\fixtures\contracts\source-evidence-contract-v0.2.0.json'
& $validator -FixturePath $fixture | Out-Null
$base = Get-Content -LiteralPath $fixture -Raw -Encoding utf8 | ConvertFrom-Json -AsHashtable -Depth 100
$temp = Join-Path ([System.IO.Path]::GetTempPath()) ("sinayxa-contract-78-" + [guid]::NewGuid().ToString('N') + '.json')
try {
    $cycleCopy = ConvertFrom-Json -InputObject (ConvertTo-Json -InputObject $base -Depth 100 -Compress) -AsHashtable -Depth 100
    $cycleEdges = @(
        @{ edge_id='cycle-a-b'; dependent_node_id='node-version-a'; origin_node_id='node-version-b'; relation_type='CITA_DE'; claim_component_id='component-entity'; evidence_refs=@('evidence-a'); recorded_at='2026-11-15T22:00:00Z'; valid_from=$null; valid_to=$null },
        @{ edge_id='cycle-b-a'; dependent_node_id='node-version-b'; origin_node_id='node-version-a'; relation_type='CITA_DE'; claim_component_id='component-entity'; evidence_refs=@('evidence-b'); recorded_at='2026-11-15T22:00:00Z'; valid_from=$null; valid_to=$null }
    )
    $cycleCopy.provenance_edges = @($cycleCopy.provenance_edges) + $cycleEdges
    ConvertTo-Json -InputObject $cycleCopy -Depth 100 | Set-Content -LiteralPath $temp -Encoding utf8
    $cycleOutput = (& $validator -FixturePath $temp | Out-String)
    if (-not $cycleOutput.Contains('CycleReviewRequired : True')) { throw 'A provenance cycle was not detected and preserved for review.' }
    $mutations = @(
        @{ Name='Orphan claim component'; Apply={ param($x) $x.claim_components[0].claim_id='missing-claim' } },
        @{ Name='UTC timestamp has a non-UTC offset'; Apply={ param($x) $x.created_at='2026-11-15T17:00:00-05:00' } },
        @{ Name='UTC timestamp contains an impossible calendar date'; Apply={ param($x) $x.created_at='2026-02-30T22:00:00Z' } },
        @{ Name='Evaluation unit source/version mismatch'; Apply={ param($x) $x.evaluation_units[0].source_id='src_fedcba98-7654-4321-8abc-fedcba987654' } },
        @{ Name='Evaluation unit bound to a different component version'; Apply={ param($x) $x.evaluation_units[0].claim_component_version_id='component-amount-v1' } },
        @{ Name='Claim version supersedes itself'; Apply={ param($x) $x.claims[0].supersedes_claim_version_id='claim-btc-purchase-v1' } },
        @{ Name='Unknown origin edge targets ordinary node'; Apply={ param($x) $x.provenance_edges[0].origin_node_id='node-version-b' } },
        @{ Name='Provenance node references missing source version'; Apply={ param($x) $x.provenance_nodes[0].entity_ref='missing-version' } },
        @{ Name='Provenance edge references missing evidence'; Apply={ param($x) $x.provenance_edges[0].evidence_refs=@('missing-evidence') } },
        @{ Name='Independent without positive evidence'; Apply={ param($x) $x.independence_assessments[0].status='INDEPENDIENTE' } },
        @{ Name='Dependent without dependency edge'; Apply={ param($x) $x.independence_assessments[0].status='DEPENDIENTE' } },
        @{ Name='Claim assessment reuses independence from another component'; Apply={ param($x) $x.claim_assessments[0].independence_assessment_refs=@('independence-amount') } },
        @{ Name='Issue 15 probative state used as factor state'; Apply={ param($x) $x.factor_assessments[0].status='CONTRADICHA' } },
        @{ Name='Missing one of ten approved factors'; Apply={ param($x) $x.factor_assessments=@($x.factor_assessments | Select-Object -Skip 1) } },
        @{ Name='Duplicate factor dimension replaces required dimension'; Apply={ param($x) $x.factor_assessments[1].dimension=$x.factor_assessments[0].dimension } },
        @{ Name='Identity label conflicts with visibility flags'; Apply={ param($x) $x.identity_assessments[0].identity='ANÓNIMA_PARA_SINAYXA' } },
        @{ Name='Unsupported probative state'; Apply={ param($x) $x.claim_assessments[0].evidentiary_status='HIGH_CONFIDENCE' } },
        @{ Name='Conclusive state bypasses human review'; Apply={ param($x) $x.claim_assessments[0].evidentiary_status='CORROBORADA'; $x.claim_assessments[0].supporting_evidence_refs=@('evidence-a'); $x.claim_assessments[0].human_review_status='PENDING' } },
        @{ Name='Unauthorized retained content'; Apply={ param($x) $x.retention_records[0].content_retained=$true } },
        @{ Name='Retention record has orphan subject'; Apply={ param($x) $x.retention_records[0].subject_ref='missing-subject' } },
        @{ Name='Audit event has orphan subject'; Apply={ param($x) $x.audit_events[0].subject_ref='missing-subject' } },
        @{ Name='Integrity MATCH with different digests'; Apply={ param($x) $x.evidence_items[0].integrity_check.result='MATCH'; $x.evidence_items[0].integrity_check.expected_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'; $x.evidence_items[0].integrity_check.observed_digest='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb' } },
        @{ Name='Retrieved before first detection'; Apply={ param($x) $x.source_versions[0].retrieved_at='2026-11-15T19:00:00Z' } },
        @{ Name='Injected numerical score'; Apply={ param($x) $x.factor_assessments[0].score=0.99 } },
        @{ Name='Injected confidential identity'; Apply={ param($x) $x.sources[0].real_name='Synthetic Person' } },
        @{ Name='Source identifier is not opaque'; Apply={ param($x) $x.sources[0].source_id='person-name' } }
    )
    foreach ($mutation in $mutations) {
        $copy = ConvertFrom-Json -InputObject (ConvertTo-Json -InputObject $base -Depth 100 -Compress) -AsHashtable -Depth 100
        & $mutation.Apply $copy
        ConvertTo-Json -InputObject $copy -Depth 100 | Set-Content -LiteralPath $temp -Encoding utf8
        $rejected = $false
        try { & $validator -FixturePath $temp | Out-Null } catch { $rejected = $true }
        if (-not $rejected) { throw "Mutation was not rejected: $($mutation.Name)" }
    }
    [pscustomobject]@{
        Result='PASS'
        BaselineScenarios=1
        PositiveCycleCases=1
        NegativeMutations=$mutations.Count
        TotalChecks=($mutations.Count + 2)
        Scope='Deterministic synthetic contract-validator rejection tests.'
    } | Format-List
}
finally {
    if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force }
}
