"""Fail-closed PostgreSQL migration runner for fresh databases only.

Legacy installations are intentionally rejected. Their read-only fingerprint
and adoption flow is a separate, not-yet-implemented operation.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import psycopg

from scripts.news_and_events.migration_manifest import (
    MigrationManifestError,
    MigrationRecord,
    load_and_verify_manifest,
)

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "database" / "migrations" / "manifest.json"
MIGRATIONS_DIR = ROOT / "database" / "migrations"
BOOTSTRAP_PATH = ROOT / "database" / "control-plane" / "bootstrap-v1.sql"
BOOTSTRAP_VERSION = 1
BOOTSTRAP_SHA256 = "1cba84056869562fa4ce831624405074c046da74d3cac31e01bac47fe746f8f4"
RUNNER_VERSION = "0.1.0"
ADVISORY_LOCK_NAMESPACE = 1936289385
ADVISORY_LOCK_KEY = 1


class MigrationRunnerError(RuntimeError):
    """Raised when database migration state is unsafe or inconsistent."""


def _read_bootstrap() -> str:
    try:
        raw = BOOTSTRAP_PATH.read_bytes()
    except OSError as exc:
        raise MigrationRunnerError(f"cannot read control-plane bootstrap SQL: {exc}") from exc
    actual = hashlib.sha256(raw).hexdigest()
    if actual != BOOTSTRAP_SHA256:
        raise MigrationRunnerError(
            f"control-plane bootstrap SHA-256 mismatch: expected {BOOTSTRAP_SHA256}, got {actual}"
        )
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MigrationRunnerError("control-plane bootstrap SQL must be UTF-8") from exc


def _lock(connection: psycopg.Connection) -> None:
    connection.execute(
        "SELECT pg_advisory_xact_lock(%s, %s)",
        (ADVISORY_LOCK_NAMESPACE, ADVISORY_LOCK_KEY),
    )


def _bootstrap_or_verify(connection: psycopg.Connection, bootstrap_sql: str) -> None:
    with connection.transaction():
        _lock(connection)
        app_schema_exists, control_schema_exists = connection.execute(
            "SELECT to_regnamespace('sinayxa') IS NOT NULL, "
            "to_regnamespace('sinayxa_control') IS NOT NULL"
        ).fetchone()

        if not control_schema_exists:
            if app_schema_exists:
                raise MigrationRunnerError(
                    "legacy application schema detected without control-plane attestation; "
                    "state remains LEGACY_UNVERIFIED"
                )
            connection.execute(bootstrap_sql, prepare=False)
            connection.execute(
                """
                INSERT INTO sinayxa_control.bootstrap_state
                    (singleton, bootstrap_version, bootstrap_sha256)
                VALUES (true, %s, %s)
                """,
                (BOOTSTRAP_VERSION, BOOTSTRAP_SHA256),
            )
            return

        required_tables = (
            "sinayxa_control.bootstrap_state",
            "sinayxa_control.migration_integrity",
            "sinayxa_control.legacy_adoption_attestations",
        )
        for table_name in required_tables:
            exists = connection.execute(
                "SELECT to_regclass(%s) IS NOT NULL", (table_name,)
            ).fetchone()[0]
            if not exists:
                raise MigrationRunnerError(
                    f"partial or unsupported control plane: missing {table_name}"
                )

        bootstrap_rows = connection.execute(
            """
            SELECT bootstrap_version, bootstrap_sha256
            FROM sinayxa_control.bootstrap_state
            ORDER BY singleton
            """
        ).fetchall()
        normalized_bootstrap_rows = [
            (version, digest.strip()) for version, digest in bootstrap_rows
        ]
        if normalized_bootstrap_rows != [(BOOTSTRAP_VERSION, BOOTSTRAP_SHA256)]:
            raise MigrationRunnerError(
                "control-plane bootstrap record is missing, duplicated, or does not match "
                "the pinned bootstrap contract"
            )


def _load_ledger(connection: psycopg.Connection) -> dict[str, tuple[int, str, str]]:
    rows = connection.execute(
        """
        SELECT migration_id, version, sha256, source_revision
        FROM sinayxa_control.migration_integrity
        ORDER BY version
        """
    ).fetchall()
    return {
        migration_id: (version, digest.strip(), source_revision.strip())
        for migration_id, version, digest, source_revision in rows
    }


def _verify_legacy_compatibility(
    connection: psycopg.Connection,
    records: tuple[MigrationRecord, ...],
    ledger: dict[str, tuple[int, str, str]],
) -> None:
    app_schema_exists = connection.execute(
        "SELECT to_regnamespace('sinayxa') IS NOT NULL"
    ).fetchone()[0]
    if not app_schema_exists:
        if ledger:
            raise MigrationRunnerError(
                "integrity ledger contains migrations but application schema is absent"
            )
        return

    legacy_table_exists = connection.execute(
        "SELECT to_regclass('sinayxa.schema_migrations') IS NOT NULL"
    ).fetchone()[0]
    if not legacy_table_exists:
        raise MigrationRunnerError(
            "application schema exists without the legacy migration ledger"
        )

    legacy_ids = {
        row[0]
        for row in connection.execute(
            "SELECT migration_id FROM sinayxa.schema_migrations ORDER BY migration_id"
        ).fetchall()
    }
    expected_ids = set(ledger)
    if legacy_ids != expected_ids:
        missing_integrity = sorted(legacy_ids - expected_ids)
        missing_legacy = sorted(expected_ids - legacy_ids)
        raise MigrationRunnerError(
            "legacy/integrity ledger disagreement; "
            f"legacy_without_integrity={missing_integrity}, "
            f"integrity_without_legacy={missing_legacy}"
        )

    if not ledger:
        raise MigrationRunnerError(
            "legacy application migration IDs have no integrity hashes; "
            "state remains LEGACY_UNVERIFIED"
        )

    known = {record.migration_id for record in records}
    unknown = sorted(legacy_ids - known)
    if unknown:
        raise MigrationRunnerError(f"unknown legacy migration IDs: {unknown}")


def _validate_ledger(
    records: tuple[MigrationRecord, ...],
    ledger: dict[str, tuple[int, str, str]],
) -> None:
    by_version = {record.version: record for record in records}
    for migration_id, (version, digest, source_revision) in ledger.items():
        record = next((item for item in records if item.migration_id == migration_id), None)
        if record is None:
            raise MigrationRunnerError(f"integrity ledger contains unknown migration ID: {migration_id}")
        if version not in by_version or by_version[version].migration_id != migration_id:
            raise MigrationRunnerError(
                f"migration version collision or drift for {migration_id}: recorded version {version}"
            )
        if digest != record.sha256:
            raise MigrationRunnerError(
                f"migration drift detected for {migration_id}: recorded SHA-256 differs from manifest"
            )
        if source_revision != record.source_revision:
            raise MigrationRunnerError(
                f"migration provenance drift detected for {migration_id}"
            )


def apply_migrations(
    connection: psycopg.Connection,
    *,
    manifest_path: Path = MANIFEST_PATH,
    migrations_dir: Path = MIGRATIONS_DIR,
) -> tuple[str, ...]:
    """Apply pending manifest migrations to a fresh database and verify prior runs.

    The function never adopts legacy databases. Each migration SQL and its
    integrity-ledger row commit in the same transaction under one advisory lock.
    """
    try:
        records = load_and_verify_manifest(manifest_path, migrations_dir)
    except MigrationManifestError as exc:
        raise MigrationRunnerError(f"migration manifest verification failed: {exc}") from exc
    bootstrap_sql = _read_bootstrap()
    applied_now: list[str] = []

    _bootstrap_or_verify(connection, bootstrap_sql)

    for record in records:
        sql_path = (migrations_dir / record.path).resolve()
        try:
            sql_bytes = sql_path.read_bytes()
            sql = sql_bytes.decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise MigrationRunnerError(f"cannot read migration {record.path}: {exc}") from exc
        if hashlib.sha256(sql_bytes).hexdigest() != record.sha256:
            raise MigrationRunnerError(
                f"migration changed after manifest verification: {record.path}"
            )

        with connection.transaction():
            _lock(connection)
            ledger = _load_ledger(connection)
            _validate_ledger(records, ledger)
            _verify_legacy_compatibility(connection, records, ledger)

            existing = ledger.get(record.migration_id)
            if existing is not None:
                if existing != (record.version, record.sha256, record.source_revision):
                    raise MigrationRunnerError(
                        f"migration drift detected for {record.migration_id}"
                    )
                continue

            occupied = next(
                (migration_id for migration_id, value in ledger.items() if value[0] == record.version),
                None,
            )
            if occupied is not None:
                raise MigrationRunnerError(
                    f"migration version {record.version} is already occupied by {occupied}"
                )

            connection.execute(sql, prepare=False)
            legacy_id_exists = connection.execute(
                """
                SELECT count(*) = 1
                FROM sinayxa.schema_migrations
                WHERE migration_id = %s
                """,
                (record.migration_id,),
            ).fetchone()[0]
            if not legacy_id_exists:
                raise MigrationRunnerError(
                    f"migration did not record its compatibility ID: {record.migration_id}"
                )
            connection.execute(
                """
                INSERT INTO sinayxa_control.migration_integrity
                    (migration_id, version, sha256, source_revision, runner_version)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    record.migration_id,
                    record.version,
                    record.sha256,
                    record.source_revision,
                    RUNNER_VERSION,
                ),
            )
            applied_now.append(record.migration_id)

    with connection.transaction():
        _lock(connection)
        ledger = _load_ledger(connection)
        _validate_ledger(records, ledger)
        _verify_legacy_compatibility(connection, records, ledger)
        expected = {record.migration_id for record in records}
        if set(ledger) != expected:
            raise MigrationRunnerError(
                f"migration chain incomplete; missing={sorted(expected - set(ledger))}"
            )

    return tuple(applied_now)
