# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features: secure document management, AI-powered case analysis, tiered reporting system (Free Quick Summary, $150 Full Detailed, $200 Extensive Log, locked Appellate Research Brief).

## Core Requirements
- **Report Tiers:** Strictly scale in depth. Appellate Research Brief is capstone synthesis.
- **Report Language:** STRICT third-person educational tool. No "we", "us", "our", "you", "your". Forensic appellate language.
- **Branding:** Forced light mode globally. High contrast only. No amber/brown (blue/slate/navy). Bright blue action buttons with white text.
- **Print/Export:** Exacting standards for footer, TOC, paragraph numbering, layout parity between on-screen and exported (PDF/Word/Print).
- **Australian English:** analyse, organise, judgement, offence throughout.
- **Independence:** All Emergent branding / auth / LLM proxy dependencies removed — app runs on user's personal OpenAI key and direct Google OAuth.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI
- Backend: FastAPI + MongoDB
- AI: OpenAI GPT-4o directly via user's personal API key (no Emergent proxy)
- Auth: Direct Google OAuth (state+localStorage+cookie CSRF protection)
- Email: Resend
- Payments: PayID
- Mobile: Capacitor (native app build finalised)

## Key Files
- `/app/backend/offence_framework.py` — 3,950+ line forensic legal dictionary (all 8 states + Cth, 18 offence categories, mens rea + 13-stage procedural flow)
- `/app/backend/services/offence_helpers.py` — LLM context builder
- `/app/frontend/src/utils/exportHtml.js` — Shared export CSS/HTML wrapper
- `/app/frontend/src/pages/BarristerView.jsx` — Appellate Research Brief view + custom export builder
- `/app/frontend/src/pages/ReportView.jsx` — Standard report view + custom export builder
- `/app/frontend/src/pages/CaseDetail.jsx` — Case detail with Print All/PDF All/Word All + Progress export
- `/app/frontend/src/components/ExportOptionsModal.jsx` — section picker for exports
- `/app/frontend/src/pages/SignupSourceAnalytics.jsx` — conversion tracking dashboard

## What's Been Implemented

### Completed (Previous Sessions)
- Full multi-tier report generation pipeline (Quick Summary, Full Detailed, Extensive Log, Appellate Research Brief)
- Document upload, timeline generation, grounds of merit investigation
- Case metadata, jurisdiction warnings
- PayID payment system, case sharing, translation, native mobile build
- All print-export formatting parity fixes (11 Apr 2026)
- Grounds Appellate Pathway restoration (14 Apr 2026)
- Legal Framework v1 hardening (14 Apr 2026)
- Blank pipeline button / metadata banner fixes

### Completed (Current Session — handoff + new work)
- **Google OAuth CSRF state mismatch** — resolved via click-time state + localStorage + domain-scoped cookie
- **Direct OpenAI key integration** — replaces Emergent proxy; runs on user's personal `OPENAI_API_KEY` with GPT-4o
- **Print / PDF / Word export overhaul** — CSS Paged Media, dynamic footers, landscape tables, correct colours
- **Export Options Modal** — user can pick sections to include per export type
- **Conversion tracking + `/admin/analytics` dashboard** — signup source + CTA conversion rates
- **Security audit & hardening** — CORS fix + global Axios 401 interceptor
- **Emergent branding purge + "Founded by Deb King" byline** across 14 public pages
- **UI bug fixes** — 5 broken Google-login CTA buttons + CaseChat UI overlap

