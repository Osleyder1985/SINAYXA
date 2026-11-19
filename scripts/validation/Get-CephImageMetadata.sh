#!/usr/bin/env bash
set -Eeuo pipefail

IMAGE_REPOSITORY="ceph/ceph"
IMAGE_TAG="v21.2.0"
IMAGE_REFERENCE="quay.io/${IMAGE_REPOSITORY}:${IMAGE_TAG}"
REGISTRY_BASE="https://quay.io"
ARTIFACT_DIR="artifacts/ceph-image-metadata"
TOKEN_FILE="$ARTIFACT_DIR/registry-token-response.json"
INDEX_FILE="$ARTIFACT_DIR/manifest-index.json"
INDEX_HEADERS="$ARTIFACT_DIR/manifest-index.headers"
REPORT_FILE="$ARTIFACT_DIR/ceph-image-metadata-report.json"
ACCEPT_HEADER="application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json, application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json"

STATUS="BLOCKED"
RESULT_CODE="NOT_STARTED"
TOP_LEVEL_DIGEST="NOT_CAPTURED"
TOP_LEVEL_MEDIA_TYPE="NOT_CAPTURED"
AMD64_DIGEST="NOT_CAPTURED"
AMD64_COMPRESSED_BYTES=0
ARM64_DIGEST="NOT_CAPTURED"
ARM64_COMPRESSED_BYTES=0
IMAGE_PULL_PERFORMED=false
IMAGE_LAYERS_DOWNLOADED=false
SOFTWARE_INSTALLED=false
RETRIEVED_AT_UTC="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
COMMIT_SHA="${GITHUB_SHA:-LOCAL_UNPINNED}"
WORKFLOW_RUN_ID="${GITHUB_RUN_ID:-LOCAL_UNPINNED}"

mkdir -p "$ARTIFACT_DIR"

write_report() {
  jq -n \
    --arg schema_version "1.0.0" \
    --arg classification "OCI_REGISTRY_METADATA_ONLY_NO_IMAGE_PULL" \
    --arg status "$STATUS" \
    --arg result_code "$RESULT_CODE" \
    --arg retrieved_at_utc "$RETRIEVED_AT_UTC" \
    --arg commit_sha "$COMMIT_SHA" \
    --arg workflow_run_id "$WORKFLOW_RUN_ID" \
    --arg image_reference "$IMAGE_REFERENCE" \
    --arg image_repository "$IMAGE_REPOSITORY" \
    --arg image_tag "$IMAGE_TAG" \
    --arg top_level_digest "$TOP_LEVEL_DIGEST" \
    --arg top_level_media_type "$TOP_LEVEL_MEDIA_TYPE" \
    --arg amd64_digest "$AMD64_DIGEST" \
    --argjson amd64_compressed_bytes "$AMD64_COMPRESSED_BYTES" \
    --arg arm64_digest "$ARM64_DIGEST" \
    --argjson arm64_compressed_bytes "$ARM64_COMPRESSED_BYTES" \
    --argjson image_pull_performed "$IMAGE_PULL_PERFORMED" \
    --argjson image_layers_downloaded "$IMAGE_LAYERS_DOWNLOADED" \
    --argjson software_installed "$SOFTWARE_INSTALLED" \
    '{
      schema_version: $schema_version,
      classification: $classification,
      status: $status,
      result_code: $result_code,
      retrieved_at_utc: $retrieved_at_utc,
      commit_sha: $commit_sha,
      workflow_run_id: $workflow_run_id,
      image_reference: $image_reference,
      image_repository: $image_repository,
      image_tag: $image_tag,
      top_level_digest: $top_level_digest,
      top_level_media_type: $top_level_media_type,
      platforms: {
        "linux/amd64": {
          manifest_digest: $amd64_digest,
          compressed_descriptor_bytes: $amd64_compressed_bytes
        },
        "linux/arm64": {
          manifest_digest: $arm64_digest,
          compressed_descriptor_bytes: $arm64_compressed_bytes
        }
      },
      image_pull_performed: $image_pull_performed,
      image_layers_downloaded: $image_layers_downloaded,
      software_installed: $software_installed,
      cephadm_bootstrap_performed: false,
      containers_started: false,
      object_lock_test_performed: false,
      production_data_used: false,
      costs_incurred: false,
      limitations: [
        "Registry manifest metadata does not verify image signatures or provenance.",
        "Compressed layer sizes are descriptor metadata, not a measured download.",
        "No image layers or binaries are downloaded.",
        "No Ceph daemon is started and no Object Lock behavior is tested.",
        "The tag-to-digest observation is time-bound; future runs may resolve differently."
      ]
    }' > "$REPORT_FILE"
}

fail() {
  RESULT_CODE="$1"
  STATUS="BLOCKED"
  write_report
  printf 'Ceph image metadata preflight blocked: %s\n' "$RESULT_CODE" >&2
  exit 1
}

for tool in curl jq sha256sum; do
  command -v "$tool" >/dev/null 2>&1 || fail "REQUIRED_TOOL_UNAVAILABLE_$tool"
done

