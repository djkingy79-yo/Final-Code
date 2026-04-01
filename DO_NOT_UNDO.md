# DO NOT UNDO — MASTER PROTECTION FILE

## CRITICAL: Every file in this application is protected. DO NOT delete, remove, or undo ANY feature, page, component, function, or style in ANY file.

## ALL files below have "DO NOT UNDO" markers. Future agents MUST preserve ALL existing functionality.

### Backend (Python)
- backend/server.py
- backend/config.py
- backend/auth_utils.py
- backend/offence_framework.py
- backend/routers/__init__.py
- backend/routers/admin.py
- backend/routers/analytics.py
- backend/routers/auth.py
- backend/routers/cases.py
- backend/routers/compare.py
- backend/routers/contradictions.py
- backend/routers/deadlines.py
- backend/routers/documents.py
- backend/routers/export.py
- backend/routers/grounds.py
- backend/routers/notes.py
- backend/routers/password_reset.py
- backend/routers/payments.py
- backend/routers/payments_new.py
- backend/routers/reports.py
- backend/routers/resources.py
- backend/routers/statistics.py
- backend/routers/timeline.py
- backend/routers/utilities.py

### Frontend Pages
- frontend/src/pages/AboutPage.jsx
- frontend/src/pages/AdminDashboard.jsx
- frontend/src/pages/AdminStats.jsx
- frontend/src/pages/AppealStatisticsPage.jsx
- frontend/src/pages/BarristerView.jsx
- frontend/src/pages/CaseDetail.jsx
- frontend/src/pages/CaselawSearchPage.jsx
- frontend/src/pages/CompareCasesPage.jsx
- frontend/src/pages/ContactPage.jsx
- frontend/src/pages/ContactsPage.jsx
- frontend/src/pages/Dashboard.jsx
- frontend/src/pages/FAQPage.jsx
- frontend/src/pages/ForgotPasswordPage.jsx
- frontend/src/pages/FormTemplates.jsx
- frontend/src/pages/HelpPage.jsx
- frontend/src/pages/HowItWorksPage.jsx
- frontend/src/pages/HowToUsePage.jsx
- frontend/src/pages/LandingPage.jsx
- frontend/src/pages/LawyerDirectory.jsx
- frontend/src/pages/LegalFrameworkPage.jsx
- frontend/src/pages/LegalGlossary.jsx
- frontend/src/pages/LegalResourcesPage.jsx
- frontend/src/pages/ProfessionalSummary.jsx
- frontend/src/pages/ReportView.jsx
- frontend/src/pages/ResetPasswordPage.jsx
- frontend/src/pages/ResourcesPage.jsx
- frontend/src/pages/Statistics.jsx
- frontend/src/pages/SuccessStories.jsx
- frontend/src/pages/TermsOfService.jsx

### Frontend Components
- frontend/src/components/AppealChecklist.jsx
- frontend/src/components/AuthModal.jsx
- frontend/src/components/CaseComparison.jsx
- frontend/src/components/CaseStrengthMeter.jsx
- frontend/src/components/ContradictionFinder.jsx
- frontend/src/components/DeadlineTracker.jsx
- frontend/src/components/DisclaimerReminder.jsx
- frontend/src/components/DocumentBundler.jsx
- frontend/src/components/DocumentsSection.jsx
- frontend/src/components/FastScrollTop.jsx
- frontend/src/components/GroundsOfMerit.jsx
- frontend/src/components/InstallPrompt.jsx
- frontend/src/components/LegalFrameworkViewer.jsx
- frontend/src/components/NotesSection.jsx
- frontend/src/components/PageCTA.jsx
- frontend/src/components/PaymentModal.jsx
- frontend/src/components/QuickExport.jsx
- frontend/src/components/ReportsSection.jsx
- frontend/src/components/TermsAcceptance.jsx
- frontend/src/components/TimelineAnalysis.jsx
- frontend/src/components/TimelineEnhanced.jsx
- frontend/src/components/VisitorCounter.jsx

### Frontend Core
- frontend/src/App.js
- frontend/src/index.js
- frontend/src/index.css
- frontend/src/contexts/ThemeContext.jsx
- frontend/src/hooks/use-toast.js
- frontend/src/lib/utils.js