### Completed (14 February 2026 — Legal Framework Gap Fill)
- **Terrorism state coverage** — added NSW/VIC/QLD/SA/WA/TAS/NT/ACT terrorism police-powers & preventative-detention Acts with Cth cross-reference stubs
- **Organised_crime completeness** — filled TAS (Police Offences Act 1935), NT (Serious Crime Control Act 2009), ACT (Crimes (Criminal Organisations Control) Act 2012); added Cth Criminal Code Div 390
- **Cth gap fills** — added Commonwealth entries for `extortion_blackmail` (Criminal Code s.138-139), `arson_property_damage` (Crimes Act 1914 s.29, Criminal Code Pt 7.8), `domestic_violence` (Family Law Act 1975 Pt VII Div 11, Criminal Code s.474.17), `public_order` (Criminal Code Pt 9.1, Crimes Act 1914 s.76/89), `robbery_theft` (Criminal Code Ch 7 Pt 7.2 Div 131-134)
- **13-stage forensic procedural flow** (`INDICTABLE_PROCEDURE_FLOW`, `HYBRID_PROCEDURE_FLOW`, `SUMMARY_PROCEDURE_FLOW`) — Incident → Arrest → Charge → Bail → First Mention → Committal → Indictment → Trial Prep → Trial → Verdict → Sentencing → Intermediate Appeal → High Court s.35A special leave. Every category now carries the pipeline tailored to its offence class.
- **Mens rea framework** (`MENS_REA_FRAMEWORK`) — intention/knowledge/recklessness/negligence/strict/absolute with authorities (He Kaw Teh, Crabbe, Aubrey, Nydam, Lavender) and application examples. Each of 18 offence categories references its relevant fault elements.
- **Context builder upgrade** — `offence_helpers.py` now surfaces `RELEVANT MENS REA` and `FORENSIC PROCEDURAL PIPELINE` sections into LLM prompts per case.
- **Currency tracker** — `LEGISLATION_CURRENCY.last_verified = "2026-02-14"`.
- **Regression tests** — `tests/test_framework_gap_fill_20260214.py` (12 new tests) + full framework suite green (409 passed).

### Completed (14 February 2026 — P1 OpenAI Cost Tracking Dashboard)
- **AI Usage Tracker** (`/app/backend/services/ai_usage_tracker.py`) — estimates tokens via `tiktoken` o200k_base; applies OpenAI Feb 2026 rate card (gpt-4o $2.50/$10 per 1M in/out; gpt-4o-mini $0.15/$0.60 per 1M); extracts case_id + report_type from session_id conventions; writes fire-and-forget to `ai_usage` Mongo collection.
- **LLM instrumentation** — `call_llm_structured` in `services/llm_service.py` records usage on success (swallow-on-error; LLM flow never blocked).
- **Admin endpoint** — `GET /api/admin/openai-costs?period=month|week|all` returns totals (cost_usd, tokens, calls, success/fail), projected month-end USD, per-model / per-task / per-report-type / per-user breakdowns, and a daily series.
- **Frontend panel** (`/app/frontend/src/components/OpenAICostsPanel.jsx`) — mounted at top of `/admin/analytics`. Four stat cards (USD spent, projection, tokens, success rate), period selector (7-day / month / all), daily sparkline, three breakdown cards, top-users table, pricing note.
- **Regression tests** — `tests/test_ai_usage_tracker.py` (24 tests) covering pricing, token estimation, session-id extractors, DB write, and error-swallow contract.
- **Testing-agent verified** — iteration_207.json confirms 100% pass on backend (433/433 + 13 new endpoint tests) and 100% on frontend (panel + preserved signup-source analytics). Zero critical/minor bugs.

### Completed (14 February 2026 — P2 Refactor: Frameworks Package)
- **Split `offence_framework.py` (3,970 lines) into `/app/backend/frameworks/` package** (13 themed modules):
  - `jurisdictions.py`: `LEGISLATION_CURRENCY`, `AUSTRALIAN_STATES`
  - `procedure.py`: `INDICTABLE/HYBRID/SUMMARY_PROCEDURE_FLOW`, `MENS_REA_FRAMEWORK`
  - `offences.py`: `OFFENCE_CATEGORIES` (all 18)
  - `states.py`: NSW/VIC/QLD/SA/WA/TAS/NT/ACT `_CRIMINAL_FRAMEWORK`
  - `federal.py`: `FEDERAL_CRIMINAL_FRAMEWORK`, `FEDERAL_FAULT_ELEMENTS`, `PROCEEDS_OF_CRIME_FRAMEWORK`
  - `appeal.py`: `APPEAL_FRAMEWORK`, `APPEAL_GROUNDS_ACCESSIBILITY`
  - Plus `common_grounds.py`, `human_rights.py`, `recent_updates.py`, `sentencing.py`, `evidence.py`, `mental_impairment.py`, `landmark_cases.py`
- **Back-compat shim** — `offence_framework.py` reduced from 3,970 → 10 lines; re-exports everything via `from frameworks import *`. All existing imports (`from offence_framework import OFFENCE_CATEGORIES` etc.) continue to work unchanged across routers/services/tests.
- **Identity-preserving** — all 27 public symbols are the SAME object via both import paths.
- **Regression tests** — `tests/test_frameworks_refactor.py` (5 tests) lock in import parity, star-import behaviour, and data integrity.
- **Full suite green** — 446 passed / 2 skipped across all framework + AI usage + refactor tests.

