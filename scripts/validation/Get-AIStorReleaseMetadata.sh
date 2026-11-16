#!/usr/bin/env bash
set -Eeuo pipefail

SERVER_SOURCE_URL="https://dl.min.io/api/releases/aistor/latest"
CLIENT_SOURCE_URL="https://dl.min.io/aistor/mc/release/notes/"
ARTIFACT_DIR="artifacts/aistor-release-metadata"
SERVER_METADATA_FILE="$ARTIFACT_DIR/aistor-server-release-metadata.json"
CLIENT_INDEX_FILE="$ARTIFACT_DIR/aistor-client-release-notes-index.html"
REPORT_FILE="$ARTIFACT_DIR/aistor-release-metadata-report.json"

STATUS=BLOCKED
RESULT_CODE=NOT_STARTED
SERVER_PRODUCT=NOT_RESOLVED
SERVER_VERSION=NOT_RESOLVED
SERVER_RELEASE_DATE=NOT_RESOLVED
SERVER_METADATA_SHA256=NOT_CAPTURED
SERVER_METADATA_BYTES=0
SERVER_TOP_LEVEL_KEYS=NOT_INSPECTED
CLIENT_PRODUCT="AIStor Client (mc)"
CLIENT_VERSION=NOT_RESOLVED
CLIENT_INDEX_SHA256=NOT_CAPTURED
CLIENT_INDEX_BYTES=0
CLIENT_RELEASE_NOTES_URL=NOT_RESOLVED
CLIENT_SBOM_CYCLONEDX_URL=NOT_RESOLVED
CLIENT_SBOM_SPDX_URL=NOT_RESOLVED
SERVER_RELEASE_NOTES_URL=NOT_RESOLVED
SERVER_SBOM_CYCLONEDX_URL=NOT_RESOLVED
SERVER_SBOM_SPDX_URL=NOT_RESOLVED
RETRIEVED_AT_UTC="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
COMMIT_SHA="$GITHUB_SHA"
WORKFLOW_RUN_ID="$GITHUB_RUN_ID"

mkdir -p "$ARTIFACT_DIR"

write_report() {
  cat > "$REPORT_FILE" <<EOF
{
  "schema_version": "1.1.0",
  "classification": "OFFICIAL_RELEASE_METADATA_CAPTURE_ONLY",
  "status": "$STATUS",
  "result_code": "$RESULT_CODE",
  "retrieved_at_utc": "$RETRIEVED_AT_UTC",
  "commit_sha": "$COMMIT_SHA",
  "workflow_run_id": "$WORKFLOW_RUN_ID",
  "server_source_uri": "$SERVER_SOURCE_URL",
  "server_product": "$SERVER_PRODUCT",
  "server_version": "$SERVER_VERSION",
  "server_release_date": "$SERVER_RELEASE_DATE",
  "server_metadata_file": "$SERVER_METADATA_FILE",
  "server_metadata_sha256": "$SERVER_METADATA_SHA256",
  "server_metadata_bytes": $SERVER_METADATA_BYTES,
  "server_metadata_top_level_keys": "$SERVER_TOP_LEVEL_KEYS",
  "server_release_notes_uri": "$SERVER_RELEASE_NOTES_URL",
  "server_sbom_cyclonedx_uri": "$SERVER_SBOM_CYCLONEDX_URL",
  "server_sbom_spdx_uri": "$SERVER_SBOM_SPDX_URL",
  "client_source_uri": "$CLIENT_SOURCE_URL",
  "client_product": "$CLIENT_PRODUCT",
  "client_version": "$CLIENT_VERSION",
  "client_index_file": "$CLIENT_INDEX_FILE",
  "client_index_sha256": "$CLIENT_INDEX_SHA256",
  "client_index_bytes": $CLIENT_INDEX_BYTES,
  "client_release_notes_uri": "$CLIENT_RELEASE_NOTES_URL",
  "client_sbom_cyclonedx_uri": "$CLIENT_SBOM_CYCLONEDX_URL",
  "client_sbom_spdx_uri": "$CLIENT_SBOM_SPDX_URL",
  "release_classification": "SERVER_LATEST_STABLE_API_CLIENT_LATEST_PUBLISHED_INDEX",
  "binary_download_performed": false,
  "image_pull_performed": false,
  "software_installation_performed": false,
  "license_requested": false,
  "license_activated": false,
  "external_resources_created": false
}
EOF
}

