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
SERVER_IMAGE_REF=NOT_RESOLVED
SERVER_OCI_DIGEST=NOT_RESOLVED
SERVER_OCI_DIGEST_LINUX_AMD64=NOT_RESOLVED
SERVER_OCI_DIGEST_LINUX_ARM64=NOT_RESOLVED
SERVER_OCI_INSPECT_SHA256=NOT_CAPTURED
SERVER_WINDOWS_CHECKSUM_URL=NOT_RESOLVED
SERVER_WINDOWS_EXPECTED_SHA256=NOT_CAPTURED
SERVER_WINDOWS_CHECKSUM_FILE_SHA256=NOT_CAPTURED
CLIENT_WINDOWS_CHECKSUM_URL=NOT_RESOLVED
CLIENT_WINDOWS_EXPECTED_SHA256=NOT_CAPTURED
CLIENT_WINDOWS_CHECKSUM_FILE_SHA256=NOT_CAPTURED
SERVER_WINDOWS_ASC_URL=NOT_RESOLVED
SERVER_WINDOWS_ASC_FILE_SHA256=NOT_CAPTURED
SERVER_WINDOWS_MINISIG_URL=NOT_RESOLVED
SERVER_WINDOWS_MINISIG_FILE_SHA256=NOT_CAPTURED
CLIENT_WINDOWS_ASC_URL=NOT_RESOLVED
CLIENT_WINDOWS_ASC_FILE_SHA256=NOT_CAPTURED
CLIENT_WINDOWS_MINISIG_URL=NOT_RESOLVED
CLIENT_WINDOWS_MINISIG_FILE_SHA256=NOT_CAPTURED
SIGNATURE_SIDECARS_CAPTURED=false
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
  "schema_version": "1.2.0",
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
  "server_image_ref": "$SERVER_IMAGE_REF",
  "server_oci_digest": "$SERVER_OCI_DIGEST",
  "server_oci_digest_linux_amd64": "$SERVER_OCI_DIGEST_LINUX_AMD64",
  "server_oci_digest_linux_arm64": "$SERVER_OCI_DIGEST_LINUX_ARM64",
  "server_oci_inspect_sha256": "$SERVER_OCI_INSPECT_SHA256",
  "server_windows_checksum_url": "$SERVER_WINDOWS_CHECKSUM_URL",
  "server_windows_expected_sha256": "$SERVER_WINDOWS_EXPECTED_SHA256",
  "server_windows_checksum_file_sha256": "$SERVER_WINDOWS_CHECKSUM_FILE_SHA256",
  "client_windows_checksum_url": "$CLIENT_WINDOWS_CHECKSUM_URL",
  "client_windows_expected_sha256": "$CLIENT_WINDOWS_EXPECTED_SHA256",
  "client_windows_checksum_file_sha256": "$CLIENT_WINDOWS_CHECKSUM_FILE_SHA256",
  "server_windows_asc_url": "$SERVER_WINDOWS_ASC_URL",
  "server_windows_asc_file_sha256": "$SERVER_WINDOWS_ASC_FILE_SHA256",
  "server_windows_minisig_url": "$SERVER_WINDOWS_MINISIG_URL",
  "server_windows_minisig_file_sha256": "$SERVER_WINDOWS_MINISIG_FILE_SHA256",
  "client_windows_asc_url": "$CLIENT_WINDOWS_ASC_URL",
  "client_windows_asc_file_sha256": "$CLIENT_WINDOWS_ASC_FILE_SHA256",
  "client_windows_minisig_url": "$CLIENT_WINDOWS_MINISIG_URL",
  "client_windows_minisig_file_sha256": "$CLIENT_WINDOWS_MINISIG_FILE_SHA256",
  "signature_sidecars_captured": "$SIGNATURE_SIDECARS_CAPTURED",
  "signature_verification_performed": false,
  "checksum_compared_to_binary": false,
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