### Completed (14 February 2026 — Translate reliability + Admin UX + Cost per Brief)
- **Translate concurrency** — `routers/translate.py` `_run_translation_background` now uses `asyncio.Semaphore(3)` so chunks translate in parallel. Regression test proves 6 chunks complete in <0.9s (vs 1.2s sequential) — meaningful 3× wall-time reduction without tripping OpenAI rate limits.
- **Translate restart-recovery** — new `_persist_task()` mirrors task state to Mongo `translation_tasks` collection; `/translate/status` falls back to Mongo when in-memory `_translate_tasks` is empty (simulates backend restart). Returns `recovered: true` flag so the UI knows state was recovered.
- **Translate frontend polling** — `ReportTranslator.jsx` bumped `maxAttempts` from 120 → 300 and `pollInterval` from 4s → 5s (25-minute ceiling instead of 8 minutes). Handles Appellate Research Briefs with 15–25 chunks comfortably.
- **Admin Dashboard reorder** — PayID Pending Payments section moved to the TOP of `/admin` (above Live Visitor Statistics) so new transfers are the first thing seen.
- **AI Cost Badge (friendly nudge)** — new `GET /api/cases/{case_id}/ai-cost` endpoint (owner-only) + `<AiCostBadge>` component mounted above the Reports tab on `/cases/:id`. Shows "Estimated AI cost: $X.XX across N AI calls" + per-report-type pills. Silent when no usage has been recorded yet (intentional — older cases show nothing until new AI calls run).
- **Cost tracker regex fix** — `_extract_case_id` / `_extract_report_type` in `ai_usage_tracker.py` now support the production `case_<12hex>` case_id format (e.g. `case_ec9b7141be1b`) alongside legacy UUIDs.
- **Regression tests** — `tests/test_translate_parallel_recovery.py` (3 tests) + expanded `tests/test_ai_usage_tracker.py` (now 31 parametrised cases).
- **Testing-agent verified** — iteration_208.json confirms 400/400 key tests pass, zero critical/minor bugs, all data-testids present.

### Completed (14 February 2026 — Section-only Translate + Third-party Independence Cleanup)
- **Translate a single section** — new `POST /api/cases/{case_id}/translate-section` endpoint (synchronous, cached). Body: `{report_id, language, section_heading, section_text}`. Validates: unsupported language (400), empty text (400), >30k chars (400), report-not-in-case (404), LLM failure (502). English no-op short-circuits. Cache collection: `report_section_translations`.
- **SectionTranslatableReport component** — splits markdown on H2 headings and adds a "Translate section" dropdown next to each heading with 20 languages. Translated text renders in a blue-bordered callout below the original with a "Hide" link. Coexists with the existing full-report `<ReportTranslator>`.
- **8 unit tests** (`tests/test_translate_section.py`) covering every error path and the cache short-circuit. Testing-agent verified iteration_209 — 18/18 backend tests + full frontend data-testid verification.
- **Emergent-independence cleanup** (user runs on their own domain `criminallawappealmanagement.com.au`, own Google OAuth client, own OpenAI billing):
  - Removed legacy `/api/auth/session` endpoint body that called `demobackend.emergentagent.com` — endpoint now returns 410 Gone cleanly.
  - Removed the `legacySessionId` fallback branch from `frontend/src/App.js` OAuth callback handler.
  - Replaced `EMERGENT_LLM_KEY` fallback in `services/llm_service.py` and `config.py` with a hard requirement on `OPENAI_API_KEY` — missing key aborts startup.
  - Updated `server.py` deep-health endpoint + `services/report_generator.py` to read `OPENAI_API_KEY` directly.
  - Deleted legacy integration test scripts (`tests/legacy/*`) that still referenced the old preview URL.
  - All remaining comments explicitly describe the self-hosted architecture on the owner's domain.
- **Result**: grep for "Emergent" across `/app/backend` and `/app/frontend/src` returns ZERO hits outside the `emergentintegrations` Python SDK import (just a library wrapper around the OpenAI SDK — no proxy, no shared key).

