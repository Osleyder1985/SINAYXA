# Ceph Image Registry Metadata Preflight

## Purpose

Capture the OCI registry metadata for the official Ceph Umbrella image without pulling image layers, installing software, starting containers, or deploying Ceph.

## Scope

- Image reference: `quay.io/ceph/ceph:v21.2.0`
- Registry: Quay OCI/Docker Registry HTTP API
- Platforms recorded when present: `linux/amd64` and `linux/arm64`
- Runner: GitHub-hosted `ubuntu-24.04`
- Trigger: manual `workflow_dispatch` only
- Permissions: `contents: read`
- Timeout: 5 minutes
- Artifact retention: 14 days

The script requests only the registry token and manifest documents. It does not download config blobs or image layers. The compressed byte count is calculated from manifest descriptors; it is not a measured pull size.

## Run

After this change is merged through the repository's normal review process:

1. Open **Actions**.
2. Select **Ceph image registry metadata preflight**.
3. Select **Run workflow** on the intended branch.
4. Download artifact `ceph-image-registry-metadata`.

The workflow is not scheduled and does not run on pushes or pull requests.

## Upstream release caution

Ceph v21.2.0 Umbrella was released on 2026-10-28. The release announcement identifies release commit `b060042deb05d33e6cc358970cfb8221240bcf3e`.

A Ceph-users discussion dated 2026-11-03 reports tracker issue 82496: Umbrella 21.2.0 shipped with `ceph_release` set to `dev`, causing cephadm to default to the `ceph-ci main` image. The advice in that discussion is to pass the explicit image reference during bootstrap:

```text
cephadm --image quay.io/ceph/ceph:v21.2.0 bootstrap ...
```

This preflight does not bootstrap Ceph. Any later execution proposal must explicitly pin the observed image digest (not rely on cephadm's inferred default), verify the upstream issue/fix status, and preserve the image manifest plus provenance evidence.

## Interpretation

A successful capture proves only that the registry returned syntactically valid manifest metadata for the requested tag at the recorded UTC time. It does not prove:

- signature or provenance validity;
- successful image pull or daemon startup;
- Ceph RGW Object Lock support or enforcement;
- COMPLIANCE-mode resistance to privileged deletion;
- persistence after restart;
- durability, replication, independent failure domains, or regulatory compliance.

A future tag resolution may differ. Preserve the top-level and platform manifest digests in every later test record.

## Safety invariants

`image_pull_performed=false`, `image_layers_downloaded=false`, `software_installed=false`, `containers_started=false`, and `object_lock_test_performed=false` are required report fields. The workflow has no secrets, no write permissions, no automatic trigger, and no production data.
