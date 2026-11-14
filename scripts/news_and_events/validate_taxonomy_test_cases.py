#!/usr/bin/env python3
"""Deterministic structural validator for SINAYXA catalyst taxonomy test cases.

This validates declared document contracts, not factual truth or causal claims.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCUMENT = ROOT / "docs/news-and-events/catalyst-taxonomy-test-cases.md"

MAIN_IDS = {
    "MAC-P", "MAC-N", "ECO-P", "ECO-N", "REG-P", "REG-N", "ETF-P", "ETF-N",
    "INS-P", "INS-N", "COM-P", "COM-N", "EXC-P", "EXC-N", "TEC-P", "TEC-N",
    "GEO-P", "GEO-N", "DeFi-P", "DeFi-N", "Stablecoins-P", "Stablecoins-N",
    "Tokenomics-P", "Tokenomics-N", "Minería-P", "Minería-N", "Gobernanza-P",
    "Gobernanza-N", "Custodia-P", "Custodia-N", "Ciberseguridad-P",
    "Ciberseguridad-N", "Materias primas/energía/tecnología-P",
    "Materias primas/energía/tecnología-N", "Filtraciones-P", "Filtraciones-N",
}
BND_IDS = {f"BND-{n:02d}" for n in range(1, 11)}
REQUIRED_CASE_FIELDS = (
    "**Entrada/objeto:**", "**Salida:**", "**Evidencia mínima:**",
    "**INDETERMINADO si:**", "**No inferir:**",
)


def _section(text: str, start: str, end: str) -> str:
    a = text.find(start)
    if a < 0:
        return ""
    b = text.find(end, a + len(start)) if end else -1
    return text[a:] if b < 0 else text[a:b]


def validate_text(text: str, root: Path | None = None) -> list[str]:
    errors: list[str] = []
    headings = re.findall(r"^#### (.+?) —", text, flags=re.MULTILINE)
    main_seen = [item for item in headings if item in MAIN_IDS]
    bnd_seen = [item for item in headings if item in BND_IDS]
    unknown = [
        item for item in headings
        if (item.endswith("-P") or item.endswith("-N") or item.startswith("BND-"))
        and item not in MAIN_IDS and item not in BND_IDS
    ]

    if len(main_seen) != 36 or set(main_seen) != MAIN_IDS or len(main_seen) != len(set(main_seen)):
        errors.append("MATRIX_IDS: deben existir exactamente los 36 IDs principales, una sola vez")
    if len(bnd_seen) != 10 or set(bnd_seen) != BND_IDS or len(bnd_seen) != len(set(bnd_seen)):
        errors.append("BOUNDARY_IDS: deben existir exactamente BND-01…BND-10, una sola vez")
    if unknown:
        errors.append("UNKNOWN_IDS: identificadores de escenario no reconocidos: " + ", ".join(unknown))

    matrix = _section(text, "## 2. Matriz de trazabilidad de los 36 escenarios", "## 3. Escenarios principales")
    rows = re.findall(r"^\|\s*\d+\s*\|[^|]*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", matrix, re.MULTILINE)
    expected_pairs = {(item[:-2] + "-P", item[:-2] + "-N") for item in MAIN_IDS if item.endswith("-P")}
    observed_pairs = {(a.strip(), b.strip()) for a, b in rows}
    if len(rows) != 18 or observed_pairs != expected_pairs:
        errors.append("TRACEABILITY: la matriz debe contener 18 pares positivos/negativos exactos")

    for case_id in sorted(MAIN_IDS | BND_IDS):
        match = re.search(rf"^#### {re.escape(case_id)} —.*?(?=^#### |^## |\Z)", text, re.MULTILINE | re.DOTALL)
        if not match:
            continue
        block = match.group(0)
        missing = [field for field in REQUIRED_CASE_FIELDS if field not in block and not (field == "**Salida:**" and "**Salida A:**" in block and "**Salida B:**" in block)]
        if missing:
            errors.append(f"CASE_CONTRACT: {case_id} carece de {', '.join(missing)}")

    for case_id in sorted(item for item in MAIN_IDS if item.endswith("-N")):
        match = re.search(rf"^#### {re.escape(case_id)} —.*?(?=^#### |^## |\Z)", text, re.MULTILINE | re.DOTALL)
        if match and not re.search(r"categoría principal NINGUNA", match.group(0), re.IGNORECASE):
            errors.append(f"NEGATIVE_CATEGORY: {case_id} debe declarar categoría principal NINGUNA")

    leak_positive = re.search(r"^#### Filtraciones-P —.*?(?=^#### |^## |\Z)", text, re.MULTILINE | re.DOTALL)
    if not leak_positive or "No exigir anuncio oficial posterior" not in leak_positive.group(0):
        errors.append("LEAK_TEMPORAL: no debe exigirse confirmación oficial posterior para conservar una señal anticipatoria trazable")
    leak_negative = re.search(r"^#### Filtraciones-N —.*?(?=^#### |^## |\Z)", text, re.MULTILINE | re.DOTALL)
    if not leak_negative or "solo falta corroboración" not in leak_negative.group(0):
        errors.append("LEAK_EVIDENCE: falta de corroboración no debe convertirse en prueba de falsedad")

    cross_contract = _section(text, "### 1.3 Contrato de salida común", "### 1.4 Reglas normativas identificadas para trazabilidad")
    if "La familia transversal **no sustituye** la categoría principal." not in cross_contract:
        errors.append("CROSS_LABEL: la familia transversal debe mantenerse separada de la categoría principal")
        errors.append("CROSS_LABEL: la familia transversal debe mantenerse separada de la categoría principal")
    if "Fecha/hora de ocurrencia, publicación, primera detección, anuncio oficial y ejecución" not in text:
        errors.append("TIME_SEPARATION: faltan campos temporales diferenciados")

    policy_markers = (
        "SINGLE-HUMAN REVIEW WITH COMPENSATING CONTROLS",
        "no equivale a dos revisiones humanas independientes",
        "H-OWNER",
        "AI-ADVERSARIAL",
        "AUTO-VALIDATION",
        "ADVERSARIAL-TEST",
        "PASS — SINGLE-HUMAN COMPENSATING CONTROLS",
        "INDEPENDENT HUMAN REVIEW VERIFIED",
    )
    if any(marker not in text for marker in policy_markers):
        errors.append("REVIEW_GOVERNANCE: faltan roles o estados de revisión honestos")

    if "MANUAL_REVIEW_REQUIRED" not in text:
        errors.append("MANUAL_REVIEW: falta estado para defectos semánticos no automatizables")

    if root is not None:
        doc_dir = root / "docs/news-and-events"
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("https://", "http://", "#", "mailto:")):
                continue
            local = (doc_dir / target.split("#", 1)[0]).resolve()
            if not local.exists():
                errors.append(f"LOCAL_LINK: destino inexistente: {target}")

    return errors


def main() -> int:
    if not DOCUMENT.is_file():
        print(f"FAIL: no se encontró {DOCUMENT}")
        return 2
    errors = validate_text(DOCUMENT.read_text(encoding="utf-8"), ROOT)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"Resultado: FAIL ({len(errors)} defectos)")
        return 1
    print("PASS: 36 escenarios, 18 pares, 10 fronteras, contratos, categorías negativas, temporalidad, roles y enlaces.")
    print("Límite: validación estructural; no demuestra verdad factual, calidad de fuentes ni causalidad.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
