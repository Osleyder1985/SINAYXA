#!/usr/bin/env bash
set -Eeuo pipefail
IMAGE_TAG="${POSTGRES_IMAGE_TAG:-postgres:18.7}"
EXPECTED_VERSION=18.7
IMAGE_PLATFORM=NOT_RESOLVED
IMAGE=NOT_RESOLVED
IMAGE_DIGEST=NOT_RESOLVED
PGDATA_PATH=NOT_DETECTED
POSTGRES_VOLUME_DESTINATION=NOT_DETECTED
CONTAINER=sinayxa-issue-95-lab-$$
PASSWORD=sinayxa-synthetic-only
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ARTIFACT_DIR="$ROOT_DIR/artifacts/postgresql-lab"
WORK_DIR="$(mktemp -d)"
REPORT="$ARTIFACT_DIR/postgresql-lab-report.json"
START_EPOCH="$(date +%s)"
STARTED_AT_UTC="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
CONTAINER_CREATED=false
POSTGRES_VOLUME=NOT_DETECTED
SERVER_VERSION=NOT_DETECTED
CLIENT_VERSION=NOT_DETECTED
BACKUP_SHA256=NOT_CREATED
BACKUP_SIZE=0
mkdir -p "$ARTIFACT_DIR"
for check in container dataset backup restore integrity corrupt_dump_rejection repeat_restore container_cleanup volume_cleanup cleanup; do eval "RESULT_$check=NOT_RUN"; done
write_report() {
  local status="$1" end
  end="$(date +%s)"
  cat > "$REPORT" <<EOF
{
  "schema_version": "1.0.0",
  "classification": "LAB_SYNTHETIC",
  "status": "$status",
  "postgres_image": "$IMAGE",
  "postgres_image_tag": "$IMAGE_TAG",
  "postgres_image_digest": "$IMAGE_DIGEST",
  "postgres_image_platform": "$IMAGE_PLATFORM",
  "postgres_expected_version": "$EXPECTED_VERSION",
  "postgres_pgdata": "$PGDATA_PATH",
  "postgres_volume_destination": "$POSTGRES_VOLUME_DESTINATION",
  "postgres_server_version": "$SERVER_VERSION",
  "postgres_client_version": "$CLIENT_VERSION",
  "started_at_utc": "$STARTED_AT_UTC",
  "duration_seconds": $((end - START_EPOCH)),
  "backup_sha256": "$BACKUP_SHA256",
  "backup_size_bytes": $BACKUP_SIZE,
  "checks": {
    "container": "$RESULT_container",
    "dataset": "$RESULT_dataset",
    "backup": "$RESULT_backup",
    "restore": "$RESULT_restore",
    "integrity": "$RESULT_integrity",
    "corrupt_dump_rejection": "$RESULT_corrupt_dump_rejection",
    "repeat_restore": "$RESULT_repeat_restore",
    "container_cleanup": "$RESULT_container_cleanup",
    "volume_cleanup": "$RESULT_volume_cleanup",
    "cleanup": "$RESULT_cleanup"
  },
  "external_database_connections": false,
  "production_data_used": false,
  "synthetic_data_only": true
}
EOF
}
cleanup() {
  local rc=$?
  trap - EXIT
  set +e
  local container_names volume_names
  if [[ "$CONTAINER_CREATED" == true ]]; then docker rm -fv "$CONTAINER" >/dev/null 2>&1 || true; fi
  RESULT_cleanup=NOT_RUN
  if [[ "$CONTAINER_CREATED" == true ]]; then
    if ! container_names="$(docker ps -a --format '{{.Names}}')"; then
      RESULT_container_cleanup=FAIL
    elif printf '%s\n' "$container_names" | grep -Fxq "$CONTAINER"; then
      RESULT_container_cleanup=FAIL
    else
      RESULT_container_cleanup=PASS
    fi
    if [[ "$POSTGRES_VOLUME" != NOT_DETECTED ]]; then
      if ! volume_names="$(docker volume ls --format '{{.Name}}')"; then
        RESULT_volume_cleanup=FAIL
      elif printf '%s\n' "$volume_names" | grep -Fxq -- "$POSTGRES_VOLUME"; then
        RESULT_volume_cleanup=FAIL
      else
        RESULT_volume_cleanup=PASS
      fi
    else
      RESULT_volume_cleanup=FAIL
    fi
    if [[ "$RESULT_container_cleanup" == PASS && "$RESULT_volume_cleanup" == PASS ]]; then
      RESULT_cleanup=PASS
    else
      RESULT_cleanup=FAIL
    fi
  fi
  if [[ "$rc" -eq 0 && "$RESULT_cleanup" == PASS ]]; then
    write_report PASS
  else
    write_report FAIL
    [[ "$rc" -ne 0 ]] || rc=1
  fi
  rm -rf "$WORK_DIR"
  exit "$rc"
}
trap cleanup EXIT
command -v docker >/dev/null
docker info >/dev/null
if [[ "$IMAGE_TAG" == *:latest || "$IMAGE_TAG" != *:* ]]; then
  echo "A concrete PostgreSQL release tag is required; floating tags are forbidden." >&2
  exit 1
