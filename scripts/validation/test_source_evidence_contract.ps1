[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$validator = Join-Path $PSScriptRoot 'validate_source_evidence_contract.ps1'
$fixture = Join-Path $PSScriptRoot '..\..\tests\fixtures\contracts\source-evidence-contract-v0.2.0.json'
& $validator -FixturePath $fixture | Out-Null
$base = Get-Content -LiteralPath $fixture -Raw -Encoding utf8 | ConvertFrom-Json -AsHashtable -Depth 100 -DateKind String
$temp = Join-Path ([System.IO.Path]::GetTempPath()) ("sinayxa-contract-78-" + [guid]::NewGuid().ToString('N') + '.json')
try {
    $cycleCopy = ConvertFrom-Json -InputObject (ConvertTo-Json -InputObject $base -Depth 100 -Compress) -AsHashtable -Depth 100
    $cycleEdges = @(
        @{ edge_id='cycle-a-b'; dependent_node_id='node-version-a'; origin_node_id='node-version-b'; relation_type='CITA_DE'; claim_component_id='component-entity'; claim_component_version_id='component-entity-v1'; evidence_refs=@('evidence-a'); recorded_at='2026-11-15T22:00:00Z'; valid_from=$null; valid_to=$null },
        @{ edge_id='cycle-b-a'; dependent_node_id='node-version-b'; origin_node_id='node-version-a'; relation_type='CITA_DE'; claim_component_id='component-entity'; claim_component_version_id='component-entity-v1'; evidence_refs=@('evidence-b'); recorded_at='2026-11-15T22:00:00Z'; valid_from=$null; valid_to=$null }
    )
    $cycleCopy.provenance_edges = @($cycleCopy.provenance_edges) + $cycleEdges
    ConvertTo-Json -InputObject $cycleCopy -Depth 100 | Set-Content -LiteralPath $temp -Encoding utf8
    $cycleOutput = (& $validator -FixturePath $temp | Out-String)
    if (-not $cycleOutput.Contains('CycleReviewRequired : True')) { throw 'A provenance cycle was not detected and preserved for review.' }
    $versionCopy = ConvertFrom-Json -InputObject (ConvertTo-Json -InputObject $base -Depth 100 -Compress) -AsHashtable -Depth 100
    $versionCopy.claims += @{
        claim_id='claim-btc-purchase'; claim_version_id='claim-btc-purchase-v2'; claim_version=2
        proposition='Una entidad X aprobó una compra de BTC por un importe revisado.'
        scope='Caso sintético; versión corregida.'; valid_time_start=$null; valid_time_end=$null
        recorded_at='2026-11-15T22:10:00Z'; supersedes_claim_version_id='claim-btc-purchase-v1'
    }
    $versionCopy.claim_components += @{
        claim_component_id='component-entity'; claim_component_version_id='component-entity-v2'
        claim_id='claim-btc-purchase'; claim_version_id='claim-btc-purchase-v2'
        component_key='entity'; proposition_fragment='La entidad X realizó la acción revisada.'
        scope='Identidad de la entidad; versión sintética.'; version=2
        recorded_at='2026-11-15T22:10:00Z'; supersedes_component_version_id='component-entity-v1'
    }
    ConvertTo-Json -InputObject $versionCopy -Depth 100 | Set-Content -LiteralPath $temp -Encoding utf8
    & $validator -FixturePath $temp | Out-Null

    $pendingDeletion = ConvertFrom-Json -InputObject (ConvertTo-Json -InputObject $base -Depth 100 -Compress) -AsHashtable -Depth 100
    $pendingDeletion.retention_records[0].content_retained = $true
    $pendingDeletion.retention_records[0].legal_basis_status = 'NOT_ESTABLISHED'
    $pendingDeletion.retention_records[0].disposition = 'DELETE_PENDING'
    $pendingDeletion.retention_records[0].expires_at = '2026-11-15T21:00:00Z'
    $pendingFile = Join-Path ([System.IO.Path]::GetTempPath()) ("sinayxa-contract-78-pending-" + [guid]::NewGuid().ToString('N') + '.json')
    try {
        ConvertTo-Json -InputObject $pendingDeletion -Depth 100 | Set-Content -LiteralPath $pendingFile -Encoding utf8
        $pendingOutput = (& $validator -FixturePath $pendingFile | Out-String)
        if (-not $pendingOutput.Contains('Result : PASS')) { throw 'DELETE_PENDING with an unverified basis must remain representable while deletion is pending.' }
    }
    finally { if (Test-Path -LiteralPath $pendingFile) { Remove-Item -LiteralPath $pendingFile -Force } }
    $mutations = @(
        @{ Name='Orphan claim component'; Apply={ param($x) $x.claim_components[0].claim_id='missing-claim' } },
        @{ Name='Duplicate claim version identifier'; Apply={ param($x) $x.claims += $x.claims[0] } },
        @{ Name='Duplicate component version identifier'; Apply={ param($x) $x.claim_components += $x.claim_components[0] } },
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
        @{ Name='Independent with two versions of the same source'; Apply={
            param($x)
            $sourceId = $x.evaluation_units[0].source_id
            $x.evaluation_units[1].source_id = $sourceId
            $versionId = $x.evaluation_units[1].source_version_id
            ($x.source_versions | Where-Object { $_.source_version_id -eq $versionId })[0].source_id = $sourceId
            $x.independence_assessments[0].status='INDEPENDIENTE'
            $x.independence_assessments[0].supporting_evidence_refs=@('evidence-a','evidence-b')
            $x.independence_assessments[0].human_review_status='REVIEWED'
            $x.independence_assessments[0].reviewed_at='2026-11-15T22:05:00Z'
        } },
        @{ Name='Unknown origin incorrectly asserted as material dependence'; Apply={
            param($x)
            $x.independence_assessments[0].status='DEPENDIENTE'
            $x.independence_assessments[0].dependency_edge_refs=@('edge-a-unknown')
            $x.independence_assessments[0].human_review_status='REVIEWED'
            $x.independence_assessments[0].reviewed_at='2026-11-15T22:05:00Z'
        } },
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
        @{ Name='Source content hash has no algorithm'; Apply={ param($x) $x.source_versions[0].content_hash='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' } },
        @{ Name='Missing source version sequence'; Apply={ param($x) $x.source_versions[1].Remove('version_sequence') } },
        @{ Name='Duplicate source version sequence within one source'; Apply={ param($x) $x.source_versions[1].source_id=$x.source_versions[0].source_id; $x.source_versions[1].version_sequence=$x.source_versions[0].version_sequence } },
        @{ Name='Hash algorithm exists without content hash'; Apply={ param($x) $x.source_versions[0].hash_algorithm='SHA-256' } },
        @{ Name='Unsupported integrity algorithm retains digest'; Apply={ param($x) $x.evidence_items[0].integrity_check.expected_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' } },
        @{ Name='Retrieved before first detection'; Apply={ param($x) $x.source_versions[0].retrieved_at='2026-11-15T19:00:00Z' } },
        @{ Name='Injected numerical score'; Apply={ param($x) $x.factor_assessments[0].score=0.99 } },
        @{ Name='Injected confidential identity'; Apply={ param($x) $x.sources[0].real_name='Synthetic Person' } },
        @{ Name='Source identifier is not opaque'; Apply={ param($x) $x.sources[0].source_id='person-name' } },
        @{ Name='Source version supersedes itself'; Apply={ param($x) $x.source_versions[0].supersedes_source_version_id='version-a1' } },
        @{ Name='Source version supersedes a later version'; Apply={ param($x) $new = $x.source_versions[0].Clone(); $new.source_version_id='version-a2'; $new.version_label='v2'; $new.version_sequence=2; $new.supersedes_source_version_id='version-a1'; $x.source_versions += $new; $x.source_versions[0].supersedes_source_version_id='version-a2' } },
        @{ Name='Factor evidence crosses dimension boundary'; Apply={ param($x) $x.factor_assessments[0].supporting_evidence_refs=@('evidence-a') } },
        @{ Name='Evidence becomes available after evaluation cutoff'; Apply={ param($x) $x.evidence_availability[0].available_at='2026-11-15T23:00:00Z' } },
        @{ Name='Known availability lacks traceable basis'; Apply={ param($x) $x.evidence_availability[0].availability_basis='UNKNOWN' } },
        @{ Name='Claim assessment uses evidence unavailable at its cutoff'; Apply={ param($x) $x.claim_assessments[0].supporting_evidence_refs=@('evidence-a'); $x.claim_assessments[0].assessment_cutoff='2026-11-15T20:00:00Z' } },
        @{ Name='Duplicate source version sequence'; Apply={ param($x) $new = $x.source_versions[0].Clone(); $new.source_version_id='version-a2'; $new.version_label='v1-duplicate'; $new.supersedes_source_version_id=$null; $x.source_versions += $new } },
        @{ Name='Retained content has an expired retention window'; Apply={ param($x) $x.retention_records[0].content_retained=$true; $x.retention_records[0].legal_basis_status='VERIFIED'; $x.retention_records[0].disposition='RETAIN'; $x.retention_records[0].expires_at='2026-11-15T21:00:00Z' } },
        @{ Name='Deleted content lacks a deletion audit event'; Apply={ param($x) $x.retention_records[0].content_retained=$false; $x.retention_records[0].disposition='DELETED' } }
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
        PositiveMultiVersionCases=1
        NegativeMutations=$mutations.Count
        TotalChecks=($mutations.Count + 3)
        Scope='Deterministic synthetic contract-validator rejection tests.'
    } | Format-List
}
finally {
    if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force }
}
