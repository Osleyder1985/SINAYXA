# Main branch protection policy

**Target:** `refs/heads/main`  
**Persisted ruleset:** `protect-main` (GitHub ruleset ID `27316946`)  
**Enforcement:** Active  
**Bypass actors:** None  
**Required approving reviews:** 0 (single-human maintainer model)

## 1. Effective GitHub controls

The persisted ruleset was read back from the GitHub Rulesets API on 2026-11-15. Its effective configuration is:

- Pull requests required for changes to `main`.
- Branch deletion prohibited.
- Force pushes prohibited (`non_fast_forward` rule).
- Linear history required.
- Review conversations must be resolved before merge.
- Stale approvals are dismissed when the PR is updated.
- No bypass actors are configured; the current user has no bypass.
- Strict required status checks; the PR branch must be up to date with its base.
- Zero required approving reviews. This repository has one human maintainer; this avoids an impossible second-human approval requirement. It does not waive PR review, evidence checks, conversation resolution, or the owner's integration decision.

### Required status checks

The ruleset requires exactly these GitHub Actions contexts (integration ID `15368`):

1. `PowerShell 7.6.6 / Windows`
2. `Secret scanning / Gitleaks`
3. `OSV dependency scan / PR / osv-scan`

`Dependency audit / npm` is an additional successful CI control, but it is **not** a required context in the persisted ruleset. Do not describe it as a merge-blocking required check unless the GitHub ruleset is changed and read back.

## 2. Machine-readable specification

`main-branch-ruleset.json` records the persisted policy, including the ruleset name, target, exact required contexts, integration IDs, zero bypass actors, and review parameters. It is a repository snapshot/specification; the GitHub API read-back is the source of truth for effective enforcement.

## 3. Verification evidence and remaining tests

On 2026-11-15, ruleset ID `27316946` was read directly from GitHub and confirmed Active with no bypass actors. The required three contexts completed successfully on PR #45 HEAD `f0e8048f2e553f116035b9225d09ade14e01bb08`; the additional npm audit also succeeded.

The following enforcement checks remain operational follow-ups and must not be reported as completed:

- A controlled negative test using a deliberately failing required check has not yet been executed. Perform it after the workflow definitions are integrated into `main`, using a disposable test PR and without weakening or bypassing the ruleset.
- The first scheduled full-history/security scan after workflow integration remains pending.

The repository connection used for this change can read rulesets but does not expose a ruleset write operation. No ruleset mutation is performed by this PR.

## 4. Integration sequence

1. Review and decide on PR #45; do not treat green CI as methodological approval.
2. After the workflows are legitimately integrated into `main`, verify their normal push/schedule executions.
3. Run the controlled negative enforcement test on a disposable PR and confirm GitHub blocks integration when a required context fails.
4. Record the test result and exact run/PR references. Do not claim the enforcement test passed before observing the blocked result.

The Issue #14 proposal, Issue #15 evidence standard, and empirical validation remain separate owner decisions. This branch-protection policy does not approve either methodology.
