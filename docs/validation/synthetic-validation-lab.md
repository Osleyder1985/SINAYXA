# Issue #93 — Synthetic validation lab

This first laboratory stage is limited to the local filesystem. It uses generated synthetic records and a temporary directory. It does not connect to the network, start services, install packages, access credentials, or touch production data.

## Requirements

- PowerShell 7.6.6.
- No PowerShell modules or external dependencies.

## Run

From the repository root:

```powershell
pwsh -NoLogo -NoProfile -File .\scripts\validation\Invoke-SyntheticValidationLab.ps1
```

To retain the temporary evidence directory:

```powershell
pwsh -NoLogo -NoProfile -File .\scripts\validation\Invoke-SyntheticValidationLab.ps1 -KeepArtifacts
```

To reproduce the same synthetic record contents:

```powershell
pwsh -NoLogo -NoProfile -File .\scripts\validation\Invoke-SyntheticValidationLab.ps1 -Seed 20261116
```

The command emits one compact JSON report and returns a non-zero exit code on failure.

## Checks

- Deterministic synthetic dataset generation.
- SHA-256 and byte-size manifest.
- Export and restore integrity.
- Detection of an intentional payload mutation.
- Deletion reconciliation across the dataset, export payload, and restored payload.

## Evidence and limitations

A PASS proves only the filesystem workflow in the isolated temporary directory. It does not prove PostgreSQL backup/restore, physical WORM/Object Lock, secure media erasure, provider-side backup deletion, external snapshots, or production migration. Those require separate environment-specific validation.

By default the temporary directory is removed after the report is generated. Use -KeepArtifacts only when inspection of synthetic artifacts is needed.
