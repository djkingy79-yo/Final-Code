# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Strictly scale in depth. Free (Base) -> $150 (2x depth) -> $200 (3x depth)
- **Barrister View:** Locked until all 3 standard reports are generated/paid
- **Report Language:** STRICT third-person educational tool. No "we", "us", "our", "you", "your"
- **Branding:** Forced light mode. High contrast. Blue/slate/navy only. Action buttons bright blue with white text
- **Legal Accuracy:** Must cite current, state-specific, and federal Australian legislation
- **Unified Document Styling:** Times New Roman, 12pt body, bold headings, indented bullets, legal footers
- **Australian English:** ALL user-facing text must use Australian spelling. auSpelling utility applied to all AI-generated content.

## Architecture
- React frontend + FastAPI backend + MongoDB
- AI: OpenAI GPT-4o via Emergent LLM Key
- Auth: Emergent-managed Google Auth + email/password
- Payments: PayID (sole payment method — PayPal/Stripe fully removed)
- Emails: Resend

## Completed — Previous Session (10 Apr 2026)
- Fixed Grounds of Merit UI: Reduced mobile fonts, displayed actual Legal Framework text
- Applied auSpelling to ALL AI-generated content (deep analysis, evidence, appellate pathway, timeline)
- Expanded auSpelling utility with 15+ additional Australian English conversions
- Fixed Barrister report card: forced inline `style={{color:'#ffffff'}}` for bright white text on teal
- Fixed Google Sign In: Changed from `<button onClick>` to `<a href>` for iOS webview compatibility
- Full forensic codebase audit (dead code, lint, duplication, MongoDB _id fixes)
- Removed PayPal/Stripe completely; PayID is sole payment method

## Completed — Current Session (10 Apr 2026)
- **Full Forensic Legal Framework Audit (`offence_framework.py`):**
  - Cross-referenced all legislation codes against real Australian law via web search
  - **20 corrections applied** to OFFENCE_CATEGORIES (zero hallucinations now):
    - NSW: s.23, s.23A, s.24, s.25 (removed—repealed), s.19B corrected
    - VIC: s.3A, s.5, s.31→s.16 in Assault corrected
    - QLD: s.300, s.302 corrected
    - WA: s.280, s.281 corrected; s.283/s.259 removed (wrong offences)
    - TAS: s.156, s.157 corrected
    - ACT: s.54, s.55, s.56, s.55A corrected
    - SA: RECENT_LEGISLATION_UPDATES coercive control entry updated
  - **7 corrections applied** to APPEAL_FRAMEWORK:
    - VIC forms: 8-1A/8-1B → Form 6-2A/6-2C
    - QLD forms: Form 21/22 → Form 26/28
    - WA time limits: clarified 28 days (summary) / 21 days (indictable)
    - TAS time: 21 days → 14 days
    - NT legislation: Part IIAA → Local Court (Criminal Procedure) Act 1928
    - ACT legislation: Part 7 → Part 2A
    - Federal court: removed "Full Federal Court" reference; clarified state court pathway
  - **2 corrections applied** to STATE CRIMINAL FRAMEWORKS:
    - QLD: "manslaughter s 303" → "manslaughter s 309"
    - VIC: "s 34AA-34AB" → "s 34AD-34AE" for non-fatal strangulation
  - Total: **29 corrections** across the entire legal framework
- **Backend Refactoring (server.py decomposition):**
  - `server.py`: 6,068 → 426 lines (93% reduction)
  - Extracted to 6 focused modules:
    - `services/report_quality.py` (453 lines) — text normalisation, dedup, forensic language
    - `services/pipeline_orchestrator.py` (529 lines) — pipeline freshness, document extraction
    - `services/report_generator.py` (1,847 lines) — `analyze_case_with_ai` engine
    - `services/barrister_generator.py` (1,092 lines) — barrister brief generation
    - `routers/reports.py` (812 lines) — report CRUD endpoints
    - `routers/report_exports.py` (1,047 lines) — PDF/DOCX export endpoints
  - All 19 regression tests passed. Zero regressions.
- **Camera/Share Native Features**: Already fully implemented (DocumentScanner.jsx, native/camera.js, native/share.js, export share flow). Verified correct.
- **Forensic Australian English Language Audit:**
  - Fixed 10 hardcoded American English strings in API endpoints, response fields, function/prop names, and data-testid attributes
  - API endpoints renamed: `/timeline/analyze` → `/timeline/analyse`, `/analyze-contradictions` → `/analyse-contradictions`
  - Response fields: `documents_analyzed` → `documents_analysed`, `analyzed_at` → `analysed_at`, `total_cases_analyzed` → `total_cases_analysed`
  - Fixed `judgment` → `judgement` in models, LLM prompts, legal disclaimers, and frontend pages
  - Added **52 new AU spelling conversions** to both frontend (`auSpelling.js`) and backend (`normalise_au_spelling`) dictionaries covering: traumatise, victimise, scrutinise, marginalise, haemorrhage, anaesthetic, paediatric, judgement, manoeuvre, wilful, skilful, pretence, cancelled, labelled, ageing, fulfil, and more
- **Forensic Appellate Language Audit:**
  - Expanded `enforce_forensic_language` from 28 → 90+ sentence-start replacement patterns covering:
    - "The judge failed to" → "It is arguable that the judge failed to"
    - "The judge was wrong/biased/misdirected/ignored/disregarded/overlooked"
    - "The court wrongly/improperly", "The trial was unfair"
    - "The verdict is/was unreasonable", "The sentence is/was inadequate"
    - "The directions were inadequate", "The evidence was wrongly/improperly"
    - "There was no proper/a failure to", "The judge should/ought to have"
  - Added 18 context-free patterns: "was clearly wrong" → "was arguably wrong", "fundamentally flawed", "no reasonable judge"
  - Added matching frontend forensic enforcement to `auSpelling.js` (31 patterns) as safety net
  - Added matching forensic enforcement to `ReportView.jsx` `cleanAIContent()` function
  - All 45 test cases pass (32 accusatory patterns caught, 4 preservation tests, 9 context-free)
  - Verified LLM prompts in both `report_generator.py` and `barrister_generator.py` already contain comprehensive forensic language instructions

## Pending Tasks
### P0
- (none)

### P1
- Verify "How It Works" page images (IMG_4323.png to IMG_4327.png)
- Build Native Mobile App (Capacitor v7 configured)

### P2
- Camera/Share native device features — DONE (already implemented)
- Backend refactoring: decompose server.py (~6000 lines) — DONE
- Counsel conference prep attachment for Barrister View