TOKEN_ENDPOINT="$REGISTRY_BASE/v2/auth?service=quay.io&scope=repository:$IMAGE_REPOSITORY:pull"
if ! curl --fail --silent --show-error --location --max-time 30 \
  --output "$TOKEN_FILE" "$TOKEN_ENDPOINT"; then
  fail "REGISTRY_TOKEN_REQUEST_FAILED"
fi

TOKEN="$(jq -r '.token // .access_token // empty' "$TOKEN_FILE")"
[[ -n "$TOKEN" ]] || fail "REGISTRY_TOKEN_MISSING"

if ! curl --fail --silent --show-error --location --max-time 30 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: $ACCEPT_HEADER" \
  -D "$INDEX_HEADERS" \
  --output "$INDEX_FILE" \
  "$REGISTRY_BASE/v2/$IMAGE_REPOSITORY/manifests/$IMAGE_TAG"; then
  unset TOKEN
  fail "TOP_LEVEL_MANIFEST_FETCH_FAILED"
fi
unset TOKEN

jq -e 'type == "object" and (.schemaVersion == 2)' "$INDEX_FILE" >/dev/null 2>&1 || fail "TOP_LEVEL_MANIFEST_INVALID"
TOP_LEVEL_MEDIA_TYPE="$(jq -r '.mediaType // "NOT_DECLARED"' "$INDEX_FILE")"
TOP_LEVEL_DIGEST="$(awk 'tolower($1) == "docker-content-digest:" {gsub("\\r","",$2); print $2; exit}' "$INDEX_HEADERS")"
[[ "$TOP_LEVEL_DIGEST" =~ ^sha256:[a-f0-9]{64}$ ]] || fail "TOP_LEVEL_DIGEST_HEADER_MISSING"

fetch_platform_manifest() {
  local architecture="$1"
  local digest="$2"
  local output="$ARTIFACT_DIR/manifest-$architecture.json"
  local headers="$ARTIFACT_DIR/manifest-$architecture.headers"
  local token
  local endpoint="$REGISTRY_BASE/v2/auth?service=quay.io&scope=repository:$IMAGE_REPOSITORY:pull"

  token="$(curl --fail --silent --show-error --location --max-time 30 "$endpoint" | jq -r '.token // .access_token // empty')"
  [[ -n "$token" ]] || return 1
  curl --fail --silent --show-error --location --max-time 30 \
    -H "Authorization: Bearer $token" \
    -H "Accept: $ACCEPT_HEADER" \
    -D "$headers" \
    --output "$output" \
    "$REGISTRY_BASE/v2/$IMAGE_REPOSITORY/manifests/$digest"
  unset token
  jq -e 'type == "object" and (.schemaVersion == 2) and (.config.size | type == "number") and (.layers | type == "array")' "$output" >/dev/null
}

if jq -e '(.manifests | type) == "array"' "$INDEX_FILE" >/dev/null 2>&1; then
  for architecture in amd64 arm64; do
    platform_digest="$(jq -r --arg arch "$architecture" '.manifests[] | select(.platform.os == "linux" and .platform.architecture == $arch) | .digest' "$INDEX_FILE" | head -n 1)"
    [[ "$platform_digest" =~ ^sha256:[a-f0-9]{64}$ ]] || continue
    if ! fetch_platform_manifest "$architecture" "$platform_digest"; then
      fail "PLATFORM_MANIFEST_FETCH_OR_VALIDATION_FAILED_$architecture"
    fi
    compressed_bytes="$(jq '[.config.size, (.layers[].size)] | add' "$ARTIFACT_DIR/manifest-$architecture.json")"
    if [[ "$architecture" == "amd64" ]]; then
      AMD64_DIGEST="$platform_digest"
      AMD64_COMPRESSED_BYTES="$compressed_bytes"
    else
      ARM64_DIGEST="$platform_digest"
      ARM64_COMPRESSED_BYTES="$compressed_bytes"
    fi
  done
else
  fail "TOP_LEVEL_MANIFEST_IS_NOT_MULTIARCH_INDEX"
fi

[[ "$AMD64_DIGEST" != "NOT_CAPTURED" ]] || fail "LINUX_AMD64_MANIFEST_NOT_FOUND"
STATUS="CAPTURED"
RESULT_CODE="OCI_MANIFEST_METADATA_CAPTURED_NO_IMAGE_PULL"
write_report

printf 'Image reference: %s\n' "$IMAGE_REFERENCE"
printf 'Top-level digest: %s\n' "$TOP_LEVEL_DIGEST"
printf 'Top-level media type: %s\n' "$TOP_LEVEL_MEDIA_TYPE"
printf 'linux/amd64 digest: %s (%s compressed descriptor bytes)\n' "$AMD64_DIGEST" "$AMD64_COMPRESSED_BYTES"
printf 'linux/arm64 digest: %s (%s compressed descriptor bytes)\n' "$ARM64_DIGEST" "$ARM64_COMPRESSED_BYTES"
echo "Image pull: false; image layers downloaded: false; Ceph started: false; Object Lock tested: false"
