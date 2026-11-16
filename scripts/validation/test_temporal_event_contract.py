"""Positive and negative semantic tests for temporal contract 1.0.0."""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts/validation/validate_temporal_event_contract.py"
SPEC = importlib.util.spec_from_file_location("temporal_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)
FIXTURE = json.loads((ROOT / "tests/fixtures/contracts/temporal-event-contract-v1.0.0.json").read_text(encoding="utf-8"))


class TemporalContractTests(unittest.TestCase):
    def setUp(self):
        self.package = copy.deepcopy(FIXTURE)

    def assert_invalid(self, mutate, expected):
        mutate(self.package)
        with self.assertRaisesRegex(validator.ContractError, expected):
            validator.validate_semantics(self.package)

    def test_base_fixture_passes(self):
        validator.validate_semantics(self.package)

    def test_unknown_role_requires_null_bounds(self):
        self.assert_invalid(lambda p: p["temporal_assertions"][2].update(precision="DAY"), "UNKNOWN role")

    def test_unknown_precision_cannot_be_actual(self):
        self.assert_invalid(lambda p: p["temporal_assertions"][0].update(precision="UNKNOWN"), "UNKNOWN precision")

    def test_range_requires_both_bounds(self):
        self.assert_invalid(lambda p: p["temporal_assertions"][1]["interval_end"].update(value=None), "RANGE requires")

    def test_inverted_interval_rejected(self):
        self.assert_invalid(lambda p: p["temporal_assertions"][0]["interval_start"].update(value="2026-12-11T00:00:00Z"), "inverted")

    def test_equal_exclusive_interval_rejected(self):
        def mutate(p):
            p["temporal_assertions"][0]["interval_end"]["value"] = p["temporal_assertions"][0]["interval_start"]["value"]
            p["temporal_assertions"][0]["interval_end"]["inclusive"] = False
        self.assert_invalid(mutate, "empty interval")

    def test_normalized_bound_must_match(self):
        self.assert_invalid(lambda p: p["temporal_assertions"][0].update(normalized_start_utc="2026-12-09T00:00:00Z"), "normalized start")

    def test_actual_requires_evidence(self):
        def mutate(p):
            p["temporal_assertions"][0].update(temporal_role="ACTUAL", evidence_ref=None)
        self.assert_invalid(mutate, "ACTUAL requires")

    def test_range_cannot_be_non_approximate(self):
        self.assert_invalid(lambda p: p["temporal_assertions"][1].update(approximation=False), "RANGE cannot")

    def test_assertion_versions_must_be_contiguous(self):
        self.assert_invalid(lambda p: p["temporal_assertions"][1].update(version=3), "contiguous")

    def test_assertion_must_supersede_immediate_previous(self):
        self.assert_invalid(lambda p: p["temporal_assertions"][1].update(supersedes_assertion_id="missing"), "immediately previous")

    def test_duplicate_assertion_id_rejected(self):
        self.assert_invalid(lambda p: p["temporal_assertions"][1].update(temporal_assertion_id="ta-event-1-v1"), "duplicate")

    def test_assertion_rejects_unknown_event(self):
        self.assert_invalid(lambda p: p["temporal_assertions"][0].update(event_id="missing-event"), "unknown event reference")

    def test_assertion_source_must_be_registered_on_event(self):
        self.assert_invalid(lambda p: p["temporal_assertions"][0].update(source_ref="unregistered-source"), "not registered")

    def test_assertion_recorded_before_retrieval_rejected(self):
        self.assert_invalid(lambda p: p["temporal_assertions"][0].update(recorded_at="2026-11-15T10:01:00Z"), "retrieval cannot occur after")

    def test_conflict_cannot_predate_assertions(self):
        self.assert_invalid(lambda p: p["temporal_conflicts"][0].update(recorded_at="2026-11-15T10:00:00Z"), "cannot predate")

    def test_conflict_rejects_unknown_assertion(self):
        self.assert_invalid(lambda p: p["temporal_conflicts"][0]["assertion_refs"].append("missing"), "unknown temporal assertion")

    def test_conflict_rejects_cross_event_assertion(self):
        self.assert_invalid(lambda p: p["temporal_conflicts"][0]["assertion_refs"].append("ta-event-2-v1"), "belong to the conflict event")

    def test_illegal_conflict_transition_rejected(self):
        self.package["conflict_decisions"] = [{
            "decision_id":"decision-1","conflict_id":"conflict-1","from_status":"OPEN","to_status":"RESOLVED",
            "assertion_refs":["ta-event-1-v1"],"supporting_evidence_refs":["ev-1"],"contrary_evidence_refs":[],
            "scope":"date","rationale":"supported","limitations":"one source","actor_ref":"actor-1",
            "decided_at":"2026-11-16T12:00:00Z","assessment_cutoff":"2026-11-16T11:00:00Z",
            "rules_version":"rules-1","supersedes_decision_id":None}]
        self.assert_invalid(lambda p: None, "illegal conflict transition")

    def test_resolution_requires_explicit_limits(self):
        self.package["conflict_decisions"] = [{
            "decision_id":"decision-1","conflict_id":"conflict-1","from_status":"UNDER_REVIEW","to_status":"RESOLVED",
            "assertion_refs":["ta-event-1-v1"],"supporting_evidence_refs":["ev-1"],"contrary_evidence_refs":[],
            "scope":"date","rationale":"supported","limitations":"","actor_ref":"actor-1",
            "decided_at":"2026-11-16T12:00:00Z","assessment_cutoff":"2026-11-16T11:00:00Z",
            "rules_version":"rules-1","supersedes_decision_id":None}]
        self.package["temporal_conflicts"][0]["status"]="RESOLVED"
        self.assert_invalid(lambda p: None, "scope and limitations")

    def test_decision_cannot_precede_cutoff(self):
        self.package["conflict_decisions"] = [{
            "decision_id":"decision-1","conflict_id":"conflict-1","from_status":"OPEN","to_status":"UNDER_REVIEW",
            "assertion_refs":["ta-event-1-v1"],"supporting_evidence_refs":[],"contrary_evidence_refs":[],
            "scope":"review","rationale":"review","limitations":"pending","actor_ref":"actor-1",
            "decided_at":"2026-11-16T10:00:00Z","assessment_cutoff":"2026-11-16T11:00:00Z",
            "rules_version":"rules-1","supersedes_decision_id":None}]
        self.package["temporal_conflicts"][0]["status"]="UNDER_REVIEW"
        self.assert_invalid(lambda p: None, "cannot precede")

    def test_assessment_rejects_late_known_assertion(self):
        self.assert_invalid(lambda p: p["temporal_assessments"][0].update(assessment_cutoff="2026-11-15T10:00:00Z"), "not known at assessment cutoff")

    def test_assessment_rejects_assertion_from_another_event(self):
        self.package["temporal_assessments"][0]["event_id"] = "event-2"
        self.assert_invalid(lambda p: None, "belongs to another event")

    def test_assessment_rejects_duplicate_assertion_reference(self):
        self.assert_invalid(lambda p: p["temporal_assessments"][0]["assertion_refs"].append("ta-event-1-v1"), "duplicate assertion reference")

    def test_assessment_rejects_unknown_event(self):
        self.package["temporal_assessments"][0]["event_id"] = "missing-event"
        self.assert_invalid(lambda p: None, "unknown event reference")

    def test_assessment_rejects_incorrect_derived_state(self):
        self.package["temporal_assessments"][0]["derived_temporal_state"] = "PAST"
        self.assert_invalid(lambda p: None, "derived temporal state must be FUTURE")

    def test_assessment_unknown_assertion_forces_undetermined_state(self):
        self.package["temporal_assessments"][0]["event_id"] = "event-2"
        self.package["temporal_assessments"][0]["assertion_refs"] = ["ta-event-2-v1"]
        self.package["temporal_assessments"][0]["derived_temporal_state"] = "FUTURE"
        self.assert_invalid(lambda p: None, "derived temporal state must be UNDETERMINED")

    def test_assessment_rejects_unknown_reference(self):
        self.assert_invalid(lambda p: p["temporal_assessments"][0]["assertion_refs"].append("missing"), "unknown assertion reference")

    def test_decision_rejects_unknown_superseded_decision(self):
        self.package["conflict_decisions"] = [{
            "decision_id":"decision-1","conflict_id":"conflict-1","from_status":"OPEN","to_status":"UNDER_REVIEW",
            "assertion_refs":["ta-event-1-v1"],"supporting_evidence_refs":[],"contrary_evidence_refs":[],
            "scope":"review","rationale":"review","limitations":"pending","actor_ref":"actor-1",
            "decided_at":"2026-11-16T12:00:00Z","assessment_cutoff":"2026-11-16T11:00:00Z",
            "rules_version":"rules-1","supersedes_decision_id":"missing-decision"}]
        self.package["temporal_conflicts"][0]["status"]="UNDER_REVIEW"
        self.assert_invalid(lambda p: None, "superseded decision does not exist")

    def test_reproducible_manifest_rejects_missing_components(self):
        assessment = self.package["temporal_assessments"][0]
        self.package["reproducibility_manifests"] = [{
            "manifest_id":"manifest-1","assessment_id":assessment["assessment_id"],"assessment_cutoff":assessment["assessment_cutoff"],
            "contract_version":"1.0.0","schema_sha256":"a"*64,"assertion_versions":[{"assertion_id":"ta-event-1-v1","version":1},{"assertion_id":"ta-event-1-v2","version":2}],
            "excluded_assertions":[],"evidence_refs":["evidence-calendar-1","evidence-calendar-2"],"conflict_decision_refs":[],
            "rules_version":assessment["rules_version"],"rules_sha256":"b"*64,"tzdb_version":"2026a","software_version":assessment["software_version"],"result_sha256":"c"*64,
            "canonicalization":"RFC8785","reproducibility_status":"REPRODUCIBLE","missing_components":["evidence body"],
            "created_at":"2026-11-16T12:02:00Z"}]
        self.assert_invalid(lambda p: None, "cannot declare missing")

    def test_manifest_rejects_assertion_set_mismatch(self):
        assessment = self.package["temporal_assessments"][0]
        self.package["reproducibility_manifests"] = [{
            "manifest_id":"manifest-1","assessment_id":assessment["assessment_id"],"assessment_cutoff":assessment["assessment_cutoff"],
            "contract_version":"1.0.0","schema_sha256":"a"*64,"assertion_versions":[{"assertion_id":"ta-event-1-v1","version":1}],
            "excluded_assertions":[],"evidence_refs":["evidence-calendar-1"],"conflict_decision_refs":[],"rules_version":assessment["rules_version"],
            "rules_sha256":"b"*64,"tzdb_version":"2026a","software_version":assessment["software_version"],"result_sha256":"c"*64,
            "canonicalization":"RFC8785","reproducibility_status":"REPRODUCIBLE","missing_components":[],
            "created_at":"2026-11-16T12:02:00Z"}]
        self.assert_invalid(lambda p: None, "must match the assessment assertion set")

    def test_partial_manifest_requires_missing_components(self):
        assessment = self.package["temporal_assessments"][0]
        self.package["reproducibility_manifests"] = [{
            "manifest_id":"manifest-1","assessment_id":assessment["assessment_id"],"assessment_cutoff":assessment["assessment_cutoff"],
            "contract_version":"1.0.0","schema_sha256":"a"*64,"assertion_versions":[{"assertion_id":"ta-event-1-v1","version":1},{"assertion_id":"ta-event-1-v2","version":2}],
            "excluded_assertions":[],"evidence_refs":["evidence-calendar-1","evidence-calendar-2"],"conflict_decision_refs":[],
            "rules_version":assessment["rules_version"],"rules_sha256":"b"*64,"tzdb_version":"2026a","software_version":assessment["software_version"],"result_sha256":"c"*64,
            "canonicalization":"RFC8785","reproducibility_status":"PARTIALLY_REPRODUCIBLE","missing_components":[],
            "created_at":"2026-11-16T12:02:00Z"}]
        self.assert_invalid(lambda p: None, "must enumerate")

    def test_manifest_cannot_predate_assessment_record(self):
        assessment = self.package["temporal_assessments"][0]
        self.package["reproducibility_manifests"] = [{
            "manifest_id":"manifest-1","assessment_id":assessment["assessment_id"],"assessment_cutoff":assessment["assessment_cutoff"],
            "contract_version":"1.0.0","schema_sha256":"a"*64,"assertion_versions":[
                {"assertion_id":"ta-event-1-v1","version":1},{"assertion_id":"ta-event-1-v2","version":2}],
            "excluded_assertions":[],"evidence_refs":["evidence-calendar-1","evidence-calendar-2"],"conflict_decision_refs":[],
            "rules_version":assessment["rules_version"],"rules_sha256":"b"*64,"tzdb_version":"2026a",
            "software_version":assessment["software_version"],"result_sha256":"c"*64,"canonicalization":"RFC8785",
            "reproducibility_status":"REPRODUCIBLE","missing_components":[],"created_at":"2026-11-16T12:00:30Z"}]
        self.assert_invalid(lambda p: None, "cannot predate its assessment record")

    def test_repro_manifest_cutoff_must_match_assessment(self):
        assessment = self.package["temporal_assessments"][0]
        self.package["reproducibility_manifests"] = [{
            "manifest_id":"manifest-1","assessment_id":assessment["assessment_id"],"assessment_cutoff":"2026-11-15T12:00:00Z",
            "contract_version":"1.0.0","schema_sha256":"a"*64,"assertion_versions":[],"excluded_assertions":[],
            "evidence_refs":[],"conflict_decision_refs":[],"rules_version":"rules-1","rules_sha256":"b"*64,
            "tzdb_version":"2026a","software_version":"1.0.0","result_sha256":"c"*64,"canonicalization":"RFC8785",
            "reproducibility_status":"REPRODUCIBLE","missing_components":[],"created_at":"2026-11-16T12:02:00Z"}]
        self.assert_invalid(lambda p: None, "cutoff differs")

if __name__ == "__main__":
    unittest.main(verbosity=2)
