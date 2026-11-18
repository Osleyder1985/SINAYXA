"""Read-only, deterministic PostgreSQL catalog fingerprint probe.

This is a laboratory verifier, not a legacy-adoption operation. It does not
write an attestation, repair a schema, or compare against an approved baseline.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from psycopg.rows import dict_row

ALGORITHM_VERSION = "sinayxa-catalog-v1-preview"
SUPPORTED_POSTGRES_MAJOR = 18


class CatalogFingerprintError(RuntimeError):
    """Raised when the catalog cannot be represented without ambiguity."""


@dataclass(frozen=True)
class CatalogFingerprint:
    algorithm_version: str
    server_version_num: int
    schema_name: str
    record_count: int
    sha256: str
    canonical_json: bytes
    records: tuple[dict[str, Any], ...]


def canonicalize_records(records: list[dict[str, Any]]) -> bytes:
    """Serialize records deterministically; OIDs must never be supplied."""
    normalized = sorted(
        records,
        key=lambda item: (
            str(item.get("object_type", "")),
            str(item.get("qualified_name", "")),
            str(item.get("identity", "")),
        ),
    )
    try:
        return json.dumps(
            normalized,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise CatalogFingerprintError(
            f"catalog records are not canonical JSON values: {exc}"
        ) from exc


def _rows(connection: Any, query: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def _record(object_type: str, qualified_name: str, identity: str, **fields: Any) -> dict[str, Any]:
    return {
        "object_type": object_type,
        "qualified_name": qualified_name,
        "identity": identity,
        **fields,
    }


def fingerprint_schema(connection: Any, schema_name: str = "sinayxa") -> CatalogFingerprint:
    """Read and fingerprint supported catalog metadata under READ ONLY isolation.

    The caller must provide an idle connection. Only PostgreSQL 18.x is
    supported. Any foreign relation, custom pseudo-type, or unsupported
    catalog state causes a fail-closed error.
    """
    if schema_name != "sinayxa":
        raise CatalogFingerprintError("preview verifier is restricted to schema 'sinayxa'")
    if connection.info.transaction_status != 0:
        raise CatalogFingerprintError("fingerprinting requires an idle connection")

    with connection.transaction():
        connection.execute("SET TRANSACTION READ ONLY")
        connection.execute("SET LOCAL search_path = pg_catalog, pg_temp")
        server_version_num, read_only = connection.execute(
            "SELECT current_setting('server_version_num')::integer, "
            "current_setting('transaction_read_only')"
        ).fetchone()
        if server_version_num // 10000 != SUPPORTED_POSTGRES_MAJOR:
            raise CatalogFingerprintError(
                f"unsupported PostgreSQL major version: {server_version_num}"
            )
        if read_only != "on":
            raise CatalogFingerprintError("catalog inspection transaction is not read-only")

        schema_rows = _rows(
            connection,
            """
            SELECT n.nspname AS schema_name, r.rolname AS owner,
                   COALESCE((
                     SELECT jsonb_agg(jsonb_build_object(
                       'grantee', CASE WHEN x.grantee = 0 THEN 'PUBLIC' ELSE grantee_role.rolname END,
                       'grantor', CASE WHEN x.grantor = 0 THEN 'PUBLIC' ELSE grantor_role.rolname END,
                       'privilege', x.privilege_type,
                       'grantable', x.is_grantable
                     ) ORDER BY COALESCE(grantee_role.rolname, 'PUBLIC'), COALESCE(grantor_role.rolname, 'PUBLIC'), x.privilege_type, x.is_grantable)
                     FROM aclexplode(COALESCE(n.nspacl, acldefault('n'::\"char\", n.nspowner))) x
                     LEFT JOIN pg_roles grantee_role ON grantee_role.oid = x.grantee
                     LEFT JOIN pg_roles grantor_role ON grantor_role.oid = x.grantor
                   ), '[]'::jsonb) AS acl
            FROM pg_namespace n
            JOIN pg_roles r ON r.oid = n.nspowner
            WHERE n.nspname = %s
            """,
            (schema_name,),
        )
        if len(schema_rows) != 1:
            raise CatalogFingerprintError(
                f"managed schema {schema_name!r} is missing or ambiguous"
            )
        s = schema_rows[0]
        records: list[dict[str, Any]] = [
            _record("schema", schema_name, schema_name, owner=s["owner"], acl=s["acl"])
        ]

        relation_rows = _rows(
            connection,
            """
            SELECT c.relname, c.relkind, c.relpersistence, c.relispartition,
                   c.relrowsecurity, c.relforcerowsecurity, c.relreplident,
                   owner.rolname AS owner,
                   COALESCE((
                     SELECT jsonb_agg(jsonb_build_object(
                       'grantee', CASE WHEN x.grantee = 0 THEN 'PUBLIC' ELSE grantee_role.rolname END,
                       'grantor', CASE WHEN x.grantor = 0 THEN 'PUBLIC' ELSE grantor_role.rolname END,
                       'privilege', x.privilege_type,
                       'grantable', x.is_grantable
                     ) ORDER BY COALESCE(grantee_role.rolname, 'PUBLIC'), COALESCE(grantor_role.rolname, 'PUBLIC'), x.privilege_type, x.is_grantable)
                     FROM aclexplode(COALESCE(
                       c.relacl,
                       acldefault((CASE WHEN c.relkind = 'S' THEN 'S' ELSE 'r' END)::\"char\", c.relowner)
                     )) x
                     LEFT JOIN pg_roles grantee_role ON grantee_role.oid = x.grantee
                     LEFT JOIN pg_roles grantor_role ON grantor_role.oid = x.grantor
                   ), '[]'::jsonb) AS acl,
                   COALESCE((
                     SELECT jsonb_agg(option ORDER BY option)
                     FROM unnest(c.reloptions) AS options(option)
                   ), '[]'::jsonb) AS relation_options,
                   COALESCE(pt.partstrat::text, '') AS partition_strategy,
                   CASE WHEN c.relkind IN ('v', 'm')
                        THEN pg_get_viewdef(c.oid, true) ELSE NULL END AS view_definition
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            JOIN pg_roles owner ON owner.oid = c.relowner
            LEFT JOIN pg_partitioned_table pt ON pt.partrelid = c.oid
            WHERE n.nspname = %s
              AND c.relkind IN ('r', 'p', 'v', 'm', 'S')
            ORDER BY c.relname
            """,
            (schema_name,),
        )
        unsupported_relations = _rows(
            connection,
            """
            SELECT c.relname, c.relkind
            FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = %s AND c.relkind NOT IN ('r', 'p', 'v', 'm', 'S', 'i', 'I', 't', 'c')
            """,
            (schema_name,),
        )
        if unsupported_relations:
            raise CatalogFingerprintError(
                f"unsupported relation kinds in {schema_name}: {unsupported_relations}"
            )

        partitioned_relations = _rows(
            connection,
            """
            SELECT c.relname, c.relkind, c.relispartition
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = %s
              AND (c.relkind = 'p' OR c.relispartition)
            ORDER BY c.relname
            """,
            (schema_name,),
        )
        if partitioned_relations:
            raise CatalogFingerprintError(
                "unsupported partitioned relations in "
                f"{schema_name}: {partitioned_relations}"
            )

        for rel in relation_rows:
            name = f"{schema_name}.{rel['relname']}"
            records.append(
                _record(
                    "relation",
                    name,
                    name,
                    kind=rel["relkind"],
                    persistence=rel["relpersistence"],
                    is_partition=rel["relispartition"],
                    row_security=rel["relrowsecurity"],
                    force_row_security=rel["relforcerowsecurity"],
                    replica_identity=rel["relreplident"],
                    owner=rel["owner"],
                    acl=rel["acl"],
                    partition_strategy=rel["partition_strategy"],
                    relation_options=rel["relation_options"],
                    view_definition=rel["view_definition"],
                )
            )

        columns = _rows(
            connection,
            """
            SELECT c.relname, a.attnum, a.attname,
                   tn.nspname AS type_schema, t.typname AS type_name,
                   pg_catalog.format_type(a.atttypid, a.atttypmod) AS formatted_type,
                   a.atttypmod, a.attnotnull,
                   cn.nspname AS collation_schema, coll.collname AS collation_name,
                   a.attidentity, a.attgenerated,
                   pg_get_expr(d.adbin, d.adrelid, true) AS default_expression,
                   CASE WHEN a.attacl IS NULL THEN '[]'::jsonb ELSE COALESCE((
                     SELECT jsonb_agg(jsonb_build_object(
                       'grantee', CASE WHEN x.grantee = 0 THEN 'PUBLIC' ELSE grantee_role.rolname END,
                       'grantor', CASE WHEN x.grantor = 0 THEN 'PUBLIC' ELSE grantor_role.rolname END,
                       'privilege', x.privilege_type,
                       'grantable', x.is_grantable
                     ) ORDER BY COALESCE(grantee_role.rolname, 'PUBLIC'),
                                  COALESCE(grantor_role.rolname, 'PUBLIC'),
                                  x.privilege_type, x.is_grantable)
                     FROM aclexplode(a.attacl) x
                     LEFT JOIN pg_roles grantee_role ON grantee_role.oid = x.grantee
                     LEFT JOIN pg_roles grantor_role ON grantor_role.oid = x.grantor
                   ), '[]'::jsonb) END AS acl
            FROM pg_attribute a
            JOIN pg_class c ON c.oid = a.attrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            JOIN pg_type t ON t.oid = a.atttypid
            JOIN pg_namespace tn ON tn.oid = t.typnamespace
            LEFT JOIN pg_collation coll ON coll.oid = a.attcollation
            LEFT JOIN pg_namespace cn ON cn.oid = coll.collnamespace
            LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
            WHERE n.nspname = %s AND a.attnum > 0 AND NOT a.attisdropped
              AND c.relkind IN ('r', 'p', 'v', 'm', 'f')
            ORDER BY c.relname, a.attnum
            """,
            (schema_name,),
        )
        for col in columns:
            name = f"{schema_name}.{col['relname']}.{col['attname']}"
            records.append(
                _record(
                    "column",
                    f"{schema_name}.{col['relname']}",
                    f"{col['attnum']}:{col['attname']}",
                    name=col["attname"],
                    ordinal=col["attnum"],
                    type_schema=col["type_schema"],
                    type_name=col["type_name"],
                    formatted_type=col["formatted_type"],
                    type_modifier=col["atttypmod"],
                    not_null=col["attnotnull"],
                    collation_schema=col["collation_schema"],
                    collation_name=col["collation_name"],
                    identity_kind=col["attidentity"],
                    generated=col["attgenerated"],
                    default_expression=col["default_expression"],
                    acl=col["acl"],
                )
            )

        constraints = _rows(
            connection,
            """
            SELECT c.relname, con.conname, con.contype, con.condeferrable,
                   con.condeferred, con.convalidated,
                   pg_get_constraintdef(con.oid, true) AS definition,
                   COALESCE((
                     SELECT jsonb_agg(a.attname ORDER BY k.ordinality)
                     FROM unnest(con.conkey) WITH ORDINALITY AS k(attnum, ordinality)
                     JOIN pg_attribute a ON a.attrelid = con.conrelid AND a.attnum = k.attnum
                   ), '[]'::jsonb) AS local_columns,
                   rn.nspname AS referenced_schema, rc.relname AS referenced_relation,
                   COALESCE((
                     SELECT jsonb_agg(a.attname ORDER BY k.ordinality)
                     FROM unnest(con.confkey) WITH ORDINALITY AS k(attnum, ordinality)
                     JOIN pg_attribute a ON a.attrelid = con.confrelid AND a.attnum = k.attnum
                   ), '[]'::jsonb) AS referenced_columns
            FROM pg_constraint con
            JOIN pg_class c ON c.oid = con.conrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            LEFT JOIN pg_class rc ON rc.oid = con.confrelid
            LEFT JOIN pg_namespace rn ON rn.oid = rc.relnamespace
            WHERE n.nspname = %s
            ORDER BY c.relname, con.conname
            """,
            (schema_name,),
        )
        for con in constraints:
            name = f"{schema_name}.{con['relname']}.{con['conname']}"
            records.append(
                _record(
                    "constraint",
                    f"{schema_name}.{con['relname']}",
                    con["conname"],
                    constraint_type=con["contype"],
                    deferrable=con["condeferrable"],
                    initially_deferred=con["condeferred"],
                    validated=con["convalidated"],
                    definition=con["definition"],
                    local_columns=con["local_columns"],
                    referenced_schema=con["referenced_schema"],
                    referenced_relation=con["referenced_relation"],
                    referenced_columns=con["referenced_columns"],
                )
            )

        indexes = _rows(
            connection,
            """
            SELECT tbl.relname AS table_name, idx.relname AS index_name,
                   am.amname AS access_method, i.indisunique, i.indisprimary,
                   i.indisexclusion, i.indisvalid, i.indisready, i.indnkeyatts,
                   pg_get_indexdef(i.indexrelid) AS definition,
                   pg_get_expr(i.indexprs, i.indrelid, true) AS expressions,
                   pg_get_expr(i.indpred, i.indrelid, true) AS predicate
            FROM pg_index i
            JOIN pg_class tbl ON tbl.oid = i.indrelid
            JOIN pg_namespace n ON n.oid = tbl.relnamespace
            JOIN pg_class idx ON idx.oid = i.indexrelid
            JOIN pg_am am ON am.oid = idx.relam
            WHERE n.nspname = %s
            ORDER BY tbl.relname, idx.relname
            """,
            (schema_name,),
        )
        for idx in indexes:
            records.append(
                _record(
                    "index",
                    f"{schema_name}.{idx['table_name']}",
                    idx["index_name"],
                    access_method=idx["access_method"],
                    unique=idx["indisunique"],
                    primary=idx["indisprimary"],
                    exclusion=idx["indisexclusion"],
                    valid=idx["indisvalid"],
                    ready=idx["indisready"],
                    key_attribute_count=idx["indnkeyatts"],
                    definition=idx["definition"],
                    expressions=idx["expressions"],
                    predicate=idx["predicate"],
                )
            )

        sequences = _rows(
            connection,
            """
            SELECT c.relname, s.seqtypid::regtype::text AS sequence_type,
                   s.seqstart, s.seqincrement, s.seqmax, s.seqmin, s.seqcache, s.seqcycle,
                   owner.rolname AS owner,
                   CASE WHEN rc.relname IS NULL THEN ''
                        ELSE concat_ws('.', rn.nspname, rc.relname, ra.attname) END AS owned_by
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            JOIN pg_sequence s ON s.seqrelid = c.oid
            JOIN pg_roles owner ON owner.oid = c.relowner
            LEFT JOIN pg_depend dep ON dep.classid = 'pg_class'::regclass
                 AND dep.objid = c.oid AND dep.refclassid = 'pg_class'::regclass
                 AND dep.deptype IN ('a', 'i')
            LEFT JOIN pg_class rc ON rc.oid = dep.refobjid
            LEFT JOIN pg_namespace rn ON rn.oid = rc.relnamespace
            LEFT JOIN pg_attribute ra ON ra.attrelid = rc.oid AND ra.attnum = dep.refobjsubid
            WHERE n.nspname = %s
            ORDER BY c.relname
            """,
            (schema_name,),
        )
        for seq in sequences:
            name = f"{schema_name}.{seq['relname']}"
            records.append(
                _record(
                    "sequence",
                    name,
                    name,
                    sequence_type=seq["sequence_type"],
                    start=seq["seqstart"],
                    increment=seq["seqincrement"],
                    maximum=seq["seqmax"],
                    minimum=seq["seqmin"],
                    cache=seq["seqcache"],
                    cycle=seq["seqcycle"],
                    owner=seq["owner"],
                    owned_by=seq["owned_by"],
                )
            )

        unsupported_procedures = _rows(
            connection,
            """
            SELECT p.proname, p.prokind
            FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
            WHERE n.nspname = %s AND p.prokind NOT IN ('f', 'p')
            ORDER BY p.proname
            """,
            (schema_name,),
        )
        if unsupported_procedures:
            raise CatalogFingerprintError(
                f"unsupported procedure kinds in {schema_name}: {unsupported_procedures}"
            )

        functions = _rows(
            connection,
            """
            SELECT p.proname, pg_get_function_identity_arguments(p.oid) AS identity_arguments,
                   pg_get_function_result(p.oid) AS result_type, l.lanname AS language,
                   pg_get_functiondef(p.oid) AS definition, p.provolatile, p.proisstrict,
                   p.prosecdef, p.proleakproof, p.proparallel, p.procost,
                   COALESCE((
                     SELECT jsonb_agg(setting ORDER BY setting)
                     FROM unnest(p.proconfig) AS config(setting)
                   ), '[]'::jsonb) AS configuration,
                   owner.rolname AS owner,
                   COALESCE((
                     SELECT jsonb_agg(jsonb_build_object(
                       'grantee', CASE WHEN x.grantee = 0 THEN 'PUBLIC' ELSE grantee_role.rolname END,
                       'grantor', CASE WHEN x.grantor = 0 THEN 'PUBLIC' ELSE grantor_role.rolname END,
                       'privilege', x.privilege_type,
                       'grantable', x.is_grantable
                     ) ORDER BY COALESCE(grantee_role.rolname, 'PUBLIC'), COALESCE(grantor_role.rolname, 'PUBLIC'), x.privilege_type, x.is_grantable)
                     FROM aclexplode(COALESCE(p.proacl, acldefault('f'::\"char\", p.proowner))) x
                     LEFT JOIN pg_roles grantee_role ON grantee_role.oid = x.grantee
                     LEFT JOIN pg_roles grantor_role ON grantor_role.oid = x.grantor
                   ), '[]'::jsonb) AS acl
            FROM pg_proc p
            JOIN pg_namespace n ON n.oid = p.pronamespace
            JOIN pg_language l ON l.oid = p.prolang
            JOIN pg_roles owner ON owner.oid = p.proowner
            WHERE n.nspname = %s
            ORDER BY p.proname, identity_arguments
            """,
            (schema_name,),
        )
        for fn in functions:
            identity = f"{fn['proname']}({fn['identity_arguments']})"
            records.append(
                _record(
                    "function",
                    f"{schema_name}.{fn['proname']}",
                    identity,
                    identity_arguments=fn["identity_arguments"],
                    result_type=fn["result_type"],
                    language=fn["language"],
                    definition=fn["definition"],
                    volatility=fn["provolatile"],
                    strict=fn["proisstrict"],
                    security_definer=fn["prosecdef"],
                    leakproof=fn["proleakproof"],
                    parallel_safety=fn["proparallel"],
                    cost=fn["procost"],
                    configuration=fn["configuration"],
                    owner=fn["owner"],
                    acl=fn["acl"],
                )
            )

        triggers = _rows(
            connection,
            """
            SELECT c.relname AS table_name, t.tgname, t.tgtype, t.tgenabled,
                   t.tgisinternal, pg_get_triggerdef(t.oid, true) AS definition,
                   pg_get_expr(t.tgqual, t.tgrelid, true) AS condition,
                   pn.nspname AS function_schema, p.proname AS function_name,
                   pg_get_function_identity_arguments(p.oid) AS function_arguments
            FROM pg_trigger t
            JOIN pg_class c ON c.oid = t.tgrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            JOIN pg_proc p ON p.oid = t.tgfoid
            JOIN pg_namespace pn ON pn.oid = p.pronamespace
            WHERE n.nspname = %s AND NOT t.tgisinternal
            ORDER BY c.relname, t.tgname
            """,
            (schema_name,),
        )
        for trigger in triggers:
            records.append(
                _record(
                    "trigger",
                    f"{schema_name}.{trigger['table_name']}",
                    trigger["tgname"],
                    event_bits=trigger["tgtype"],
                    enabled=trigger["tgenabled"],
                    internal=trigger["tgisinternal"],
                    definition=trigger["definition"],
                    condition=trigger["condition"],
                    function_schema=trigger["function_schema"],
                    function_name=trigger["function_name"],
                    function_arguments=trigger["function_arguments"],
                )
            )

        types = _rows(
            connection,
            """
            SELECT t.typname, t.typtype, t.typcategory, t.typnotnull, t.typdefault,
                   t.typtypmod, t.typcollation::regcollation::text AS collation,
                   owner.rolname AS owner,
                   COALESCE((
                     SELECT jsonb_agg(jsonb_build_object(
                       'grantee', CASE WHEN x.grantee = 0 THEN 'PUBLIC' ELSE grantee_role.rolname END,
                       'grantor', CASE WHEN x.grantor = 0 THEN 'PUBLIC' ELSE grantor_role.rolname END,
                       'privilege', x.privilege_type,
                       'grantable', x.is_grantable
                     ) ORDER BY COALESCE(grantee_role.rolname, 'PUBLIC'),
                                  COALESCE(grantor_role.rolname, 'PUBLIC'),
                                  x.privilege_type, x.is_grantable)
                     FROM aclexplode(COALESCE(t.typacl, acldefault('T'::"char", t.typowner))) x
                     LEFT JOIN pg_roles grantee_role ON grantee_role.oid = x.grantee
                     LEFT JOIN pg_roles grantor_role ON grantor_role.oid = x.grantor
                   ), '[]'::jsonb) AS acl,
                   pg_catalog.format_type(t.typbasetype, t.typtypmod) AS base_type,
                   COALESCE((
                     SELECT jsonb_agg(e.enumlabel ORDER BY e.enumsortorder)
                     FROM pg_enum e WHERE e.enumtypid = t.oid
                   ), '[]'::jsonb) AS enum_labels,
                   COALESCE((
                     SELECT jsonb_agg(jsonb_build_object(
                       'name', a.attname,
                       'type', pg_catalog.format_type(a.atttypid, a.atttypmod),
                       'not_null', a.attnotnull
                     ) ORDER BY a.attnum)
                     FROM pg_attribute a
                     WHERE a.attrelid = t.typrelid AND a.attnum > 0 AND NOT a.attisdropped
                   ), '[]'::jsonb) AS attributes
            FROM pg_type t
            JOIN pg_namespace n ON n.oid = t.typnamespace
            JOIN pg_roles owner ON owner.oid = t.typowner
            WHERE n.nspname = %s AND t.typtype <> 'p'
            ORDER BY t.typname
            """,
            (schema_name,),
        )
        for typ in types:
            records.append(
                _record(
                    "type",
                    f"{schema_name}.{typ['typname']}",
                    typ["typname"],
                    type_kind=typ["typtype"],
                    category=typ["typcategory"],
                    not_null=typ["typnotnull"],
                    default_expression=typ["typdefault"],
                    type_modifier=typ["typtypmod"],
                    collation=typ["collation"],
                    owner=typ["owner"],
                    acl=typ["acl"],
                    base_type=typ["base_type"],
                    enum_labels=typ["enum_labels"],
                    attributes=typ["attributes"],
                )
            )

        domain_constraints = _rows(
            connection,
            """
            SELECT t.typname, con.conname, con.convalidated,
                   pg_get_constraintdef(con.oid, true) AS definition
            FROM pg_constraint con
            JOIN pg_type t ON t.oid = con.contypid
            JOIN pg_namespace n ON n.oid = t.typnamespace
            WHERE n.nspname = %s
            ORDER BY t.typname, con.conname
            """,
            (schema_name,),
        )
        for constraint in domain_constraints:
            records.append(
                _record(
                    "domain_constraint",
                    f"{schema_name}.{constraint['typname']}",
                    constraint["conname"],
                    validated=constraint["convalidated"],
                    definition=constraint["definition"],
                )
            )

        pseudo_types = _rows(
            connection,
            """
            SELECT t.typname
            FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace
            WHERE n.nspname = %s AND t.typtype = 'p'
            ORDER BY t.typname
            """,
            (schema_name,),
        )
        if pseudo_types:
            raise CatalogFingerprintError(
                f"unsupported pseudo-types in {schema_name}: {pseudo_types}"
            )

        policies = _rows(
            connection,
            """
            SELECT c.relname, p.polname, p.polcmd, p.polpermissive,
                   COALESCE((
                     SELECT jsonb_agg(
                       CASE WHEN role_oid = 0 THEN 'PUBLIC' ELSE r.rolname END
                       ORDER BY CASE WHEN role_oid = 0 THEN 'PUBLIC' ELSE r.rolname END
                     )
                     FROM unnest(p.polroles) role_oid
                     LEFT JOIN pg_roles r ON r.oid = role_oid
                   ), '[]'::jsonb) AS roles,
                   pg_get_expr(p.polqual, p.polrelid, true) AS using_expression,
                   pg_get_expr(p.polwithcheck, p.polrelid, true) AS check_expression
            FROM pg_policy p
            JOIN pg_class c ON c.oid = p.polrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = %s
            ORDER BY c.relname, p.polname
            """,
            (schema_name,),
        )
        for policy in policies:
            records.append(
                _record(
                    "policy",
                    f"{schema_name}.{policy['relname']}",
                    policy["polname"],
                    command=policy["polcmd"],
                    permissive=policy["polpermissive"],
                    roles=policy["roles"],
                    using_expression=policy["using_expression"],
                    check_expression=policy["check_expression"],
                )
            )

        extensions = _rows(
            connection,
            """
            SELECT e.extname, e.extversion, n.nspname AS schema_name,
                   owner.rolname AS owner
            FROM pg_extension e
            JOIN pg_namespace n ON n.oid = e.extnamespace
            JOIN pg_roles owner ON owner.oid = e.extowner
            WHERE n.nspname = %s
            ORDER BY e.extname
            """,
            (schema_name,),
        )
        for ext in extensions:
            records.append(
                _record(
                    "extension",
                    ext["schema_name"],
                    ext["extname"],
                    version=ext["extversion"],
                    owner=ext["owner"],
                )
            )

        default_privileges = _rows(
            connection,
            """
            SELECT owner.rolname AS owner, d.defaclobjtype,
                   COALESCE(n.nspname, 'GLOBAL') AS privilege_scope,
                   COALESCE((
                     SELECT jsonb_agg(jsonb_build_object(
                       'grantee', CASE WHEN x.grantee = 0 THEN 'PUBLIC' ELSE grantee_role.rolname END,
                       'grantor', CASE WHEN x.grantor = 0 THEN 'PUBLIC' ELSE grantor_role.rolname END,
                       'privilege', x.privilege_type,
                       'grantable', x.is_grantable
                     ) ORDER BY COALESCE(grantee_role.rolname, 'PUBLIC'),
                                  COALESCE(grantor_role.rolname, 'PUBLIC'),
                                  x.privilege_type, x.is_grantable)
                     FROM aclexplode(d.defaclacl) x
                     LEFT JOIN pg_roles grantee_role ON grantee_role.oid = x.grantee
                     LEFT JOIN pg_roles grantor_role ON grantor_role.oid = x.grantor
                   ), '[]'::jsonb) AS acl
            FROM pg_default_acl d
            LEFT JOIN pg_namespace n ON n.oid = d.defaclnamespace
            JOIN pg_roles owner ON owner.oid = d.defaclrole
            WHERE d.defaclnamespace = 0 OR n.nspname = %s
            ORDER BY privilege_scope, owner.rolname, d.defaclobjtype
            """,
            (schema_name,),
        )
        for privilege in default_privileges:
            records.append(
                _record(
                    "default_privileges",
                    privilege["privilege_scope"],
                    f"{privilege['owner']}:{privilege['defaclobjtype']}",
                    owner=privilege["owner"],
                    scope=privilege["privilege_scope"],
                    object_type_code=privilege["defaclobjtype"],
                    acl=privilege["acl"],
                )
            )

    canonical = canonicalize_records(records)
    return CatalogFingerprint(
        algorithm_version=ALGORITHM_VERSION,
        server_version_num=server_version_num,
        schema_name=schema_name,
        record_count=len(records),
        sha256=hashlib.sha256(canonical).hexdigest(),
        canonical_json=canonical,
        records=tuple(records),
    )
