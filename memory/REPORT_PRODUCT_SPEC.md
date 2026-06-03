# REPORT_PRODUCT_SPEC.md

**Status:** PROPOSED (not yet implemented).
**Locked:** 24 February 2026.
**Audience:** Engineering + product + legal review. Any change to this file
requires owner sign-off before any code refactor.
**Constraints:** This spec is an overlay on the existing codebase. It does
NOT delete or rename any existing code, route, database key, or payment
feature. It defines the **target product state**; a separate refactor plan
(to be approved later) will map the path from current → target.

---

## 1. Product tier overview

| # | Product tier (UI label) | Price | Gate type | Prerequisite |
|---|---|---|---|---|
| T0 | **Free Grounds Detection** | Free | Open (post-upload) | At least one document uploaded |
| T1 | **Case Summary** | Free | Open | Case created |
| T2 | **Grounds Unlock** | **AUD $99** | Payment | Case Summary generated |
| T3 | **Full Detailed Report** | **AUD $150** | Payment | Grounds Unlock purchased |
| T4 | **Extensive Log Report** | **AUD $200** | Payment | Full Detailed Report purchased |
| T5 | **Appellate Research Brief** | Free | Content-gated | T1 + T3 + T4 all exist + completed |

The 5 paid/content-gated tiers together form the **canonical report stack**.
No other report offered by the app sits inside this stack — derivative
exports (Barrister Quick Research Brief, Acceptance Pack, Complete Case
Pack, Timeline PDF, Translated Report, Payment Receipt) are output formats
of these five, not independent products.

---

## 2. Full product specification — tier by tier

### T0 · Free Grounds Detection

**What the user sees after upload**

> *"We detected **N potential grounds** in your case materials. Unlock
> the full Grounds of Merit analysis for $99 to see the titles,
> detailed investigation, legal framework mapping, and appellate
> pathways."*

**Locked UI state**

- Numeric count only (`N potential grounds`).
- A single "Unlock Grounds ($99)" button.
- **No ground titles**, no ground descriptions, no framework, no pathways,
  no analysis, no strength indicators, no law-section citations.

**Backend contract**

| Attribute | Value |
|---|---|
| Storage | `db.grounds_of_merit` (titles exist in DB; API response redacts them) |
| Response when unlocked = false | `{ "ground_count": N, "titles_available": false, "analysis_available": false }` |
| Response when unlocked = true | Full ground objects |
| Route | `GET /api/cases/{id}/grounds` (existing — response shape gains a redaction mode) |
| Feature key | `grounds_of_merit` (canonical) / `grounds_unlock` (alias) |

**Must include**
- Count of detected grounds.
- Explanatory sentence about what unlocking reveals.

**Must NOT include**
- Ground titles.
- Ground types (`judicial_error`, `sentencing_error`, etc.).
- Strength / confidence indicators.
- Any analysis text.
- Any legal-reference text.

---

### T1 · Case Summary (FREE)

**UI label:** "Case Summary"
**Backend `report_type`:** `quick_summary` *(existing key preserved —
no DB rename; only the UI label changes)*
**Payment feature key:** none (free)

**Purpose**
Plain-English summary of the case that helps the user understand what they
uploaded — orientation only. Contains **no grounds of merit, no legal
strategy, no appellate analysis**.

**Exact section list**
1. CASE SNAPSHOT
   - Appellant name, jurisdiction, offence type, sentence, court of
     conviction, plea (if known), sentence date.
2. CASE NARRATIVE
   - 3–5 paragraphs of plain-English summary of the facts as recorded.
3. DOCUMENTS UPLOADED
   - Names + one-line description of each uploaded document.
4. KEY DATES
   - Date of offence, date of conviction, date of sentence, appeal lodging
     deadline.
5. APPEAL DEADLINE STATUS
   - Days remaining (or expired).
6. WHAT HAPPENS NEXT
   - Four-bullet list linking T2 (Grounds Unlock) and T3/T4 (paid reports)
     with price labels.

**Must include**
- Facts drawn strictly from uploaded documents + case metadata.
- AU spelling; Times New Roman export per `print_styles.py` canonical spec.
- Disclaimer: NOT LEGAL ADVICE.

**Must NOT include**
- Grounds of merit (titles, types, analysis, count).
- Appellate pathways / statutory framework.
- Sentencing comparisons.
- Legal recommendations or strategy.
- "Appeal outlook" / "likelihood of success" language.
- Precedent case references.

