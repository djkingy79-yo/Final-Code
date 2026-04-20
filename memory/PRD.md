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

## Remaining / Backlog
- **P2**: Backend self-hosting migration guide (Railway/Render/AWS) to remove final Emergent dependency (`REACT_APP_BACKEND_URL`)
- **P2**: Second attachment for counsel conference prep on Appellate Research Brief
- **P3**: Expose a small "Legal Framework Version" badge on each exported report (e.g., "Framework v2026.02 · 8 jurisdictions verified") — turn invisible heavy lifting into a visible quality signal

## Test Credentials
- Email: djkingy79@gmail.com
- Password: Grubbygrub88
