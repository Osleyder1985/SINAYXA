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
    session_user: str | None
    current_user: str | None
    current_role: str | None
    role_memberships: tuple[tuple[str, str, bool, bool, bool], ...]
    algorithm_version: str
    computed_fingerprint: str | None
    expected_fingerprint: str
    legacy_migration_ids: tuple[str, ...]


def preflight_legacy_adoption(
    connection,
    *,
    approved_baseline_sha256: str,
    approved_identity: str,
    approved_memberships: tuple[tuple[str, str, bool, bool, bool], ...] = (),
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
    if not isinstance(approved_identity, str) or not approved_identity.strip():
        raise LegacyAdoptionPreflightError(
            "an explicitly allowlisted PostgreSQL login identity is required"
        )
    if connection.info.transaction_status != 0:
        raise LegacyAdoptionPreflightError(
            "legacy adoption preflight requires an idle connection"
        )

    reasons: list[str] = []
    server_version_num: int | None = None
    session_user: str | None = None
    current_user: str | None = None
    current_role: str | None = None
    role_memberships: tuple[tuple[str, str, bool, bool, bool], ...] = ()
    legacy_ids: tuple[str, ...] = ()
    computed_fingerprint: str | None = None

    with connection.transaction():
        connection.execute(
            "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"
        )
        server_version_num = connection.execute(
            "SELECT current_setting('server_version_num')::integer"
        ).fetchone()[0]
        if server_version_num != SUPPORTED_SERVER_VERSION_NUM:
            reasons.append(
                "unsupported PostgreSQL server version: "
                f"{server_version_num}; expected {SUPPORTED_SERVER_VERSION_NUM}"
            )

        session_user, current_user, current_role, database_name = connection.execute(
            "SELECT session_user, current_user, current_role, current_database()"
        ).fetchone()
        if (session_user, current_user, current_role) != (
            approved_identity, approved_identity, approved_identity
        ):
            reasons.append(
                "authenticated/effective PostgreSQL identity mismatch; "
                f"session_user={session_user}, current_user={current_user}, "
                f"current_role={current_role}, approved={approved_identity}"
            )

        membership_rows = connection.execute(
            """
            WITH RECURSIVE membership_edges AS (
                SELECT m.member, m.roleid, m.inherit_option, m.set_option,
                       m.admin_option, ARRAY[m.member, m.roleid] AS path
                FROM pg_auth_members m
                JOIN pg_roles login_role ON login_role.oid = m.member
                WHERE login_role.rolname = %s
                UNION ALL
                SELECT m.member, m.roleid, m.inherit_option, m.set_option,
                       m.admin_option, edge.path || m.roleid
                FROM pg_auth_members m
                JOIN membership_edges edge ON m.member = edge.roleid
                WHERE NOT m.roleid = ANY(edge.path)
            )
            SELECT DISTINCT member_role.rolname, granted_role.rolname,
                   edge.inherit_option, edge.set_option, edge.admin_option
            FROM membership_edges edge
            JOIN pg_roles member_role ON member_role.oid = edge.member
            JOIN pg_roles granted_role ON granted_role.oid = edge.roleid
            ORDER BY member_role.rolname, granted_role.rolname
            """,
            (approved_identity,),
        ).fetchall()
        role_memberships = tuple(
            (member, granted, inherit_option, set_option, admin_option)
            for member, granted, inherit_option, set_option, admin_option in membership_rows
        )
        if role_memberships != tuple(sorted(approved_memberships)):
            reasons.append(
                "PostgreSQL role membership graph differs from the approved allowlist; "
                f"actual={role_memberships}, approved={tuple(sorted(approved_memberships)}"
            )
        if any(set_option or admin_option for _, _, _, set_option, admin_option in role_memberships):
            reasons.append(
                "preflight identity has an unapproved SET ROLE or ADMIN OPTION capability"
            )

        reachable_roles = sorted(
            {approved_identity} | {granted for _, granted, _, _, _ in role_memberships}
        )
        role_flags = connection.execute(
            """
            SELECT rolname, rolsuper, rolcreatedb, rolcreaterole, rolbypassrls
            FROM pg_roles
            WHERE rolname = ANY(%s)
            ORDER BY rolname
            """,
            (reachable_roles,),
        ).fetchall()
        if len(role_flags) != len(reachable_roles):
            reasons.append("one or more allowlisted PostgreSQL roles could not be inspected")
        elevated_roles = [
            name for name, superuser, createdb, createrole, bypassrls in role_flags
            if superuser or createdb or createrole or bypassrls
        ]
        if elevated_roles:
            reasons.append(
                "preflight identity or reachable memberships have elevated role attributes: "
                f"{elevated_roles}"
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

        can_read_legacy_ledger = False
        database_connect, database_create = connection.execute(
            """
            SELECT has_database_privilege(current_user, current_database(), 'CONNECT'),
                   has_database_privilege(current_user, current_database(), 'CREATE')
            """
        ).fetchone()
        if not database_connect:
            reasons.append("preflight identity lacks CONNECT on the target database")
        if database_create:
            reasons.append("read-only preflight identity has CREATE privilege on the database")

        if app_schema_exists:
            schema_usage, schema_create = connection.execute(
                """
                SELECT has_schema_privilege(current_user, 'sinayxa', 'USAGE'),
                       has_schema_privilege(current_user, 'sinayxa', 'CREATE')
                """
            ).fetchone()
            if not schema_usage:
                reasons.append("preflight identity lacks USAGE on schema sinayxa")
            if schema_create:
                reasons.append("read-only preflight identity has CREATE on schema sinayxa")

        if legacy_ledger_exists:
            can_read_legacy_ledger, ledger_write = connection.execute(
                """
                SELECT has_table_privilege(
                           current_user, 'sinayxa.schema_migrations', 'SELECT'
                       ),
                       has_table_privilege(
                           current_user, 'sinayxa.schema_migrations', 'INSERT'
                       )
                       OR has_table_privilege(
                           current_user, 'sinayxa.schema_migrations', 'UPDATE'
                       )
                       OR has_table_privilege(
                           current_user, 'sinayxa.schema_migrations', 'DELETE'
                       )
                       OR has_table_privilege(
                           current_user, 'sinayxa.schema_migrations', 'TRUNCATE'
                       )
                       OR has_table_privilege(
                           current_user, 'sinayxa.schema_migrations', 'REFERENCES'
                       )
                       OR has_table_privilege(
                           current_user, 'sinayxa.schema_migrations', 'TRIGGER'
                       )
                """
            ).fetchone()
            if not can_read_legacy_ledger:
                reasons.append("preflight identity lacks SELECT on the legacy migration ledger")
            if ledger_write:
                reasons.append("preflight identity has write privileges on the legacy migration ledger")

        if app_schema_exists:
            table_write = connection.execute(
                """
                SELECT COALESCE(bool_or(
                    has_table_privilege(current_user, c.oid, 'INSERT')
                    OR has_table_privilege(current_user, c.oid, 'UPDATE')
                    OR has_table_privilege(current_user, c.oid, 'DELETE')
                    OR has_table_privilege(current_user, c.oid, 'TRUNCATE')
                    OR has_table_privilege(current_user, c.oid, 'REFERENCES')
                    OR has_table_privilege(current_user, c.oid, 'TRIGGER')
                ), false)
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = 'sinayxa'
                  AND c.relkind IN ('r', 'p', 'v', 'm', 'f')
                """
            ).fetchone()[0]
            sequence_write = connection.execute(
                """
                SELECT COALESCE(bool_or(
                    has_sequence_privilege(current_user, c.oid, 'USAGE')
                    OR has_sequence_privilege(current_user, c.oid, 'UPDATE')
                ), false)
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = 'sinayxa' AND c.relkind = 'S'
                """
            ).fetchone()[0]
            if table_write or sequence_write:
                reasons.append(
                    "read-only preflight identity has write privileges on application objects"
                )

        if app_schema_exists and legacy_ledger_exists and can_read_legacy_ledger:
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
                if ALGORITHM_VERSION.endswith("-preview"):
                    reasons.append(
                        "catalog fingerprint algorithm is still a preview and cannot authorize legacy adoption"
                    )

    return LegacyAdoptionPreflight(
        status="PREFLIGHT_MATCH" if not reasons else "LEGACY_UNVERIFIED",
        reasons=tuple(reasons),
        server_version_num=server_version_num,
        session_user=session_user,
        current_user=current_user,
        current_role=current_role,
        role_memberships=role_memberships,
        algorithm_version=ALGORITHM_VERSION,
        computed_fingerprint=computed_fingerprint,
        expected_fingerprint=approved_baseline_sha256,
        legacy_migration_ids=legacy_ids,
    )