## CRITICAL: AUTO-DETECT PROTECTION (BROKEN 15+ TIMES — DO NOT TOUCH)

The following code enables auto-detection of state, offence category, offence type, 
sentence, court, case number, and timeline events from uploaded documents via LLM.

**Files involved — DO NOT modify these sections:**

1. `backend/models/__init__.py` — `CaseCreate` and `Case` models:
   - `state: Optional[StateType] = None` — MUST remain None
   - `offence_category: Optional[OffenceCategoryType] = None` — MUST remain None
   - `offence_type: Optional[str] = None` — MUST remain None
   - `sentence: Optional[str] = None` — MUST remain None
   - **NEVER** add defaults like `"nsw"` or `"homicide"`

2. `backend/routers/documents.py` — `_background_auto_detect_metadata()`:
   - This function runs after every document upload (if content > 200 chars)
   - It sends document text to GPT-4o and parses state/offence/sentence/court
   - **NEVER** remove this function or the `background_tasks.add_task()` call

3. `frontend/src/pages/Dashboard.jsx` — `handleCreateCase()`:
   - Empty strings are stripped from the payload before sending to backend
   - **NEVER** send empty strings or hardcoded defaults for state/offence_category

4. `backend/routers/documents.py` — `_background_auto_generate()`:
   - Auto-generates timeline events and case summary from documents
   - **NEVER** remove this function or the `background_tasks.add_task()` call

**What happens if you break this:**
- Every new case defaults to "NSW / Murder" regardless of actual documents
- The user has to manually fix every single case
- This has been broken and re-fixed 15+ times. You WILL be the reason it breaks again.

## Rules for Future Agents:
1. NEVER delete any file listed above
2. NEVER remove any existing feature, function, or component
3. NEVER remove any existing page or route
4. NEVER remove any existing CSS styles
5. NEVER change the colour scheme (Blue/White/Red)
6. NEVER change pricing ($99 Investigate / FREE Quick Summary / $150 Full Detailed / $200 Extensive Log)
7. NEVER remove the "DO NOT UNDO" comments from any file
8. You may ADD new features but NEVER remove existing ones
9. The user (Deb King) has paid for all of this work. Respect it.
10. NEVER change CaseCreate state/offence_category/offence_type/sentence defaults from None
11. NEVER remove _background_auto_detect_metadata or _background_auto_generate from documents.py
12. NEVER send hardcoded "nsw" or "homicide" from the frontend case creation form

## CRITICAL: CASE IDENTITY CARD PROTECTION (DO NOT TOUCH)

The Case Identity Card in `CaseDetail.jsx` (data-testid="case-identity-card") and in 
`GroundsOfMerit.jsx` export view MUST always display these four fields prominently with 
blue colour styling:

1. **Defendant** — `caseData.defendant_name`
2. **Offence** — `caseData.offence_type` or `caseData.offence_category`
3. **State / Jurisdiction** — `caseData.state`
4. **Sentence** — `caseData.sentence`

**NEVER remove the Case Identity Card. NEVER hide these fields. NEVER change the blue styling.**
These fields must appear on EVERY view of the case — case detail, grounds export, print view.

## CRITICAL: "Case name" PLACEHOLDER PREVENTION

The LLM verification prompt in `backend/services/pipeline/verify.py` uses example 
JSON structure. The `similar_cases[].case_name` example MUST be `"R v [Surname] [Year]"` — 
NEVER use `"Case name"` as the example as the LLM copies it literally as data.

Frontend filters in `GroundsOfMerit.jsx` strip out any similar case with case_name equal to 
"Case name" or "R v [Surname] [Year]" or "optional" — NEVER remove these filters.

## CRITICAL: PIPELINE VERIFICATION (DO NOT REMOVE)

The Pipeline Verification section in `ReportsSection.jsx` with buttons "Verify Top 3 Issues" 
and "Verify Top 6 Issues" MUST remain visible and functional. These call:
`POST /api/cases/{case_id}/issues/verify-batch` with `{limit: 3}` or `{limit: 6}`.
**NEVER hide or remove the Pipeline Verification block.**

