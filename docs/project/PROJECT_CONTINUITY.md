# SINAYXA — Project Continuity Record

> **Record type:** initial continuity baseline; not a substitute for the full technical audit.
> **Snapshot date:** 2026-11-17 (UTC)
> **Repository:** [SINAYXA](https://github.com/Osleyder1985/SINAYXA)
> **Default branch:** `main`
> **Snapshot source:** GitHub repository metadata, Git refs, open PR list, open Issue list, and PR descriptions retrieved on 2026-11-17.
> **Integrity rule:** a claim is considered verified only for the exact commit/run cited. A successful historical run does not validate a later HEAD.

## 1. Repository identity and protected baseline

- Repository: `Osleyder1985/SINAYXA` (public; not archived).
- Default branch: `main`.
- Main HEAD at snapshot: `75583efab8be33a3739e3409ae54690ebc02d62b`.
- Latest main commit: `Document neutral validation environment ADR` (2026-11-17T02:17:31Z).
- Previous main commit: `3e6c764ed8fb72d190351aa99ebb856f5933e2d3` — preserve source evidence artifacts and block registry truncation.
- Main was not modified while creating this record. This document is being prepared on a separate branch.
- Repository metadata reported 36 open items in total: 7 open pull requests and 29 open Issues.

## 2. Open Pull Requests at snapshot

The following list is the exact open-PR inventory returned by GitHub at snapshot time. “Base” is the target branch. Stacked PRs are explicitly identified; their dependencies must be resolved before integration.

| PR | Purpose | State | Head branch / SHA | Base |
| --- | --- | --- | --- | --- |
| [#117](https://github.com/Osleyder1985/SINAYXA/pull/117) | Remove vulnerable picomatch from Markdown lint dependency tree without weakening npm audit | OPEN, ready | `fix/issue-116-markdownlint-without-globbing-dependency` / `67b1db9e9b31f4a2bd36bb9eeadece2d8ce8b85a` | `main` |
| [#115](https://github.com/Osleyder1985/SINAYXA/pull/115) | Reconcile deletion dispositions before exposing restored PostgreSQL backups | OPEN, DRAFT | `feature/issue-113-postgresql-restore-reconciliation-v2` / `e61257a37d355818f093a5ccea605e1b02e7de34` | #96 branch |
| [#100](https://github.com/Osleyder1985/SINAYXA/pull/100) | Capture and verify official AIStor metadata without deploying software | OPEN, ready | `feature/issue-100-aistor-metadata-preflight` / `f78ed629ce3e007aa68a0062c5dc2f9cf6a4fee0` | `main` |
| [#99](https://github.com/Osleyder1985/SINAYXA/pull/99) | Contract 0.2.2 and audit minimization (RET-09) | OPEN, DRAFT | `feature/issue-98-contract-0.2.2-on-0.2.1` / `923d89f4823607a327b2ea0f8e08db298da6bf60` | #85 branch |
| [#96](https://github.com/Osleyder1985/SINAYXA/pull/96) | Synthetic PostgreSQL backup/restore validation lab | OPEN, ready | `feature/issue-95-postgresql-backup-restore-lab` / `c68011d384942a7d1f0fa1de836b623899703616` | `main` |
| [#94](https://github.com/Osleyder1985/SINAYXA/pull/94) | Local synthetic validation lab | OPEN, ready | `feature/issue-93-synthetic-validation-lab` / `74966d25dec23b5012954543deb5b994bfee0552` | `main` |
| [#85](https://github.com/Osleyder1985/SINAYXA/pull/85) | Logical evidence and provenance contract v0.2.1 | OPEN, ready | `feature/issue-78-contract-v0.2.0` / `521745d1a3edd88046e646fcc6cea154909bbb20` | `main` |

### 2.1 Dependencies and review cautions

- **#115 depends on #96:** it targets the PostgreSQL lab branch, not `main`. Do not merge it before the base PR is integrated and the dependent branch is retargeted/revalidated.
- **#99 depends on #85:** it targets the contract 0.2.1 branch. Do not merge it before #85 is integrated and #99 is rebased/retargeted and revalidated.
- **#85 and #117:** their PR descriptions report successful CI runs, but the currently observed PR HEAD SHAs differ from some SHAs cited in their evidence narratives. Reconfirm required checks on the exact current HEAD before treating them as merge-ready.
- **#94, #96, #100:** PR descriptions contain detailed test/preflight evidence and explicit limitations. Verify the exact current HEAD and all required checks, not only historical runs.
- No PR is considered approved for merge merely because its state is “ready” or its description says “SUCCESS”. Human review, scope completion, branch freshness, resolved review threads, and exact-HEAD checks remain required.

## 3. Open Issues at snapshot

GitHub returned 29 open Issues (excluding PRs):

`#116, #113, #98, #97, #95, #93, #89, #88, #78, #46, #27, #26, #25, #24, #20, #19, #18, #17, #14, #12, #11, #10, #9, #8, #7, #6, #5, #4, #3`.

Priority/dependency clusters visible from their titles and linked PRs:

- **Source evidence / provenance:** #78, #88, #89; implementation #85; follow-on #97/#98 and PR #99.
- **Synthetic validation and deletion reconciliation:** #93/#94, #95/#96, #113/#115; external/production evidence remains separately tracked in #89 and #88.
- **AIStor metadata preflight:** #100; the PR body explicitly leaves the overall state BLOCKED pending additional digest, Windows artifact integrity, and license/use evidence.
- **Security dependency remediation:** #116/#117.
- **News and events requirements / decisions:** #3–#27, including leak/indicia detection (#3), source credibility (#4), impact direction/intensity/horizon (#5/#14), alerts (#8/#17), monitoring latency (#7/#18), expectations (#9/#24), observed reaction (#10/#20), catalyst lifecycle (#11/#25), combined events (#12/#26), and requirements index/scope (#27).
- **PowerShell validation quality:** #46.

This list is an inventory, not a claim that all Issues have complete acceptance criteria or are ready for implementation. Each Issue must be fetched and checked for latest decisions, comments, and closure evidence during the full audit.

## 4. Verified repository structure on main

The recursive Git tree for main at the snapshot included (among other files):

- `.github/workflows/event-registry-validation.yml`
- `.github/workflows/powershell-validation.yml`
- `.github/workflows/security-quality.yml`
- `database/migrations/0001_event_registry.sql` through `0005_append_only_truncate_guard.sql`
- `docs/architecture/adr/0001-validation-environment-options.md`
- Governance documents under `docs/governance/`
- News/event specifications, test records, and evidence standards under `docs/news-and-events/`
- `package.json` and `package-lock.json`

Existing governance and technical documentation should be reused and cross-linked. Do not create duplicate policy documents where a maintained source of truth already exists.

## 5. Project decisions and constraints to preserve

The following are continuity constraints already established in project discussions and/or repository records. Verify their current canonical document/Issue during the full audit:

1. Do not modify `main` directly. Work on a task-specific branch and use a PR.
2. Do not merge a PR without exact-HEAD evidence, complete scope, and review of unresolved comments/threads.
3. Do not treat CI “SKIPPED” as “PASS”.
4. Distinguish synthetic validation from operational/production evidence.
5. Do not claim external deletion, immutable storage, WORM/Object Lock, archival durability, or production migration based only on synthetic filesystem/PostgreSQL tests.
6. Preserve historical evidence and event records; do not silently overwrite or truncate them.
7. Maintain traceability from requirement → Issue → implementation → tests → CI evidence → review/decision.
8. Distinguish temporal association from demonstrated causality; preserve alternative explanations and uncertainty.
9. Do not activate source monitoring/capture or external services without the applicable source-use and authorization review.
10. Keep repository file/directory names in English; project explanations and Issues/PR descriptions are generally in Spanish, preserving technical terms.

## 6. Local development environment — last known checkpoint, not reverified

A prior local validation checkpoint reported:

- Windows PowerShell development environment.
- Python 3.15.2 selected as the validation target; Python 3.12.10 retained until compatibility is demonstrated.
- In worktree `C:\Proyecto\SINAYXA-PR85`, Python 3.15.2 virtual environment and dependencies were reported installed; `pip check` passed.
- Functional tests and final PR #85 evaluation were still pending at that checkpoint; `pytest` was reported unavailable.
- Earlier local work also used `C:\Proyecto\SINAYXA` and a separate Issue #35 branch.

**Important:** this is historical user-reported workstation state. The current local filesystem, active branch, uncommitted changes, installed tools, and exact PR #85 worktree HEAD have not been inspected in this snapshot. Do not assume they are clean or synchronized with GitHub.

## 7. Required continuation audit

The baseline is not yet a “safe to delete chats” certificate. Complete these tasks before deleting project conversations:

- [ ] Fetch all 7 PRs individually, including full bodies, diffs, changed files, commits, reviews, review threads, comments, mergeability, and exact-head checks.
- [ ] Inspect all 29 open Issues, their comments, cross-links, decisions, acceptance criteria, and dependencies.
- [ ] Inspect merged/closed PRs and Issues for durable decisions not reflected in current docs.
- [ ] Inspect canonical governance, ADRs, schemas, migration history, validation scripts, fixtures, and workflow definitions.
- [ ] Reconcile the local Windows worktrees and uncommitted changes when the workstation is available.
- [ ] Record exact test commands, versions, outcomes, CI run IDs, artifacts, and known limitations.
- [ ] Create or update the canonical requirements/decision/PR traceability index without duplicating existing sources.
- [ ] Run Markdown lint and relevant project validation against this documentation branch.
- [ ] Open a PR for the continuity package; do not merge automatically.
- [ ] Verify that a new chat can resume from this record plus repository links without needing deleted chat history.

## 8. Chat deletion gate

**Current decision: DO NOT DELETE PROJECT CHATS YET.**

Chats may be considered safe to delete only after:

- all material decisions and constraints have canonical repository references;
- all active PR and Issue states/dependencies are current;
- local-only work and uncommitted changes have been reconciled;
- test and CI evidence is traceable and exact-HEAD scoped;
- the continuity PR is reviewed and merged (or its durable location is otherwise explicitly established);
- a fresh-session recovery test successfully reconstructs the next task.

## 9. Next action

Continue the full audit of the seven open PRs, starting with #85 because #99 depends on it, then #96 because #115 depends on it. In parallel, audit the mainline PRs #117, #94, and #100. Preserve all current branches and do not merge or close anything during the audit.

## 10. PR audit — exact HEAD check-runs and review state

The following was retrieved from GitHub's commit check-runs API for each currently observed PR head. A skipped job is not a pass. Review states are comments unless explicitly stated otherwise.

| PR | Exact-head CI result | Review state | Audit conclusion |
| --- | --- | --- | --- |
| #85 | PowerShell 7.6.6 PASS; PowerShell 7.7.0 PASS; PostgreSQL event registry PASS; Gitleaks PASS; OSV PR PASS; npm audit FAIL; OSV full SKIPPED. Run [#44202513299](https://github.com/Osleyder1985/SINAYXA/actions/runs/44202513299). | 3 COMMENT reviews; no APPROVE; no inline threads returned. | Blocked by the same picomatch advisory tracked in #116. Its five areas A–E also remain open in #88/#89. |
| #94 | PowerShell 7.6.6 PASS; PowerShell 7.7.0 PASS; event registry PASS; Gitleaks PASS; npm audit PASS; OSV PR PASS; OSV full SKIPPED. Runs [#44013758761](https://github.com/Osleyder1985/SINAYXA/actions/runs/44013758761) and [run #44013759030](https://github.com/Osleyder1985/SINAYXA/actions/runs/44013759030). | 4 COMMENT reviews; no APPROVE; no inline threads returned. | CI supports the filesystem-only synthetic lab. It does not prove PostgreSQL, physical erasure, external copies, WORM/Object Lock, or production migration. |
| #96 | PowerShell 7.6.6 PASS; PowerShell 7.7.0 PASS; PostgreSQL 18.7 lab PASS; Gitleaks PASS; OSV PR PASS; npm audit FAIL; OSV full SKIPPED. Run [#44188987821](https://github.com/Osleyder1985/SINAYXA/actions/runs/44188987821). | 3 COMMENT reviews; no APPROVE; no inline threads returned. | Lab scope passes, but security gate fails due to five HIGH picomatch findings. Must be revalidated after #117 is integrated. |
| #99 | PowerShell 7.6.6/7.7.0 checks PASS; Gitleaks PASS; npm audit PASS; OSV PR PASS; OSV full SKIPPED in the returned checks. | 4 COMMENT reviews; no APPROVE; no inline threads returned. | Remains DRAFT and stacked on #85. The synthetic contract/migration does not close human semantic mapping, operational retention, external immutability, or deletion evidence. Revalidate after base integration. |
| #100 | AIStor metadata preflight PASS; PowerShell 7.6.6/7.7.0 PASS; Gitleaks PASS; OSV PR PASS; npm audit FAIL; OSV full SKIPPED. Run [#44190081816](https://github.com/Osleyder1985/SINAYXA/actions/runs/44190081816). | 1 COMMENT review; no APPROVE; no inline threads returned. | Metadata/digests/sidecars are captured, but executable signatures have not been cryptographically verified against trusted keys, checksums have not been compared to downloaded binaries, and license/use review remains pending. Security gate also fails. Overall deployment/use remains BLOCKED. |
| #115 | PostgreSQL 18.7 / Docker 29.10.0 adversarial fixture and lab PASS. Run [#44201807263](https://github.com/Osleyder1985/SINAYXA/actions/runs/44201807263). No security/dependency workflow is present in the returned exact-head checks. | No reviews returned; no inline threads returned. | DRAFT, stacked on #96. Its lab passes, but the security gate is not evidenced for this head and the base PR has a failing npm audit. Keep blocked. |
| #117 | PowerShell 7.6.6/7.7.0 PASS; event registry PASS; Gitleaks PASS; npm audit PASS; OSV PR PASS; OSV full SKIPPED. Run [#44203986892](https://github.com/Osleyder1985/SINAYXA/actions/runs/44203986892). | No reviews returned; no inline threads returned. | The security remediation's exact current HEAD has green executed checks and no HIGH/CRITICAL npm audit findings. It is the prerequisite remediation for #85/#96/#100. Still requires review and integration; do not merge automatically. |

### 10.1 Review interpretation

- No APPROVE review was returned for any of the seven PRs.
- Existing technical reviews are COMMENT, not APPROVE. They explicitly preserve scope limits and/or identify open operational gaps.
- No inline review threads were returned by the review-thread listing for these PRs. This does not replace checking issue/PR conversation comments and latest review history.
- The mergeable=true metadata reported by GitHub is only a merge-conflict signal; it does not mean policy, CI, architecture, scope, or review gates are satisfied.
- The combined commit-status endpoint returned no legacy status contexts. The check-runs endpoint is the evidence source used above.

### 10.2 Recommended dependency order — no merge performed

1. Review #117's six-file diff and exact-head tests; if complete, it is the first security remediation candidate.
2. After #117 is integrated, update/rebase #85, #96, and #100 onto the corrected base and rerun every required gate on their new exact HEADs.
3. Re-review #85 against #88/#89. The current evidence does not close areas A–E; determine whether the PR's declared scope is complete without claiming those external gaps are resolved.
4. Only after #85's base decision, rebase/retarget #99 and rerun all checks on the resulting head. Keep it DRAFT until the semantic and governance gates are met.
5. Only after #96's base decision and security revalidation, rebase/retarget #115 and run the complete required quality suite, not only the PostgreSQL lab.
6. #94 may be considered independently for its narrow filesystem-lab scope after review of its exact diff and merge policy; it must not be represented as production deletion/backup proof.
7. #100 remains blocked for the full AIStor use/deployment objective until cryptographic artifact verification and license/use review are completed, regardless of metadata capture success.

Issue tracking this continuity work: [#118](https://github.com/Osleyder1985/SINAYXA/issues/118).

## 11. Issue audit — current scope and preserved decisions

The bodies and current metadata of all 29 Issues in the initial snapshot were fetched. This is a content inventory, not yet a complete audit of every comment thread. Comment histories were inspected for the principal dependency cluster (#78, #88, #89, #97, #98, #113, #116); other Issue comment histories remain to be reviewed.

### 11.1 Decisions and blockers that must survive chat deletion

- **#78 — logical contract 0.2.1:** the owner explicitly approved the contract version and continuation of formal review. This is not closure of #78, approval of PR #85, or closure of areas A–E. The PR review is COMMENT, not APPROVE.
- **#88 — five-area verification matrix:** remains OPEN and blocks final acceptance of #85. Its latest update records 125 corrective tests passing on the current PR #85 code HEAD, including a regression that rejects AMBAS when there are independent secondary sources but no primary direct support. The exact-head Security Quality Gate still fails npm audit due to five HIGH picomatch findings. Areas A–E remain OPEN; automated synthetic coverage does not replace human semantic review or operational evidence.
- **#89 — external operational evidence:** remains OPEN. It requires real-scope deletion/reconciliation, object/version-specific WORM/Object Lock or equivalent evidence, and representative productive migration. Its only retrieved comment reiterates that no physical deletion, immutable-storage test, or productive migration has been executed. Do not use synthetic tests as substitutes.
- **#97/#98 — RET-09 audit minimization:** the owner approved the hardened alternative B: versioned closed catalogs for actor roles and reasons, opaque random non-semantic identifiers, and prohibition of free text/URLs/content hashes/identifying data in minimum audit events. PR #99 implements the first contract 0.2.2 delivery, remains DRAFT, and depends on #85. It does not prove full anonymization or external retention/deletion.
- **#93/#95 and #94/#96:** the filesystem lab and PostgreSQL lab are separate scopes. #94 supports only synthetic filesystem export/restore/reconciliation. #96 supports synthetic PostgreSQL backup/restore and passes its lab, but its npm dependency gate fails on the current head. Neither establishes external backup durability, physical deletion, WORM/Object Lock, PITR, or production migration.
- **#113/#115:** the adversarial synthetic test rejects an unknown deletion reference even when row counts happen to match. The specific PostgreSQL workflow passes on #115's HEAD, but no complete security/dependency workflow was returned for that stacked PR. It remains DRAFT on #96.
- **#116/#117:** the security issue is addressed on PR #117's branch, not in main. Exact current PR #117 check-runs show npm audit, Markdown lint/self-test, Gitleaks, OSV PR, PowerShell and event-registry checks passing; OSV full is skipped by design. The PR still needs review/integration before the base branch is considered remediated.
- **#46:** governs PowerShell analyzer/security quality; it remains open and its comments/closure evidence must be reviewed as part of the complete governance audit.
- **#3–#27:** remain the requirements/decision layer for the News and Events module. The initial inventory includes leak/early-indicia detection (#3), source credibility (#4), impact direction/intensity/horizon (#5/#14), monitoring (#7/#18), alerts (#8/#17), expectations (#9/#24), observed reaction (#10/#20), catalyst lifecycle (#11/#25), combined events (#12/#26), historical comparability (#19), and the requirements/scope index (#27). Their decision gates must not be inferred as approved merely because documents or implementation PRs exist.

### 11.2 Issue audit completion status

- [x] Current title, state, update timestamp, comment count, and body retrieved for all 29 Issues in the initial snapshot.
- [x] Core decision and blocker bodies inspected for #78, #88, #89, #97, #98, #113, and #116.
- [x] Recent comment history inspected for #78, #88, #89, #97, #98, #113, and #116 where available.
- [ ] Fetch and review the remaining comment histories for all other open Issues, including the full decision history of #3–#27 and #46.
- [ ] Reconcile references to historical PRs, including closed/merged duplicates and the exact merge commits that established current policy.
- [ ] Confirm no conversation-only decision contradicts the canonical Issue/document state.

## 12. Continuity PR #119 — validation status

Tracking Issue: [#118](https://github.com/Osleyder1985/SINAYXA/issues/118). Draft PR: [#119](https://github.com/Osleyder1985/SINAYXA/pull/119).

- PR #119 was opened as DRAFT against main; it changes one documentation file only. Main remains unchanged.
- Initial head `83feed40364e871c19aff70fb39f276d858685a7` failed the Security/dependency workflow at Markdown lint. The exact report identified 21 MD060/MD032/MD012 violations in the new document. npm ci completed; the job stopped at lint, so npm audit was not executed in that run.
- The table separator spacing, list spacing, and repeated blank lines were corrected.
- Updated head: `6ee8566e4359e6771367ccfa4435824095495972`.
- New Security/dependency workflow: [run #44205865609](https://github.com/Osleyder1985/SINAYXA/actions/runs/44205865609), in progress at the time of this record update. Gitleaks and OSV PR checks had started; npm lint/audit was queued.
- PowerShell quality workflow [run #44205865077](https://github.com/Osleyder1985/SINAYXA/actions/runs/44205865077) was pending at the time of this record update.

Do not mark the documentation lint as passed until the rerun completes successfully on the corrected HEAD. If lint reports additional errors, correct them and rerun. The continuity PR remains DRAFT and unmerged.

## 13. Updated chat deletion gate

**DO NOT DELETE PROJECT CHATS.** The continuity package now has a draft PR and a substantially improved inventory, but acceptance remains incomplete because:

- the corrected documentation HEAD has not yet passed all applicable quality gates;
- the full comment history of every open Issue has not been reviewed;
- the full diff-level audit of all seven original PRs is not complete (the #117 diff has received the first focused review);
- merged/closed historical decisions have not been comprehensively reconciled;
- local Windows worktrees and uncommitted changes remain unverified;
- the fresh-session recovery test has not been executed.

### 12.1 Corrected Markdown and dependency-gate result — HEAD `af2068898a4fc26adc51719ddecf29392f015296`

Exact-head evidence retrieved for the continuity PR:

- Markdown lint: **PASS**, 24 Markdown files, 0 issues. The earlier MD060/MD012/MD032 failures were corrected.
- Gitleaks: **PASS**.
- OSV PR scan: still running when this update was inspected.
- OSV full: **SKIPPED** by workflow design; not a PASS.
- npm audit: **FAIL**, five HIGH findings from the still-unfixed main-branch dependency chain `markdownlint-cli2 → globby/fast-glob/micromatch → picomatch`. The lint step itself passed; the job proceeded to npm audit and failed there.
- PowerShell 7.7.0 / Windows: still running when this update was inspected.

Runs: [Security/dependency #44206108625](https://github.com/Osleyder1985/SINAYXA/actions/runs/44206108625) and [PowerShell #44206108054](https://github.com/Osleyder1985/SINAYXA/actions/runs/44206108054).

**Interpretation:** the continuity document now passes Markdown lint. The remaining Security Quality Gate failure is inherited from main and is expected to be addressed by PR #117. PR #119 should remain DRAFT until #117 is reviewed/integrated, then #119 must be updated/rebased and all required gates rerun on the new exact HEAD.

After opening #118/#119, the repository currently has one additional open Issue and one additional open PR compared with the initial snapshot: 30 open Issues (including #118) and 8 open PRs (including #119). The original inventory in Sections 2–3 remains explicitly historical.

## 14. Continued PR audit — review of #117 and #100; exact-head status of remaining stack

Audit snapshot: 2026-11-17. No PR was merged, closed, retargeted, or rebased in this phase.

### 14.1 PR #117 — security remediation

Current PR head: `67b1db9e9b31f4a2bd36bb9eeadece2d8ce8b85a`, base `main` at `75583efab8be33a3739e3409ae54690ebc02d62b`.

Exact-head checks:

- PowerShell 7.6.6 / Windows: SUCCESS.
- PowerShell 7.7.0 / Windows: SUCCESS.
- PostgreSQL 18.7 event registry integration: SUCCESS.
- npm audit: SUCCESS.
- Gitleaks: SUCCESS.
- OSV PR scan: SUCCESS.
- OSV full: SKIPPED by workflow design; not a PASS.

Diff-level findings:

- Replaces markdownlint-cli2 with markdownlint@0.42.1 and a direct API runner.
- Removes picomatch/globby/fast-glob/micromatch from the lockfile.
- Preserves MD013=false and includes an MD018 canary self-test.
- The direct runner enumerates tracked and non-ignored untracked Markdown with git ls-files.
- **Scope question:** the same diff deletes the entire pull_request.paths filter from powershell-validation.yml. This broadens the workflow to every PR targeting main. It is not required to remove picomatch on the evidence inspected and should be justified or reverted if not an intentional repository-wide policy change.
- The claimed equivalence of file enumeration/rule behavior should be documented for root/subdirectory Markdown, ignored files, new files, and filenames with spaces.

A formal COMMENT review was submitted on the exact current HEAD (review ID 5948846417). It is not an APPROVE and does not request automatic merge. PR #117 is technically strong and its exact-head executed checks pass, but this scope question remains open. Issue #116 remains open until the correction is integrated and verified on main.

### 14.2 PR #100 — AIStor metadata-only preflight

Current head: `f78ed629ce3e007aa68a0062c5dc2f9cf6a4fee0`; exact-head checks:

- AIStor metadata preflight: SUCCESS.
- PowerShell 7.6.6 / 7.7.0: SUCCESS.
- Gitleaks: SUCCESS.
- OSV PR scan: SUCCESS.
- npm audit: FAILURE due to the five HIGH picomatch findings on the base line.
- OSV full: SKIPPED; not a PASS.

The branch's effective diff against current main is limited to the three intended files: the AIStor preflight workflow, shell capture script, and Spanish documentation. It preserves Server/Client metadata, OCI index and platform digests, checksums and detached signature sidecars, while explicitly not downloading binaries/images or verifying signatures/checksums against executable bytes.

New robustness findings submitted as COMMENT review ID 5948864410:

1. JSON report values from the remote metadata endpoint are interpolated into a hand-built JSON heredoc without general JSON escaping or strict validation of version/date/key strings.
2. HTTP 200 zero-byte sidecars can be hashed and counted as captured because file non-emptiness is not checked.
3. The machine-readable report should distinguish metadata `capture_status` from overall `readiness_status`; CAPTURED metadata must not be interpreted as authorization or readiness when artifact verification and license review remain pending.

Existing issue evidence still leaves checksum-to-binary comparison, cryptographic signature verification against trusted keys, and license/use review pending. The metadata-only capture is useful, but the broader AIStor readiness manifest remains BLOCKED. No artifact download, installation, license activation, or resource creation is authorized by this preflight.

### 14.3 Remaining open PRs — latest exact-head checks and dependencies

| PR | Current exact-head checks / state | Current technical disposition |
| --- | --- | --- |
| #85 | PowerShell 7.6.6/7.7.0 SUCCESS; PostgreSQL event registry SUCCESS; Gitleaks SUCCESS; OSV PR SUCCESS; npm audit FAILURE (five HIGH picomatch); OSV full SKIPPED. 125 corrective tests PASS. | Contract 0.2.1 implementation has strong synthetic coverage, but npm audit blocks integration until #117 is integrated/revalidated. All five areas A–E remain OPEN; human semantic and external operational evidence are not closed. |
| #94 | PowerShell 7.6.6/7.7.0 SUCCESS; event registry SUCCESS; Gitleaks SUCCESS; npm audit SUCCESS; OSV PR SUCCESS; OSV full SKIPPED. | 9.3/10 for its explicitly synthetic filesystem lab. Does not prove physical deletion, external copies, WORM/Object Lock, PostgreSQL backup/restore, or production migration. Existing reviews are COMMENT, not APPROVE. |
| #96 | PostgreSQL 18.7 / Docker 29.10.0 lab SUCCESS; PowerShell 7.6.6/7.7.0 SUCCESS; Gitleaks SUCCESS; OSV PR SUCCESS; npm audit FAILURE (five HIGH picomatch); OSV full SKIPPED. | Lab passes in its synthetic PostgreSQL scope. Security gate blocks merge pending #117 integration and exact-head rerun. Does not prove PITR, external backups, WORM/Object Lock, physical deletion, or production migration. |
| #99 | DRAFT; stacked on #85. PowerShell checks SUCCESS; npm audit SUCCESS on its branch; Gitleaks SUCCESS; OSV PR SUCCESS; OSV full SKIPPED. | 0.2.2 contract/migration tests are documented as passing (124 + 12 + 5 + 16). Keep DRAFT until #85 is integrated and this branch is rebased/retargeted and revalidated. Human review of semantic migration mappings and real emitter integration remain open. |
| #115 | DRAFT; stacked on #96. PostgreSQL 18.7 / Docker 29.10.0 specific workflow SUCCESS. No full security/dependency workflow is evidenced for this exact head. | Adversarial synthetic reconciliation is validated, including rejection of an unknown reference without an exact receipt. Must wait for #96/#117 dependency resolution, then run the complete applicable security and integration suite on the rebased head. |

### 14.4 Integration order reaffirmed

1. Resolve the review COMMENT on #117; if the path-filter change is justified or reverted, review and integrate #117 under repository governance.
2. Rebase/update #85, #96, and #100 onto the corrected main and rerun all applicable gates on each new exact HEAD.
3. Reconcile #85 against Issues #78/#88/#89; do not close A–E based on synthetic CI.
4. Rebase #99 onto the accepted #85/main line and rerun all checks; retain DRAFT until semantic and operational acceptance criteria are met.
5. Rebase #115 onto the accepted #96/main line and run the complete quality/security suite, not only the lab workflow.
6. Review #94 independently for its narrow synthetic filesystem scope; do not overstate its evidence.

No merge is performed by this audit. The continuity deletion gate in Section 13 remains in force.

### 14.5 Continuity PR validation after the 14.3 table — HEAD `0422d0103d380f703170cbcc03aa174b44f25866`

The first run on the expanded audit section found 13 Markdown lint errors (MD012, MD032 and MD060). These were corrected in the next commit. On the corrected HEAD:

- Markdown lint: **PASS**, 24 files, 0 issues.
- Gitleaks: **PASS**.
- OSV PR scan: **SUCCESS**.
- OSV full: **SKIPPED**, not a PASS.
- npm audit: **FAIL** due to the five HIGH findings in the base dependency tree (`markdownlint-cli2 → globby/fast-glob/micromatch → picomatch)); this is the known #117 dependency blocker, not a Markdown lint failure.
- PowerShell 7.7.0 / Windows: still running at the time of this record.

Runs: [Security/dependency #44207128924](https://github.com/Osleyder1985/SINAYXA/actions/runs/44207128924) and [PowerShell #44207128530](https://github.com/Osleyder1985/SINAYXA/actions/runs/44207128530).

Do not mark PR #119 fully validated until the PowerShell run completes and the npm audit gate passes on a rebased HEAD after the #117 dependency correction is integrated.

### 14.6 Revisión de seguimiento — 2026-11-17/18

#### PR #117 — remediación GHSA-fc5q-39xc-vjpf

HEAD verificado: `d933dc6849fedca4e74fe1c2f6b0221d13f4d9b4`.

- Se restauró en `.github/workflows/powershell-validation.yml` el filtro `pull_request.paths` original de `main`; se elimina la ampliación innecesaria a todos los PR.
- Revisión adicional del runner `scripts/validation/lint-markdown.mjs`: enumera archivos con `git ls-files -z`, conserva la configuración `MD013: false` y prueba MD018 con un canary antes del lint completo.
- Security/dependency run [#44207589168](https://github.com/Osleyder1985/SINAYXA/actions/runs/44207589168): workflow **SUCCESS**. Gitleaks **SUCCESS**, OSV PR scan **SUCCESS**, npm audit **SUCCESS**; OSV full **SKIPPED** y no se cuenta como PASS.
- Review de seguimiento registrada como COMMENT, no APPROVE (review ID `5948913667`).
- PR #117 está OPEN, READY FOR REVIEW y NOT MERGED. La remediación está validada en su rama, pero todavía no está integrada en `main`; Issue #116 permanece abierto hasta integración y verificación en la línea base.

#### PR #119 — continuidad documental

- HEAD actual: `40d6487d8e0cb5751c186b510a7434c38d6703ea`.
- Se corrigió el único error de lint identificado en el HEAD anterior `c86d76dfc7c7509833f0e9c9a82e8a51614cff8f`: MD012 por dos líneas en blanco consecutivas en `docs/project/PROJECT_CONTINUITY.md`.
- Para el nuevo HEAD, la consulta de workflow runs y el combined commit status no devolvieron ejecuciones ni estados. Esto se registra como **PENDING / NO EVIDENCE**, no como PASS ni FAIL.
- PR #119 continúa DRAFT / OPEN / NOT MERGED. Requiere ejecutar los quality gates sobre el HEAD exacto y completar la revisión documental.

No se fusionó ningún PR en esta actualización. La prueba de recuperación desde una conversación nueva y la verificación del estado local de Windows continúan pendientes. La prohibición de eliminar chats del proyecto sigue vigente.

### 14.7 Integración de la remediación de seguridad y revalidación de continuidad — 2026-11-18

#### PR #117 / Issue #116 — integración confirmada

- PR #117 fue fusionada mediante squash en `main`: commit `fcfc85925e823a00e8ee57ebf4d445f55d5a1d3c`.
- Issue #116 fue cerrado como COMPLETED después de verificar la línea base.
- En `main`, Security/dependency gate [run #44208391474](https://github.com/Osleyder1985/SINAYXA/actions/runs/44208391474): **SUCCESS**; npm audit **SUCCESS**, Gitleaks **SUCCESS**, OSV full **SUCCESS** en el evento push; OSV PR scan quedó SKIPPED en ese evento y no se cuenta como PASS.
- En `main`, PowerShell quality gate [run #44208391001](https://github.com/Osleyder1985/SINAYXA/actions/runs/44208391001): **SUCCESS**, incluidos los contextos PowerShell 7.7.0 y 7.6.6.

#### PR #119 — HEAD actualizado y gates aplicables

Para incorporar la corrección de seguridad sin alterar el contenido documental, la rama `docs/project-continuity-baseline` se actualizó con un merge commit que tiene como primer padre el nuevo `main` y como segundo padre el HEAD documental anterior. El diff funcional respecto de `main` continúa limitado a `docs/project/PROJECT_CONTINUITY.md`.

- HEAD: `b64c9cb830ad0197aed9dce6fe5f517875f6b064`.
- Security/dependency run [#44208527319](https://github.com/Osleyder1985/SINAYXA/actions/runs/44208527319): **SUCCESS**; npm audit, Gitleaks y OSV PR scan **SUCCESS**; OSV full **SKIPPED** por diseño para pull_request, no contado como PASS.
- PowerShell quality gate [run #44208526966](https://github.com/Osleyder1985/SINAYXA/actions/runs/44208526966): **SUCCESS**; PowerShell 7.7.0 y contexto requerido 7.6.6 **SUCCESS**.
- La ejecución anterior sobre el HEAD `96e6321...` falló en npm audit por el baseline previo a #117; esa evidencia histórica no representa el HEAD actualizado.

PR #119 permanece DRAFT / OPEN / NOT MERGED. Los gates del HEAD actual pasan, pero aún falta completar la auditoría de historiales de Issues/decisiones, la revisión documental integral y la prueba de recuperación desde una conversación nueva. La verificación de worktrees locales de Windows tampoco está disponible mientras el propietario no esté en el PC. No eliminar conversaciones todavía.

#### Actualización de ramas dependientes

- PR #96 se actualizó incorporando `main` en un merge commit: HEAD `9a6eaf06e2efa2e110e825f96640f78f56689da8`. Sus cambios funcionales permanecen en los tres archivos del laboratorio PostgreSQL.
- PR #100 se actualizó incorporando `main` en un merge commit: HEAD `8207bd60a841bf7e328ce6006e20e7c9a2825280`. Sus cambios funcionales permanecen en los tres archivos del preflight AIStor.
- PR #115 se actualizó para incorporar la nueva base de PR #96, preservando sus cambios en documentación y script de reconciliación: HEAD `a0c798bdb9ef31c558434b8d025527ab6857524c`.
- Los nuevos quality gates de #96 y #100 están ejecutándose; #115 requiere comprobar que el evento de sincronización y sus gates se hayan generado. No se transfieren resultados CI de HEAD anteriores a estos nuevos commits.
- PR #85 y #94 modifican workflows que también fueron cambiados por la remediación #117; sus ramas requieren reconciliación manual de esos archivos antes de revalidación. PR #99 depende de #85 y debe esperar esa reconciliación.

No se fusionaron #85, #94, #96, #99, #100, #115 ni #119. La única integración de esta etapa fue #117, validada en su HEAD exacto y posteriormente en `main`.

### 14.8 Integraciones adicionales y estado actualizado — 2026-11-18

#### PR #96 / Issue #95

- PR #96 integrada en main mediante squash: 93082ea734a82c093b81d02bfed5b4eb0f7be534.
- Issue #95 cerrado como COMPLETED.
- En main, Security/dependency [run #44209479593](https://github.com/Osleyder1985/SINAYXA/actions/runs/44209479593) SUCCESS, incluidos npm audit, Gitleaks y OSV full.
- En main, PowerShell [run #44209479425](https://github.com/Osleyder1985/SINAYXA/actions/runs/44209479425) SUCCESS, contextos 7.7.0 y 7.6.6.

#### PR #115 / Issue #113

- PR #115 fue convertida de stacked PR a PR contra main después de integrar #96; se reconstruyó su árbol sobre la nueva base para que el diff funcional quedara limitado a documentación y arnés de reconciliación.
- Un HEAD intermedio falló al no encontrar el socket local de PostgreSQL; se añadió diagnóstico de estado/logs del contenedor antes de cleanup. El HEAD final 332c352382ecdace926716172bd921545edb7376 pasó PostgreSQL lab [#44209916744](https://github.com/Osleyder1985/SINAYXA/actions/runs/44209916744), Security [#44209917212](https://github.com/Osleyder1985/SINAYXA/actions/runs/44209917212) y PowerShell [#44209916920](https://github.com/Osleyder1985/SINAYXA/actions/runs/44209916920).
- PR #115 integrada mediante squash en main: 453690f006400775dff92b225ab4e5ed369a861b.
- Issue #113 cerrado como COMPLETED. No se cierran #89 ni Área C de #88.

#### PR #94 / Issue #93

- Rama actualizada sobre main 453690f..., conservando exclusivamente los tres archivos propios del laboratorio filesystem.
- HEAD actual: 6cad0923ec0a18a13bb24e7abcc2ebfc8863cb7e.
- Security [run #44210713000](https://github.com/Osleyder1985/SINAYXA/actions/runs/44210713000), workflow Issue [#44210712731](https://github.com/Osleyder1985/SINAYXA/actions/runs/44210712731) y PowerShell [#44210712727](https://github.com/Osleyder1985/SINAYXA/actions/runs/44210712727) estaban queued/pending o in progress en el momento de esta actualización. No se reutilizan resultados de HEAD anteriores como PASS del HEAD actual.

#### PR #100 — AIStor metadata preflight

- Se reemplazó la construcción manual del JSON por serialización jq -n con argumentos tipados.
- Se exige que los sidecars no estén vacíos y que cumplan estructura mínima: SHA-256 hexadecimal + nombre de archivo, delimitadores OpenPGP y estructura Minisign.
- Se corrigió la derivación de URLs .asc/.minisig; el primer intento de hardening escapó incorrectamente las expansiones Bash y produjo una captura PARTIAL. La corrección posterior fue verificada.
- En el HEAD 17c41af1df36894ceea20a918426f90f9f188591, preflight [run #44210617351](https://github.com/Osleyder1985/SINAYXA/actions/runs/44210617351) SUCCESS: estado de captura CAPTURED, sidecars CAPTURED, sin descargar binarios ni imágenes.
- Artefacto [aistor-release-metadata](https://github.com/Osleyder1985/SINAYXA/actions/runs/44210617351/artifacts/14384809984), reporte schema 1.3.0: capture_status=CAPTURED, readiness_status=BLOCKED, signature_verification_performed=false, checksum_compared_to_binary=false.
- Security/dependency [run #44210617723](https://github.com/Osleyder1985/SINAYXA/actions/runs/44210617723) SUCCESS. PowerShell para ese HEAD seguía pending/in progress. PR #100 no se fusiona mientras falte la revalidación completa y revisión final; la preparación global AIStor permanece BLOCKED.

#### PR #85 / PR #99

- PR #85 se actualizó con main y con rutas específicas para disparar los contextos requeridos cuando cambian los archivos Node/Markdown lint.
- HEAD c36cc48d494fa870c0bb39205f47fc6e9b6ecfcd: Security [#44209730185](https://github.com/Osleyder1985/SINAYXA/actions/runs/44209730185), Issue [#44209727836](https://github.com/Osleyder1985/SINAYXA/actions/runs/44209727836) y PowerShell [#44209727785](https://github.com/Osleyder1985/SINAYXA/actions/runs/44209727785) SUCCESS. Sigue sin estar listo para merge porque los criterios semánticos A–E de #88 y la aceptación operacional de #89 continúan abiertos.
- PR #99 permanece DRAFT y apilada sobre #85; no se declara integrable ni se transfieren checks de su base.

#### PR #119 / continuidad

- Rama actualizada sobre main 453690f...; HEAD actual de la rama en el momento de esta anotación: de10871eb751607f116a1384f12fbc1297e72ee7.
- Debe verificarse CI sobre este HEAD exacto. Los PASS del HEAD anterior ef85fa0... no se transfieren.
- PR #119 continúa DRAFT / OPEN. Aunque el paquete documental y los gates anteriores pasaron, siguen pendientes la revisión integral de historiales de Issues/decisiones, la prueba de recuperación desde una conversación nueva y la verificación de worktrees/cambios locales en Windows.
- No borrar conversaciones hasta completar esas tres verificaciones y cerrar formalmente la revisión de continuidad.

### 14.9 Reconciliación de Issues del módulo y estado de integraciones — 2026-11-18

#### Integraciones y cierre de Issues

- PR #94 integrada en main: 3292428d0c8edeffa68f8086007b0fdecbf7c2a3; Issue #93 cerrado después de verificar el push gate en main.
- PR #96 integrada en main: 93082ea734a82c093b81d02bfed5b4eb0f7be534; Issue #95 cerrado después de verificar Security/dependency y PowerShell en main.
- PR #115 integrada en main: 453690f006400775dff92b225ab4e5ed369a861b; Issue #113 cerrado después de verificar Security/dependency y PowerShell en main.
- PR #117 integrada en main: fcfc85925e823a00e8ee57ebf4d445f55d5a1d3c; Issue #116 cerrado después de verificar npm audit, Gitleaks, OSV full en push y PowerShell.
- PR #93/#95/#113/#116 se cierran solo por el alcance sintético o de remediación que efectivamente quedó integrado. No se cierran #88/#89/#91 ni sus áreas operacionales.

#### PR #100 — estado exacto de captura AIStor

- La rama se actualizó sobre el main que incluye PR #94. HEAD actual: b91baad4a2c9c9592e3b2ea46aa8391fa456b5a6.
- AIStor metadata preflight [run #44211342715](https://github.com/Osleyder1985/SINAYXA/actions/runs/44211342715): SUCCESS. El log confirma CAPTURED, digest OCI index, sidecars checksum/OpenPGP/Minisign capturados y que no se descargaron binarios ni imagen.
- Artefacto [aistor-release-metadata](https://github.com/Osleyder1985/SINAYXA/actions/runs/44211342715/artifacts/14386755563), schema 1.3.0: capture_status=CAPTURED; readiness_status=BLOCKED; signature_sidecars_captured=true; signature_verification_performed=false; checksum_compared_to_binary=false; binary_download_performed=false; image_pull_performed=false.
- Security/dependency [run #44211342959](https://github.com/Osleyder1985/SINAYXA/actions/runs/44211342959): SUCCESS en npm audit, Gitleaks y OSV PR; OSV full SKIPPED por diseño en pull_request.
- PowerShell [run #44211342709](https://github.com/Osleyder1985/SINAYXA/actions/runs/44211342709) seguía en ejecución en el momento de esta anotación. No se declara mergeable/complete hasta su resultado final.
- Issue #100 permanece OPEN por las verificaciones posteriores aún pendientes: comparar checksum con el binario seleccionado, verificar criptográficamente la firma contra una clave confiable y revisar licencia/uso. El estado de readiness no se elevará a READY por la mera captura de sidecars.

#### Revisión de Issues #3–#27 — historial y estado metodológico

Se inspeccionaron bodies e historiales disponibles de los Issues del módulo. Resumen de estado, sin inferir aprobación donde no existe:

- #3 indicios/filtraciones: OPEN; depende del registro de acontecimientos #2, aplica el estándar aprobado #15 y la rúbrica cerrada #16. No hay detector productivo.
- #4 contraste de fuentes: OPEN; #15 y #16 están resueltos metodológicamente, pero el contrato lógico #78 sigue siendo prerequisito para implementación.
- #5 impacto potencial: OPEN; la escala/horizontes de #14 y expectativas de #24 siguen bloqueantes.
- #6 antecedentes comparables: OPEN; depende de metodología de comparabilidad #19.
- #7 vigilancia: OPEN; depende de límites/latencia #18 y autorización por fuente.
- #8 alertas: OPEN; depende de severidad/deduplicación #17 y del contenido de #5/#11.
- #9 expectativas/descuento: OPEN; depende de #24.
- #10 reacción real: OPEN; depende de #20. No atribuir causalidad por coincidencia temporal.
- #11 vigencia/ciclo de vida: OPEN; depende de #25.
- #12 relaciones/efectos combinados: OPEN; depende de #26.
- #13 definiciones operativas: CLOSED; aprobación expresa e integración del glosario mediante PR #39.
- #14 intensidad/horizontes: OPEN; fixture T01–T20 y CI no equivalen a aprobación metodológica ni ejecución humana formal. I0–I4 y tres relojes siguen como propuesta no aprobada.
- #15 estándar probatorio: CLOSED y aprobado expresamente; PR #43 integrada.
- #16 credibilidad/independencia: CLOSED y aprobado expresamente; rúbrica, S01–S16, evaluaciones por factor y controles negativos integrados. No implica automatización productiva.
- #17 severidad/deduplicación: OPEN; propuesta y fixtures A01–A15 integrados, pero umbrales/canales/cooldowns y aprobación metodológica siguen pendientes.
- #18 latencia/límites: OPEN; propuesta integrada mediante PR #68; faltan fuentes autorizadas, mediciones reales y pruebas L01–L15.
- #19 comparabilidad histórica: OPEN; no consta protocolo aprobado en el historial revisado.
- #20 reacción/atribución: OPEN; no consta protocolo aprobado en el historial revisado.
- #21, #22 y #23 están CLOSED como DUPLICATE de #18, #19 y #20 respectivamente; no se cuentan como decisiones independientes resueltas.
- #24 expectativas/descuento, #25 ciclo de vida y #26 relaciones/efectos combinados: OPEN; no consta aprobación metodológica en los historiales revisados.
- #27 índice maestro: OPEN; su body requiere reconciliación con las integraciones #94/#96/#115 y con los estados actualizados de #100/#119.

Los Issues #3–#12 son requisitos funcionales pendientes, no funcionalidades disponibles. La documentación y los fixtures sintéticos no acreditan ingestión operativa, vigilancia, alertas, análisis automatizado, predicción ni causalidad.

#### PR #119 / estado de continuidad actualizado

- Rama actualizada sobre main 3292428...; HEAD actual de rama f79ac13377e69dccddf6b672c911dbb43e6e094b.
- El CI del HEAD exacto debe finalizar; no se transfieren resultados de 560e994... ni de de10871....
- PR #119 sigue DRAFT / OPEN. Quedan pendientes: revisión integral de decisiones/historiales que no se cubrieron en esta pasada, prueba real de recuperación desde una conversación nueva y verificación de worktrees/cambios locales de Windows.
- No borrar conversaciones hasta completar y registrar las tres verificaciones pendientes.

### 14.10 Reconciliación final de integraciones y CI de continuidad — 2026-11-18

#### PR #100 / Issue #100

- PR #100 fue fusionada en main mediante squash: 73de7b25c79ca4b65d91903606b704554959d286.
- Issue #100 permanece OPEN; la captura de metadata/sidecars está integrada, pero readiness sigue BLOCKED hasta verificar checksum contra binario, firma criptográfica y licencia/uso.
- Gates post-merge en main: Security/dependency [run #44211589746](https://github.com/Osleyder1985/SINAYXA/actions/runs/44211589746) SUCCESS; PowerShell [run #44211589469](https://github.com/Osleyder1985/SINAYXA/actions/runs/44211589469) SUCCESS, incluidos 7.7.0 y 7.6.6.
- El Issue #27 y #118 recibieron comentarios de reconciliación: #100 ya no figura como PR abierta; sus pendientes se mantienen en el Issue.

#### Issue #46 — primer escaneo programado

- Se encontró y verificó la primera ejecución con event=schedule en main: [run #43870638585](https://github.com/Osleyder1985/SINAYXA/actions/runs/43870638585), HEAD 3e5f7b29da741d61b7fdce0f1c599f00930b98a3, conclusión SUCCESS.
- OSV full, Gitleaks full-history y npm audit: SUCCESS. OSV PR scan quedó SKIPPED por diseño en evento schedule.
- El ruleset protect-main permanece ACTIVE, ID 27316946, bypass vacío; el control negativo de PR #52 ya demostró bloqueo ante check requerido fallido.
- Issue #46 fue cerrado como COMPLETED; esto cierra solo la calidad/gobernanza de sus controles, no la calidad 10/10 del producto completo.

#### PR #85 / Issue #78 — actualización de rama

- La rama de PR #85 se actualizó sobre main 73de7b25... conservando su contrato 0.2.1 y reconciliando manualmente el workflow PowerShell para preservar tanto los pasos de contrato #78 como el laboratorio filesystem #93 integrado en main.
- HEAD actual: b229a17176e8b9bb1259311e4ccfb9e8c8849ee0. Sus nuevos workflows están pending/queued al registrar esta sección; no se transfieren resultados de c36cc48... ni del commit intermedio 813a7cc....
- PR #85 continúa OPEN / NOT MERGED. El contrato 0.2.1 está aprobado por el propietario, pero A–E de #88 y las brechas operativas de #89 siguen abiertas. No fusionar por el mero hecho de que la nueva base se haya actualizado.
- PR #99 permanece DRAFT / OPEN y apilada sobre #85; debe esperar la integración de 0.2.1 y una revalidación exacta de su propio HEAD.

#### Auditoría de historiales

- Se revisaron los cuerpos y comentarios disponibles de #3–#27, incluidos los 41 comentarios de #88, y los historiales de #78, #89, #97 y #98.
- #21/#22/#23 se confirmaron CLOSED como DUPLICATE de #18/#19/#20; no son decisiones independientes.
- #97 contiene aprobación expresa de la alternativa B endurecida; #98 contiene la especificación de implementación 0.2.2 y su historial de correcciones. PR #99 sigue sin integrar.
- Esta pasada no certifica todavía la revisión integral de todos los artefactos externos ni sustituye la recuperación real desde una conversación nueva.

#### PR #119 — CI del HEAD verificado

- HEAD: 484357d3e25ee80bbdc193f0d0f4953cfbb7cc69, actualizado sobre main 73de7b25...
- Security/dependency [run #44211712700](https://github.com/Osleyder1985/SINAYXA/actions/runs/44211712700): SUCCESS; npm audit, Gitleaks y OSV PR scan SUCCESS; OSV full SKIPPED en pull_request.
- PowerShell [run #44211712140](https://github.com/Osleyder1985/SINAYXA/actions/runs/44211712140): SUCCESS; contextos 7.7.0 y 7.6.6.
- Markdown lint pasó dentro del security/dependency job. El HEAD anterior efc4edd falló por MD024; se corrigió el encabezado duplicado y el HEAD 484357d pasó.
- PR #119 continúa DRAFT / OPEN / NOT MERGED. La documentación debe actualizarse una vez más para registrar su HEAD definitivo después de esta anotación y ejecutar CI sobre ese nuevo HEAD.

#### Inventario actual

- PR abiertas: 3 — #85, #99 y #119.
- Issues abiertas: 25.
- Issues cerradas en esta secuencia: #46, #93, #95, #113 y #116. Issue #100 permanece abierto por sus verificaciones posteriores.
- La prohibición de eliminar conversaciones sigue vigente: falta verificar worktrees/cambios locales en Windows y ejecutar la prueba real de recuperación desde una conversación nueva.

### 14.11 Corrección de HEADs y revalidación de las PR abiertas — 2026-11-18

#### PR #119 — resultado CI corregido

La actualización documental anterior produjo el HEAD 891ae7e4babeedd6cea950977b41d721539f1622. Sobre ese HEAD exacto:

- Security/dependency [run #44212240381](https://github.com/Osleyder1985/SINAYXA/actions/runs/44212240381): SUCCESS; npm audit, Gitleaks y OSV PR scan SUCCESS; OSV full SKIPPED en pull_request.
- PowerShell [run #44212240105](https://github.com/Osleyder1985/SINAYXA/actions/runs/44212240105): SUCCESS en 7.7.0 y 7.6.6.
- La corrección de MD024 se verificó; Markdown lint pasó.
- El HEAD 891ae es el último HEAD documental con CI verificado antes de esta nueva anotación. La anotación genera otro HEAD y requiere revalidación exacta.

#### PR #85 — resultado de revalidación

HEAD b229a17176e8b9bb1259311e4ccfb9e8c8849ee0:

- Security/dependency [run #44212018919](https://github.com/Osleyder1985/SINAYXA/actions/runs/44212018919): SUCCESS.
- PowerShell [run #44212018393](https://github.com/Osleyder1985/SINAYXA/actions/runs/44212018393): SUCCESS en 7.7.0 y 7.6.6.
- Workflow Issue/integración [run #44212018449](https://github.com/Osleyder1985/SINAYXA/actions/runs/44212018449): SUCCESS.
- Revisión COMMENT #5949240236: 9.2/10 para el contrato 0.2.1. No merge por brechas A–E de #88, evidencia operacional de #89 y dependencia #99.

#### PR #99 — rebase de la entrega 0.2.2

- Se actualizó la rama apilada sobre el HEAD actual de #85, sin arrastrar el diff de la antigua base ni duplicar el workflow del registro de eventos ya integrado.
- Se combinaron los pasos de contrato 0.2.1, laboratorio #93 y pruebas 0.2.2; se habilitó el security gate para PR dirigidas a la rama base #85.
- HEAD actual: 54c0edc3a62e9d90ed8c5a44463ea5cc8b1e4c87.
- Security/dependency [run #44212493747](https://github.com/Osleyder1985/SINAYXA/actions/runs/44212493747): SUCCESS; Gitleaks, npm audit y OSV PR SUCCESS; OSV full SKIPPED.
- PowerShell [run #44212493216](https://github.com/Osleyder1985/SINAYXA/actions/runs/44212493216) seguía in progress al registrar esta nota. No se transfiere el PASS histórico del HEAD ec3d3923.
- PR #99 continúa DRAFT / OPEN / NOT MERGED. Debe permanecer apilada y bloqueada hasta que #85 sea aceptada e integrada; además se mantiene la revisión semántica de mappings y de opacidad.

#### PR #100 — estado de integración y pendientes

PR #100 ya está MERGED (commit 73de7b25c79ca4b65d91903606b704554959d286). Issue #100 sigue OPEN por verificación de binario, firma y licencia/uso. El estado de captura CAPTURED no cambia readiness BLOCKED.

#### Inventario y continuidad

- Issues abiertas: 25. PR abiertas: 3 (#85, #99, #119).
- Issue #46 está CLOSED tras el primer scan programado en main [run #43870638585](https://github.com/Osleyder1985/SINAYXA/actions/runs/43870638585), SUCCESS.
- Historiales recuperados y revisados: #3–#27, #46, #78, #88 (41 comentarios), #89, #97 y #98. Se registraron las decisiones explícitas y las dependencias; los duplicados #21–#23 no se cuentan como decisiones resueltas.
- La prueba de recuperación desde conversación nueva y la verificación de worktrees/cambios locales de Windows siguen pendientes. La documentación no demuestra que no existan cambios locales sin subir.
- No borrar conversaciones hasta completar esas verificaciones.

### 14.12 Reconciliación de PR abiertas y evidencia exacta — 2026-11-18

Esta sección actualiza el inventario y los resultados posteriores a 14.11. Se conserva el historial previo; los estados PASS/FAIL/SKIPPED se vinculan al HEAD exacto y no se transfieren entre commits.

#### Inventario vigente

- Rama `main`: `73de7b25c79ca4b65d91903606b704554959d286`.
- PR abiertas: **3** — #85, #99 y #119.
- Issues abiertas: **25**.
- PR #117, #96, #115, #94 y #100 ya están integradas según las secciones anteriores; sus límites funcionales/operacionales no se consideran cerrados por esa integración.

#### PR #85 — contrato 0.2.1

HEAD verificado: `b229a17176e8b9bb1259311e4ccfb9e8c8849ee0`.

- PowerShell quality gate [run #44212018393](https://github.com/Osleyder1985/SINAYXA/actions/runs/44212018393): SUCCESS; PowerShell 7.7.0 y contexto requerido 7.6.6 SUCCESS; 12 archivos PowerShell inventariados; 0 errores de parser; PSScriptAnalyzer 1.24.0 con 0 findings; 125 pruebas correctivas 0.2.1 PASS y 36 pruebas de regresión de seguridad PASS.
- Security/dependency [run #44212018919](https://github.com/Osleyder1985/SINAYXA/actions/runs/44212018919): SUCCESS; npm audit sin vulnerabilidades; Markdown lint, Gitleaks full-history y OSV PR scan PASS. OSV full SKIPPED por diseño en pull_request; no es PASS.
- Workflow Issue/integración [run #44212018449](https://github.com/Osleyder1985/SINAYXA/actions/runs/44212018449): SUCCESS.
- Dictamen registrado en la revisión COMMENT: 9.2/10 para la entrega contractual sintética. PR #85 continúa OPEN / NOT MERGED; las áreas A–E de #88 y la evidencia operacional de #89 permanecen abiertas. No hay APPROVE técnico ni autorización de merge.

#### PR #99 — contrato 0.2.2

HEAD verificado: `54c0edc3a62e9d90ed8c5a44463ea5cc8b1e4c87`.

- PowerShell quality gate [run #44212493216](https://github.com/Osleyder1985/SINAYXA/actions/runs/44212493216): SUCCESS; 125 pruebas 0.2.1, 12 pruebas 0.2.2, 5 pruebas CSPRNG UUIDv4, 17 pruebas de migración 0.2.1→0.2.2 y 36 pruebas de regresión de seguridad PASS; PSScriptAnalyzer 1.24.0 con 0 findings.
- Security/dependency [run #44212493747](https://github.com/Osleyder1985/SINAYXA/actions/runs/44212493747): SUCCESS; npm audit, Gitleaks y OSV PR scan PASS. OSV full SKIPPED por diseño en pull_request.
- Dictamen registrado en revisión COMMENT: 9.5/10 para la entrega sintética 0.2.2. Sigue DRAFT / OPEN y apilada sobre #85. No se integra antes de resolver la aceptación de #85; la suficiencia semántica de mappings históricos y la integración del generador en un emisor operativo siguen requiriendo revisión/evidencia específica.

#### PR #119 — continuidad documental: verificación previa

HEAD verificado antes de esta actualización: `200980640e2f2e76738d237e653928ce61396d0a`.

- PowerShell [run #44212711921](https://github.com/Osleyder1985/SINAYXA/actions/runs/44212711921): SUCCESS; contextos PowerShell 7.7.0 y 7.6.6 SUCCESS.
- Security/dependency [run #44212712043](https://github.com/Osleyder1985/SINAYXA/actions/runs/44212712043): SUCCESS; Markdown lint, npm audit, Gitleaks y OSV PR scan PASS. OSV full SKIPPED por diseño en pull_request.
- La comparación del HEAD contra `main` confirma que el diff funcional de esta PR está limitado a `docs/project/PROJECT_CONTINUITY.md`; los resultados de checks de este HEAD no validan el nuevo commit documental que añade esta sección. Ejecutar de nuevo los gates aplicables sobre el HEAD resultante y registrar el resultado sin reutilizar estos PASS.
- PR #119 continúa DRAFT / OPEN / NOT MERGED y sin review APPROVE.

#### Puertas de continuidad aún pendientes

1. Completar la revisión de historiales/comentarios y decisiones de los 25 Issues abiertos, dejando trazabilidad de cualquier decisión material no preservada todavía.
2. Ejecutar una prueba real de recuperación desde una conversación nueva: reconstruir el proyecto, las restricciones, los estados de las tres PR y la siguiente tarea usando este documento y sus referencias, sin depender del historial de chats.
3. Inspeccionar el equipo Windows cuando esté disponible y reconciliar worktrees, ramas, HEADs locales y cambios sin commit/no publicados. GitHub no puede demostrar el estado de esos archivos locales.

La aprobación de CI no equivale a completar la continuidad. **No eliminar conversaciones del proyecto** hasta que las tres puertas anteriores estén verificadas y registradas, y la prueba de recuperación sea satisfactoria.

### 14.13 Revalidación de Markdown y quality gates — HEAD 94a04ee — 2026-11-18

#### Corrección del fallo inicial

El HEAD anterior `a8f46c9a528bd995d8a1e9e02f27fb6e21ec2b00` falló en Security/dependency [run #44239747432](https://github.com/Osleyder1985/SINAYXA/actions/runs/44239747432). La causa exacta fue Markdown lint en `docs/project/PROJECT_CONTINUITY.md`:

- Línea 554: MD012/no-multiple-blanks (dos líneas vacías consecutivas).
- Línea 583: MD024/no-duplicate-heading (duplicación de `#### PR #119 — continuidad documental`, que ya aparecía en la sección 14.6).

Se corrigieron ambas infracciones en el commit `94a04ee530e776da4668fc545a2393dc8d84831a`: se dejó una sola línea vacía y se renombró el encabezado duplicado como `#### PR #119 — continuidad documental: verificación previa`.

#### Resultado de CI sobre el HEAD exacto 94a04ee

- Security/dependency [run #44240188144](https://github.com/Osleyder1985/SINAYXA/actions/runs/44240188144): **SUCCESS**. Gitleaks full-history SUCCESS; Markdown lint SUCCESS; npm audit SUCCESS; OSV PR scan SUCCESS. OSV full quedó **SKIPPED** por diseño en pull_request; no se cuenta como PASS.
- PowerShell [run #44240187749](https://github.com/Osleyder1985/SINAYXA/actions/runs/44240187749): **SUCCESS**. PowerShell 7.7.0 SUCCESS; contexto requerido 7.6.6 SUCCESS; instalación de PSScriptAnalyzer, inventario/parser, análisis estático, detección de regla de seguridad, fixture sintético, pruebas positivas/negativas/robustez, validaciones de Issues y registro de procedencia SUCCESS.

Estos resultados validan únicamente el HEAD `94a04ee...`; cualquier cambio posterior exige nuevos checks.

#### Reconciliación de la vista de diff de PR #119

La comparación explícita de `main` (base de comparación `73de7b25c79ca4b65d91903606b704554959d286`) contra HEAD `94a04ee...` devuelve 27 commits ahead, 0 behind y un único archivo en el diff: `docs/project/PROJECT_CONTINUITY.md`.

Sin embargo, el payload de PR #119 todavía informa `base_sha=75583efab8be33a3739e3409ae54690ebc02d62b` y `changed_files=15`; la lista de archivos de la PR devuelve 15 rutas. Esos datos no concuerdan con la comparación contra la referencia actual `main`. No se debe ocultar ni asumir resuelta esta discrepancia: antes de considerar #119 merge-ready hay que reconciliar la base efectiva y el diff mostrado por GitHub, y confirmar que los 14 archivos restantes son historial/base ya integrado y no cambios exclusivos de la PR. No se autoriza merge por el mero hecho de que `mergeable=true`.

#### Estado

PR #119 continúa OPEN / DRAFT / NOT MERGED. Los dos quality gates aplicables pasan en el HEAD 94a04ee, pero quedan pendientes: reconciliación del diff/base, recuperación real desde conversación nueva, revisión completa de decisiones/historiales de Issues y verificación local de worktrees/cambios Windows. No borrar conversaciones del proyecto.

### 14.14 Reconciliación de PR de integración — corte 2026-11-19 00:30 UTC

Esta sección actualiza el inventario histórico anterior. Los estados se verificaron directamente en GitHub; no sustituye los requisitos de cada Issue ni convierte checks omitidos en satisfactorios.

#### Fusiones confirmadas después del snapshot anterior

| PR | Resultado | Evidencia |
| --- | --- | --- |
| #120 | MERGED | merge commit `e55600b7e02b9b3e0acde4277fa224928970efbf` |
| #123 | MERGED | merge commit `be54f026b4e4b821590d397f29191f835cb047d5` |
| #124 | MERGED | merge commit `c7c0f72fd3af27ac43d44769cfd67f250efc277d` |
| #125 | MERGED | merge commit `faa30287e222a606bfe88f0012f3f312585ef132` |

El HEAD de `main` observado después de estas integraciones es `faa30287e222a606bfe88f0012f3f312585ef132`.

#### Inventario de PR abiertos

| PR | HEAD observado | Base | Estado / bloqueo |
| --- | --- | --- | --- |
| #85 | `b229a17176e8b9bb1259311e4ccfb9e8c8849ee0` | `main` | OPEN, no DRAFT; cuatro commits detrás de `main`. #99 depende de esta rama. |
| #99 | `54c0edc3a62e9d90ed8c5a44463ea5cc8b1e4c87` | `feature/issue-78-contract-v0.2.0` (#85) | OPEN, DRAFT; 64 commits por delante de su base, sin divergencia respecto a ese HEAD de base. Integrar después de #85 y revalidar. |
| #119 | `14df2dda7dc2f5c2c12b19ebdacf49d9eb874902` | `main` | OPEN, DRAFT; cuatro commits detrás de `main`. Su rama aún requiere actualización y CI exact-HEAD. |
| #126 | `0b9b50e6a465a766afc5fda6b9642c692c813a63` | `feat/issue-121-fresh-database-migration-runner` (#125) | OPEN, DRAFT; rama divergente respecto al HEAD actualizado de #125. Corrección de arrays enviada, PostgreSQL 18.7 aún no verificado en ese HEAD. |
| #127 | `e080476d4d921766cf38af4448a62c42db0dced0` | `feat/issue-121-catalog-fingerprint-readonly` (#126) | OPEN, DRAFT; rama divergente respecto al HEAD de #126 y check PostgreSQL 18.7 fallido en el HEAD consultado. |

#### Contrato 0.2.1 → 0.2.2

La rama de #85 coincide exactamente con la base de #99: `b229a17176e8b9bb1259311e4ccfb9e8c8849ee0`. #99 tiene como merge-base ese mismo commit y aporta 64 commits adicionales. La dependencia es explícita y no se debe retargetear ni fusionar #99 antes de resolver #85.

#### Cadena de migraciones #121

La integración de #123–#125 no cierra automáticamente los defectos funcionales descubiertos durante la auditoría:

- #124: la ancestralidad de cada `source_revision` respecto a `baseline_revision` quedó implementada en el cambio integrado; el caso negativo debe seguir formando parte de la suite.
- #125: permanecen como criterios de cierre la detección de duplicados/NULL antes de transformar filas a `dict`/`set`, el prefijo continuo del ledger y la verificación estructural del control plane y de ambos ledgers. La integración no acredita por sí sola que esos casos estén resueltos.
- #126: el check PostgreSQL 18.7 del HEAD anterior registró 40 pruebas, con 29 errores y 2 fallos porque los arrays generados por PostgreSQL se clasificaban como tipos base personalizados. La corrección `t.typelem = 0` quedó validada en el commit `0b9b50e6a465a766afc5fda6b9642c692c813a63`: el job PostgreSQL 18.7 terminó SUCCESS en [run #44429507363](https://github.com/Osleyder1985/SINAYXA/actions/runs/44429507363), ejecutó 40 pruebas de fingerprint y el test de rechazo fail-closed de tipos base personalizados pasó. La rama sigue pendiente de sincronización con el HEAD actualizado de #125.
- #127: no se considera listo mientras dependa de una base #126 divergente y falle la validación PostgreSQL. La identidad efectiva, memberships/SET ROLE, flags y privilegios reales siguen siendo requisitos del preflight.

#### Estado de las comprobaciones

En los HEAD consultados de #85 y #99, los checks ejecutados de PowerShell, PostgreSQL (cuando aplicaba), Gitleaks, npm audit y OSV PR aparecen satisfactorios; OSV full aparece SKIPPED. Para #119, en el HEAD `2d039d2c3f0eb0bac2998e8eddcce92c4d6a66c3`, PowerShell 7.6.6/7.7.0 y Security/dependency están SUCCESS; Markdown lint 29 archivos PASS, npm audit 0 vulnerabilidades, Gitleaks y OSV PR SUCCESS; OSV full SKIPPED. El fallo inicial de Markdown lint fue corregido. #126 tiene PostgreSQL 18.7 SUCCESS en el HEAD `0b9b50e6...`; #127 conserva PostgreSQL FAILURE en el HEAD `e080476d...`. Un check verde de seguridad/dependencias no compensa un check PostgreSQL fallido o ausente.

#### Siguiente orden seguro

1. #126: resolver la divergencia de rama mediante actualización/rebase estándar de GitHub; ejecutar PostgreSQL 18.7 en el HEAD resultante y cerrar los tests de tipos.
2. #127: actualizar sobre el HEAD ya validado de #126; resolver la divergencia, ejecutar pruebas con roles reales y mantener `LEGACY_UNVERIFIED` ante cualquier identidad o privilegio no verificable.
3. #85: actualizar contra `main`, inspeccionar el diff posterior a la actualización y repetir CI exact-HEAD; no fusionar solo por tener checks históricos verdes.
4. #99: mantener su base en #85 hasta que #85 esté integrado; después actualizarlo y revalidar compatibilidad/migración 0.2.1 → 0.2.2.
5. #119: actualizar contra `main`, revisar el diff de continuidad y ejecutar lint/validaciones en el HEAD resultante.
6. No hacer DDL/DML productivo, adopción legacy ni modificar las migraciones históricas `0001–0005`.

La herramienta GitHub utilizada en este corte no expone una operación segura de “Update branch” para sincronizar las ramas divergentes. No se han forzado refs, rebases manuales ni commits de merge construidos a ciegas. La actualización de ramas debe realizarse con la operación estándar de GitHub y verificarse después.

### 14.15 Revalidación de integración y preflight PostgreSQL — corte 2026-11-19 (actualizado)

Este corte sustituye los estados de ramas del inventario 14.14 cuando exista discrepancia. Los HEAD y ejecuciones citados se consultaron directamente en GitHub.

#### Inventario actual de PR abiertas

| PR | HEAD | Base | Estado comprobado |
| --- | --- | --- | --- |
| #85 | `d2a08ea8d104f2a4756e3cd970f5159a270cba25` | `main` | OPEN; 0 detrás; PowerShell, Security y Issue workflow SUCCESS en este HEAD. Issue #88 mantiene brechas A–E; Issue #89 mantiene bloqueos operacionales. |
| #99 | `d1da9ba3f9c89a27e36d5d4297b1bf755870030d` | rama #85 | OPEN / DRAFT; 0 detrás de su base; PowerShell y Security SUCCESS en este HEAD. Depende de #85. |
| #119 | `15c5bdff04e4d06134ad01fdba9c933d2551c977` | `main` | OPEN / DRAFT; actualización documental en validación; PowerShell SUCCESS y Security falló por Markdown lint, ahora corregido en este cambio. |
| #126 | `2ace99daafbb4bbef1c95470cdbe9e4d686fe9d0` | `main` | OPEN / DRAFT; 0 detrás; diff de cinco archivos. PowerShell, PostgreSQL y Security exact-HEAD SUCCESS. OSV full SKIPPED, no PASS. |
| #127 | `a4ba27663d864ad6ff06b3cc0e77c0717a3c95c6` | rama #126 | OPEN / DRAFT; CI exact-HEAD pendiente para controles de privilegios por columna, REPLICATION y MAINTAIN. |

#### #126 — fingerprint del catálogo

La genealogía de la rama histórica de #125 se reconcilió con `main` tras comprobar que ambos snapshots tenían el mismo árbol Git. El HEAD final de #126 se reconstruyó desde el árbol exacto de `main`, aplicando solo los cambios de fingerprint y sus workflows. No se modificó `main` ni se utilizó force-push.

Ejecuciones sobre HEAD `2ace99d...`:

- PowerShell: [44439914633](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439914633) — SUCCESS.
- PostgreSQL / Issue: [44439914345](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439914345) — SUCCESS.
- Security/dependency: [44439914777](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439914777) — SUCCESS; OSV full SKIPPED.

#### #127 — preflight legacy: revisión ampliada de privilegios

El primer HEAD integrado `a94bad8...` falló porque el rol de prueba se creaba sin contraseña y PostgreSQL exigía autenticación. Se añadió contraseña efímera para el rol lector, sin usar superusuario en la ejecución del preflight.

El siguiente HEAD `2d19ec1...` reveló la causa adicional y real del fallo: los GRANT/REVOKE de esquema y tabla se ejecutaban mediante una conexión a la base de servicio, aunque cada prueba opera en una base aislada creada dinámicamente. Esto provocó `permission denied for schema sinayxa` y errores de cleanup al intentar eliminar roles que aún tenían privilegios.

La corrección de autenticación y grants quedó en `9cb25bc...`. La corrección vigente en HEAD `8eedf02d4228ef320d753014cdcc617bd4acac54`:

- aplica GRANT/REVOKE de esquema y tabla mediante la conexión a la base aislada;
- confirma las transacciones antes de abrir la conexión del rol lector y después de cada cambio de privilegios;
- reserva la conexión administrativa para operaciones de ámbito clúster (crear/eliminar roles y bases);
- conserva el rol lector autenticado y las verificaciones de mínimo privilegio;
- calcula el baseline aprobado después de aplicar los ACL esperados, porque el fingerprint incluye los privilegios de esquema y tabla.

CI exact-HEAD `8eedf02...` (validación anterior):

- PowerShell [44441538244](https://github.com/Osleyder1985/SINAYXA/actions/runs/44441538244) — SUCCESS.
- Security/dependency [44441538832](https://github.com/Osleyder1985/SINAYXA/actions/runs/44441538832) — SUCCESS; OSV full SKIPPED.
- PostgreSQL / Issue [44441538140](https://github.com/Osleyder1985/SINAYXA/actions/runs/44441538140) — SUCCESS.

Revisión adicional del contrato detectó dos vías de privilegio que el preflight anterior no evaluaba completamente: grants `INSERT`/`UPDATE`/`REFERENCES` a nivel de columna y el atributo de rol `REPLICATION`. La documentación PostgreSQL distingue `has_table_privilege` de `has_any_column_privilege`, que detecta concesiones por columna; `pg_roles` expone `rolreplication`. Se añadieron ambas comprobaciones y pruebas de regresión en HEAD `672d48a...`; posteriormente se detectó también el privilegio de tabla `MAINTAIN`, que quedó cubierto en HEAD `a4ba276...`. El CI exact-HEAD de este último commit debe terminar antes de considerar cerrada la revisión.

La ejecución `8eedf02...` pasó los tres gates aplicables. La ejecución `672d48a...` pasó PostgreSQL/Issue, Security y PowerShell; añadió controles de ACL por columna y atributo REPLICATION. El HEAD posterior `a4ba276...` añade MAINTAIN y aún no tiene resultado de CI. El estado funcional de adopción sigue siendo `LEGACY_UNVERIFIED`; no se habilita adopción, DDL/DML productivo ni modificación de migraciones históricas.

#### Contrato 0.2.1 / 0.2.2

\#85 y #99 están sincronizadas en sus respectivas relaciones de dependencia y sus gates aplicables finalizaron SUCCESS sobre sus HEAD actuales. Eso no cierra los criterios metodológicos:

- Issue #88 mantiene abiertas brechas de cobertura/revisión en A–E.
- Issue #89 mantiene pendientes las pruebas externas de eliminación, WORM/Object Lock y migración productiva.
- #99 no se integra antes de #85 y debe revalidarse tras la integración de su base.

#### Decisión de integración

No se fusionó ninguna de las cinco PR abiertas en este corte. Ningún estado SKIPPED se contabiliza como PASS. No se ha modificado `main` directamente ni se ha usado force-push. Las decisiones y evidencias de reconciliación de #126/#127 están registradas en Issues #129 y #130 y en los comentarios de las PR respectivas.

#### Próxima secuencia verificable

1. Esperar y revisar CI exact-HEAD `9cb25bc...` de #127; inspeccionar logs si falla.
2. Si PostgreSQL pasa, revisar exhaustivamente el preflight: identidad efectiva, memberships/SET ROLE, atributos elevados, privilegios de lectura/escritura y ausencia de mutación.
3. Si todos los gates aplicables pasan, actualizar el inventario de #119 con los resultados finales y reevaluar la integración de #126/#127.
4. Mantener #85/#99 bloqueadas por los criterios abiertos de #88/#89, no por el simple estado de CI.
5. Verificar recuperación real de continuidad desde una conversación nueva y el estado local de worktrees Windows antes de considerar cerrada #119.

## 14.16 Corte de verificación y correcciones — 2026-11-19 UTC

Este apartado registra únicamente los estados consultados en GitHub en este corte. Sustituye los HEAD anteriores de 14.15 cuando exista discrepancia. No declara ninguna PR lista para merge.

### Inventario y CI exact-HEAD

| PR | HEAD actual comprobado | CI observado | Estado y decisión |
| --- | --- | --- | --- |
| #85 | d2a08ea8d104f2a4756e3cd970f5159a270cba25 | PowerShell [44439012103](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439012103) SUCCESS; PostgreSQL/Issue [44439012421](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439012421) SUCCESS; Security [44439012589](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439012589) SUCCESS. OSV full SKIPPED. | OPEN, no DRAFT. No fusionar: Issues #88/#89 mantienen brechas A–E y evidencia operacional pendientes. |
| #99 | d1da9ba3f9c89a27e36d5d4297b1bf755870030d | PowerShell [44439159091](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439159091) SUCCESS; Security [44439159479](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439159479) SUCCESS. OSV full SKIPPED. | OPEN / DRAFT; depende de #85. |
| #119 | 416351bac1ff887be3f139a89964b36a17248f82 | PowerShell [44442274425](https://github.com/Osleyder1985/SINAYXA/actions/runs/44442274425) SUCCESS; Security [44442274845](https://github.com/Osleyder1985/SINAYXA/actions/runs/44442274845) SUCCESS. | OPEN / DRAFT. El documento conserva snapshots históricos; la recuperación en una conversación nueva y la reconciliación de worktrees locales siguen pendientes. |
| #126 | 2ace99daafbb4bbef1c95470cdbe9e4d686fe9d0 | PowerShell [44439914633](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439914633) SUCCESS; PostgreSQL/Issue [44439914345](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439914345) SUCCESS; Security [44439914777](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439914777) SUCCESS. OSV full SKIPPED. | OPEN / DRAFT; 0 commits behind main; diff funcional de cinco archivos. No fusionar: revisión estática reciente detectó una posible clasificación incorrecta de arrays generados. |
| #127 | 4264fa2f77db516922780fe34a514768c964330b | En el momento de este corte: PostgreSQL/Issue [44443047619](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443047619) IN_PROGRESS; PowerShell [44443047590](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443047590) PENDING; Security [44443048108](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443048108) PENDING. | OPEN / DRAFT; dependiente de #126. No contabilizar los estados pendientes como PASS. |

### #126 — nuevo hallazgo de clasificación de tipos

Revisión COMMENT registrada en GitHub, review ID 5968332955, sobre HEAD 2ace99d.

La consulta unsupported_base_types usa un predicado basado en NOT EXISTS (... element_type.typarray = t.oid). Ese predicado no identifica correctamente el tipo array actual; la clasificación debe comprobarse con los metadatos del tipo array, incluyendo typelem, sin volver a clasificar arrays generados como tipos base personalizados.

Corrección requerida y aún no demostrada:

- Un tipo base personalizado no modelado debe ser rechazado.
- Su array generado no debe provocar un falso positivo.
- Arrays generados para tipos compuestos/tablas no deben bloquear por sí solos el fingerprint.
- Repetir toda la suite PostgreSQL 18.7 y quality gates sobre el HEAD corregido.

Hasta cerrar esta revisión, mantener sinayxa-catalog-v1-preview; no aprobar baseline ni adopción legacy.

### #127 — correcciones de revisión publicadas

Tras la revisión complementaria (review 5968311393), se publicaron dos commits en la rama feat/issue-121-legacy-adoption-preflight:

- eef99924745014dd3e285a6e33a4b86f96d8db26: añade tres pruebas PostgreSQL que separan membresía allowlisted válida, capacidad SET ROLE y ADMIN OPTION.
- 4264fa2f77db516922780fe34a514768c964330b: corrige la anotación de role_attributes para reflejar los siete campos devueltos por la consulta de pg_roles.

Los cambios se registraron también en el comentario de PR 6997628686. El CI del nuevo HEAD estaba pendiente/en curso al momento de este corte. No se debe declarar resuelta la revisión hasta obtener los tres gates aplicables en SUCCESS y revisar los resultados PostgreSQL. El estado operativo sigue siendo LEGACY_UNVERIFIED.

### Decisión de integración y próxima secuencia

1. Corregir #126 y demostrar los tres escenarios de tipos/arrays anteriores; CI exact-HEAD completo.
2. Sincronizar #127 únicamente después de que #126 tenga un HEAD corregido y validado; volver a ejecutar CI exact-HEAD y revisar todas las pruebas de roles/permisos.
3. Mantener #85/#99 sin merge mientras los criterios funcionales y operacionales aplicables de #88/#89 permanezcan abiertos.
4. Actualizar este documento desde los resultados finales, no desde ejecuciones históricas ni estados PENDING/IN_PROGRESS.
5. No modificar main, no usar force-push, no ejecutar adopción legacy ni DDL/DML productivo.

## 14.17 Rectificación de revisión y CI posterior — 2026-11-19 UTC

Esta sección corrige expresamente el hallazgo sobre arrays registrado en 14.16. La revisión inicial 5968332955 de PR #126 se retira como defecto del algoritmo.

### #126 — interpretación correcta de pg_type.typarray

La condición NOT EXISTS (SELECT 1 FROM pg_type element_type WHERE element_type.typarray = t.oid) sí excluye los tipos array generados: el tipo elemento referencia el OID de su array mediante su campo typarray. La interpretación anterior confundió el sentido de esa relación. No se requiere reemplazarla por typelem = 0 a causa de ese hallazgo.

El HEAD 2ace99daafbb4bbef1c95470cdbe9e4d686fe9d0 ya contiene las pruebas:

- test_fingerprint_accepts_generated_array_types_for_composite_types.
- test_fingerprint_rejects_user_defined_base_types_until_fully_modeled.

PostgreSQL 18.7 [run 44439914345](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439914345) terminó SUCCESS en ese HEAD. La rectificación quedó publicada en el comentario de PR #126 6997663073. Mantener las limitaciones generales del algoritmo preview; no afirmar que esta revisión aislada certifica la cobertura completa del catálogo.

### CI posterior de PR #127

En HEAD 4264fa2f77db516922780fe34a514768c964330b:

- PostgreSQL / Issue [44443047619](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443047619): SUCCESS.
- Security [44443048108](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443048108): SUCCESS; OSV full SKIPPED.
- PowerShell [44443047590](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443047590): seguía IN_PROGRESS en la última consulta; no declarar el gate completo.

### CI documental de PR #119

El HEAD dfcbf57 falló Markdown lint por MD012 y MD032. Se corrigieron ambas incidencias en HEAD c1470c388205a36e1eebd72f6ed38818f972d10b. Al último sondeo, PowerShell [44443261198](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443261198) estaba PENDING y Security [44443261594](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443261594) QUEUED. No declarar validada la documentación hasta que ambos finalicen SUCCESS.

### Decisión actual

El hallazgo de arrays no bloquea #126. Permanecen los bloqueos independientes: algoritmo etiquetado preview, revisión integral de clases de objetos/cobertura de catálogo, baseline independiente aprobado y controles de adopción legacy. #127 continúa DRAFT y LEGACY_UNVERIFIED hasta completar PowerShell y la revisión funcional. #119 continúa DRAFT hasta completar sus nuevos gates y la prueba de recuperación de continuidad.

## 14.18 Confirmación de gates #127 y estado documental — 2026-11-19 UTC

### PR #127 — gates exact-HEAD completos

HEAD 4264fa2f77db516922780fe34a514768c964330b:
- PostgreSQL 18.7 / Issue [44443047619](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443047619): SUCCESS.
- PowerShell [44443047590](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443047590): SUCCESS; perfil 7.7.0 y compatibilidad 7.6.6.
- Security [44443048108](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443048108): SUCCESS; OSV full SKIPPED.

Las tres pruebas de memberships y la corrección de typing están en un HEAD con todos los gates aplicables ejecutados en SUCCESS. La revisión técnica 5968311393 queda atendida. La PR sigue DRAFT y LEGACY_UNVERIFIED; no autoriza adopción ni merge.

### PR #119 — CI del documento actualizado

HEAD actual 354317a1c44517056abf81636c4eb162758dece3:

- PowerShell [44443370659](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443370659): PENDING.
- Security [44443371153](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443371153): IN_PROGRESS en el último sondeo.

El HEAD anterior dfcbf57 falló Markdown lint por MD012 y MD032. Se corrigieron en c1470c3 y luego se añadió la rectificación de #126 en 354317a. La validación del nuevo HEAD queda pendiente hasta que PowerShell y Security terminen SUCCESS.

### Estado de la revisión de #126

El hallazgo 5968332955 sobre typarray fue retirado como falso positivo mediante comentario 6997663073. No se requiere ese cambio de código. Se mantienen los límites del algoritmo preview y la necesidad de revisión completa de cobertura del catálogo y baseline independiente.

## 14.19 Revalidación exacta del HEAD documental y matriz de CI — 2026-11-19 UTC

Este apartado prevalece sobre cualquier estado anterior de CI cuando el HEAD citado haya cambiado.

### PR #119 — HEAD `1d261531ee4f910a02286d047c04b0d7238c7595`

- PowerShell quality gate [44443439183](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443439183): **SUCCESS**.
- Security/dependency quality gate [44443439448](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443439448): **FAILURE**.
- Gitleaks: SUCCESS.
- OSV PR scan: SUCCESS.
- OSV full: SKIPPED; no se contabiliza como PASS.
- El fallo se produjo en `npm run lint:markdown`, antes de ejecutar `npm audit`. El log identificó seis infracciones en este mismo documento:
  - MD012 en las líneas 794 y 824 (líneas del archivo inspeccionado por ese run).
  - MD032 en las líneas 804, 812, 830 y 839.
- Por tanto, el gate de seguridad no está aprobado y el resultado de npm audit no se obtuvo en esa ejecución. No se debe describir como un fallo de vulnerabilidades ni como un PASS de dependencias.

Se corrige únicamente el formato Markdown de las listas y separaciones de las secciones 14.17–14.18. El siguiente commit deberá ejecutar ambos workflows sobre el nuevo HEAD exacto. #119 permanece OPEN / DRAFT. La recuperación desde una conversación nueva y la reconciliación de los worktrees locales continúan pendientes.

### PR #126 — HEAD `2ace99daafbb4bbef1c95470cdbe9e4d686fe9d0`

- PowerShell [44439914633](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439914633): SUCCESS.
- PostgreSQL / Issue [44439914345](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439914345): SUCCESS.
- Security [44439914777](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439914777): SUCCESS; OSV full SKIPPED.
- La revisión 5968332955 sobre `pg_type.typarray` fue retirada como falso positivo mediante el comentario 6997663073. No se cambia el SQL por ese motivo.
- La aprobación de baseline y el uso del algoritmo como contrato estable siguen bloqueados: el identificador continúa siendo `sinayxa-catalog-v1-preview`; falta completar la revisión semántica de cobertura y un baseline independiente aprobado.

### PR #127 — HEAD `4264fa2f77db516922780fe34a514768c964330b`

- PostgreSQL / Issue [44443047619](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443047619): SUCCESS.
- PowerShell [44443047590](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443047590): SUCCESS.
- Security [44443048108](https://github.com/Osleyder1985/SINAYXA/actions/runs/44443048108): SUCCESS; OSV full SKIPPED.
- Las pruebas de memberships allowlisted, SET ROLE y ADMIN OPTION están presentes. La revisión de código y CI de esta PR no constituyen autorización para adoptar una base: el estado operativo permanece `LEGACY_UNVERIFIED`.

### PR #85 y #99

- #85 HEAD `d2a08ea8d104f2a4756e3cd970f5159a270cba25`: PowerShell [44439012103](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439012103), PostgreSQL/Issue [44439012421](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439012421) y Security [44439012589](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439012589) SUCCESS; OSV full SKIPPED. A–E y las evidencias operacionales de #88/#89 siguen abiertas.
- #99 HEAD `d1da9ba3f9c89a27e36d5d4297b1bf755870030d`: PowerShell [44439159091](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439159091) y Security [44439159479](https://github.com/Osleyder1985/SINAYXA/actions/runs/44439159479) SUCCESS; OSV full SKIPPED. Sigue DRAFT y depende de #85.

### Decisión

No se fusiona ninguna PR en este corte. No se modifica `main`, no se usa force-push, no se ejecuta DDL/DML productivo y no se activa adopción legacy. Los checks SUCCESS se atribuyen exclusivamente a los HEAD indicados; los checks SKIPPED no se cuentan como PASS.