### Completed (14 February 2026 — Legislation Currency Monitoring + Friendly Nudges)
- **Legislation registry** (`/app/backend/frameworks/legislation_registry.py`) — 79 Australian Acts catalogued across NSW (13), VIC (10), QLD (9), SA (9), WA (9), TAS (8), NT (8), ACT (8), Cth (5). Each entry has direct AustLII URL + AustLII search fallback + `last_verified` ISO date. (`/app/backend/frameworks/legislation_registry.py`) — 79 Australian Acts catalogued across NSW (13), VIC (10), QLD (9), SA (9), WA (9), TAS (8), NT (8), ACT (8), Cth (5). Each entry has direct AustLII URL + AustLII search fallback + `last_verified` ISO date.
- **Currency dashboard service** (`/app/backend/services/legislation_currency.py`) — age bucketing (🟢 <90d current, 🟡 90–180d review soon, 🔴 >180d overdue), Mongo `framework_audit_log` collection mirrors manual ticks, dashboard prefers the later of registry date or audit-log date.
- **Three new admin endpoints** (`/app/backend/routers/admin.py`):
  - `GET /api/admin/legislation-currency` — returns full dashboard with per-Act rows, totals, and a forensic notice card
  - `POST /api/admin/legislation-currency/mark-verified` — user-initiated tick after manual AustLII review
  - `POST /api/admin/legislation-currency/ai-check` — heavily-guardrailed GPT-4o cross-check
- **HEAVY ANTI-HALLUCINATION guardrails** on the AI check:
  - Strict JSON schema enforcement: `status` ∈ {appears_current, possible_change, cannot_verify, outside_knowledge_cutoff}; `confidence` ∈ {low, medium, high}; `knowledge_cutoff`, `forensic_summary`, `suggested_review_focus[]`, `flagged_amendments[]`, `forensic_caveat` all required
  - Validator (`_validate_ai_response`) rejects: missing keys, invalid enums, non-list fields, generic filler ("as an AI", "I'm sorry", "Lorem ipsum"), first-person pronouns (i/we/you/us/our), short summaries (<15 chars)
  - On any validation failure, the AI content is SUPPRESSED and the response becomes `{ok:false, guardrail:"schema_violation"|"llm_failure", error, forensic_caveat}` — potentially-fabricated text NEVER reaches the UI
  - On validation pass, the service OVERWRITES the model's `forensic_caveat` with authoritative wording that explicitly states this is a prompt for manual review, not verification
  - The dashboard NEVER updates `last_verified` from AI output — only manual `/mark-verified` ticks count, by design