fi
docker pull "$IMAGE_TAG"
IMAGE_DIGEST="$(docker image inspect --format '{{index .RepoDigests 0}}' "$IMAGE_TAG")"
if [[ "$IMAGE_DIGEST" != *@sha256:* ]]; then
  IMAGE_DIGEST=NOT_RESOLVED
  echo "An immutable PostgreSQL image digest could not be resolved." >&2
  exit 1
fi
IMAGE="$IMAGE_DIGEST"
IMAGE_PLATFORM="$(docker image inspect --format '{{.Os}}/{{.Architecture}}' "$IMAGE_TAG")"
docker run -d --network none --name "$CONTAINER" -e POSTGRES_PASSWORD="$PASSWORD" "$IMAGE" >/dev/null
CONTAINER_CREATED=true
for attempt in $(seq 1 60); do
  docker exec "$CONTAINER" pg_isready -U postgres >/dev/null 2>&1 && break
  [[ "$attempt" -lt 60 ]] || { echo "PostgreSQL readiness timeout" >&2; exit 1; }
  sleep 1
done
PGDATA_PATH="$(docker exec "$CONTAINER" sh -c 'printf "%s" "${PGDATA:-}"')"
if [[ -z "$PGDATA_PATH" ]]; then
  PGDATA_PATH=NOT_DETECTED
  echo "PostgreSQL PGDATA could not be resolved from the running container." >&2
  exit 1
fi
MOUNT_INFO="$(docker inspect --format '{{range .Mounts}}{{printf "%s\t%s\t%s\n" .Type .Name .Destination}}{{end}}' "$CONTAINER")"
while IFS=$'\t' read -r mount_type mount_name mount_destination; do
  [[ -n "$mount_destination" ]] || continue
  if [[ "$mount_type" == volume && ( "$PGDATA_PATH" == "$mount_destination" || "$PGDATA_PATH" == "$mount_destination/"* ) ]]; then
    POSTGRES_VOLUME="$mount_name"
    POSTGRES_VOLUME_DESTINATION="$mount_destination"
    break
  fi
done <<< "$MOUNT_INFO"
if [[ "$POSTGRES_VOLUME" == NOT_DETECTED || -z "$POSTGRES_VOLUME" ]]; then
  POSTGRES_VOLUME=NOT_DETECTED
  POSTGRES_VOLUME_DESTINATION=NOT_DETECTED
  echo "PostgreSQL data volume covering PGDATA could not be identified." >&2
  exit 1
fi
RESULT_container=PASS
SERVER_VERSION="$(docker exec "$CONTAINER" psql -U postgres -Atc 'SHOW server_version')"
CLIENT_VERSION="$(docker exec "$CONTAINER" pg_dump --version | awk '{print $3}')"
if [[ "$SERVER_VERSION" != "$EXPECTED_VERSION"* || "$CLIENT_VERSION" != "$EXPECTED_VERSION"* ]]; then
  echo "Resolved PostgreSQL server/client version does not match $EXPECTED_VERSION." >&2
  exit 1
