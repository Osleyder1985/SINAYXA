[CmdletBinding()]
param([Parameter()][string]$FixturePath)
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($FixturePath)) {
    $FixturePath = Join-Path $PSScriptRoot '..\..\tests\fixtures\methodology\alerts\a01-a15-synthetic-conformance-v1.0.0.json'
}
function Assert-Condition {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}
$resolvedPath = (Resolve-Path -LiteralPath $FixturePath).Path
try { $fixture = Get-Content -LiteralPath $resolvedPath -Raw -Encoding UTF8 | ConvertFrom-Json -Depth 50 }
catch { throw "Fixture JSON could not be parsed: $($_.Exception.Message)" }
Assert-Condition ($fixture.schema_version -eq '1.0.0') 'Unsupported alert fixture schema_version.'
Assert-Condition ($fixture.package_id -eq 'SINAYXA-ALERTS-A01-A15-SYNTHETIC-001') 'Unexpected alert fixture package_id.'
Assert-Condition ($fixture.status -eq 'SYNTHETIC_TEST_FIXTURE_NOT_REAL_WORLD_EVIDENCE') 'Fixture must be explicitly marked synthetic.'
Assert-Condition ($fixture.source_proposal -eq 'docs/news-and-events/alert-severity-and-deduplication-proposal.md') 'Fixture source proposal does not match Issue #17.'
Assert-Condition ($fixture.source_issue -eq 17) 'Fixture must identify Issue #17.'
Assert-Condition ($fixture.scope -like '*unapproved Issue #17 proposal*' -and $fixture.scope -like '*do not approve the methodology*') 'Fixture scope must preserve the pending-approval boundary.'
$expectedIds = 1..15 | ForEach-Object { 'A{0:D2}' -f $_ }
$actualIds = @($fixture.cases | ForEach-Object { $_.id })
Assert-Condition ($actualIds.Count -eq 15) "Expected exactly 15 alert cases; found $($actualIds.Count)."
Assert-Condition (@($actualIds | Select-Object -Unique).Count -eq 15) 'Duplicate alert case IDs detected.'
for ($index = 0; $index -lt $expectedIds.Count; $index++) {
    Assert-Condition ($actualIds[$index] -eq $expectedIds[$index]) "Alert case order/ID mismatch at position $($index + 1)."
}
$allowedDecisions = @('SUPPRESS_DUPLICATE','GROUP_DEPENDENT_REFERENCE','EVALUATE_OFFICIAL_ACT','CREATE_WATCH_ALERT_IF_GUARDS_PASS','ISSUE_VISIBLE_MATERIAL_UPDATE','REASSESS_CLAIM_AND_UPDATE_IF_MATERIAL','NO_PROOF_OR_SEVERITY_UPGRADE','KEEP_EVENTS_SEPARATE_OPTIONAL_GROUP','CREATE_MATERIAL_VERSION_UPDATE','NO_RESEND_ATTACH_CONTEXT','UPDATE_URGENCY_ONLY_IF_POLICY_ALLOWS','REASSESS_PERSISTENCE_ONLY_WITH_EVIDENCE','KEEP_CLAIMS_SEPARATE_AND_LINK_EVENT','PRESERVE_UNRESOLVED_SOURCE_RELATIONSHIP','SUPPRESS_DELIVERY_WITH_AUDIT_RECORD')
$allowedSeverities = @('NOT_ASSIGNED','REQUIRES_SCOPE_ASSESSMENT','REQUIRES_JUSTIFICATION','REASSESS_WITH_REASON','NO_CHANGE_FROM_PRICE_ALONE','ASSESS_PER_EVENT','REASSESS_CURRENT_IMPACT_IF_EVIDENCED','ASSESS_PER_CLAIM','NO_CHANGE_FROM_UNKNOWN_INDEPENDENCE','UNCHANGED','NO_CHANGE')
$allowedUrgencies = @('PRESERVE_EXISTING','REQUIRES_VERIFIED_MILESTONE','DESCONOCIDA_UNLESS_VERIFIED','REASSESS_WITH_REASON','NO_CHANGE_FROM_PRICE_ALONE','ASSESS_PER_EVENT','NO_CHANGE','MAY_CHANGE_WITH_TEMPORAL_EVIDENCE','PASADA','ASSESS_PER_CLAIM','NO_CHANGE_FROM_UNKNOWN_INDEPENDENCE','UNCHANGED')
$allowedStatuses = @('PRESERVE_EXISTING','CORROBORADA','NO_CORROBORADA','PRESERVE_PRIOR_CLAIM_STATUS_UNTIL_REASSESSED','REASSESS_FROM_NEW_EVIDENCE','NO_CHANGE_FROM_PRICE_ALONE','ASSESS_PER_CLAIM','REASSESS_EXACT_CLAIM_SCOPE','NO_CHANGE','UNCHANGED','PRESERVE_UNTIL_NEW_EVIDENCE','PRESERVE_EACH_CLAIM_AND_UNRESOLVED_CONFLICT','NO_UPGRADE_FROM_UNKNOWN_INDEPENDENCE')
$requiredInvariants = @('price_changes_evidentiary_status','severity_changes_evidentiary_status','republishing_is_independent','grouping_merges_evidence','suppression_deletes_history','retroactive_rewrite')
foreach ($case in $fixture.cases) {
    $id = [string]$case.id
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($case.scenario)) "$($id): scenario is required."
    Assert-Condition ($null -ne $case.input -and $null -ne $case.expected -and $null -ne $case.invariants) "$($id): input, expected, and invariants are required."
    Assert-Condition ($allowedDecisions -contains [string]$case.expected.decision) "$($id): unsupported decision."
    Assert-Condition ($allowedSeverities -contains [string]$case.expected.severity) "$($id): unsupported severity expectation."
    Assert-Condition ($allowedUrgencies -contains [string]$case.expected.urgency) "$($id): unsupported urgency expectation."
    Assert-Condition ($allowedStatuses -contains [string]$case.expected.evidentiary_status) "$($id): unsupported evidentiary-status expectation."
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($case.expected.history)) "$($id): history handling is required."
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($case.expected.reason)) "$($id): decision rationale is required."
    foreach ($invariant in $requiredInvariants) {
        Assert-Condition (@($case.invariants.PSObject.Properties.Name) -contains $invariant) "$($id): missing invariant $invariant."
        Assert-Condition ($case.invariants.$invariant -eq $false) "$($id): invariant $invariant must remain false."
    }
}
$byId = @{}
foreach ($case in $fixture.cases) { $byId[[string]$case.id] = $case }
Assert-Condition ($byId.A01.expected.decision -eq 'SUPPRESS_DUPLICATE' -and $byId.A01.input.same_source_item -eq $true -and $byId.A01.input.same_version -eq $true) 'A01 must suppress only the same source item and version.'
Assert-Condition ($byId.A02.expected.decision -eq 'GROUP_DEPENDENT_REFERENCE' -and $byId.A02.input.independent_origins_proven -eq $false) 'A02 must not count syndicated republications as independent corroboration.'
Assert-Condition ($byId.A03.expected.evidentiary_status -eq 'CORROBORADA' -and $byId.A03.expected.evidence_scope -eq 'OFFICIAL_ACT_ONLY') 'A03 must corroborate only the official act/publication.'
Assert-Condition ($byId.A04.expected.evidentiary_status -eq 'NO_CORROBORADA' -and $byId.A04.expected.visible_label -eq 'NO_CONFIRMADA' -and $byId.A04.expected.severity -eq 'REQUIRES_JUSTIFICATION') 'A04 must keep the rumour uncorroborated and visibly unconfirmed.'
Assert-Condition ($byId.A05.expected.history -eq 'RETAIN_RUMOUR_AND_DENIAL' -and $byId.A05.input.denial_truth_independently_established -eq $false) 'A05 must retain both the rumour and denial without treating the denial as automatic refutation.'
Assert-Condition ($byId.A06.input.independent_origin_proven -eq $true -and $byId.A06.expected.evidentiary_status -eq 'REASSESS_FROM_NEW_EVIDENCE') 'A06 must require demonstrated independent origin and reassessment from new evidence.'
Assert-Condition ($byId.A07.input.only_new_observation -eq 'PRICE_DECLINE' -and $byId.A07.expected.evidentiary_status -eq 'NO_CHANGE_FROM_PRICE_ALONE') 'A07 must not use price movement as corroboration.'
Assert-Condition ($byId.A08.input.same_real_world_event -eq $false -and $byId.A08.expected.history -eq 'RETAIN_SEPARATE_EVENT_IDENTITIES') 'A08 must preserve distinct event identities.'
Assert-Condition ($byId.A09.input.material_field_changed -eq 'AMOUNT_OR_DATE' -and $byId.A09.expected.history -eq 'RETAIN_PREVIOUS_VERSION') 'A09 must preserve the previous version after a material correction.'
Assert-Condition ($byId.A10.input.new_evidence -eq $false -and $byId.A10.expected.decision -eq 'NO_RESEND_ATTACH_CONTEXT') 'A10 must not resend when no new evidence or claim exists.'
Assert-Condition ($byId.A11.input.verified_future_milestone -eq $true -and $byId.A11.expected.severity -eq 'UNCHANGED' -and $byId.A11.expected.evidentiary_status -eq 'UNCHANGED') 'A11 may change urgency only; severity and evidentiary status remain unchanged.'
Assert-Condition ($byId.A12.input.event_is_past -eq $true -and $byId.A12.expected.urgency -eq 'PASADA' -and $byId.A12.input.age_used_as_future_horizon -eq $false) 'A12 must keep past-event age separate from future urgency.'
Assert-Condition ($byId.A13.input.same_event -eq $true -and $byId.A13.expected.decision -eq 'KEEP_CLAIMS_SEPARATE_AND_LINK_EVENT' -and $byId.A13.input.evidence_lines_individually_sufficient -eq $false) 'A13 must preserve separate claims and must not resolve by majority.'
Assert-Condition ($byId.A14.expected.independence_of_origin -eq 'DESCONOCIDA' -and $byId.A14.expected.evidentiary_status -eq 'NO_UPGRADE_FROM_UNKNOWN_INDEPENDENCE') 'A14 must not upgrade corroboration when source independence is unknown.'
Assert-Condition ($byId.A15.expected.decision -eq 'SUPPRESS_DELIVERY_WITH_AUDIT_RECORD' -and ($byId.A15.expected.audit_fields -join ',') -eq 'reason,rule_id,actor,timestamp') 'A15 must preserve an auditable suppression record.'
[pscustomobject]@{ Result='PASS'; Package=$fixture.package_id; Cases=$fixture.cases.Count; DecisionsValidated=@($fixture.cases.expected.decision | Sort-Object -Unique).Count; InvariantsChecked=$requiredInvariants.Count; Scope='Synthetic structural conformance to the unapproved Issue #17 proposal only; not empirical validation or production alert implementation.' } | Format-List