> **Change from current state:** The existing `quick_summary` report today
> includes sections 3 ("All Grounds Identified (Preview)") and 4 ("Key
> Legislation (Preview)"). Under this spec those two sections move to T2/T3.
> The existing prompt at `services/report_generator.py:690` MUST be updated
> in the refactor (not now) to drop grounds and legislation from T1 output.

---

### T2 · Grounds Unlock — AUD $99

**UI label:** "Unlock Grounds of Merit"
**Backend:** not a persisted report; unlocks fields on `db.grounds_of_merit`
**Payment feature key:** `grounds_of_merit` (canonical) / `grounds_unlock`
(alias — both currently in `FEATURE_TYPE_ALIASES`, both must remain valid)
**Payment price key:** `FEATURE_PRICES["grounds_of_merit"]` = $99.00 AUD

**Purpose**
Reveals the full Grounds of Merit investigation for the case.

**Exact content unlocked**
1. **Ground titles + types** for every detected ground.
2. **Detailed grounds investigation** — per-ground analysis block:
   - Description
   - Legal issue
   - Evidence support
   - Strength rating
   - Verification status
3. **Legal framework** per ground:
   - Relevant Acts and sections (NSW/VIC/QLD/SA/WA/TAS/NT/ACT/CTH)
   - Common-law authorities
   - Appellate-pathway classification (conviction, sentencing, leave,
     procedural, etc.)
4. **Appeal pathways** — jurisdiction-specific pathway string from
   `frameworks/appeal.py` (e.g. *"Criminal Appeal Act 1912 (NSW) s 5"*).

**Must include**
- Every ground stored in `db.grounds_of_merit` for the case.
- Deduplicated titles (fuzzy-dedup via `services/ground_dedup.py`).
- Jurisdiction-correct legislation (no silent NSW fallback per the
  National Framework engine).

**Must NOT include**
- Strategic appeal recommendations.
- Counsel-grade submissions drafting.
- Precedent outcome matrix.
- Sentencing comparison tables (reserved for T3).
- Plain-English client brief (reserved for T3).

**UI states**

| State | UI |
|---|---|
| Locked | Count-only badge + "Unlock ($99)" button |
| Payment submitted | "Awaiting confirmation" amber badge |
| Payment pending | "Pending" blue badge |
| Unlocked | Full grounds list + per-ground investigation cards |
| Admin bypass | Same as Unlocked |

---

### T3 · Full Detailed Report — AUD $150

**UI label:** "Full Detailed Report"
**Backend `report_type`:** `full_detailed`
**Payment feature key:** `full_report` (canonical) / `full_detailed` (alias)
**Payment price key:** `FEATURE_PRICES["full_report"]` = $150.00 AUD

**Purpose**
Counsel-grade dossier that composes T1 + T2 + the case's timeline +
uploaded documents + the legal framework into a single deep report.

**Prerequisite**
T2 (Grounds Unlock) purchased OR user is admin.
*(If the user attempts T3 while T2 is still locked, the 402 response must
instruct them to unlock grounds first.)*

**Exact section list (15 sections)**
1. EXECUTIVE BRIEF
2. FORENSIC CASE CHRONOLOGY  *(draws from `db.timeline_events` + case extract)*
3. DOCUMENT EVIDENCE DIGEST  *(draws from `db.document_extracts`)*
4. GROUNDS OF MERIT — APPELLATE PATHWAY ANALYSIS  *(requires T2; draws from `db.grounds_of_merit`)*
5. COMPARATIVE SENTENCING TABLE (8+ CASES)
6. COMMON APPEAL GROUNDS FOR THIS OFFENCE TYPE  *(from `frameworks/appeal.py`)*
7. OUTCOME OPTIONS AVAILABLE
8. EVIDENTIARY GAPS + REMEDIATION CHECKLIST
9. PRECEDENT OUTCOME MATRIX (10–12 CASES)
10. STATUTORY + DOCTRINAL FRAMEWORK MAP  *(via `national_framework_engine.py`)*
11. HOW TO ARGUE EACH TOP GROUND
12. SUBMISSIONS BLUEPRINT
13. HOW TO START YOUR APPEAL + REQUIRED FORMS  *(jurisdiction-specific)*
14. PRIORITISED ACTION PLAN
15. CLIENT PLAIN-ENGLISH BRIEF

**Must include**
- All content of T1 folded into sections 1–3.
- All content of T2 folded into sections 4 + 10.
- Jurisdiction-correct statutory references.
- Third-person forensic appellate language (no "we/us/our/you/your").

**Must NOT include**
- "Hearing preparation pack" or "Conference preparation pack" (T4 only).
- "Court pathway operations playbook" (T4 only).
- "Operations engine — critical missing evidence" (T4 only).
- Deep 900+ word per-ground expansions (T4 only).
- Counsel Synthesis section (T5 only).

---

### T4 · Extensive Log Report — AUD $200

**UI label:** "Extensive Log Report"
**Backend `report_type`:** `extensive_log`
**Payment feature key:** `extensive_report` (canonical) / `extensive_log` (alias)
**Payment price key:** `FEATURE_PRICES["extensive_report"]` = $200.00 AUD

**Purpose**
Master litigation brief that **combines and expands on T3** and adds its
own deeper forensic commentary, evidence log, contradictions, strategy,
and action plan.

**Prerequisite**
T3 (Full Detailed Report) purchased OR user is admin.

**Exact section list (24 sections)**
1. EXECUTIVE BRIEF (expanded)
2. FORENSIC CASE CHRONOLOGY (expanded)
3. DOCUMENT EVIDENCE DIGEST (expanded)
4. GROUNDS OF MERIT — DEEP APPELLATE ANALYSIS  *(900+ words per ground)*
5. COMPARATIVE SENTENCING TABLE (12+ CASES)
6. COMMON APPEAL GROUNDS FOR THIS OFFENCE TYPE
7. OUTCOME OPTIONS — DETAILED PATHWAY ANALYSIS
8. EVIDENTIARY GAPS + REMEDIATION CHECKLIST
9. PRECEDENT OUTCOME MATRIX (15+ CASES)
10. STATUTORY + DOCTRINAL FRAMEWORK MAP
11. HOW TO ARGUE EACH TOP GROUND — DETAILED STRATEGY
12. SUBMISSIONS BLUEPRINT
13. HEARING PREPARATION NOTES
14. CONFERENCE PREPARATION PACK
15. COURT PATHWAY OPERATIONS PLAYBOOK
16. HOW TO START YOUR APPEAL + REQUIRED FORMS
17. SIMILAR CASE SEARCH OPTIONS
18. PRIORITISED ACTION PLAN
19. OPERATIONS ENGINE — CRITICAL MISSING EVIDENCE
20. FORENSIC COMMENTARY — CASE-SPECIFIC
21. EVIDENCE LOG (TIMELINED, CROSS-REFERENCED)
22. CONTRADICTIONS REGISTER  *(pulls from `db.contradictions`)*
23. STRATEGIC DECISION TREE
24. DEEP ACTION PLAN

**Must include**
- Every section of T3 (expanded).
- Strict forensic commentary for sections 20–24 (no speculation beyond
  the record; any inference must be flagged as such).
- Cross-reference to each document extract that supports each finding.

**Must NOT include**
- Counsel Synthesis section (T5 only).
- Composite Source-Report Synthesis (T5 only).
- Any invented authority or precedent not resolvable to real case law.

---

### T5 · Appellate Research Brief (FREE, content-gated)

**UI label:** "Appellate Research Brief"
**Backend `report_type`:** `barrister_view`
**Payment feature key:** none (free)
**Content gate:** T1 **AND** T3 **AND** T4 all exist and have `status =
completed` (enforced by
`services/barrister_generator.py::_get_latest_standard_reports`).

**Purpose**
Counsel-only synthesis brief. Consumes the three generated reports
(T1 + T3 + T4) and produces a barrister-ready research brief. Not a
replacement for T3 / T4 — it sits ABOVE them.

**Exact section list**
1. COUNSEL SYNTHESIS
   - Primary Issue · Secondary Issue · Tertiary Issue
   - Priority Order
   - Overall Appellate Position
2. EXECUTIVE OVERVIEW FOR COUNSEL
3. SOURCE REPORT SYNTHESIS
   - Quick Summary Synthesis
   - Full Detailed Report Synthesis
   - Extensive Log Synthesis
4. CASE BACKGROUND AND PROCEDURAL HISTORY
5. CONVICTION, OFFENCE AND SENTENCE ANALYSIS
6. EVIDENTIARY TENSIONS AND APPEAL PRESSURE POINTS
7. GROUNDS OF MERIT (one `### Ground N:` block per stored ground)
8. STATUTORY FRAMEWORK AND GOVERNING TESTS
9. AUTHORITIES AND COMPARATIVE CASES *(with comparative authorities table)*
10. SENTENCING COMPARISON AND RELIEF PATHWAYS *(with sentencing comparison table + relief pathways matrix)*
11. EVIDENTIARY PRESSURE POINTS TABLE

**Must include**
- At least one `### Ground N:` subsection for every ground in
  `db.grounds_of_merit`.
- Source-report cross-references (which of T1/T3/T4 contributed each
  paragraph of synthesis).
- Jurisdiction-correct legislation.

**Must NOT include**
- Any non-forensic language ("we/us/our").
- Any generic legal advice not traceable to the sourced T1/T3/T4 content.
- Any new ground not present in `db.grounds_of_merit`.

---

## 3. Cross-tier mapping table

### 3.1 Frontend button labels

| Tier | Button label (PROPOSED) | Current label to change from |
|---|---|---|
| T0 | "N potential grounds detected · Unlock for $99" | (new — no current equivalent) |
| T1 | "Generate Case Summary" | "Generate Quick Summary" |
| T2 | "Unlock Grounds of Merit ($99)" | "Unlock Grounds" |
| T3 | "Generate Full Detailed Report ($150)" | unchanged |
| T4 | "Generate Extensive Log Report ($200)" | unchanged |
| T5 | "View Appellate Research Brief" (only visible once T1+T3+T4 ready) | "View Appellate Research Brief" (unchanged) |

### 3.2 Backend `report_type` keys (DB + API contract)

| Tier | `report_type` key | Stored in `db.reports`? |
|---|---|---|
| T0 | *(n/a — uses `db.grounds_of_merit` directly)* | No |
| T1 | `quick_summary` | Yes |
| T2 | *(n/a — payment only, unlocks fields on T0 data)* | No |
| T3 | `full_detailed` | Yes |
| T4 | `extensive_log` | Yes |
| T5 | `barrister_view` | Yes |

**Constraint:** Existing keys must NOT be renamed. Only UI labels and
prompt content change. This preserves every historical payment,
pipeline test, and report persisted to date.

### 3.3 Payment feature keys (Stripe / internal)

| Tier | Canonical feature key | Accepted aliases (all must keep resolving) | Price (AUD) |
|---|---|---|---|
| T2 | `grounds_of_merit` | `grounds_unlock` | 99.00 |
| T3 | `full_report` | `full_detailed` | 150.00 |
| T4 | `extensive_report` | `extensive_log` | 200.00 |

Source of truth: `backend/models/__init__.py::FEATURE_PRICES` +
`FEATURE_TYPE_ALIASES` + `canonical_feature_type()` helper.

### 3.4 Locked / unlocked UI states

| Feature | Locked UI | Payment submitted | Unlocked UI |
|---|---|---|---|
| T2 Grounds | Count-only badge + "Unlock ($99)" | "Awaiting confirmation" (amber) | Full grounds list + investigation |
| T3 Full Detailed | "Generate Full Detailed ($150)" button | "Pending" (blue) → "Generating…" | "Regenerate" + "View" buttons |
| T4 Extensive Log | "Generate Extensive Log ($200)" button | "Pending" → "Generating…" | "Regenerate" + "View" + "Barrister Brief" button appears |
| T5 Research Brief | **Button hidden** until T1+T3+T4 complete | n/a | "View Appellate Research Brief" button |

All four gate states already exist in
`frontend/src/components/ReportsSection.jsx::getPaymentBadge` — no
new states required.

### 3.5 Admin bypass (CRITICAL — must be preserved everywhere)

| Path | Bypass check | File |
|---|---|---|
| T2 grounds response | `is_admin_user(user.email)` → title + analysis both returned | `routers/grounds.py:685` |
| T3 generation | `is_admin_user(user.email)` → skip `db.payments` lookup | `routers/reports.py:209` |
| T4 generation | `is_admin_user(user.email)` → skip `db.payments` lookup | `routers/reports.py:229` |
| T5 content gate | No admin bypass — even admins need T1+T3+T4 to exist | by design |

### 3.6 Deliverable formats per tier

| Tier | HTML view | Print | PDF | DOCX |
|---|---|---|---|---|
| T0 | Yes (Grounds tab, count-only) | — | — | — |
| T1 | `ReportView.jsx` | ✓ (canonical print CSS) | ✓ `export_report_pdf` | ✓ `export_report_docx` |
| T2 | `GroundsOfMerit.jsx` | ✓ | — (no dedicated PDF route; covered by T3 + R6 + R7) | — |
| T3 | `ReportView.jsx` | ✓ | ✓ | ✓ |
| T4 | `ReportView.jsx` | ✓ | ✓ | ✓ |
| T5 | `BarristerView.jsx` | ✓ | ✓ `barrister-view/export-pdf` | ✓ `barrister-view/export-docx` |

---

## 4. Data-source matrix (read-only inputs per tier)

| Tier | Reads |
|---|---|
| T0 | `db.cases`, `db.grounds_of_merit` (count only) |
| T1 | `db.cases`, `db.documents`, `db.document_extracts`, `db.case_extracts` |
| T2 | `db.grounds_of_merit`, `frameworks/*` (appeal, sentencing, evidence, mental_impairment, mens_rea) |
| T3 | T1 sources + T2 sources + `db.timeline_events` + `db.issue_classifications` + `db.issue_verifications` + `frameworks/*` |
| T4 | T3 sources + `db.contradictions` + `db.notes` (if user opted in) + deeper extract of `document_extracts` |
| T5 | `db.reports` (latest completed `quick_summary` + `full_detailed` + `extensive_log`) + `db.grounds_of_merit` + `frameworks/*` |

---

## 5. Exclusions — what this spec is NOT

- NOT a refactor plan. No files to be touched under this document.
- NOT a rename of DB keys, route URLs, or payment feature keys.
- NOT a change to the existing  blocks in `reports.py`,
  `report_generator.py`, `grounds.py`, `pipeline_actions.py`.
- NOT a change to the canonical print-style engine
  (`services/print_styles.py` + `utils/printStyles.js` — locked 24 Feb 2026).
- NOT a change to the national framework engine
  (`services/national_framework_engine.py` — frozen).

---

## 6. What implementation will eventually require (reference only)

When and only when the owner approves a refactor, the sequence below is the
**cheapest safe path** to the target state. Listed here so engineering has
a shared mental model — NOT a commitment to execute.

1. **UI-label flip only** — rename "Quick Summary" → "Case Summary" in
   `REPORT_TYPES` array + every button / badge / toast. No backend change.
   Zero risk.
2. **T1 prompt trim** — remove sections 3 + 4 (grounds preview + legislation
   preview) from the `quick_summary` prompt in `report_generator.py:690`.
   Add regression test: T1 output must not contain `## ALL GROUNDS` or
   `## KEY LEGISLATION`.
3. **T0 count-only UI** — add a read-only API mode to
   `GET /api/cases/{id}/grounds` that returns
   `{ ground_count: N, titles_available: false }` when T2 is locked. The
   existing response shape continues to work for unlocked users.
4. **T0 frontend** — update `GroundsOfMerit.jsx` to render count-only card
   when `titles_available === false`. Hide all existing ground rendering
   behind that flag.
5. **T2 prerequisite for T3** — add a soft gate in `routers/reports.py` that
   returns a 402 payload including `"prerequisite": "grounds_of_merit"` if
   T3 is requested while T2 is locked. Existing T3 payment flow unchanged;
   only the copy of the 402 message changes.
6. **T3 prerequisite for T4** — analogous soft gate. `"prerequisite":
   "full_report"`.
7. **T5 button visibility rule** — already enforced content-gate in
   `barrister_generator.py::_get_latest_standard_reports`. No change.
8. **Price display** — ensure all buttons show the $99 / $150 / $200 price
   label explicitly (currently priced only in some places).
9. **Regression suite** — add `test_report_product_spec.py` asserting each
   tier's must-include / must-NOT-include content rules.

Each step above is independently revertable. No step deletes code. No
schema change. No payment-history migration.

---

## 7. Governance

- Any change to tier names, prices, feature keys, or prerequisites requires
  an update to **this document first**, signed off by owner, before any
  code change.
- Any new report product must either (a) join this spec as a new tier, or
  (b) be explicitly carved out as a derivative output format of an existing
  tier (as the Barrister Quick Research Brief, Acceptance Pack, and
  Complete Case Pack currently are).
- Any deprecation of a deprecated endpoint
  (`/api/cases/*` legacy pipeline routes — see
  `memory/DEPRECATED_ENDPOINTS.md`) is independent of this spec.

---

## 8. Change log

| Date | Author | Change |
|---|---|---|
| 24 Feb 2026 | E1 (proposed, awaiting owner sign-off) | Initial draft following 7-point owner directive locking six-tier product stack |