SERVER_IMAGE_REF="quay.io/minio/aistor/minio:$SERVER_VERSION"
OCI_INSPECT_FILE="$ARTIFACT_DIR/aistor-server-oci-manifest-inspect.txt"
if command -v docker >/dev/null 2>&1 && docker buildx version >/dev/null 2>&1; then
  if docker buildx imagetools inspect "$SERVER_IMAGE_REF" > "$OCI_INSPECT_FILE" 2>/dev/null; then
    OCI_HASH_LINE="$(sha256sum "$OCI_INSPECT_FILE")"
    read -r SERVER_OCI_INSPECT_SHA256 _ <<< "$OCI_HASH_LINE"
    SERVER_OCI_DIGEST="$(awk '/^Digest:/ {print $2; exit}' "$OCI_INSPECT_FILE" || true)"
    SERVER_OCI_DIGEST_LINUX_AMD64="$(awk '/^  Name:/ {manifest=$2} /^  Platform:[[:space:]]+linux\/amd64/ {sub(/^.*@/, "", manifest); print manifest; exit}' "$OCI_INSPECT_FILE" || true)"
    SERVER_OCI_DIGEST_LINUX_ARM64="$(awk '/^  Name:/ {manifest=$2} /^  Platform:[[:space:]]+linux\/arm64/ {sub(/^.*@/, "", manifest); print manifest; exit}' "$OCI_INSPECT_FILE" || true)"
  fi
fi

SERVER_WINDOWS_CHECKSUM_URL="https://dl.min.io/aistor/minio/release/windows-amd64/minio.exe.$SERVER_VERSION.sha256sum"
CLIENT_WINDOWS_CHECKSUM_URL="https://dl.min.io/aistor/mc/release/windows-amd64/mc.exe.$CLIENT_VERSION.sha256sum"
SERVER_CHECKSUM_FILE="$ARTIFACT_DIR/aistor-server-windows-amd64.sha256sum"
CLIENT_CHECKSUM_FILE="$ARTIFACT_DIR/aistor-client-windows-amd64.sha256sum"

if curl --fail --silent --show-error --location --max-time 30 --output "$SERVER_CHECKSUM_FILE" "$SERVER_WINDOWS_CHECKSUM_URL"; then
  read -r SERVER_WINDOWS_EXPECTED_SHA256 _ < "$SERVER_CHECKSUM_FILE"
  SERVER_CHECKSUM_HASH_LINE="$(sha256sum "$SERVER_CHECKSUM_FILE")"
  read -r SERVER_WINDOWS_CHECKSUM_FILE_SHA256 _ <<< "$SERVER_CHECKSUM_HASH_LINE"
fi
if curl --fail --silent --show-error --location --max-time 30 --output "$CLIENT_CHECKSUM_FILE" "$CLIENT_WINDOWS_CHECKSUM_URL"; then
  read -r CLIENT_WINDOWS_EXPECTED_SHA256 _ < "$CLIENT_CHECKSUM_FILE"
  CLIENT_CHECKSUM_HASH_LINE="$(sha256sum "$CLIENT_CHECKSUM_FILE")"
  read -r CLIENT_WINDOWS_CHECKSUM_FILE_SHA256 _ <<< "$CLIENT_CHECKSUM_HASH_LINE"
fi

SERVER_WINDOWS_ASC_URL="${SERVER_WINDOWS_CHECKSUM_URL%.sha256sum}.asc"
SERVER_WINDOWS_MINISIG_URL="${SERVER_WINDOWS_CHECKSUM_URL%.sha256sum}.minisig"
CLIENT_WINDOWS_ASC_URL="${CLIENT_WINDOWS_CHECKSUM_URL%.sha256sum}.asc"
CLIENT_WINDOWS_MINISIG_URL="${CLIENT_WINDOWS_CHECKSUM_URL%.sha256sum}.minisig"
SERVER_ASC_FILE="$ARTIFACT_DIR/aistor-server-windows-amd64.asc"
SERVER_MINISIG_FILE="$ARTIFACT_DIR/aistor-server-windows-amd64.minisig"
CLIENT_ASC_FILE="$ARTIFACT_DIR/aistor-client-windows-amd64.asc"
CLIENT_MINISIG_FILE="$ARTIFACT_DIR/aistor-client-windows-amd64.minisig"

