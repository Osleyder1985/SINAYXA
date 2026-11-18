"""Pure validation for the reviewed PostgreSQL migration manifest.

This module performs filesystem and digest checks only. It never connects to
PostgreSQL, executes SQL, or changes migration files.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


class MigrationManifestError(ValueError):
    """Raised when the migration manifest or its SQL inventory is invalid."""


@dataclass(frozen=True)
class MigrationRecord:
    version: int
    migration_id: str
    path: str
    sha256: str
    source_revision: str
    execution_mode: str


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise MigrationManifestError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _require_exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise MigrationManifestError(
            f"{label} keys mismatch; missing={missing}, unexpected={unexpected}"
        )


def _git_output(repository_root: Path, *arguments: str) -> bytes:
    """Run a read-only Git command and fail closed on missing history or objects."""
    import subprocess

    try:
        completed = subprocess.run(
            ["git", "-C", str(repository_root), *arguments],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", b"") or b""
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", errors="replace").strip()
        raise MigrationManifestError(
            f"Git provenance verification failed for {' '.join(arguments)}: {detail or exc}"
        ) from exc
    return completed.stdout


def _verify_git_provenance(
    records: tuple[MigrationRecord, ...],
    baseline_revision: str,
    manifest_path: Path,
    migrations_dir: Path,
) -> None:
    """Verify manifest digests against baseline blobs and source commits against Git history."""
    import subprocess

    manifest_path = manifest_path.resolve()
    migrations_dir = migrations_dir.resolve()
    # Pure temporary-directory tests may validate structure without Git. Once a
    # .git marker exists in an ancestor, however, provenance verification is
    # mandatory: Git errors must fail closed rather than silently skip checks.
    git_marker = next(
        (parent / ".git" for parent in (manifest_path.parent, *manifest_path.parent.parents)
         if (parent / ".git").exists()),
        None,
    )
    if git_marker is None:
        return

    try:
        repository_root_text = subprocess.run(
            ["git", "-C", str(manifest_path.parent), "rev-parse", "--show-toplevel"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", b"") or b""
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", errors="replace").strip()
        raise MigrationManifestError(
            f"Git checkout detected but provenance cannot be verified: {detail or exc}"
        ) from exc

    repository_root = Path(repository_root_text).resolve()
    try:
        migrations_relative = migrations_dir.relative_to(repository_root)
    except ValueError as exc:
        raise MigrationManifestError(
            "migrations directory must be inside the Git repository"
        ) from exc

    _git_output(repository_root, "cat-file", "-e", f"{baseline_revision}^{{commit}}")

    baseline_sql_output = _git_output(
        repository_root,
        "ls-tree",
        "-r",
        "--name-only",
        baseline_revision,
        "--",
        migrations_relative.as_posix(),
    ).decode("utf-8", errors="strict")
    baseline_sql_paths = {
        path[len(migrations_relative.as_posix()) + 1 :]
        for path in baseline_sql_output.splitlines()
        if path.startswith(migrations_relative.as_posix() + "/") and path.endswith(".sql")
    }
    declared_sql_paths = {record.path for record in records}
    if baseline_sql_paths != declared_sql_paths:
        raise MigrationManifestError(
            "baseline SQL inventory mismatch; "
            f"unlisted={sorted(baseline_sql_paths - declared_sql_paths)}, "
            f"missing={sorted(declared_sql_paths - baseline_sql_paths)}"
        )

    for record in records:
        git_path = (migrations_relative / PurePosixPath(record.path)).as_posix()
        baseline_bytes = _git_output(
            repository_root, "show", f"{baseline_revision}:{git_path}"
        )
        baseline_digest = hashlib.sha256(baseline_bytes).hexdigest()
        if baseline_digest != record.sha256:
            raise MigrationManifestError(
                f"baseline SHA-256 mismatch for {record.path}: "
                f"manifest={record.sha256}, baseline={baseline_digest}"
            )

        _git_output(repository_root, "cat-file", "-e", f"{record.source_revision}^{{commit}}")
        change_output = _git_output(
            repository_root,
            "diff-tree",
            "--root",
            "--no-commit-id",
            "--name-status",
            "-r",
            record.source_revision,
            "--",
            git_path,
        ).decode("utf-8", errors="strict")
        changes = [line.split("\t", 1) for line in change_output.splitlines() if line]
        if not any(len(parts) == 2 and parts[0] == "A" and parts[1] == git_path for parts in changes):
            raise MigrationManifestError(
                f"source_revision did not add declared migration path: "
                f"{record.source_revision} -> {git_path}"
            )

        source_bytes = _git_output(
            repository_root, "show", f"{record.source_revision}:{git_path}"
        )
        source_digest = hashlib.sha256(source_bytes).hexdigest()
        if source_digest != record.sha256:
            raise MigrationManifestError(
                f"source revision SHA-256 mismatch for {record.path}: "
                f"manifest={record.sha256}, source={source_digest}"
            )


def load_and_verify_manifest(
    manifest_path: Path, migrations_dir: Path
) -> tuple[MigrationRecord, ...]:
    """Load, structurally validate, and SHA-256 verify the complete SQL inventory."""
    manifest_path = Path(manifest_path)
    migrations_dir = Path(migrations_dir).resolve()

    try:
        raw_manifest = manifest_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise MigrationManifestError(f"cannot read UTF-8 manifest: {exc}") from exc

    try:
        document = json.loads(raw_manifest, object_pairs_hook=_reject_duplicate_keys)
    except MigrationManifestError:
        raise
    except (json.JSONDecodeError, TypeError) as exc:
        raise MigrationManifestError(f"invalid manifest JSON: {exc}") from exc

    if not isinstance(document, dict):
        raise MigrationManifestError("manifest root must be an object")
    _require_exact_keys(
        document, {"manifest_version", "baseline_revision", "migrations"}, "manifest"
    )
    if type(document["manifest_version"]) is not int or document["manifest_version"] != 1:
        raise MigrationManifestError("manifest_version must be integer 1")

    baseline = document["baseline_revision"]
    if not isinstance(baseline, str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", baseline):
        raise MigrationManifestError("baseline_revision must be a lowercase Git commit SHA")

    entries = document["migrations"]
    if not isinstance(entries, list) or not entries:
        raise MigrationManifestError("migrations must be a non-empty array")

    records: list[MigrationRecord] = []
    seen_versions: set[int] = set()
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()

    for index, entry in enumerate(entries):
        label = f"migrations[{index}]"
        if not isinstance(entry, dict):
            raise MigrationManifestError(f"{label} must be an object")
        _require_exact_keys(
            entry,
            {"version", "migration_id", "path", "sha256", "source_revision", "execution_mode"},
            label,
        )

        version = entry["version"]
        if type(version) is not int or version < 1:
            raise MigrationManifestError(f"{label}.version must be a positive integer")
        if version in seen_versions:
            raise MigrationManifestError(f"duplicate migration version: {version}")
        if records and version <= records[-1].version:
            raise MigrationManifestError("migration versions must be strictly increasing")
        seen_versions.add(version)

        migration_id = entry["migration_id"]
        if not isinstance(migration_id, str) or not re.fullmatch(
            r"[a-z0-9][a-z0-9._-]*", migration_id
        ):
            raise MigrationManifestError(f"{label}.migration_id is invalid")
        if migration_id in seen_ids:
            raise MigrationManifestError(f"duplicate migration ID: {migration_id}")
        seen_ids.add(migration_id)

        relative_path = entry["path"]
        if not isinstance(relative_path, str) or not relative_path:
            raise MigrationManifestError(f"{label}.path must be a non-empty string")
        posix_path = PurePosixPath(relative_path)
        if (
            posix_path.is_absolute()
            or "\\" in relative_path
            or relative_path != posix_path.as_posix()
            or any(part in {".", ".."} for part in posix_path.parts)
        ):
            raise MigrationManifestError(f"{label}.path must be a canonical relative POSIX path")
        if relative_path in seen_paths:
            raise MigrationManifestError(f"duplicate migration path: {relative_path}")
        seen_paths.add(relative_path)

        expected_digest = entry["sha256"]
        if not isinstance(expected_digest, str) or not re.fullmatch(
            r"[0-9a-f]{64}", expected_digest
        ):
            raise MigrationManifestError(f"{label}.sha256 must be 64 lowercase hexadecimal characters")

        source_revision = entry["source_revision"]
        if not isinstance(source_revision, str) or not re.fullmatch(
            r"[0-9a-f]{40}|[0-9a-f]{64}", source_revision
        ):
            raise MigrationManifestError(f"{label}.source_revision must be a lowercase Git commit SHA")

        execution_mode = entry["execution_mode"]
        if execution_mode != "transactional":
            raise MigrationManifestError(
                f"{label}.execution_mode is unsupported; only transactional is allowed"
            )

        candidate = (migrations_dir / Path(*posix_path.parts)).resolve()
        try:
            candidate.relative_to(migrations_dir)
        except ValueError as exc:
            raise MigrationManifestError(f"{label}.path escapes the migrations directory") from exc
        if not candidate.is_file():
            raise MigrationManifestError(f"migration file does not exist: {relative_path}")

        try:
            sql_bytes = candidate.read_bytes()
            sql_bytes.decode("utf-8")
        except (OSError, UnicodeError) as exc:
            raise MigrationManifestError(
                f"migration is not readable UTF-8: {relative_path}"
            ) from exc

        actual_digest = hashlib.sha256(sql_bytes).hexdigest()
        if actual_digest != expected_digest:
            raise MigrationManifestError(
                f"SHA-256 mismatch for {relative_path}: expected {expected_digest}, got {actual_digest}"
            )

        records.append(
            MigrationRecord(
                version=version,
                migration_id=migration_id,
                path=relative_path,
                sha256=actual_digest,
                source_revision=source_revision,
                execution_mode=execution_mode,
            )
        )

    actual_sql_paths = {
        path.relative_to(migrations_dir).as_posix()
        for path in migrations_dir.rglob("*.sql")
        if path.is_file()
    }
    unlisted = sorted(actual_sql_paths - seen_paths)
    missing = sorted(seen_paths - actual_sql_paths)
    if unlisted or missing:
        raise MigrationManifestError(
            f"SQL inventory mismatch; unlisted={unlisted}, missing={missing}"
        )

    verified_records = tuple(records)
    _verify_git_provenance(
        verified_records, baseline, manifest_path, migrations_dir
    )
    return verified_records