- **Admin dashboard page** (`/app/frontend/src/pages/LegislationCurrency.jsx`) — forensic notice card at top, jurisdiction filter, per-Act rows with AustLII links, "Mark verified" (prompts for forensic note), "AI check" (opens dialog with amber "PROMPT FOR MANUAL REVIEW — NOT VERIFICATION" banner; shows red "Guardrail tripped — output suppressed" when anti-hallucination tripwire fires)
- **Admin dashboard header** — new "Legislation Currency" + "Signup Source Analytics" links + friendly-nudge self-hosted footer ("Self-hosted · your OpenAI key · your Google OAuth · criminallawappealmanagement.com.au")
- **Framework version badge on exports** (`/app/frontend/src/utils/exportHtml.js`) — every PDF/Word/Print export now includes "Legal Framework v2026.02 · 79 Australian Acts manually verified · criminallawappealmanagement.com.au" in the footer branding block
- **Self-hosting deployment guide** (`/app/memory/SELF_HOSTING_GUIDE.md`) — step-by-step Railway walk-through for retiring the Emergent preview URL dependency
- **20 unit tests** (`tests/test_legislation_currency.py`) covering registry coverage, bucketing, all guardrail rejection paths, dashboard shape, mark_verified persistence. Testing-agent verified iteration_210 — 100% backend + frontend pass, zero critical/minor issues, all data-testids present, anti-hallucination guardrails confirmed working end-to-end.
- **README.md fully refreshed (14 Feb 2026)** — removed all references to the deprecated 2-page Appellate Research Brief Quick Brief, added new sections for Legislation Currency Dashboard (#11), Admin Dashboard & Analytics with OpenAI Cost Tracker (#16), and Anti-Hallucination & Forensic Language Rules. Renumbered sections 1–20. Updated backend routers, service layer, and frameworks package listings. Rewrote Security section with self-hosting independence block. Replaced Emergent references with explicit self-hosted architecture (owner's OpenAI key, Google OAuth client, domain `criminallawappealmanagement.com.au`).

### Completed (15 February 2026 — Legal Seal in Export Footers)
- **Navy/gold "FRAMEWORK VERIFIED" seal injected into PDF/Print footers** — both shared export builder (`/app/frontend/src/utils/exportHtml.js`) and the `ReportView.jsx` preview pipeline now emit a compact navy pill in the CSS Paged Media `@bottom-center` margin box, reading `✓  FRAMEWORK VERIFIED  ·  79 Australian Acts`. White 6.5pt serif text, 0.14em tracking, `#0b1e3f` background with `#1e3a8a` 0.5pt border, padded `2pt 8pt`, rounded `2pt`. Added to both `@page` (portrait) and `@page landscape-table` so the seal persists when tables flip landscape.
- **Layout parity preserved** — existing `@bottom-left` (italic document label + appellant) and `@bottom-right` (Page X of Y) are untouched; the seal sits centrally between them.
- **Visually verified** — rendered a sample A4 PDF via headless Chromium print pipeline with `emulate_media("print")`; file-analysis confirmed: italic label left, navy pill with white checkmark + "FRAMEWORK VERIFIED · 79 Australian Acts" centred, page number right. `-webkit-print-color-adjust: exact` ensures Chrome/Edge/Safari all honour the background fill.

### Completed (21 February 2026 — Canonical Print Spec + Dead External-Link Repair)
- **Canonical print spec locked across 7 export builders** (6 frontend + backend): body 11pt Times / line-height 1.5 / H1 14pt bold / H2 12pt bold / H3 12pt bold italic / paragraph-gap 10pt / margins 18/20/22mm / footer `{Appellant} · {Doc Type} · {Date}` left + `Page X of Y` right at 9pt italic. Mobile @media keeps canonical sizes for WYSIWYG parity (only container padding shrinks). Removed the `page-break-before/after: always` on `.section-body table` that had been forcing half-blank preceding pages — ROOT CAUSE of the 1100+ iteration whitespace-gap bug. Removed the `@bottom-center` FRAMEWORK VERIFIED placard per owner's strict 2-box footer spec.
- **Dead external links across Law / Legal / Progress tabs swept and repaired**:
  - **Research Case Law tiles** (NSW, VIC, QLD, SA, WA, TAS, NT, ACT, HCA, Federal Court) — all routed through AustLII's `cgi-bin/viewdb/au/cases/<jur>/` landing pages (verified 200 OK). Replaced dead `caselaw.nsw.gov.au`, `sclqld.org.au`, `courts.sa.gov.au/judgments`, `ecourts.justice.wa.gov.au` (WA eCourts blocks iOS Safari), `courts.act.gov.au/supreme/judgments`, `hcourt.gov.au/cases/cases-heard` and `fedcourt.gov.au/judgments`.
  - **Section-level chips** on Law tab (`s.18`, `s.19A`, `s.23A`, `s.52A` etc.) — previously hardcoded `/au/legis/nsw/consol_act/` which broke every VIC/QLD/SA/WA/TAS/NT/ACT chip. Also AustLII's `sinosrch.cgi` is now 410 Gone. New approach: Google site-search scoped to `austlii.edu.au` (`site:austlii.edu.au "<Act>" s X`) — bulletproof, resolves first-hit to correct AustLII section page across every jurisdiction.
  - **Appeal Forms & Court Registries** tiles — NSW CCA, Vic Court of Appeal, QLD/SA/WA Supreme Courts, Legal Aid NSW — all switched to stable homepage URLs. WA Supreme Court moved to the new `wa.gov.au` consolidated domain path.
  - **CaselawSearchPage** URL map — same AustLII routing applied (QLD, SA, WA, ACT, HCA, Federal Court).
  - **LegalResourcesPage** SmallResourceCards — QLD, SA, WA court portals repointed to stable homepage paths.
  - **Progress tab step 3 "View legislation on AustLII"** chip — defensively lowercases `selectedState` so the AustLII legis path always resolves.
- **Backend DOCX/PDF canonical** — `Pt(11)` body / `Pt(14)` H1 / `Pt(12)` H2 bold / `Pt(12)` H3 bold italic / `build_footer_label` emits middle-dot format with en-AU long-form date / PDF `NumberedCanvas` at 9pt italic with 20mm margin-aligned.

### Completed (21 February 2026 — Real-Time Legislative Alerts)
- **New `legislation_alerts` router** with 5 endpoints providing case-aware amendment tracking across all 9 Australian jurisdictions (NSW, VIC, QLD, SA, WA, TAS, NT, ACT, CTH):
  - `POST /api/admin/legislation/amendments` — admin records a confirmed amendment (jurisdiction + Act + section + effective_date + amending_act + summary + source_url + severity low|medium|high|critical)
  - `PATCH /api/admin/legislation/amendments/{id}` — correct / edit published amendments
  - `DELETE /api/admin/legislation/amendments/{id}` — retract mistaken amendments
  - `POST /api/admin/legislation/ai-scan` — runs the existing guardrailed `ai_currency_check` across the top 12 REGISTRY Acts, shortlists candidates with `verification_status="ai_flagged"` for manual review (never auto-published — zero hallucination risk)
  - `GET /api/legislation/amendments?jurisdiction=&since=&limit=` — public confirmed feed
  - `GET /api/cases/{case_id}/legislation-alerts` — case-aware feed combining jurisdiction-matched amendments + all CTH amendments with per-user `acknowledged` flags
  - `POST /api/cases/{case_id}/legislation-alerts/{amendment_id}/acknowledge` — clears the bell badge for that user/case/amendment
- **Two new Mongo collections**: `legislation_amendments` (confirmed feed) and `legislation_alert_reads` (per-user ack tracking)
- **Admin UI** — `Publish Legislative Amendment` card added to `LegislationCurrency.jsx` page with 9-field dialog (jurisdiction, Act, section, effective date, amending Act, change type, severity, summary, source URL) + `Run AI scan` button for the LLM shortlist workflow
- **User UI** — `LegislationAlertsPanel` inside `BarristerToolsPanel` shows jurisdiction-filtered alerts with colour-coded severity pills (red critical, amber high, blue medium, slate low) + jurisdiction chips (NSW blue, VIC purple, QLD red, SA red, WA emerald, TAS teal, NT orange, ACT indigo, CTH navy) + `Mark as read` per alert. Red count badge next to the section header on the Progress tab.
- **Strategy decision**: We deliberately do NOT scrape 9 state parliamentary registers. Scraping is brittle, breaks on any redesign, and hallucination risk is unacceptable in a legal product. Instead: (a) admin publishes confirmed amendments sourced from AustLII / legislation.gov.au → guaranteed accurate; (b) AI scan produces a shortlist of candidate amendments the admin then confirms → cheap, fast, safe.
- **Testing** — end-to-end curl verified: 4 seed amendments published (200 each), NSW case retrieves 3 matched alerts (2 NSW + 1 CTH; correctly excludes VIC), acknowledge flips unread 3→2. Frontend compiles cleanly, 0 lint issues.


Three senior-barrister-grade features added, mounted on the Progress tab via new `BarristerToolsPanel` component:

1. **Deadline Tracker with ICS export** — new `POST /api/cases/{case_id}/deadlines/compute` auto-computes the four critical appeal deadlines (Notice of Intention, Notice of Appeal, Submissions draft target, Legal Aid merit application) from `sentence_date + jurisdiction`. Rules hardcoded for NSW 28d, VIC 28d, QLD 30d, SA 21d, WA 21d, TAS 21d, NT 28d, ACT 28d, Cth 28d, each referencing the governing statute/rule. New `GET /api/cases/{case_id}/deadlines.ics` streams an iCalendar file with VALARM reminders at T-14, T-7, T-3, T-1 so the user can import to Apple / Google / Outlook. Frontend: colour-coded countdown chips (emerald ≥14d → amber 7-13d → red <7d → red-bold overdue).

2. **Crown Response Simulator** — new `POST /api/cases/{case_id}/grounds/{ground_id}/crown-response`. An LLM-backed endpoint that generates the DPP's strongest possible written reply to a ground, with: (a) weakness score 1-10, (b) weakness reasons list, (c) Crown's counter-authorities in AGLC4, (d) strategic response the appellant should adopt pre-emptively. System prompt enforces strict 3rd-person forensic Australian English with validation that rejects first-person pronoun leakage. Results persist to `crown_responses` collection and can be regenerated.

3. **Fresh Evidence Wizard (R v Gallagher)** — new `POST /api/cases/{case_id}/fresh-evidence/evaluate`. 5-field wizard (evidence description / reason for delay / materiality / credibility basis / source type) produces: (a) per-factor Gallagher assessment (new / reasonable diligence / credible / material — each satisfied|not_satisfied|uncertain with reasoning), (b) admissibility likelihood low|moderate|high, (c) 250-450 word submission paragraph ready for inclusion in written submissions with AGLC4 citations (R v Gallagher (1986) 160 CLR 392, Mickelberg v The Queen (1989) 167 CLR 259, R v Lawless [1974] VR 398, Ratten v The Queen (1974) 131 CLR 510), (d) recommended authorities, (e) practical next steps. Results persist to `fresh_evidence_applications` collection with history.

4. **AGLC4 Citation Insert in Notes Editor** — inline citation builder above the note content textarea. User types Act name / selects jurisdiction / enters section → one-tap "Insert citation" inserts AGLC4-formatted text at the current caret position. Complements the existing Copy-Cite chips on the Law tab.

**Registration & tests** — new `barrister_tools.py` router registered in `routers/__init__.py`; two new Mongo collections (`crown_responses`, `fresh_evidence_applications`); 1/1 deadlines test passes; full backend suite still 739 pass. Frontend lint clean, webpack compiles. End-to-end curl verification:
- `POST /deadlines/compute` with `{"sentence_date":"2026-04-01"}` → HTTP 200, 4 deadlines computed (dates match ISO rule arithmetic)
- `GET /deadlines.ics` → HTTP 200, `text/calendar`, 4 × BEGIN:VEVENT
- `POST /fresh-evidence/evaluate` → HTTP 200, all 4 Gallagher factors evaluated, 1624-char submission paragraph, 4 authorities, 5 next-step actions


- **Fixed all Pipeline Progress action buttons** (`Extract All Documents`, `Classify Issues`, `Verify Top 3/6`, `Sync Grounds`, `Refresh Pipeline Now`, `Refresh + Verify Top 3/6`) reported not working on iOS Safari. **Root cause**: `CaseDetail.jsx` was passing `sessionToken` + `onRunStage` props but the `PipelineProgress` component expected `documents`, `onRefreshCase`, `onRefreshGrounds`, `onRefreshReports`. Result: (a) `documents=[]` default made "Extract All Documents" permanently disabled, and (b) after any action succeeded, the parent page never refreshed so nothing appeared to change. Fixed by wiring the correct props. Backend endpoints were working all along (verified via curl).
- **Document Download fallback** — new `GET /api/cases/{case_id}/documents/{document_id}/download` streams the stored binary with `Content-Disposition: attachment` + RFC 5987 filename encoding. Added Download icon button (`<Download/>`) beside every document card in `DocumentsSection.jsx` — toast: "Downloaded — open in Pages / Word / Files app". Bypasses the iOS Safari "This file cannot be previewed" error by handing the file to the OS to open natively.
- **AGLC4 "Copy citation" button on section chips** — per owner's enhancement request. Each section chip on the Law tab now shows a small copy icon beside it; one tap copies a correctly-formatted AGLC4 citation to clipboard: e.g. `Crimes Act 1900 (NSW) s 18 ('Murder and manslaughter defined')`. Handles: jurisdiction suffix normalisation (CTH→Cth; else uppercase), `s.` prefix stripping, duplicate `(NSW)` suffix removal in Act name, non-secure-context fallback (iOS Safari private mode uses legacy `document.execCommand('copy')` via hidden textarea). Toast: "Citation copied (AGLC4)".
- **Tests** — 23 document router tests pass; full backend suite 739/741 (two pre-existing async teardown failures unrelated to changes). Frontend lint clean, webpack clean compile.

## Remaining / Backlog
- **P1**: iOS device verification of all three fixes above (pipeline buttons, download fallback, AGLC cite).
- **P1**: Verify direct `/export-pdf` and `/export-word` buttons bypass Safari iOS print headers on a real device.
- **P2**: Second attachment for counsel conference prep on the Appellate Research Brief.
- **P2 (deferred)**: Founder video testimonial / explainer on the landing page.
- **P3**: When the user deploys the backend to Railway per `SELF_HOSTING_GUIDE.md`, flip `REACT_APP_BACKEND_URL` to `https://api.criminallawappealmanagement.com.au`.

## Test Credentials
- Email: djkingy79@gmail.com
- Password: Grubbygrub88
