# PowerShell runtime and validation standard

**Status:** implemented in `main`; this document reflects the repository workflows inspected on 2026-11-18.  
**PowerShell runtime:** 7.7.0 (downloaded and version-checked by CI)  
**Static analyzer:** PSScriptAnalyzer 1.24.0  
**Execution platform:** GitHub-hosted Windows runner

## 1. Runtime policy

The current `.github/workflows/powershell-validation.yml` workflow installs PowerShell 7.7.0 from the official GitHub release archive, verifies the archive against its declared SHA-256 value, expands it into the runner's temporary directory, and checks that the executable reports exactly 7.7.0. CI does not rely on the runner's preinstalled PowerShell version.

PSScriptAnalyzer is installed at version 1.24.0 and imported with that required version.

Windows PowerShell 5.1 is not a mandatory parallel target. Add compatibility testing only when a documented requirement or identified consumer needs it.

## 2. Source selection and provenance

The workflow checks out the workflow revision and the exact source revision separately. For a pull request, the source checkout uses the PR head SHA; for a manual run, it uses the explicitly selected `target_ref`; for a push, it uses the triggering commit.

A successful workflow definition without a completed successful run for the exact source SHA is not evidence. When reporting a result, record the workflow run ID, source SHA, workflow SHA, event, runtime, analyzer version, and the relevant uploaded evidence artifact.

## 3. Automated PowerShell controls

The current workflow:

- Inventories tracked `.ps1` and `.psm1` files using Git and fails if the inventory is empty.
- Parses every inventoried PowerShell source file with the PowerShell language parser.
- Runs PSScriptAnalyzer 1.24.0 against every inventoried source file and enforces zero findings.
- Runs the repository's synthetic methodology fixture validators and their positive, negative, and robustness cases where included in the workflow path filters.
- Tests selected PSScriptAnalyzer security rules using synthetic snippets.
- Preserves machine-readable findings and provenance evidence as workflow artifacts.

PSScriptAnalyzer includes useful security-oriented rules, but it is not a complete security audit, dependency scanner, secret scanner, or runtime sandbox. Those controls are separate.

## 4. Test boundaries

A PASS proves only that the exact selected tracked PowerShell source passed the listed static checks and that the synthetic fixture validators behaved as expected for the tested inputs under PowerShell 7.7.0 on a GitHub-hosted Windows runner.

It does **not** prove that methodological cases were validated against real-world data, that synthetic expectations are empirically valid, that sources are independent in reality, that evidence establishes factual truth or legal compliance, or that any causal conclusion has been established.

The current repository contains a limited PowerShell surface. Coverage must be reported as the actual tracked-file inventory and count; do not imply broad application coverage where only a small number of scripts exist.

## 5. Security-rule regression tests

The workflow tests selected PSScriptAnalyzer rules with synthetic snippets, including:

- Plain-text password parameters: `PSAvoidUsingPlainTextForPassword`.
- Dynamic expression execution: `PSAvoidUsingInvokeExpression`.
- Plain-text input to `ConvertTo-SecureString`: `PSAvoidUsingConvertToSecureStringWithPlainText`.
- Hardcoded remote computer names: `PSAvoidUsingComputerNameHardcoded`.

These tests demonstrate that selected rules are active in the pinned analyzer version. They do not establish complete detection of credential leaks, malicious code, unsafe dependencies, runtime behavior, or supply-chain compromise.

## 6. Independent secret and dependency controls

The current `.github/workflows/security-quality.yml` workflow provides separate controls:

- Gitleaks CLI 8.30.1 is downloaded from its official release and checked against a pinned SHA-256 digest before execution.
- A synthetic canary is tested against a dedicated temporary Gitleaks rule; CI requires the expected leak-detected exit code and rule ID.
- The full Git history is scanned for secrets; redacted scan evidence is uploaded with 90-day retention.
- `npm ci --ignore-scripts` installs the committed lockfile dependency graph.
- `npm audit --audit-level=high` checks direct and transitive npm dependencies; high and critical findings fail the job.
- OSV-Scanner PR scanning uses the reusable workflow pinned to commit `d3c1414ded37de590f207572e37a7d180f1d0ef7` (v2.7.1) and fails on introduced vulnerabilities.
- Full OSV scanning runs on pushes to `main`, scheduled runs, and manual dispatches; it is intentionally skipped for pull-request events.

A skipped full-history OSV job on a pull request is **not** a PASS. Report the PR OSV scan and the full OSV scan separately.

The workflow uses read-only repository permissions where possible and disables credential persistence for checkout. These controls complement rather than replace GitHub-native secret scanning and Dependabot alerts.

## 7. Runtime and dependency pinning boundaries

- PowerShell is pinned to exact version 7.7.0 and its release archive is verified by SHA-256.
- PSScriptAnalyzer is pinned to 1.24.0.
- Gitleaks CLI is pinned to 8.30.1 and its archive digest is verified.
- Node.js is currently constrained by `package.json` to `>=22`; the security workflow checks only that the major version is at least 22. The npm lockfile pins package dependencies, not the Node.js or npm runtime. Therefore the Node/npm runtime is **not fully pinned**.
- Python contract validation currently requests Python 3.12, not an exact patch release. The Python package requirements are version-pinned, but the interpreter patch is **not fully pinned**.
- The PostgreSQL event-registry workflow uses PostgreSQL 18.7 through an immutable image digest. The backup/restore lab separately pins Docker Engine/CLI 29.10.0 and resolves the PostgreSQL image digest before running the container.

Do not describe a runtime as fully reproducible unless its exact runtime version and relevant artifact identity are recorded for the run.

## 8. Branch protection and integration governance

Branch-protection requirements must be read from the currently active GitHub ruleset and compared with the actual status-check names emitted by the workflows. Do not rely on this document as a substitute for a live ruleset inspection, and do not preserve stale required-context names after a workflow job is renamed.

A green CI run does not by itself approve methodology, prove operational readiness, or authorize external services, costs, production data, or deployment. PR integration must follow the repository's current review, required-check, and issue-governance rules.

## 9. Local execution policy

GitHub Actions is the standard validation path. The project owner is not required to install PowerShell or run routine validation commands on a personal computer. Local execution may be used for diagnosis or development, but its results must identify the local OS, runtime, tool versions, and exact source revision.

## 10. Change history and scope

This document was reconciled against the current PowerShell and security workflow definitions on 2026-11-18. It supersedes older references in this file to PowerShell 7.6.6, Gitleaks 8.24.3, OSV-Scanner v2.7.0, and a pending integration of the validation workflows. Those older statements no longer describe the inspected repository state.

This update documents existing configuration; it does not change runtime versions, branch protection, dependency versions, or security policy.
