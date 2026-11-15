# Main branch protection policy

**Target:** `refs/heads/main`  
**Desired enforcement:** Active  
**Bypass actors:** None  
**Application status:** Specification committed; GitHub repository setting not yet applied

## Required controls

The machine-readable specification is `main-branch-ruleset.json`. It defines:

- Pull requests required for all changes to `main`.
- No configured bypass actors.
- Deletion and force-push protection.
- Linear history.
- Conversation resolution before merge.
- Strict required status checks, including:
  - `PowerShell 7.6.6 / Windows`
  - `Secret scanning / Gitleaks`
  - `Dependency audit / npm`
  - `Dependency review`
- Zero required approving reviews. This repository has one human maintainer; requiring an approval from a second person would make the normal workflow impossible. This does not remove the requirement to use a PR or resolve review threads.

## Application and verification

The GitHub connector available to this work session can read repository rulesets, but it does not expose a ruleset creation/update operation. Its installation also cannot read the classic branch-protection endpoint (HTTP 403). Therefore, committing the JSON is **not** equivalent to activating protection.

A repository administrator must create the ruleset in GitHub:

1. Open **Settings → Rules → Rulesets → New branch ruleset**.
2. Name it `main-protection`; target branch `main`; enforcement `Active`.
3. Add the rules and required status checks exactly as listed in the JSON.
4. Leave the bypass list empty.
5. Save the ruleset.

Then verify the persisted policy through the GitHub rulesets API or repository settings and test a PR with a deliberately failing check to confirm merging is blocked. Do not claim the governance gap closed until both configuration and enforcement are demonstrated.

## Operational note

The ruleset can only require checks that have completed at least once on a pull request targeting `main`. The security workflows introduced with this policy must first complete successfully on PR #45 so their exact check names are available for selection.