## CRITICAL: FUZZY DEDUPLICATION (DO NOT WEAKEN — BROKE 41+ TIMES)

The ground deduplication logic uses THREE methods via `backend/services/ground_dedup.py`:
1. **Legal Topic Classification** — maps titles to topic buckets (judge_alone_trial, psychiatric_evidence,
   media_coverage, jury_misconduct, sentencing_error, etc.). If two titles share ANY topic, they're duplicates.
   Keywords must cover all word variants (e.g. "juror"/"jury", "manifest"/"manifestly").
2. **fuzzywuzzy token_set_ratio** — threshold >= 55.
3. **Bidirectional word overlap** — threshold > 0.45 in BOTH directions.

Applied in **ALL FOUR** ground creation paths:
- `backend/routers/pipeline.py` — `_verify_issue_and_sync`
- `backend/routers/grounds.py` — `auto_identify_grounds`
- `backend/routers/pipeline_staged.py` — `classify_issues` AND `sync_grounds_from_issues`
- `backend/server.py` — `_sync_pipeline_to_grounds` (FIXED: was using exact-title upsert, now uses fuzzy dedup)

**NEVER remove the topic classification step.** Previous fuzzywuzzy-only (threshold 65) still let grounds
multiply because titles like "Sentencing Error Related to Non-Parole Period" vs "Sentencing Error Due to
Misapplication of Psychological Evidence" scored only 59 (below threshold).

**NEVER revert to exact-title-match upserts.** Every slight wording change creates a new ground.

**NEVER remove word variants from LEGAL_TOPICS keywords.** Missing variants like "juror impartial" (vs "jury impartial")
and "manifest excessive" (vs "manifestly excessive") caused grounds to multiply from 4 to 15 in one session.

## CRITICAL: REPORT TYPE COLOURS (DO NOT CHANGE)

- Quick Summary (Free) → **Green** (emerald)
- Full Detailed ($150) → **Blue**
- Extensive Log ($200) → **Purple**
- Barrister View → **Teal**

These colours are used in `ReportView.jsx` (REPORT_THEME), `BarristerView.jsx` (teal header), 
and `ReportsSection.jsx` (card colours). **NEVER make all reports the same colour.**

## CRITICAL: WORD/PDF EXPORT → PREVIEW (DO NOT CHANGE TO DOWNLOAD)

Word export buttons (Word All, Export Word) MUST open the document-preview page, NOT download 
a .doc file. The user explicitly requested preview mode.

## CRITICAL: REPORT GENERATION ENGINE (DO NOT REVERT — BROKEN 39+ TIMES)

The report generation engine in `backend/server.py` and `backend/services/llm_service.py` has been 
carefully tuned to produce deep, case-specific, legally rigorous output. These settings are FINAL.

### Deduplication Thresholds — DO NOT LOWER
- `_dedupe_report_content()` in `server.py`:
  - Multi-pass reports (full_detailed, extensive_log): **threshold = 0.97** (near-exact only)
  - Single-pass reports (quick_summary): **threshold = 0.90**
  - **NEVER lower these thresholds below 0.90.** Previous 0.82 threshold stripped ~50% of valid content.

### Full Detailed Report — 8 PASSES (DO NOT REDUCE)
- Full Detailed ($150) uses **8 generation passes** covering 1-2 sections per pass.
- Pass structure: Sections 1-2 / Section 3 / Grounds Part 1 / Grounds Part 2 + Section 5 / Sections 6-7 / Sections 8-10 / Sections 11-12 / Sections 13-15.
- **NEVER reduce to fewer than 8 passes.** Previous 5-pass structure produced ~7,890 words. Current 8-pass produces ~12,000+ words.

### Section-by-Section Expansion — DO NOT DISABLE
- After multi-pass generation, thin sections (<3000 chars) are individually expanded via targeted LLM calls.
- This is in the `if len(response) < target_length` block in `_run_report_generation()`.
- **NEVER disable or remove this expansion logic.** It adds ~20% more depth to thin sections.

