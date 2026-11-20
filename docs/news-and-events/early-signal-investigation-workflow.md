# Early-signal and possible-leak investigation workflow

- **Issue:** [#3 — Detect indications and possible leaks before official announcements](https://github.com/Osleyder1985/SINAYXA/issues/3)
- **Status:** implementation design proposal; not an approved change to the evidentiary methodology.
- **Normative basis:** approved Issue #15 standard and approved Issue #16 source-credibility/independence rubric.
- **Existing capability:** Issue #2 event registry and operator-supplied source/evidence artifacts.
- **Contract dependency:** Issue #78 / PR #85 (logical claim, source-version, evidence and provenance contract 0.2.1); PR #85 is OPEN / NOT MERGED. The current persistence-mapping gap is tracked separately in Issue #153.
- **Scope of this document:** define a reproducible, operator-led investigation workflow using public and lawfully accessible information. It does not implement a crawler, source monitor, automated classification, prediction or trading signal.

## 1. Product objective

SINAYXA should help an analyst investigate whether a publicly observable signal may precede an event that has not yet been officially announced. It must preserve what was knowable at each historical cutoff and distinguish:

1. the underlying event or hypothesis;
2. each concrete assertion about that event;
3. the nature of the information (for example, indication, rumour or possible leak);
4. the evidentiary state of that assertion;
5. the identity, credibility and independence of each source;
6. the exact evidence and its lawful-access basis;
7. what later evidence changed, without rewriting the earlier assessment.

The workflow is successful when another analyst can reconstruct why a signal was investigated, what evidence was available at each cutoff, which alternatives remained plausible and why the conclusion did or did not change.

## 2. Mandatory methodological constraints

This workflow applies the approved standards; it does not create replacement labels or scores.

- Evaluate a **specific assertion and scope**, not an entire article or publisher as one indivisible fact.
- Keep information nature separate from evidentiary state, attribution, document authenticity, source identity, independence and access legitimacy.
- Use only the approved evidentiary states: `NO_CORROBORADA`, `PARCIALMENTE_CORROBORADA`, `CORROBORADA`, `CONTRADICHA`, `REFUTADA`, `NO_RESUELTA`.
- Keep `INDICIO`, `RUMOR`, `POSIBLE_FILTRACIÓN`, `PUBLICACIÓN_OFICIAL` and `HECHO_OBSERVADO` as descriptions of the information's nature, not grades of truth.
- Do not count syndicated articles, translations, citations or reposts as independent corroboration when they derive from the same origin.
- If provenance cannot be established, preserve independence as `DESCONOCIDA`; do not infer it from different domains, authors or brands.
- A primary source confirms only what it directly establishes. Authenticity of a document, integrity of a stored copy and truth of its contents are separate questions.
- Preserve evidence both for and against the assertion, and record at least one plausible alternative explanation where relevant.
- A later official announcement must not rewrite what was known before the announcement. A later confirmation of the event does not automatically authenticate an earlier alleged leak or prove its claimed origin.
- Market price, volume or order-book movements may motivate a research question, but **must never be used as corroboration of the news or proof of a leak**.
- Do not invent probabilities, confidence percentages, source scores, time horizons or causal claims.
- Exclude material obtained through unauthorized access, stolen credentials, intrusion or circumvention. Flag suspected privileged or confidential information for the restrictions in Issue #15; do not solicit or ingest it.

## 3. Investigation lifecycle

### Stage 0 — Open an investigation hypothesis

The analyst creates a candidate event only when there is an identifiable research question. Record:

- a stable investigation/event identifier;
- a neutral, falsifiable description of the hypothesized event;
- potentially affected assets only when there is a defensible link;
- the reason the investigation was opened;
- the analyst and the opening time;
- the initial knowledge cutoff;
- known unknowns and alternative explanations.

Do not title an investigation as a confirmed event or as a leak merely because the signal is unusual.

### Stage 1 — Register each observed signal

For every candidate publication, document, public filing, statement, observable preparation or other signal, record separately:

- exact source reference and original publisher/account where known;
- exact title and the relevant assertion, quoted only to the extent lawful and necessary;
- the source's own stated publication time, including original timezone and precision;
- first observed/detected time and who or what observed it;
- retrieval time, if applicable;
- time the bytes were supplied to the SINAYXA registry;
- the exact content/version identifier and lawful-access status;
- what the signal could support and what it does not establish.

Do not substitute one timestamp for another. In particular:

- `published_at` is the publisher's stated publication time;
- first observation/detection is when the analyst first observed the signal;
- `retrieved_at` is when a copy was retrieved, if distinct;
- registry `captured_at` is assigned when the operator supplies bytes to the existing registry;
- registry `recorded_at` / `inserted_at` records when the item entered the registry.

The current Issue #2 temporal assertion contract uses `first_observed_at`; the Issue #78 contract uses more explicit source-version temporal fields. Their semantic mapping must be reviewed before implementation. Do not silently equate a publisher's timestamp, first public availability, first observation by an analyst, first detection by SINAYXA and registry capture.

If the time is unknown, preserve it as unknown with its precision/limitation; do not estimate a timestamp to make the sequence look complete.

### Stage 2 — Identify the original source and provenance chain

For each publication, establish whether it is:

- an original publication or primary record;
- a direct statement attributed to a named or anonymous source;
- a syndication, translation, summary, repost or quotation;
- an analysis derived from a common dataset or document;
- a derivative whose upstream origin is unknown.

Record each known dependency edge and its supporting evidence. Do not infer an origin from the earliest item found unless the search coverage justifies that limited statement. Use wording such as “earliest located reference in this investigation”, not “original source”, when the actual origin is unknown.

A later publication may be useful for discovery but does not create an independent corroboration path merely by being a separate URL.

### Stage 3 — Assess the signal under Issue #15

For each assertion, document:

- information nature;
- attribution status and source identity as separate dimensions;
- document authenticity, if there is a document;
- access/provenance status;
- evidentiary state and its basis;
- exact supported and unsupported scope;
- evidence gaps and limitations.

For a possible leak, answer separately:

1. Is there a concrete, identifiable and dateable item?
2. What does the item actually assert?
3. What is known about its provenance, and what remains unverified?
4. Is the item authentic, preliminary, partial, recreated or unauthenticated?
5. Was access public or authorized?
6. Does it contain potentially privileged or confidential information requiring restriction?
7. Which assertion components does it support directly, and which are inference?

The initial treatment of a claimed leak should remain `POSIBLE_FILTRACIÓN` with `NO_CORROBORADA` or `NO_RESUELTA`, according to available evidence. The label “leak” does not raise the evidentiary state.

### Stage 4 — Assess source credibility and independence under Issue #16

Apply the approved rubric to the specific assertion, scope, period and intended use. Preserve the dimensions separately:

- source type and knowledge basis;
- identity status;
- access legitimacy;
- proximity and relevant competence;
- traceability and provenance;
- methodology/transparency and accountability;
- relevant correction history;
- incentives/conflicts, where evidenced;
- timeliness;
- assertion-specific support;
- independence of the acquisition/origin chain.

Do not calculate a universal reputation score or numerical credibility weight. A source can be credible in one domain and not competent for another. Anonymous status, a conflict of interest or missing history is a limitation to document, not proof of falsity.

### Stage 5 — Record counterevidence and alternatives

Every substantive assessment must preserve:

- evidence supporting the assertion;
- evidence contradicting it;
- evidence that is relevant but neutral;
- at least one plausible alternative explanation where applicable;
- the precise scope each item addresses;
- unresolved questions and the next verification that could discriminate between explanations.

Examples of alternatives include routine operational preparation, a previously announced plan, a third-party interpretation, a stale document, a draft that was never adopted, a coincidental event or a false/recreated document. These are examples, not mandatory assumptions.

### Stage 6 — Reassess without rewriting history

When a new publication, correction, denial or official announcement appears:

- append a new source version or evidence item when permitted;
- preserve the previous bytes and prior assessment;
- set a new assessment cutoff;
- document exactly which assertion component changed;
- record whether the new material confirms the event, only confirms that a statement was issued, contradicts a detail or leaves the question unresolved;
- preserve the old assessment as the state known at its original cutoff.

Do not backdate detection, registration or assessment. Do not upgrade an earlier signal retrospectively because the hypothesized event later occurred.

## 4. Use of the existing Issue #2 registry

The current registry is operator-driven and does not fetch sources. It can already:

- create an event;
- append source references;
- append temporal assertion versions;
- query the state known at a UTC cutoff;
- register source bytes and extracted evidence bytes supplied by the operator;
- verify SHA-256 and byte length on export;
- preserve append-only histories and generate reproducibility manifests.

The existing CLI entry points are documented in `docs/news-and-events/event-registry.md` and `scripts/news_and_events/register_event.py`:

- `create-event`
- `add-source`
- `append-assertion`
- `show-as-of`
- `history`
- `register-source-artifact`
- `register-evidence-artifact`
- `export-source-artifact`
- `export-evidence-artifact`
- `create-manifest` / `show-manifest`

Use only data the operator is authorized to supply. For real artifacts, the operator must verify the applicable license/access basis and provide the authorization reference required by the registry. A declared `AUTHORIZED` value is not a legal determination by SINAYXA.

### Contract boundary

The current event registry is not, by itself, a complete claim/source-version/provenance assessment engine. PR #85 contains the logical contract 0.2.1 and remains OPEN / NOT MERGED. Issue #88 separates logical contract review from operational C/E and external WORM validation; those operational validations do not by themselves block a provider-neutral logical contract. RET-09's approved 0.2.2 hardening is in PR #99 and remains pending integration.

Until that dependency is resolved:

- do not invent an ad-hoc persistent claim/evidence schema in JSON metadata;
- do not claim that the current event registry automatically evaluates Issues #15/#16;
- do not create a second competing registry;
- do not activate crawling, scraping, continuous monitoring or automated classification;
- keep this workflow as an operator-led investigation procedure and synthetic conformance design.

The concrete contract-to-registry persistence gap was inspected and is tracked in Issue #153. Do not add ad-hoc persistence in this PR; implement the reviewed mapping in #153 after the 0.2.1 contract base is stabilized.


### Contract-to-registry mapping audit — 2026-11-20

A direct comparison of the 0.2.1 schema with the five current PostgreSQL migrations establishes the following boundary:

| 0.2.1 contract entity | Existing #2 registry representation | Mapping status |
| --- | --- | --- |
| Event | `events` | DIRECT for event identity/payload |
| Source identity | `event_sources`, `source_artifacts` | PARTIAL; no typed source-version history |
| Source version and timestamp observations | source artifact metadata plus `temporal_assertions` fields | PARTIAL; these do not preserve the complete versioned source contract |
| Claim and claim component versions | None | MISSING |
| Identity assessment and evaluation unit | None | MISSING |
| Evidence bytes | `evidence_artifacts` | DIRECT for bytes/hash/length; not the full evidence contract |
| Evidence availability by claim/version/cutoff | `temporal_assertions` only partially overlaps | MISSING as a typed relation |
| Claim-evidence links | None | MISSING |
| Provenance nodes and edges | None | MISSING |
| Factor, independence and claim assessments | `temporal_assessments` only derives event chronology | MISSING; semantics are not interchangeable |
| Archive attestations | Source/evidence hashes and capture timestamps only | PARTIAL; no explicit attestation record |

This is a persistence/integration gap, not a reason to create another event registry. Issue #153 defines the required field-level mapping, reuse boundaries, append-only migrations and regression tests. The temporal event assertion is not an analytical claim; the event's derived temporal assessment is not an evidentiary or source-credibility assessment.

### Current operational boundary

- The artifact-storage and TRUNCATE-guard work in PR #111 is already merged into `main` (merge commit `3e6c764ed8fb72d190351aa99ebb856f5933e2d3`). The registry documentation must not describe it as still under review.
- C/E operational validation remains in #89. WORM/Object Lock remains separate in #152. Neither should be conflated with the logical mapping in #153.
- PR #85 remains OPEN / NOT MERGED. Do not implement against an unstable contract SHA or merge by assuming that successful CI alone is a human approval.

## 5. Minimum investigation record

The following is a conceptual checklist, not a new JSON contract. A field may be unknown only when the unknown state and reason are explicit.

| Area | Minimum information |
| --- | --- |
| Investigation | Stable ID, neutral hypothesis, opening reason, analyst, opening time, cutoff |
| Assertion | Exact proposition, component/scope, information nature, attribution |
| Source | Stable source reference, publisher/author if known, identity status, source type |
| Time | Published, first observed/detected, retrieved, registry captured, registry recorded; original timezone and precision |
| Provenance | Original/derivative status, known upstream references, dependency evidence, unknown links |
| Access | Public/authorized basis, license/authorization reference, restrictions |
| Artifact | Exact bytes when lawful, media type, version, SHA-256, extraction provenance |
| Assessment | Issue #15 evidentiary state, basis, supported/unsupported scope, limitations |
| Source review | Issue #16 factors and independence state for this assertion |
| Counterevidence | Supporting, contrary, neutral evidence and alternative explanations |
| History | Cutoff, reviewer, rule/method version, prior assessment reference, reason for change |

## 6. Synthetic acceptance scenarios for the future implementation

These cases are intended to become executable fixtures after the contract integration is resolved. They are not empirical validation and do not introduce new methodology.

| ID | Scenario | Required behaviour |
| --- | --- | --- |
| ES-01 | A public filing appears before an official announcement and directly establishes only that a filing was submitted | Preserve the filing and time sequence; do not infer approval or execution |
| ES-02 | Five outlets reproduce one anonymous post | Record the dependency chain; do not count five independent sources |
| ES-03 | A possible leak is later followed by an official announcement of the event | Confirm only the event scope established by the official evidence; preserve the earlier leak's original authenticity/provenance state |
| ES-04 | A document's stated publication time predates detection, but no evidence proves it was publicly available then | Keep the stated time distinct from first observed/available time; do not backdate availability |
| ES-05 | A source corrects one material detail | Append a new version and assess the corrected component at a later cutoff; preserve the earlier version and assessment |
| ES-06 | An anonymous source is quoted by two outlets that share an upstream origin | Independence remains dependent or unknown, not independent |
| ES-07 | A document is authentic but its central assertion is contradicted by direct evidence | Separate authenticity from evidentiary state; record both lines and exact scope |
| ES-08 | The event occurs after an earlier ambiguous signal | Do not retrospectively promote the earlier signal or claim it caused the event |
| ES-09 | A signal is based only on price/volume movement | It cannot be corroborating evidence for the news or a leak |
| ES-10 | A source item may contain privileged or unlawfully obtained information | Do not ingest or preserve it; apply Issue #15 restrictions and escalate review |
| ES-11 | The origin of a repost cannot be located | Record the earliest located reference and origin unknown; do not call it the original source |
| ES-12 | A later denial addresses only one component of a multi-part assertion | Reassess only the addressed component; leave other components unresolved unless separately evidenced |

For each case, future automated tests must assert both the allowed result and the prohibited inference. Tests must not invent probabilities, thresholds or empirical performance claims.

## 7. Implementation sequence and gates

1. **Gate 1 — contract integration:** resolve Issue #88 and review/merge PR #85 only when its explicit acceptance criteria are met. Current CI success alone does not close the outstanding semantic and operational gaps.
2. **Gate 2 — workflow mapping:** map the investigation checklist and ES-01–ES-12 to the approved contract entities and existing Issue #2 registry; document any genuine schema gap before proposing a change.
3. **Gate 3 — synthetic conformance:** implement only deterministic validations supported by the approved standards, with positive, negative and boundary cases. Human judgments (truth, semantic scope, authenticity and real-world source independence) remain review decisions.
4. **Gate 4 — operator-assisted pilot:** use a small set of public, lawfully accessible historical cases with provenance and authorization records. Report coverage and limitations; do not call the sample statistically representative.
5. **Gate 5 — optional acquisition automation:** consider a provider/API/feed integration only after separate review of terms, lawful access, privacy, rate limits, retention and operational cost. No default crawling or scraping.
6. **Gate 6 — market linkage:** only after event/source evidence is sound, connect an assessed event to asset movements as a separate analysis. Temporal association is not causation; price action is never evidence that a leak is true.

## 8. Explicit non-goals

This workflow does not deliver:

- a news aggregator or crawler;
- automatic source discovery or continuous monitoring;
- automatic truth, leak or credibility classification;
- numerical credibility scores or event probabilities;
- predictions, buy/sell recommendations or trading signals;
- proof of causal impact on an asset;
- authorization to collect private, confidential or privileged material;
- WORM/Object Lock infrastructure or a new storage platform.

## 9. Definition of done for this design stage

- The workflow reuses Issues #15 and #16 without changing their semantics.
- It reuses the existing Issue #2 registry and does not create a competing persistence model.
- It preserves publication, observation, retrieval and registry timestamps as distinct concepts.
- It specifies counterevidence, alternatives, provenance and historical cutoffs.
- It includes explicit safeguards against retrospective confirmation, republication counting and price-based corroboration.
- It identifies the #78/#85/#88 contract integration gate and makes no claim of production implementation.

Passing these design criteria does not close Issue #3. The functional requirement remains open until the approved contract mapping, executable tests and operator-assisted validation are complete.
