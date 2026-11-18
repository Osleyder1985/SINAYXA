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
  jq -n \
    --arg schema_version "1.3.0" \
    --arg status "$STATUS" \
    --arg capture_status "$STATUS" \
    --arg readiness_status "BLOCKED" \
    --arg result_code "$RESULT_CODE" \
    --arg retrieved_at_utc "$RETRIEVED_AT_UTC" \
    --arg commit_sha "$COMMIT_SHA" \
    --arg workflow_run_id "$WORKFLOW_RUN_ID" \
    --arg server_source_uri "$SERVER_SOURCE_URL" \
    --arg server_product "$SERVER_PRODUCT" \
    --arg server_version "$SERVER_VERSION" \
    --arg server_release_date "$SERVER_RELEASE_DATE" \
    --arg server_metadata_file "$SERVER_METADATA_FILE" \
    --arg server_metadata_sha256 "$SERVER_METADATA_SHA256" \
    --argjson server_metadata_bytes "$SERVER_METADATA_BYTES" \
    --arg server_metadata_top_level_keys "$SERVER_TOP_LEVEL_KEYS" \
    --arg server_release_notes_uri "$SERVER_RELEASE_NOTES_URL" \
    --arg server_sbom_cyclonedx_uri "$SERVER_SBOM_CYCLONEDX_URL" \
    --arg server_sbom_spdx_uri "$SERVER_SBOM_SPDX_URL" \
    --arg client_source_uri "$CLIENT_SOURCE_URL" \
    --arg client_product "$CLIENT_PRODUCT" \
    --arg client_version "$CLIENT_VERSION" \
    --arg client_index_file "$CLIENT_INDEX_FILE" \
    --arg client_index_sha256 "$CLIENT_INDEX_SHA256" \
    --argjson client_index_bytes "$CLIENT_INDEX_BYTES" \
    --arg client_release_notes_uri "$CLIENT_RELEASE_NOTES_URL" \
    --arg client_sbom_cyclonedx_uri "$CLIENT_SBOM_CYCLONEDX_URL" \
    --arg client_sbom_spdx_uri "$CLIENT_SBOM_SPDX_URL" \
    --arg server_image_ref "$SERVER_IMAGE_REF" \
    --arg server_oci_digest "$SERVER_OCI_DIGEST" \
    --arg server_oci_digest_linux_amd64 "$SERVER_OCI_DIGEST_LINUX_AMD64" \
    --arg server_oci_digest_linux_arm64 "$SERVER_OCI_DIGEST_LINUX_ARM64" \
    --arg server_oci_inspect_sha256 "$SERVER_OCI_INSPECT_SHA256" \
    --arg server_windows_checksum_url "$SERVER_WINDOWS_CHECKSUM_URL" \
    --arg server_windows_expected_sha256 "$SERVER_WINDOWS_EXPECTED_SHA256" \
    --arg server_windows_checksum_file_sha256 "$SERVER_WINDOWS_CHECKSUM_FILE_SHA256" \
    --arg client_windows_checksum_url "$CLIENT_WINDOWS_CHECKSUM_URL" \
    --arg client_windows_expected_sha256 "$CLIENT_WINDOWS_EXPECTED_SHA256" \
    --arg client_windows_checksum_file_sha256 "$CLIENT_WINDOWS_CHECKSUM_FILE_SHA256" \
    --arg server_windows_asc_url "$SERVER_WINDOWS_ASC_URL" \
    --arg server_windows_asc_file_sha256 "$SERVER_WINDOWS_ASC_FILE_SHA256" \
    --arg server_windows_minisig_url "$SERVER_WINDOWS_MINISIG_URL" \
    --arg server_windows_minisig_file_sha256 "$SERVER_WINDOWS_MINISIG_FILE_SHA256" \
    --arg client_windows_asc_url "$CLIENT_WINDOWS_ASC_URL" \
    --arg client_windows_asc_file_sha256 "$CLIENT_WINDOWS_ASC_FILE_SHA256" \
    --arg client_windows_minisig_url "$CLIENT_WINDOWS_MINISIG_URL" \
    --arg client_windows_minisig_file_sha256 "$CLIENT_WINDOWS_MINISIG_FILE_SHA256" \
    --arg signature_sidecars_captured "$SIGNATURE_SIDECARS_CAPTURED" \
    '{
      schema_version: $schema_version,
      classification: "OFFICIAL_RELEASE_METADATA_CAPTURE_ONLY",
      status: $status,
      capture_status: $capture_status,
      readiness_status: $readiness_status,
      readiness_reasons: [
        "Binary checksums have not been compared with downloaded binaries",
        "Detached signatures have not been cryptographically verified",
        "License and permitted-use terms have not been approved",
        "No software deployment or infrastructure activation is authorized by this preflight"
      ],
      result_code: $result_code,
      retrieved_at_utc: $retrieved_at_utc,
      commit_sha: $commit_sha,
      workflow_run_id: $workflow_run_id,
      server_source_uri: $server_source_uri,
      server_product: $server_product,
      server_version: $server_version,
      server_release_date: $server_release_date,
      server_metadata_file: $server_metadata_file,
      server_metadata_sha256: $server_metadata_sha256,
      server_metadata_bytes: $server_metadata_bytes,
      server_metadata_top_level_keys: $server_metadata_top_level_keys,
      server_release_notes_uri: $server_release_notes_uri,
      server_sbom_cyclonedx_uri: $server_sbom_cyclonedx_uri,
      server_sbom_spdx_uri: $server_sbom_spdx_uri,
      client_source_uri: $client_source_uri,
      client_product: $client_product,
      client_version: $client_version,
      client_index_file: $client_index_file,
      client_index_sha256: $client_index_sha256,
      client_index_bytes: $client_index_bytes,
      client_release_notes_uri: $client_release_notes_uri,
      client_sbom_cyclonedx_uri: $client_sbom_cyclonedx_uri,
      client_sbom_spdx_uri: $client_sbom_spdx_uri,
      server_image_ref: $server_image_ref,
      server_oci_digest: $server_oci_digest,
      server_oci_digest_linux_amd64: $server_oci_digest_linux_amd64,
      server_oci_digest_linux_arm64: $server_oci_digest_linux_arm64,
      server_oci_inspect_sha256: $server_oci_inspect_sha256,
      server_windows_checksum_url: $server_windows_checksum_url,
      server_windows_expected_sha256: $server_windows_expected_sha256,
      server_windows_checksum_file_sha256: $server_windows_checksum_file_sha256,
      client_windows_checksum_url: $client_windows_checksum_url,
      client_windows_expected_sha256: $client_windows_expected_sha256,
      client_windows_checksum_file_sha256: $client_windows_checksum_file_sha256,
      server_windows_asc_url: $server_windows_asc_url,
      server_windows_asc_file_sha256: $server_windows_asc_file_sha256,
      server_windows_minisig_url: $server_windows_minisig_url,
      server_windows_minisig_file_sha256: $server_windows_minisig_file_sha256,
      client_windows_asc_url: $client_windows_asc_url,
      client_windows_asc_file_sha256: $client_windows_asc_file_sha256,
      client_windows_minisig_url: $client_windows_minisig_url,
      client_windows_minisig_file_sha256: $client_windows_minisig_file_sha256,
      signature_sidecars_captured: ($signature_sidecars_captured == "true"),
      signature_verification_performed: false,
      checksum_compared_to_binary: false,
      release_classification: "SERVER_LATEST_STABLE_API_CLIENT_LATEST_PUBLISHED_INDEX",
      binary_download_performed: false,
      image_pull_performed: false,
      software_installation_performed: false,
      license_requested: false,
      license_activated: false,
      external_resources_created: false
    }' > "$REPORT_FILE"
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

