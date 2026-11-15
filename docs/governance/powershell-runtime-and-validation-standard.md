# PowerShell runtime and validation standard

**Status:** implemented in a reviewable branch; integration into `main` pending  
**Standard runtime:** PowerShell 7.6.6 LTS  
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
- Validates the versioned synthetic fixture v1.2.0.
- Runs a positive control, twelve negative mutation cases, and robustness checks for missing and malformed fixture files.
- Uploads machine-readable findings and provenance evidence as a GitHub Actions artifact.

PSScriptAnalyzer includes useful security-oriented rules, but it is not a complete security audit, dependency scanner, secret scanner, or runtime sandbox. Those controls must be evaluated separately before claiming comprehensive security coverage.

## 4. Test boundaries

A PASS proves only that the selected tracked PowerShell source passed the listed static checks and that the synthetic fixture validator behaved as expected for the tested inputs under PowerShell 7.6.6 on a GitHub-hosted Windows runner.

It does **not** prove that methodological cases T01–T19 were formally executed, that synthetic expectations are empirically valid, or that any causal conclusion has been established.

The current repository contains a small PowerShell surface. Coverage is reported as an absolute file inventory and count; no claim of broad application coverage is made where only a few PowerShell files exist.


## 4. Security-rule regression tests

In addition to analyzing production scripts, CI runs controlled, synthetic snippets to verify that PSScriptAnalyzer 1.24.0 actually detects these security patterns:

- Plain-text password parameters: `PSAvoidUsingPlainTextForPassword`.
- Dynamic expression execution: `PSAvoidUsingInvokeExpression`.
- Plain-text input to `ConvertTo-SecureString`: `PSAvoidUsingConvertToSecureStringWithPlainText`.
- Hardcoded remote computer names: `PSAvoidUsingComputerNameHardcoded`.

The test harness requires every expected rule to fire and verifies temporary test-directory cleanup. These snippets are deliberately synthetic and are not executed; they are analyzed statically.

This demonstrates that selected security rules are active in the pinned analyzer version. It does not establish complete detection of all credential leaks, malicious code, unsafe dependencies, runtime behavior, or supply-chain compromise. Independent secret scanning and dependency/security review remain separate controls.

## 5. Integration governance

The workflow must be merged into `main` before it can act as the normal pull-request workflow. A repository ruleset must then require the successful check for protected integration. The presence of a workflow or a green bootstrap run does not itself make the check mandatory.

## 6. Local execution policy

GitHub Actions is the standard validation path. The project owner is not required to install PowerShell or run routine validation commands on a personal computer.
