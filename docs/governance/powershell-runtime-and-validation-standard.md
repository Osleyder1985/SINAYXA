# PowerShell runtime and validation standard

**Status:** approved project runtime decision; automation implementation pending CI evidence  
**Standard runtime:** PowerShell 7.6.6 LTS  
**Execution platform:** GitHub-hosted Windows runner

## 1. Runtime policy

PowerShell 7.6.6 is the pinned runtime for project scripts and automated validation. A workflow must verify the exact version rather than relying on whichever PowerShell version happens to be preinstalled on a hosted runner.

Windows PowerShell 5.1 is not a mandatory parallel target. Add compatibility testing only when a documented requirement or an identified consumer needs it.

## 2. Automated controls

The GitHub Actions workflow `.github/workflows/powershell-validation.yml` is responsible for:

- Installing and verifying PowerShell 7.6.6.
- Parsing every tracked PowerShell source file (`.ps1` and `.psm1`) with the PowerShell language parser.
- Running PSScriptAnalyzer 1.24.0 recursively across the repository's PowerShell source files.
- Blocking on analyzer findings with severity `Error`; non-error findings remain visible for review and are not silently treated as blockers.
- Validating the versioned synthetic fixture, including schema, ordered unique case IDs, required fields, timestamp offsets, elapsed-time arithmetic, and versioned semantic contracts.
- Running a positive control and ten negative mutation tests, including duplicate IDs, malformed date-only input, invalid timezone offsets, and daylight-saving elapsed-time inconsistencies.
- Keeping test artifacts isolated in a unique temporary directory and removing them in a `finally` block.
- Recording the exact source commit and fixture SHA-256 in the job log.

The current validator harness is a project-specific PowerShell test script. Pester is not added as a dependency until the repository contains Pester-native test suites that benefit from it. Static analysis findings with severity `Error` block the job; non-error findings remain visible for triage and are not silently promoted to blockers. The validation scripts use the information stream for console reporting and avoid assignment to PowerShell automatic variables so that analyzer findings are actionable rather than dominated by avoidable style warnings.

## 3. Triggers

The workflow supports:

- A bootstrap push on its dedicated CI branch, which exercises the current Issue #41 validator branch.
- Pull requests targeting `main` that modify PowerShell scripts, the intensity/horizons fixtures, or this workflow.
- Manual dispatch with an explicit branch or commit to validate.

The workflow file must first be integrated into the default branch before it can serve as the normal pull-request gate for subsequent work. The bootstrap push runs the Issue #41 validator branch before that integration decision, providing an initial real Windows-runner result.

## 4. Evidence and interpretation

A successful job proves only that the selected scripts passed the stated static and deterministic synthetic-fixture checks under PowerShell 7.6.6 on a GitHub-hosted Windows runner.

It does **not** mean that methodological cases T01–T19 have been formally executed, that synthetic expectations are empirically valid, or that any causal market conclusion has been established.

Every reported PASS must identify the workflow run, source commit, runtime version, fixture version and SHA-256. A workflow definition without a completed successful run is not validation evidence.

## 5. Local execution policy

The standard validation path is GitHub Actions. The project owner is not required to install PowerShell, run scripts, or reproduce CI commands on a personal computer for routine acceptance evidence.
