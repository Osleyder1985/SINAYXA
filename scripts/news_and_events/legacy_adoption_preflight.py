"""Read-only legacy database adoption preflight.

This module never bootstraps the control plane and never writes an adoption
attestation. A matching result is only permission to proceed to a separately
implemented, revalidating adoption operation.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from scripts.news_and_events.catalog_fingerprint import (
    ALGORITHM_VERSION,
    CatalogFingerprintError,
    fingerprint_schema,
)

SUPPORTED_SERVER_VERSION_NUM = 180007
LEGACY_MIGRATION_IDS = (
    "issue-2-event-registry-0001",
    "issue-2-temporal-conflicts-0002",
    "issue-2-temporal-assessments-manifests-0003",
    "issue-2-source-evidence-artifacts-0004",
    "issue-2-append-only-truncate-guard-0005",
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class LegacyAdoptionPreflightError(RuntimeError):
    """Raised when the preflight cannot be safely executed."""


@dataclass(frozen=True)
class LegacyAdoptionPreflight:
    status: str
    reasons: tuple[str, ...]
    server_version_num: int | None
    algorithm_version: str
    computed_fingerprint: str | None
    expected_fingerprint: str
    legacy_migration_ids: tuple[str, ...]


def preflight_legacy_adoption(
    connection,
    *,
    approved_baseline_sha256: str,
) -> LegacyAdoptionPreflight:
    """Compare a legacy schema with an externally approved clean baseline.

    The caller must supply a reviewed baseline digest. The function performs
    read-only catalog/ledger inspection and does not create, repair, or attest
    anything. A PREFLIGHT_MATCH is not an adoption state: a future adoption
    operation must repeat every check under its own transaction/locking
    protocol immediately before writing an attestation.
    """
    if not isinstance(approved_baseline_sha256, str) or not _SHA256_RE.fullmatch(
        approved_baseline_sha256
    ):
        raise LegacyAdoptionPreflightError(
            "an explicitly approved lowercase SHA-256 baseline is required"
        )
    if connection.info.transaction_status != 0:
        raise LegacyAdoptionPreflightError(
            "legacy adoption preflight requires an idle connection"
        )

    reasons: list[str] = []
    server_version_num: int | None = None
    legacy_ids: tuple[str, ...] = ()

    with connection.transaction():
        connection.execute("SET TRANSACTION READ ONLY")
        server_version_num = connection.execute(
            "SELECT current_setting('server_version_num')::integer"
        ).fetchone()[0]
        if server_version_num != SUPPORTED_SERVER_VERSION_NUM:
            reasons.append(
                "unsupported PostgreSQL server version: "
                f"{server_version_num}; expected {SUPPORTED_SERVER_VERSION_NUM}"
            )

        app_schema_exists, control_schema_exists, legacy_ledger_exists = connection.execute(
            """
            SELECT
                to_regnamespace('sinayxa') IS NOT NULL,
                to_regnamespace('sinayxa_control') IS NOT NULL,
                to_regclass('sinayxa.schema_migrations') IS NOT NULL
            """
        ).fetchone()

        if not app_schema_exists:
            reasons.append("legacy application schema sinayxa is missing")
        if control_schema_exists:
            reasons.append(
                "sinayxa_control already exists; this is not an unadopted legacy state"
            )
        if not legacy_ledger_exists:
            reasons.append("legacy migration ledger sinayxa.schema_migrations is missing")

        if app_schema_exists and legacy_ledger_exists:
            rows = connection.execute(
                """
                SELECT migration_id
                FROM sinayxa.schema_migrations
                ORDER BY migration_id
                """
            ).fetchall()
            legacy_ids = tuple(row[0] for row in rows)
            if len(legacy_ids) != len(LEGACY_MIGRATION_IDS) or set(legacy_ids) != set(
                LEGACY_MIGRATION_IDS
            ):
                missing = sorted(set(LEGACY_MIGRATION_IDS) - set(legacy_ids))
                unknown = sorted(set(legacy_ids) - set(LEGACY_MIGRATION_IDS))
                reasons.append(
                    "legacy migration ID inventory mismatch; "
                    f"missing={missing}, unknown={unknown}, count={len(legacy_ids)}"
                )

    computed_fingerprint: str | None = None
    if not reasons:
        try:
            fingerprint = fingerprint_schema(connection, "sinayxa")
        except CatalogFingerprintError as exc:
            reasons.append(f"catalog fingerprint failed closed: {exc}")
        else:
            computed_fingerprint = fingerprint.sha256
            if computed_fingerprint != approved_baseline_sha256:
                reasons.append(
                    "application catalog does not match the approved baseline fingerprint"
                )

    return LegacyAdoptionPreflight(
        status="PREFLIGHT_MATCH" if not reasons else "LEGACY_UNVERIFIED",
        reasons=tuple(reasons),
        server_version_num=server_version_num,
        algorithm_version=ALGORITHM_VERSION,
        computed_fingerprint=computed_fingerprint,
        expected_fingerprint=approved_baseline_sha256,
        legacy_migration_ids=legacy_ids,
    )
