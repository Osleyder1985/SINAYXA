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
    $partialCopy = ConvertFrom-Json -InputObject (ConvertTo-Json -InputObject $base -Depth 100 -Compress) -AsHashtable -Depth 100
    $partialCopy.claim_assessments[0].evidentiary_status='PARCIALMENTE_CORROBORADA'
    $partialCopy.claim_assessments[0].rationale='La evidencia respalda la existencia de la declaración, pero no la ejecución.'
    $partialCopy.claim_assessments[0].supported_scope='Existencia y atribución de la declaración.'
    $partialCopy.claim_assessments[0].unsupported_scope='Ejecución material de la compra.'
    $partialCopy.claim_assessments[0].human_review_status='REVIEWED'
    $partialCopy.claim_assessments[0].reviewed_at='2026-11-15T22:05:00Z'
    ConvertTo-Json -InputObject $partialCopy -Depth 100 | Set-Content -LiteralPath $temp -Encoding utf8
    & $validator -FixturePath $temp | Out-Null

    $historicalImport = ConvertFrom-Json -InputObject (ConvertTo-Json -InputObject $base -Depth 100 -Compress) -AsHashtable -Depth 100
    $historicalImport.evidence_availability[0].availability_basis = 'INDEPENDENT_ARCHIVE'
    $historicalFile = Join-Path ([System.IO.Path]::GetTempPath()) ("sinayxa-contract-78-archive-" + [guid]::NewGuid().ToString('N') + '.json')
    try {
        ConvertTo-Json -InputObject $historicalImport -Depth 100 | Set-Content -LiteralPath $historicalFile -Encoding utf8
        $historicalOutput = (& $validator -FixturePath $historicalFile | Out-String)
        if (-not $historicalOutput.Contains('Result : PASS')) { throw 'Historical evidence with an independent archive timestamp must remain valid without rewriting original timestamps.' }
    }
    finally { if (Test-Path -LiteralPath $historicalFile) { Remove-Item -LiteralPath $historicalFile -Force } }
    $independentCopy = ConvertFrom-Json -InputObject (ConvertTo-Json -InputObject $base -Depth 100 -Compress) -AsHashtable -Depth 100
    $independentA = $independentCopy.evidence_items[0].Clone()
    $independentA.evidence_id = 'independent-evidence-a'
    $independentA.information_nature = 'HECHO_OBSERVADO'
    $independentA.content_reference = 'synthetic-observation://independent-a'
    $independentB = $independentCopy.evidence_items[1].Clone()
    $independentB.evidence_id = 'independent-evidence-b'
    $independentB.information_nature = 'HECHO_OBSERVADO'
    $independentB.content_reference = 'synthetic-observation://independent-b'
    $independentCopy.evidence_items += @($independentA,$independentB)
    $independentAvailabilityA = $independentCopy.evidence_availability[0].Clone()
    $independentAvailabilityA.availability_id = 'availability-independent-a'
    $independentAvailabilityA.evidence_id = 'independent-evidence-a'
    $independentAvailabilityB = $independentCopy.evidence_availability[1].Clone()
    $independentAvailabilityB.availability_id = 'availability-independent-b'
    $independentAvailabilityB.evidence_id = 'independent-evidence-b'
    $independentCopy.evidence_availability += @($independentAvailabilityA,$independentAvailabilityB)
    $independentCopy.independence_assessments[0].status = 'INDEPENDIENTE'
    $independentCopy.independence_assessments[0].supporting_evidence_refs = @('independent-evidence-a','independent-evidence-b')
    $independentCopy.independence_assessments[0].human_review_status = 'REVIEWED'
    $independentCopy.independence_assessments[0].reviewed_at = '2026-11-15T22:05:00Z'
    $independentFile = Join-Path ([System.IO.Path]::GetTempPath()) ("sinayxa-contract-78-independent-" + [guid]::NewGuid().ToString('N') + '.json')
    try {
        ConvertTo-Json -InputObject $independentCopy -Depth 100 | Set-Content -LiteralPath $independentFile -Encoding utf8
        $independentOutput = (& $validator -FixturePath $independentFile | Out-String)
        if (-not $independentOutput.Contains('Result : PASS')) { throw 'A reviewed independence assessment with evidence for both distinct sources must validate.' }
    }
    finally { if (Test-Path -LiteralPath $independentFile) { Remove-Item -LiteralPath $independentFile -Force } }

    $dependentCopy = ConvertFrom-Json -InputObject (ConvertTo-Json -InputObject $base -Depth 100 -Compress) -AsHashtable -Depth 100
    $dependencyEvidence = $dependentCopy.evidence_items[0].Clone()
    $dependencyEvidence.evidence_id = 'evidence-dependency'
    $dependencyEvidence.information_nature = 'HECHO_OBSERVADO'
    $dependencyEvidence.content_reference = 'synthetic-observation://source-a-cites-source-b'
    $dependentCopy.evidence_items += $dependencyEvidence
    $dependencyAvailability = $dependentCopy.evidence_availability[0].Clone()
    $dependencyAvailability.availability_id = 'availability-dependency'
    $dependencyAvailability.evidence_id = 'evidence-dependency'
    $dependentCopy.evidence_availability += $dependencyAvailability
    $dependentCopy.provenance_edges += @{
        edge_id='edge-a-b'; dependent_node_id='node-version-a'; origin_node_id='node-version-b'
        relation_type='CITA_DE'; claim_component_id='component-entity'
        claim_component_version_id='component-entity-v1'; evidence_refs=@('evidence-dependency')
        recorded_at='2026-11-15T22:00:00Z'; valid_from=$null; valid_to=$null
    }
    $dependentCopy.independence_assessments[0].status = 'DEPENDIENTE'
    $dependentCopy.independence_assessments[0].dependency_edge_refs = @('edge-a-b')
    $dependentCopy.independence_assessments[0].human_review_status = 'REVIEWED'
    $dependentCopy.independence_assessments[0].reviewed_at = '2026-11-15T22:05:00Z'
    $dependentFile = Join-Path ([System.IO.Path]::GetTempPath()) ("sinayxa-contract-78-dependent-" + [guid]::NewGuid().ToString('N') + '.json')
    try {
        ConvertTo-Json -InputObject $dependentCopy -Depth 100 | Set-Content -LiteralPath $dependentFile -Encoding utf8
        $dependentOutput = (& $validator -FixturePath $dependentFile | Out-String)
        if (-not $dependentOutput.Contains('Result : PASS')) { throw 'A reviewed dependency edge connecting the exact two evaluated source versions must validate.' }
    }
    finally { if (Test-Path -LiteralPath $dependentFile) { Remove-Item -LiteralPath $dependentFile -Force } }

    $mutations = @(
        @{ Name='Orphan claim component'; Apply={ param($x) $x.claim_components[0].claim_id='missing-claim' } },
        @{ Name='Stable component identity changes owning claim'; Apply={ param($x) $newClaim=$x.claims[0].Clone(); $newClaim.claim_id='claim-other'; $newClaim.claim_version_id='claim-other-v1'; $newClaim.supersedes_claim_version_id=$null; $x.claims += $newClaim; $newComponent=$x.claim_components[0].Clone(); $newComponent.claim_id='claim-other'; $newComponent.claim_version_id='claim-other-v1'; $newComponent.claim_component_version_id='component-entity-other-v1'; $newComponent.supersedes_component_version_id=$null; $x.claim_components += $newComponent } },
        @{ Name='Duplicate claim version identifier'; Apply={ param($x) $x.claims += $x.claims[0] } },
        @{ Name='Duplicate component version identifier'; Apply={ param($x) $x.claim_components += $x.claim_components[0] } },
        @{ Name='UTC timestamp has a non-UTC offset'; Apply={ param($x) $x.created_at='2026-11-15T17:00:00-05:00' } },
        @{ Name='UTC timestamp contains an impossible calendar date'; Apply={ param($x) $x.created_at='2026-02-30T22:00:00Z' } },
        @{ Name='Evaluation unit source/version mismatch'; Apply={ param($x) $x.evaluation_units[0].source_id='src_fedcba98-7654-4321-8abc-fedcba987654' } },
        @{ Name='Duplicate evaluation unit tuple'; Apply={ param($x) $newUnit=$x.evaluation_units[0].Clone(); $newUnit.assessment_unit_id='unit-a-entity-duplicate'; $x.evaluation_units += $newUnit } },
        @{ Name='Evaluation unit bound to a different component version'; Apply={ param($x) $x.evaluation_units[0].claim_component_version_id='component-amount-v1' } },
        @{ Name='Claim version supersedes itself'; Apply={ param($x) $x.claims[0].supersedes_claim_version_id='claim-btc-purchase-v1' } },
        @{ Name='Unknown origin edge targets ordinary node'; Apply={ param($x) $x.provenance_edges[0].origin_node_id='node-version-b' } },
        @{ Name='Provenance node references missing source version'; Apply={ param($x) $x.provenance_nodes[0].entity_ref='missing-version' } },
        @{ Name='Provenance edge references missing evidence'; Apply={ param($x) $x.provenance_edges[0].evidence_refs=@('missing-evidence') } },
        @{ Name='Independent without positive evidence'; Apply={ param($x) $x.independence_assessments[0].status='INDEPENDIENTE' } },
        @{ Name='Independent evidence does not cover every evaluated source'; Apply={ param($x) $x.independence_assessments[0].status='INDEPENDIENTE'; $x.independence_assessments[0].supporting_evidence_refs=@('evidence-a'); $x.independence_assessments[0].human_review_status='REVIEWED'; $x.independence_assessments[0].reviewed_at='2026-11-15T22:05:00Z' } },
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
        @{ Name='Dependency edge points outside evaluated source set'; Apply={
            param($x)
            $newSource=$x.sources[0].Clone(); $newSource.source_id='src_11111111-1111-4111-8111-111111111111'; $x.sources += $newSource
            $newVersion=$x.source_versions[0].Clone(); $newVersion.source_version_id='version-c1'; $newVersion.source_id='src_11111111-1111-4111-8111-111111111111'; $newVersion.version_label='v1'; $newVersion.version_sequence=1; $newVersion.supersedes_source_version_id=$null; $x.source_versions += $newVersion
            $x.provenance_nodes += @{ node_id='node-version-c'; node_type='SOURCE_VERSION'; entity_ref='version-c1' }
            $x.provenance_edges += @{ edge_id='edge-a-c'; dependent_node_id='node-version-a'; origin_node_id='node-version-c'; relation_type='CITA_DE'; claim_component_id='component-entity'; claim_component_version_id='component-entity-v1'; evidence_refs=@('evidence-a'); recorded_at='2026-11-15T22:00:00Z'; valid_from=$null; valid_to=$null }
            $x.independence_assessments[0].status='DEPENDIENTE'; $x.independence_assessments[0].dependency_edge_refs=@('edge-a-c'); $x.independence_assessments[0].human_review_status='REVIEWED'; $x.independence_assessments[0].reviewed_at='2026-11-15T22:05:00Z'
        } },
        @{ Name='Dependency edge belongs to another component version'; Apply={
            param($x)
            $x.provenance_edges += @{ edge_id='edge-a-b-entity'; dependent_node_id='node-version-a'; origin_node_id='node-version-b'; relation_type='CITA_DE'; claim_component_id='component-entity'; claim_component_version_id='component-entity-v1'; evidence_refs=@('evidence-a'); recorded_at='2026-11-15T22:00:00Z'; valid_from=$null; valid_to=$null }
            $x.independence_assessments[1].status='DEPENDIENTE'; $x.independence_assessments[1].dependency_edge_refs=@('edge-a-b-entity'); $x.independence_assessments[1].human_review_status='REVIEWED'; $x.independence_assessments[1].reviewed_at='2026-11-15T22:05:00Z'
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
        @{ Name='Duplicate identity assessment at same source cutoff'; Apply={ param($x) $newIdentity=$x.identity_assessments[0].Clone(); $newIdentity.identity_assessment_id='identity-duplicate'; $x.identity_assessments += $newIdentity } },
        @{ Name='Unsupported probative state'; Apply={ param($x) $x.claim_assessments[0].evidentiary_status='HIGH_CONFIDENCE' } },
        @{ Name='Claim assessment missing rationale'; Apply={ param($x) $x.claim_assessments[0].rationale='' } },
        @{ Name='Partial corroboration without delimited scopes'; Apply={ param($x) $x.claim_assessments[0].evidentiary_status='PARCIALMENTE_CORROBORADA'; $x.claim_assessments[0].human_review_status='REVIEWED'; $x.claim_assessments[0].reviewed_at='2026-11-15T22:05:00Z'; $x.claim_assessments[0].supported_scope=$null; $x.claim_assessments[0].unsupported_scope=$null } },
        @{ Name='Conclusive state bypasses human review'; Apply={ param($x) $x.claim_assessments[0].evidentiary_status='CORROBORADA'; $x.claim_assessments[0].supporting_evidence_refs=@('evidence-a'); $x.claim_assessments[0].human_review_status='PENDING' } },
        @{ Name='Unauthorized retained content'; Apply={ param($x) $x.retention_records[0].content_retained=$true } },
        @{ Name='Retention record has orphan subject'; Apply={ param($x) $x.retention_records[0].subject_ref='missing-subject' } },
        @{ Name='Audit event has orphan subject'; Apply={ param($x) $x.audit_events[0].subject_ref='missing-subject' } },
        @{ Name='Integrity MATCH with different digests'; Apply={ param($x) $x.evidence_items[0].integrity_check.result='MATCH'; $x.evidence_items[0].integrity_check.expected_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'; $x.evidence_items[0].integrity_check.observed_digest='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb' } },
        @{ Name='Source content hash has no algorithm'; Apply={ param($x) $x.source_versions[0].content_hash='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' } },
        @{ Name='Missing source version sequence'; Apply={ param($x) $x.source_versions[1].Remove('version_sequence') } },
        @{ Name='Duplicate source version sequence within one source'; Apply={ param($x) $x.source_versions[1].source_id=$x.source_versions[0].source_id; $x.source_versions[1].version_sequence=$x.source_versions[0].version_sequence } },
        @{ Name='Duplicate claim version number within one claim'; Apply={ param($x) $new = $x.claims[0].Clone(); $new.claim_version_id='claim-btc-purchase-v2'; $x.claims += $new } },
        @{ Name='Duplicate component version number within one component'; Apply={ param($x) $new = $x.claim_components[0].Clone(); $new.claim_component_version_id='component-entity-v2'; $x.claim_components += $new } },
        @{ Name='Hash algorithm exists without content hash'; Apply={ param($x) $x.source_versions[0].hash_algorithm='SHA-256' } },
        @{ Name='Unsupported integrity algorithm retains digest'; Apply={ param($x) $x.evidence_items[0].integrity_check.expected_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' } },
        @{ Name='Retrieved before first detection'; Apply={ param($x) $x.source_versions[0].retrieved_at='2026-11-15T19:00:00Z' } },
        @{ Name='Injected numerical score'; Apply={ param($x) $x.factor_assessments[0].score=0.99 } },
        @{ Name='Injected confidential identity'; Apply={ param($x) $x.sources[0].real_name='Synthetic Person' } },
        @{ Name='Source identifier is not opaque'; Apply={ param($x) $x.sources[0].source_id='person-name' } },
        @{ Name='Source version supersedes itself'; Apply={ param($x) $x.source_versions[0].supersedes_source_version_id='version-a1' } },
        @{ Name='Source version supersedes a later version'; Apply={ param($x) $new = $x.source_versions[0].Clone(); $new.source_version_id='version-a2'; $new.version_label='v2'; $new.version_sequence=2; $new.supersedes_source_version_id='version-a1'; $x.source_versions += $new; $x.source_versions[0].supersedes_source_version_id='version-a2' } },
        @{ Name='Three-version source supersession cycle'; Apply={ param($x) $new2 = $x.source_versions[0].Clone(); $new2.source_version_id='version-a2'; $new2.version_label='v2'; $new2.version_sequence=2; $new2.supersedes_source_version_id='version-a1'; $new3 = $x.source_versions[0].Clone(); $new3.source_version_id='version-a3'; $new3.version_label='v3'; $new3.version_sequence=3; $new3.supersedes_source_version_id='version-a2'; $x.source_versions += @($new2,$new3); $x.source_versions[0].supersedes_source_version_id='version-a3' } },
        @{ Name='Hour precision cannot be silently upgraded to minute'; Apply={ param($x) $x.source_versions[0].original_timestamps[0].precision='MINUTE' } },
        @{ Name='Factor evidence crosses dimension boundary'; Apply={ param($x) $x.factor_assessments[0].supporting_evidence_refs=@('evidence-a') } },
        @{ Name='Factor evidence crosses component version'; Apply={ param($x) $x.evidence_items[0].factor_dimensions=@('RELATION_WITH_FACT'); $x.factor_assessments[20].supporting_evidence_refs=@('evidence-a') } },
        @{ Name='Factor evidence crosses source version'; Apply={ param($x) $x.evidence_items[0].factor_dimensions=@('RELATION_WITH_FACT'); $x.factor_assessments[10].supporting_evidence_refs=@('evidence-a') } },
        @{ Name='Evidence availability crosses component version'; Apply={ param($x) $x.evidence_availability[0].claim_component_version_id='component-amount-v1' } },
        @{ Name='Evidence availability crosses source version'; Apply={ param($x) $x.evidence_availability[0].assessment_unit_id='unit-b-entity' } },
        @{ Name='Evidence becomes available after evaluation cutoff'; Apply={ param($x) $x.evidence_availability[0].available_at='2026-11-15T23:00:00Z' } },
        @{ Name='Known availability lacks traceable basis'; Apply={ param($x) $x.evidence_availability[0].availability_basis='UNKNOWN' } },
        @{ Name='Duplicate evidence availability for the same unit'; Apply={ param($x) $x.evidence_availability += $x.evidence_availability[0] } },
        @{ Name='Source-stated timestamp cannot prove cutoff availability'; Apply={ param($x) $x.evidence_availability[0].availability_basis='SOURCE_STATED'; $x.claim_assessments[0].supporting_evidence_refs=@('evidence-a') } },
        @{ Name='Claim assessment uses evidence unavailable at its cutoff'; Apply={ param($x) $x.claim_assessments[0].supporting_evidence_refs=@('evidence-a'); $x.claim_assessments[0].assessment_cutoff='2026-11-15T20:00:00Z' } },
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
        PositivePartialScopeCases=1
        PositiveRetentionPendingDeletionCases=1
        PositiveHistoricalImportCases=1
        PositiveIndependenceCases=1
        PositiveDependencyCases=1
        NegativeMutations=$mutations.Count
        TotalChecks=($mutations.Count + 8)
        Scope='Deterministic synthetic contract-validator rejection tests.'
    } | Format-List
}
finally {
    if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force }
}