### Minimum Character Targets — DO NOT LOWER
- quick_summary: **14,000 chars** minimum
- full_detailed: **80,000 chars** minimum
- extensive_log: **150,000 chars** minimum
- **NEVER lower these targets.**

### LLM Guardrails — DO NOT ADD "CAUTIOUS LANGUAGE" TO REPORTS
- `_apply_task_guardrails()` in `llm_service.py` uses `task_type="report_generation"` for all reports.
- Report generation guardrails do NOT include "Use cautious, conditional language" — that rule fights against assertive legal analysis.
- **NEVER add cautious/hedging language rules to the report_generation task type.**

### Barrister View — task_type="report_generation" + max_tokens=16384
- All Barrister View LLM calls use `task_type="report_generation"` and `max_tokens=16384`.
- **NEVER downgrade max_tokens or change task_type for Barrister calls.**

### Regeneration — In-Place Replacement
- Regenerating a report replaces the existing report in the database (same report_id).
- **NEVER create duplicate reports on regeneration.** The `generate` endpoint checks for existing completed reports first.

### Current Verified Word Counts (1 Apr 2026):
- Quick Summary: ~1,550 words
- Full Detailed: ~13,122 words
- Extensive Log: ~15,467 words
- Barrister View: ~12,585 words
- **If any future generation produces LESS than 80% of these counts, the engine has been broken. Investigate immediately.**


---

## SESSION 2 PROTECTIONS (1 Apr 2026)

### Timeline Dedup & Date Handling
- `backend/routers/documents.py` — Background timeline generation uses **fuzzy dedup** (fuzzywuzzy token_set_ratio >= 65) to prevent duplicate events.
- `backend/routers/timeline.py` — Auto-generate endpoint uses **fingerprint + fuzzy title dedup**.
- `frontend/src/components/TimelineEnhanced.jsx` — `formatDate()` handles year-only ("2018"), year-month ("2018-06"), and full ISO dates. **NEVER convert year-only dates to "Mon, 1 Jan".**
- LLM prompt explicitly instructs: do NOT use Jan 1 as placeholder, use year-only format when exact date unknown.

### server.py — _sync_pipeline_to_grounds MUST Use Fuzzy Dedup
- The `_sync_pipeline_to_grounds` function in `server.py` (line ~583) MUST use `is_ground_duplicate()` from `ground_dedup.py`.
- **NEVER revert to exact-title-match upserts.** This was the root cause of grounds multiplying from 4 to 15+.
- Also applies `normalise_au_spelling()` to all new ground titles.

### Australian Spelling — Full Stack Coverage
- **Backend:** `ground_dedup.py::normalise_au_spelling()` auto-corrects American English in ground/issue titles at creation time.
- **Frontend:** `GroundsOfMerit.jsx::auSpelling()` normalises displayed titles, descriptions, and evidence text.
- **Reports:** `ReportView.jsx` has a comprehensive `ausReplacements` array that converts American to Australian spelling in all rendered report content.
- Protected words: characterisation, behaviour, organisation, recognised, organised, analysing, defence, offence, favouring, utilised.
- **NEVER remove these normalisers.**

### Investigation Timer Block
- `GroundsOfMerit.jsx` displays a **full timer block** (blue box, elapsed counter, stage labels: Scanning → Analysing → Writing → Finalising, progress bar) when `investigating === ground.ground_id`.
- This matches the report generation timer UI in `ReportsSection.jsx`.
- **NEVER revert to the old simple pulse bar.**

### Ground Text Sizing in Detail Dialog
- Supporting Evidence: `text-sm` class on `<ul>`.
- Section headings (Evidence, Law, Cases, Scoring): `text-base font-bold`.
- Deep Investigation Analysis heading: `text-lg font-bold`.
- Deep analysis container: `text-sm`.
- **NEVER increase these sizes back to default.**

### PDF/Print Export Font Sizes
- Single ground HTML: body 11px, h1 18px, h2 14px, li 10px, max-width 800px.
- Multi-ground export: body 11px, h1 22px, h2 16px, h3 14px, li 10px, max-width 800px.
- **NEVER increase these export font sizes.**