if [[ ! "$SERVER_VERSION" =~ ^RELEASE\.[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z$ ]]; then
  RESULT_CODE=SERVER_RELEASE_VERSION_FORMAT_INVALID
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

fetch_nonempty_sidecar() {
  local url="$1"
  local output="$2"
  if ! curl --fail --silent --show-error --location --max-time 30 --output "$output" "$url"; then
    rm -f "$output"
    return 1
  fi
  if [[ ! -s "$output" ]]; then
    rm -f "$output"
    return 1
  fi
}

capture_checksum_sidecar() {
  local url="$1"
  local output="$2"
  local -n expected_ref="$3"
  local -n digest_ref="$4"
  local checksum filename extra
  if ! fetch_nonempty_sidecar "$url" "$output"; then
    return 1
  fi
  read -r checksum filename extra < "$output" || true
  if [[ ! "$checksum" =~ ^[a-fA-F0-9]{64}$ || -z "$filename" || -n "$extra" ]]; then
    rm -f "$output"
    return 1
  fi
  expected_ref="$(printf '%s' "$checksum" | tr '[:upper:]' '[:lower:]')"
  digest_ref="$(sha256sum "$output" | awk '{print $1}')"
}

capture_openpgp_sidecar() {
  local url="$1"
  local output="$2"
  local -n digest_ref="$3"
  if ! fetch_nonempty_sidecar "$url" "$output"; then
    return 1
  fi
  if ! grep -q '^-----BEGIN PGP SIGNATURE-----$' "$output" ||
     ! grep -q '^-----END PGP SIGNATURE-----$' "$output"; then
    rm -f "$output"
    return 1
  fi
  digest_ref="$(sha256sum "$output" | awk '{print $1}')"
}

capture_minisign_sidecar() {
  local url="$1"
  local output="$2"
  local -n digest_ref="$3"
  if ! fetch_nonempty_sidecar "$url" "$output"; then
    return 1
  fi
  if ! grep -q '^untrusted comment:' "$output" ||
     ! grep -q '^trusted comment:' "$output" ||
     [[ "$(wc -l < "$output")" -lt 4 ]]; then
    rm -f "$output"
    return 1
  fi
  digest_ref="$(sha256sum "$output" | awk '{print $1}')"
}

capture_checksum_sidecar "$SERVER_WINDOWS_CHECKSUM_URL" "$SERVER_CHECKSUM_FILE" SERVER_WINDOWS_EXPECTED_SHA256 SERVER_WINDOWS_CHECKSUM_FILE_SHA256 || true
capture_checksum_sidecar "$CLIENT_WINDOWS_CHECKSUM_URL" "$CLIENT_CHECKSUM_FILE" CLIENT_WINDOWS_EXPECTED_SHA256 CLIENT_WINDOWS_CHECKSUM_FILE_SHA256 || true

SERVER_WINDOWS_ASC_URL="\${SERVER_WINDOWS_CHECKSUM_URL%.sha256sum}.asc"
SERVER_WINDOWS_MINISIG_URL="\${SERVER_WINDOWS_CHECKSUM_URL%.sha256sum}.minisig"
CLIENT_WINDOWS_ASC_URL="\${CLIENT_WINDOWS_CHECKSUM_URL%.sha256sum}.asc"
CLIENT_WINDOWS_MINISIG_URL="\${CLIENT_WINDOWS_CHECKSUM_URL%.sha256sum}.minisig"
SERVER_ASC_FILE="$ARTIFACT_DIR/aistor-server-windows-amd64.asc"
SERVER_MINISIG_FILE="$ARTIFACT_DIR/aistor-server-windows-amd64.minisig"
CLIENT_ASC_FILE="$ARTIFACT_DIR/aistor-client-windows-amd64.asc"
CLIENT_MINISIG_FILE="$ARTIFACT_DIR/aistor-client-windows-amd64.minisig"

capture_openpgp_sidecar "$SERVER_WINDOWS_ASC_URL" "$SERVER_ASC_FILE" SERVER_WINDOWS_ASC_FILE_SHA256 || true
capture_minisign_sidecar "$SERVER_WINDOWS_MINISIG_URL" "$SERVER_MINISIG_FILE" SERVER_WINDOWS_MINISIG_FILE_SHA256 || true
capture_openpgp_sidecar "$CLIENT_WINDOWS_ASC_URL" "$CLIENT_ASC_FILE" CLIENT_WINDOWS_ASC_FILE_SHA256 || true
capture_minisign_sidecar "$CLIENT_WINDOWS_MINISIG_URL" "$CLIENT_MINISIG_FILE" CLIENT_WINDOWS_MINISIG_FILE_SHA256 || true

if [[ "$SERVER_WINDOWS_EXPECTED_SHA256" =~ ^[a-fA-F0-9]{64}$ &&
      "$CLIENT_WINDOWS_EXPECTED_SHA256" =~ ^[a-fA-F0-9]{64}$ &&
      "$SERVER_WINDOWS_CHECKSUM_FILE_SHA256" != NOT_CAPTURED &&
      "$CLIENT_WINDOWS_CHECKSUM_FILE_SHA256" != NOT_CAPTURED &&
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
printf 'AIStor Server OCI index digest: %s\n' "$SERVER_OCI_DIGEST"
printf 'AIStor Server OCI linux/amd64 manifest digest: %s\n' "$SERVER_OCI_DIGEST_LINUX_AMD64"
printf 'AIStor Server OCI linux/arm64 manifest digest: %s\n' "$SERVER_OCI_DIGEST_LINUX_ARM64"
printf 'AIStor Server Windows SHA-256 sidecar: %s\n' "$SERVER_WINDOWS_EXPECTED_SHA256"
printf 'AIStor Client Windows SHA-256 sidecar: %s\n' "$CLIENT_WINDOWS_EXPECTED_SHA256"
printf 'Windows detached signature sidecars captured: %s\n' "$SIGNATURE_SIDECARS_CAPTURED"
printf 'Binary downloaded: false; image pulled: false; signature verification performed: false\n'
echo "Official AIStor Server and Client release metadata captured; no binary or image was downloaded."