fi
for db in sinayxa_source sinayxa_restored sinayxa_repeated; do docker exec "$CONTAINER" psql -v ON_ERROR_STOP=1 -U postgres -c "CREATE DATABASE $db"; done
docker exec -i "$CONTAINER" psql -v ON_ERROR_STOP=1 -U postgres -d sinayxa_source <<'SQL'
CREATE SCHEMA research;
CREATE TABLE research.assets (
 asset_id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
 symbol TEXT NOT NULL UNIQUE, active BOOLEAN NOT NULL DEFAULT TRUE,
 created_at TIMESTAMPTZ NOT NULL
);
CREATE TABLE research.observations (
 observation_id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
 asset_id BIGINT NOT NULL REFERENCES research.assets(asset_id),
 observed_at TIMESTAMPTZ NOT NULL, price NUMERIC(20,8) NOT NULL CHECK (price > 0),
 source_label TEXT NOT NULL
);
CREATE INDEX observations_asset_time_idx ON research.observations(asset_id, observed_at DESC);
CREATE UNIQUE INDEX observations_asset_time_source_uq ON research.observations(asset_id, observed_at, source_label);
INSERT INTO research.assets(asset_id,symbol,active,created_at) VALUES
 (1,'BTCUSDT',TRUE,'2026-01-01T00:00:00Z'),
 (2,'ETHUSDT',TRUE,'2026-01-02T00:00:00Z'),
 (3,'XRPUSDT',FALSE,'2026-01-03T00:00:00Z');
INSERT INTO research.observations(observation_id,asset_id,observed_at,price,source_label) VALUES
 (1,1,'2026-02-01T00:00:00Z',65000.12500000,'synthetic-a'),
 (2,1,'2026-02-02T00:00:00Z',66100.50000000,'synthetic-a'),
 (3,2,'2026-02-01T00:00:00Z',3200.75000000,'synthetic-b'),
 (4,3,'2026-02-03T00:00:00Z',1.25000000,'synthetic-c');
SELECT setval(pg_get_serial_sequence('research.assets','asset_id'),3,true);
SELECT setval(pg_get_serial_sequence('research.observations','observation_id'),4,true);
SQL
RESULT_dataset=PASS
docker exec "$CONTAINER" pg_dump -Fc --no-owner --no-acl -U postgres -d sinayxa_source > "$WORK_DIR/backup.dump"
test -s "$WORK_DIR/backup.dump"
BACKUP_SHA256="$(sha256sum "$WORK_DIR/backup.dump" | awk '{print $1}')"
BACKUP_SIZE="$(stat -c '%s' "$WORK_DIR/backup.dump")"
RESULT_backup=PASS
docker exec -i "$CONTAINER" pg_restore --exit-on-error --no-owner --no-acl -U postgres -d sinayxa_restored < "$WORK_DIR/backup.dump"
RESULT_restore=PASS
compare_db() {
 local db="$1"
 docker exec "$CONTAINER" pg_dump --schema-only --no-owner --no-acl -U postgres -d "$db" > "$WORK_DIR/$db-schema.sql"
 docker exec "$CONTAINER" pg_dump --data-only --column-inserts --no-owner --no-acl -U postgres -d "$db" > "$WORK_DIR/$db-data.sql"
 # PostgreSQL 18 adds per-dump random psql guard tokens; normalize only those non-schema lines.
 sed -i -e '/^\\restrict /d' -e '/^\\unrestrict /d' "$WORK_DIR/$db-schema.sql" "$WORK_DIR/$db-data.sql"
}
compare_db sinayxa_source
compare_db sinayxa_restored
if ! cmp -s "$WORK_DIR/sinayxa_source-schema.sql" "$WORK_DIR/sinayxa_restored-schema.sql"; then
 echo "Restored PostgreSQL schema differs from source." >&2
 diff -u "$WORK_DIR/sinayxa_source-schema.sql" "$WORK_DIR/sinayxa_restored-schema.sql" >&2 || true
 exit 1
fi
if ! cmp -s "$WORK_DIR/sinayxa_source-data.sql" "$WORK_DIR/sinayxa_restored-data.sql"; then
 echo "Restored PostgreSQL data differs from source." >&2
 diff -u "$WORK_DIR/sinayxa_source-data.sql" "$WORK_DIR/sinayxa_restored-data.sql" >&2 || true
 exit 1
