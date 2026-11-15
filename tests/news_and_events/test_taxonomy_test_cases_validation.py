"""Mutation tests for the taxonomy document validator (M-01…M-13)."""
from __future__ import annotations

import unittest
from pathlib import Path

from scripts.news_and_events.validate_taxonomy_test_cases import validate_text

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/news-and-events/catalyst-taxonomy-test-cases.md"
BASE = DOC.read_text(encoding="utf-8")


class TaxonomyMutationTests(unittest.TestCase):
    def assert_mutation_rejected(self, mutated: str, code: str) -> None:
        errors = validate_text(mutated, ROOT)
        self.assertTrue(any(error.startswith(code) for error in errors), errors)

    def test_m01_duplicate_scenario_id(self):
        needle = "#### MAC-P —"
        self.assert_mutation_rejected(BASE.replace(needle, needle + " duplicate\n\n" + needle, 1), "MATRIX_IDS")

    def test_m02_missing_scenario_id(self):
        self.assert_mutation_rejected(BASE.replace("#### MAC-P —", "#### MAC-P-REMOVED —", 1), "MATRIX_IDS")

    def test_m03_unknown_scenario_id(self):
        self.assert_mutation_rejected(BASE.replace("#### MAC-P —", "#### UNKNOWN-P —", 1), "UNKNOWN_IDS")

    def test_m04_broken_traceability_pair(self):
        self.assert_mutation_rejected(BASE.replace("| 1 | Política monetaria y bancos centrales | MAC-P | MAC-N |", "| 1 | Política monetaria y bancos centrales | MAC-P | ECO-N |", 1), "TRACEABILITY")

    def test_m05_negative_without_none_category(self):
        self.assert_mutation_rejected(BASE.replace("categoría principal NINGUNA", "categoría principal MAC", 1), "NEGATIVE_CATEGORY")

    def test_m06_missing_required_case_field(self):
        self.assert_mutation_rejected(BASE.replace("**Entrada/objeto:**", "**Entrada:**", 1), "CASE_CONTRACT")

    def test_m07_leak_requires_official_confirmation(self):
        self.assert_mutation_rejected(BASE.replace("No exigir anuncio oficial posterior", "Exigir anuncio oficial posterior", 1), "LEAK_TEMPORAL")

    def test_m08_absence_of_corroboration_treated_as_false(self):
        self.assert_mutation_rejected(BASE.replace("solo falta corroboración", "la falta de corroboración demuestra falsedad", 1), "LEAK_EVIDENCE")

    def test_m09_cross_family_label_removed(self):
        self.assert_mutation_rejected(BASE.replace("**no sustituye**", "**sustituye**", 1), "CROSS_LABEL")

    def test_m10_broken_local_link(self):
        self.assert_mutation_rejected(BASE.replace("(catalyst-taxonomy.md)", "(missing-taxonomy-file.md)", 1), "LOCAL_LINK")

    def test_m11_temporal_fields_collapsed(self):
        self.assert_mutation_rejected(BASE.replace("Fecha/hora de ocurrencia, publicación, primera detección, anuncio oficial y ejecución", "Fecha genérica", 1), "TIME_SEPARATION")

    def test_m12_false_independence_claim(self):
        self.assert_mutation_rejected(BASE.replace("no equivale a dos revisiones humanas independientes", "equivale a dos revisiones humanas independientes", 1), "REVIEW_GOVERNANCE")

    def test_m13_h_owner_requirement_stays_in_original_case(self):
        needle = "**Requisitos H-OWNER consolidados — Filtraciones-N:**"
        self.assertIn(needle, BASE)
        mutated = BASE.replace(
            needle,
            "**Requisitos H-OWNER consolidados — Filtraciones-N (desvinculado):**",
            1,
        )
        self.assert_mutation_rejected(mutated, "H_OWNER_CONSOLIDATION")


if __name__ == "__main__":
    unittest.main()