if curl --fail --silent --show-error --location --max-time 30 --output "$SERVER_ASC_FILE" "$SERVER_WINDOWS_ASC_URL"; then
  HASH_LINE="$(sha256sum "$SERVER_ASC_FILE")"
  read -r SERVER_WINDOWS_ASC_FILE_SHA256 _ <<< "$HASH_LINE"
fi
if curl --fail --silent --show-error --location --max-time 30 --output "$SERVER_MINISIG_FILE" "$SERVER_WINDOWS_MINISIG_URL"; then
  HASH_LINE="$(sha256sum "$SERVER_MINISIG_FILE")"
  read -r SERVER_WINDOWS_MINISIG_FILE_SHA256 _ <<< "$HASH_LINE"
fi
if curl --fail --silent --show-error --location --max-time 30 --output "$CLIENT_ASC_FILE" "$CLIENT_WINDOWS_ASC_URL"; then
  HASH_LINE="$(sha256sum "$CLIENT_ASC_FILE")"
  read -r CLIENT_WINDOWS_ASC_FILE_SHA256 _ <<< "$HASH_LINE"
fi
if curl --fail --silent --show-error --location --max-time 30 --output "$CLIENT_MINISIG_FILE" "$CLIENT_WINDOWS_MINISIG_URL"; then
  HASH_LINE="$(sha256sum "$CLIENT_MINISIG_FILE")"
  read -r CLIENT_WINDOWS_MINISIG_FILE_SHA256 _ <<< "$HASH_LINE"
fi

if [[ "$SERVER_WINDOWS_EXPECTED_SHA256" =~ ^[a-fA-F0-9]{64}$ &&
      "$CLIENT_WINDOWS_EXPECTED_SHA256" =~ ^[a-fA-F0-9]{64}$ &&
      "$SERVER_WINDOWS_ASC_FILE_SHA256" != NOT_CAPTURED &&
      "$SERVER_WINDOWS_MINISIG_FILE_SHA256" != NOT_CAPTURED &&
      "$CLIENT_WINDOWS_ASC_FILE_SHA256" != NOT_CAPTURED &&
      "$CLIENT_WINDOWS_MINISIG_FILE_SHA256" != NOT_CAPTURED ]]; then
  SIGNATURE_SIDECARS_CAPTURED=true
fi

RETRIEVED_AT_UTC="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
if [[ "$SIGNATURE_SIDECARS_CAPTURED" == true ]]; then
  STATUS=CAPTURED
  RESULT_CODE=SERVER_AND_CLIENT_METADATA_CHECKSUMS_AND_SIGNATURE_SIDECARS_PRESERVED
else
  STATUS=PARTIAL
  RESULT_CODE=RELEASE_METADATA_CAPTURED_BUT_CHECKSUM_OR_SIGNATURE_SIDECARS_INCOMPLETE
fi
write_report

printf 'AIStor metadata status: %s (%s)\n' "$STATUS" "$RESULT_CODE"
printf 'AIStor Server OCI digest: %s\n' "$SERVER_OCI_DIGEST"
printf 'AIStor Server Windows SHA-256 sidecar: %s\n' "$SERVER_WINDOWS_EXPECTED_SHA256"
printf 'AIStor Client Windows SHA-256 sidecar: %s\n' "$CLIENT_WINDOWS_EXPECTED_SHA256"
printf 'Windows detached signature sidecars captured: %s\n' "$SIGNATURE_SIDECARS_CAPTURED"
printf 'Binary downloaded: false; image pulled: false; signature verification performed: false\n'
echo "Official AIStor Server and Client release metadata captured; no binary or image was downloaded."