if ! command -v curl >/dev/null 2>&1 || ! command -v jq >/dev/null 2>&1; then
  RESULT_CODE=REQUIRED_TOOL_UNAVAILABLE
  write_report
  exit 1
fi

if ! curl --fail --silent --show-error --location --retry 2 --retry-all-errors --max-time 30 \
  --output "$SERVER_METADATA_FILE" "$SERVER_SOURCE_URL"; then
  RESULT_CODE=SERVER_METADATA_FETCH_FAILED
  write_report
  exit 1
fi

if ! jq -e 'type == "object"' "$SERVER_METADATA_FILE" >/dev/null 2>&1; then
  RESULT_CODE=SERVER_METADATA_INVALID_JSON
  write_report
  exit 1
fi

SERVER_PRODUCT="$(jq -r '.product // "NOT_RESOLVED"' "$SERVER_METADATA_FILE")"
SERVER_VERSION="$(jq -r '.version // "NOT_RESOLVED"' "$SERVER_METADATA_FILE")"
SERVER_RELEASE_DATE="$(jq -r '.release_date // "NOT_RESOLVED"' "$SERVER_METADATA_FILE")"
SERVER_TOP_LEVEL_KEYS="$(jq -r 'keys | sort | join(",")' "$SERVER_METADATA_FILE")"
SERVER_HASH_LINE="$(sha256sum "$SERVER_METADATA_FILE")"
read -r SERVER_METADATA_SHA256 _ <<< "$SERVER_HASH_LINE"
SERVER_METADATA_BYTES="$(wc -c < "$SERVER_METADATA_FILE" | tr -d ' ')"

if [[ "$SERVER_PRODUCT" != "AIStor Server" || "$SERVER_VERSION" == "NOT_RESOLVED" ]]; then
  RESULT_CODE=SERVER_RELEASE_FIELDS_UNRESOLVED
  write_report
  exit 1
fi

SERVER_RELEASE_NOTES_URL="https://dl.min.io/aistor/minio/release/notes/release-notes-$SERVER_VERSION.md"
SERVER_SBOM_CYCLONEDX_URL="https://dl.min.io/aistor/minio/release/notes/sbom-$SERVER_VERSION.cyclonedx.json"
SERVER_SBOM_SPDX_URL="https://dl.min.io/aistor/minio/release/notes/sbom-$SERVER_VERSION.spdx.json"

if ! curl --fail --silent --show-error --location --retry 2 --retry-all-errors --max-time 30 \
  --output "$CLIENT_INDEX_FILE" "$CLIENT_SOURCE_URL"; then
  STATUS=PARTIAL
  RESULT_CODE=CLIENT_RELEASE_INDEX_FETCH_FAILED
  write_report
  exit 1
fi

CLIENT_VERSION="$(grep -oE 'RELEASE\.[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z' "$CLIENT_INDEX_FILE" | sort -Vu | tail -n 1 || true)"
if [[ -z "$CLIENT_VERSION" ]]; then
  STATUS=PARTIAL
  RESULT_CODE=CLIENT_RELEASE_VERSION_NOT_FOUND
  CLIENT_VERSION=NOT_RESOLVED
  write_report
  exit 1
fi

CLIENT_HASH_LINE="$(sha256sum "$CLIENT_INDEX_FILE")"
read -r CLIENT_INDEX_SHA256 _ <<< "$CLIENT_HASH_LINE"
CLIENT_INDEX_BYTES="$(wc -c < "$CLIENT_INDEX_FILE" | tr -d ' ')"
CLIENT_RELEASE_NOTES_URL="$CLIENT_SOURCE_URL"release-notes-"$CLIENT_VERSION".md
CLIENT_SBOM_CYCLONEDX_URL="$CLIENT_SOURCE_URL"sbom-"$CLIENT_VERSION".cyclonedx.json
CLIENT_SBOM_SPDX_URL="$CLIENT_SOURCE_URL"sbom-"$CLIENT_VERSION".spdx.json

RETRIEVED_AT_UTC="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
STATUS=CAPTURED
RESULT_CODE=SERVER_AND_CLIENT_RELEASE_METADATA_PRESERVED
write_report

echo "Official AIStor Server and Client release metadata captured; no binary or image was downloaded."
