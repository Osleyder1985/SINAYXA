# PowerShell runtime and validation standard

**Status:** validation workflow and standard implemented on PR #45; integration into `main` pending  
**Standard runtime:** PowerShell 7.6.6  
**Static analyzer:** PSScriptAnalyzer 1.24.0  
**Execution platform:** GitHub-hosted Windows runner

## 1. Runtime policy

PowerShell 7.6.6 is the pinned runtime for project scripts and automated validation. The workflow installs and verifies the exact runtime instead of trusting the version preinstalled on the runner.

Windows PowerShell 5.1 is not a mandatory parallel target. Add compatibility testing only when a documented requirement or identified consumer needs it.

## 2. Source selection and provenance

Every validation run must analyze the exact source revision it claims to validate:

- `pull_request`: the PR head SHA, not a fixed branch and not an unrelated checkout.
- `push`: the pushed commit SHA.
- `workflow_dispatch`: the explicitly selected branch, tag, or commit.

The job records the source SHA, workflow SHA, event, runtime, analyzer version, fixture path, fixture SHA-256, and run ID. A successful workflow definition without a completed successful run is not evidence.

## 3. Automated controls

The workflow:

- Inventories tracked `.ps1` and `.psm1` files using Git, fails if the inventory is empty, and uploads the inventory.
- Parses every inventoried PowerShell source file with the PowerShell language parser.
- Runs PSScriptAnalyzer 1.24.0 on every inventoried source file.
- Fails on any analyzer finding. Findings must be corrected; an exception requires a narrowly scoped written rationale and review, never a global suppression.
- Validates the versioned synthetic intensity/horizon fixture v1.2.0.
- Runs a positive control, twelve negative mutation cases, and robustness checks for missing and malformed fixture files.
- Validates the Issue #15 E01–E18 synthetic evidence-standard fixture and runs its positive/negative mutation harness.
- Validates the Issue #17 A01–A15 synthetic alert fixture and runs positive, negative, and robustness tests (missing/malformed files); the fixture remains explicitly unapproved and is not an alert engine.
- Tests selected PSScriptAnalyzer security rules with synthetic snippets.
- Uploads machine-readable findings and provenance evidence as a GitHub Actions artifact.

PSScriptAnalyzer includes useful security-oriented rules, but it is not a complete security audit, dependency scanner, secret scanner, or runtime sandbox. Those controls must be evaluated separately before claiming comprehensive security coverage.

## 4. Test boundaries

A PASS proves only that the selected tracked PowerShell source passed the listed static checks and that the synthetic fixture validators behaved as expected for the tested inputs under PowerShell 7.6.6 on a GitHub-hosted Windows runner.

It does **not** prove that methodological cases T01–T19 were formally executed, that E01–E18 establish real-world truth or legal compliance, that synthetic expectations are empirically valid, or that any causal conclusion has been established.

The current repository contains a small PowerShell surface. Coverage is reported as an absolute file inventory and count; no claim of broad application coverage is made where only a few PowerShell files exist.

## 5. Security-rule regression tests

In addition to analyzing project scripts, CI runs controlled, synthetic snippets to verify that PSScriptAnalyzer 1.24.0 detects selected security patterns:

- Plain-text password parameters: `PSAvoidUsingPlainTextForPassword`.
- Dynamic expression execution: `PSAvoidUsingInvokeExpression`.
- Plain-text input to `ConvertTo-SecureString`: `PSAvoidUsingConvertToSecureStringWithPlainText`.
- Hardcoded remote computer names: `PSAvoidUsingComputerNameHardcoded`.

The harness requires every expected rule to fire and verifies temporary test-directory cleanup. These snippets are deliberately synthetic and are analyzed statically, not executed.

This demonstrates that selected security rules are active in the pinned analyzer version. It does not establish complete detection of all credential leaks, malicious code, unsafe dependencies, runtime behavior, or supply-chain compromise. Independent secret scanning and dependency/security review remain separate controls.

## 6. Independent secret and dependency controls

The separate `.github/workflows/security-quality.yml` workflow adds:

- Gitleaks Action v3.0.0 and CLI 8.24.3, pinned to immutable versions; scans PR history and full repository history on PRs, with scheduled full-history scans after workflow integration into `main`.
- A synthetic canary matched by a dedicated test rule in a temporary Git repository; CI requires the exact rule and expected leak-detected exit code, then deletes the temporary repository.
- `npm ci --ignore-scripts` against the committed lockfile.
- `npm audit --audit-level=high` across the locked dependency graph; high and critical vulnerabilities fail the check.
- OSV-Scanner v2.7.0 on every pull request, failing when the PR introduces a known vulnerability.
- Full OSV-Scanner scans on pushes to `main` and weekly schedules.
- A 90-day JSON audit artifact for traceability.
- Weekly Dependabot update PRs for npm dependencies and GitHub Actions.

The workflow uses read-only repository permissions where possible and disables Gitleaks PR comments. It does not intentionally print or upload secret values.

These controls complement rather than replace GitHub-native secret scanning and Dependabot alerts. The GitHub Dependency Review action was not used because the repository dependency graph is disabled; OSV-Scanner and npm audit inspect the committed lockfile dependency graph without requiring that setting. GitHub-native Dependabot alerts and dependency graph should still be enabled separately if desired.

## 7. Main branch protection

The persisted GitHub ruleset is `protect-main` (ID `27316946`), Active, targeting `refs/heads/main`, with no bypass actors. Its exact required status contexts are:

- `PowerShell 7.6.6 / Windows`
- `Secret scanning / Gitleaks`
- `OSV dependency scan / PR / osv-scan`

`Dependency audit / npm` is an additional successful CI check, not a required context in the active ruleset. The ruleset requires strict up-to-date checks, pull requests, linear history, and review-thread resolution; it requires zero approving reviews for the single-human maintainer model. A controlled negative required-check enforcement test remains pending until after workflow integration.

## 8. Integration governance

The validation workflows and supporting tests are present on PR #45 and have passed on its current HEAD. They are not yet integrated into `main`; the persisted branch ruleset is already active. Green bootstrap checks do not approve the methodology or authorize a merge. After the owner decides to integrate the PR, the workflows will run from `main`; a disposable negative test must then demonstrate that a failed required context blocks integration.

## 9. Local execution policy

GitHub Actions is the standard validation path. The project owner is not required to install PowerShell or run routine validation commands on a personal computer.
