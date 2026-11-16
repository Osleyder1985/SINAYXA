#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE_URL="https://dl.min.io/api/releases/aistor/latest"
ARTIFACT_DIR="artifacts/aistor-release-metadata"
METADATA_FILE="$ARTIFACT_DIR/aistor-release-metadata.json"
REPORT_FILE="$ARTIFACT_DIR/aistor-release-metadata-report.json"
STATUS=BLOCKED
RESULT_CODE=NOT_STARTED
METADATA_SHA256=NOT_CAPTURED
METADATA_BYTES=0
TOP_LEVEL_KEYS=NOT_INSPECTED
RETRIEVED_AT_UTC="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
COMMIT_SHA="$GITHUB_SHA"
WORKFLOW_RUN_ID="$GITHUB_RUN_ID"

mkdir -p "$ARTIFACT_DIR"

write_report() {
  cat > "$REPORT_FILE" <<EOF
{
  "schema_version": "1.0.0",
  "classification": "OFFICIAL_METADATA_CAPTURE_ONLY",
  "status": "$STATUS",
  "result_code": "$RESULT_CODE",
  "source_uri": "$SOURCE_URL",
  "retrieved_at_utc": "$RETRIEVED_AT_UTC",
  "commit_sha": "$COMMIT_SHA",
  "workflow_run_id": "$WORKFLOW_RUN_ID",
  "metadata_file": "$METADATA_FILE",
  "metadata_sha256": "$METADATA_SHA256",
  "metadata_bytes": $METADATA_BYTES,
  "metadata_top_level_keys": "$TOP_LEVEL_KEYS",
  "binary_download_performed": false,
  "image_pull_performed": false,
  "software_installation_performed": false,
  "license_requested": false,
  "license_activated": false,
  "external_resources_created": false,
  "release_classification": "NOT_CLASSIFIED"
}
EOF
}

if ! command -v curl >/dev/null 2>&1; then
  RESULT_CODE=CURL_UNAVAILABLE
  write_report
  exit 1
fi
if ! command -v jq >/dev/null 2>&1; then
  RESULT_CODE=JQ_UNAVAILABLE
  write_report
  exit 1
fi

if ! curl --fail --silent --show-error --location --retry 2 --retry-all-errors --max-time 30 \
  --output "$METADATA_FILE" "$SOURCE_URL"; then
  RESULT_CODE=FETCH_FAILED
  write_report
  exit 1
fi

if ! jq -e 'type == "object"' "$METADATA_FILE" >/dev/null 2>&1; then
  RESULT_CODE=INVALID_OR_UNEXPECTED_JSON
  write_report
  exit 1
fi

HASH_LINE="$(sha256sum "$METADATA_FILE")"
read -r METADATA_SHA256 _ <<< "$HASH_LINE"
METADATA_BYTES="$(wc -c < "$METADATA_FILE" | tr -d ' ')"
TOP_LEVEL_KEYS="$(jq -r 'keys | sort | join(",")' "$METADATA_FILE")"
RETRIEVED_AT_UTC="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
STATUS=CAPTURED
RESULT_CODE=OFFICIAL_JSON_PRESERVED
write_report

echo "Official AIStor release metadata captured; no image or binary was downloaded."