fi
read_database_metadata() {
 local db="$1"
 docker exec -i "$CONTAINER" psql -U postgres -d "$db" -At <<'SQL'
SELECT
 (SELECT count(*) FROM research.assets)::text || ':' ||
 (SELECT count(*) FROM research.observations)::text || ':' ||
 current_setting('server_encoding') || ':' ||
 current_setting('TimeZone');
SQL
}
SOURCE_META="$(read_database_metadata sinayxa_source)"
RESTORE_META="$(read_database_metadata sinayxa_restored)"
if [[ "$SOURCE_META" != "$RESTORE_META" ]]; then
 echo "Restored PostgreSQL metadata differs: source=$SOURCE_META restored=$RESTORE_META" >&2
 exit 1
fi
RESULT_integrity=PASS
head -c 128 "$WORK_DIR/backup.dump" > "$WORK_DIR/corrupt.dump"
if docker exec -i "$CONTAINER" pg_restore --list < "$WORK_DIR/corrupt.dump" >"$WORK_DIR/corrupt.out" 2>"$WORK_DIR/corrupt.err"; then
 echo "Truncated archive was unexpectedly accepted" >&2; exit 1
fi
RESULT_corrupt_dump_rejection=PASS
docker exec -i "$CONTAINER" pg_restore --exit-on-error --no-owner --no-acl -U postgres -d sinayxa_repeated < "$WORK_DIR/backup.dump"
compare_db sinayxa_repeated
cmp -s "$WORK_DIR/sinayxa_source-schema.sql" "$WORK_DIR/sinayxa_repeated-schema.sql"
cmp -s "$WORK_DIR/sinayxa_source-data.sql" "$WORK_DIR/sinayxa_repeated-data.sql"
RESULT_repeat_restore=PASS
echo "PostgreSQL synthetic backup/restore laboratory completed."
\\t' read -r mount_type mount_name mount_destination; do
  [[ -n "$mount_destination" ]] || continue
  if [[ "$mount_type" == volume && ( "$PGDATA_PATH" == "$mount_destination" || "$PGDATA_PATH" == "$mount_destination/"* ) ]]; then
    POSTGRES_VOLUME="$mount_name"
    POSTGRES_VOLUME_DESTINATION="$mount_destination"
    break
  fi
done <<< "$MOUNT_INFO"
if [[ "$POSTGRES_VOLUME" == NOT_DETECTED || -z "$POSTGRES_VOLUME" ]]; then
  POSTGRES_VOLUME=NOT_DETECTED
  POSTGRES_VOLUME_DESTINATION=NOT_DETECTED
  echo "PostgreSQL data volume covering PGDATA could not be identified." >&2
  exit 1
fi
RESULT_container=PASS
SERVER_VERSION="$(docker exec "$CONTAINER" psql -U postgres -Atc 'SHOW server_version')"
CLIENT_VERSION="$(docker exec "$CONTAINER" pg_dump --version | awk '{print $3}')"
for db in sinayxa_source sinayxa_restored sinayxa_repeated; do docker exec "$CONTAINER" psql -v ON_ERROR_STOP=1 -U postgres -c "CREATE DATABASE $db"; done
docker exec -i "$CONTAINER" psql -v ON_ERROR_STOP=1 -U postgres -d sinayxa_source <<'SQL'
CREATE SCHEMA research;
CREATE TABLE research.assets (
 asset_id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
 symbol TEXT NOT NULL UNIQUE, active BOOLEAN NOT NULL DEFAULT TRUE,
 created_at TIMESTAMPTZ NOT NULL
);
CREATE TABLE research.observations (
 observation_id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
 asset_id BIGINT NOT NULL REFERENCES research.assets(asset_id),
 observed_at TIMESTAMPTZ NOT NULL, price NUMERIC(20,8) NOT NULL CHECK (price > 0),
 source_label TEXT NOT NULL
);
CREATE INDEX observations_asset_time_idx ON research.observations(asset_id, observed_at DESC);
CREATE UNIQUE INDEX observations_asset_time_source_uq ON research.observations(asset_id, observed_at, source_label);
INSERT INTO research.assets(asset_id,symbol,active,created_at) VALUES
 (1,'BTCUSDT',TRUE,'2026-01-01T00:00:00Z'),
 (2,'ETHUSDT',TRUE,'2026-01-02T00:00:00Z'),
 (3,'XRPUSDT',FALSE,'2026-01-03T00:00:00Z');
INSERT INTO research.observations(observation_id,asset_id,observed_at,price,source_label) VALUES
 (1,1,'2026-02-01T00:00:00Z',65000.12500000,'synthetic-a'),
 (2,1,'2026-02-02T00:00:00Z',66100.50000000,'synthetic-a'),
 (3,2,'2026-02-01T00:00:00Z',3200.75000000,'synthetic-b'),
 (4,3,'2026-02-03T00:00:00Z',1.25000000,'synthetic-c');
SELECT setval(pg_get_serial_sequence('research.assets','asset_id'),3,true);
SELECT setval(pg_get_serial_sequence('research.observations','observation_id'),4,true);
SQL
RESULT_dataset=PASS
docker exec "$CONTAINER" pg_dump -Fc --no-owner --no-acl -U postgres -d sinayxa_source > "$WORK_DIR/backup.dump"
test -s "$WORK_DIR/backup.dump"
BACKUP_SHA256="$(sha256sum "$WORK_DIR/backup.dump" | awk '{print $1}')"
BACKUP_SIZE="$(stat -c '%s' "$WORK_DIR/backup.dump")"
RESULT_backup=PASS
docker exec -i "$CONTAINER" pg_restore --exit-on-error --no-owner --no-acl -U postgres -d sinayxa_restored < "$WORK_DIR/backup.dump"
RESULT_restore=PASS
compare_db() {
 local db="$1"
 docker exec "$CONTAINER" pg_dump --schema-only --no-owner --no-acl -U postgres -d "$db" > "$WORK_DIR/$db-schema.sql"
 docker exec "$CONTAINER" pg_dump --data-only --column-inserts --no-owner --no-acl -U postgres -d "$db" > "$WORK_DIR/$db-data.sql"
 # PostgreSQL 18 adds per-dump random psql guard tokens; remove only those non-schema lines before byte comparison.
 sed -i -e '/^\\restrict /d' -e '/^\\unrestrict /d' "$WORK_DIR/$db-schema.sql" "$WORK_DIR/$db-data.sql"
}
compare_db sinayxa_source
compare_db sinayxa_restored
if ! cmp -s "$WORK_DIR/sinayxa_source-schema.sql" "$WORK_DIR/sinayxa_restored-schema.sql"; then
 echo "Restored PostgreSQL schema differs from source." >&2
 diff -u "$WORK_DIR/sinayxa_source-schema.sql" "$WORK_DIR/sinayxa_restored-schema.sql" >&2 || true
 exit 1
fi
if ! cmp -s "$WORK_DIR/sinayxa_source-data.sql" "$WORK_DIR/sinayxa_restored-data.sql"; then
 echo "Restored PostgreSQL data differs from source." >&2
 diff -u "$WORK_DIR/sinayxa_source-data.sql" "$WORK_DIR/sinayxa_restored-data.sql" >&2 || true
 exit 1
fi
if [[ "$SOURCE_META" != "$RESTORE_META" ]]; then
 echo "Restored PostgreSQL metadata differs: source=$SOURCE_META restored=$RESTORE_META" >&2
 exit 1
fi
RESULT_integrity=PASS
head -c 128 "$WORK_DIR/backup.dump" > "$WORK_DIR/corrupt.dump"
if docker exec -i "$CONTAINER" pg_restore --list < "$WORK_DIR/corrupt.dump" >"$WORK_DIR/corrupt.out" 2>"$WORK_DIR/corrupt.err"; then
 echo "Truncated archive was unexpectedly accepted" >&2; exit 1
fi
RESULT_corrupt_dump_rejection=PASS
docker exec -i "$CONTAINER" pg_restore --exit-on-error --no-owner --no-acl -U postgres -d sinayxa_repeated < "$WORK_DIR/backup.dump"
compare_db sinayxa_repeated
cmp -s "$WORK_DIR/sinayxa_source-schema.sql" "$WORK_DIR/sinayxa_repeated-schema.sql"
cmp -s "$WORK_DIR/sinayxa_source-data.sql" "$WORK_DIR/sinayxa_repeated-data.sql"
RESULT_repeat_restore=PASS
echo "PostgreSQL synthetic backup/restore laboratory completed."
