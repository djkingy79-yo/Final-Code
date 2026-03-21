# Appeal Case Manager — Changelog

## 2026-03-21 — Session 15
### AI Endpoint Fallback (P0)
- All secondary endpoints use `call_llm_with_fallback` with model rotation

### Print Buttons Fixed (P0)
- Print on ALL 7 tabs (was missing Documents, Reports, Legal)
- iOS: BarristerView/ReportView → PDF export; CaseDetail → iframe extraction

### AI Content Quality (P0)
- `cleanAIContent` strips `[Note: ...]` AND `(Note: ...)` bracket/round notes
- Section filtering threshold 80 chars
- Backend guardrails: anti-preamble, anti-bracket, legislation years required

### Report Structure Overhaul (P0)
- **Quick Summary**: Trimmed from 12 to 7 sections, true overview
- **Full Detailed**: Reordered 15 sections (Analysis → Strategy → Practical → Client Brief LAST). Removed scattered "How to Start" from middle, combined with Forms.
- **Extensive Log**: Expanded from 4500-6500 to 7000-10000 word target. Now 20 sections with 5 unique sections (Hearing Prep, Conference Pack, Court Pathway, Similar Case Search, Risk Assessment). 300+ words per ground, 12+ sentencing cases, 15+ precedent cases. Increased context limits (32K chars).
- Eliminated content doubling between reports
- Client Plain-English Brief always LAST section in all reports

### Other Fixes
- PayID admin Refresh: loading state + error toasts
- BarristerView parser: markdown heading detection + cleanTitle
- Sentence field on Case model + edit dialog
- iOS PDF export fixed for Timeline

## 2026-03-21 — Session 14 (Critical Report & PDF Fix)
- **Report generation fully fixed** (P0):
  - Root cause 1: `emergentintegrations` module missing — installed
  - Root cause 2: Subprocess `python3` not resolving to venv — fixed with `sys.executable`
  - Root cause 3: LLM budget exceeded ($50.47 vs $50.20 limit) — user topped up
  - Root cause 4: gpt-4o intermittently refuses extensive_log prompts with aggressive/filing language — toned down prompts, removed "DRAFT NOTICE OF APPEAL", "ORAL HEARING SCRIPTS" etc.
  - Root cause 5: Extensive_log 25-section template causes model to produce outlines not content — reduced to 20 sections matching full_detailed's proven template
  - Root cause 6: Model says word target too high — reduced from 12K-18K to 4500-6500 words
  - Switched from subprocess to direct async LLM calls (simpler, more reliable)
  - All 3 report types now working: Quick Summary (7.7K chars), Full Detailed (16.3K chars), Extensive Log (22.9K chars)
- **PDF/Print export fixed for iOS Safari** (P1):
  - Blob URLs blocked by iOS Safari popup blocker — replaced with direct API URL anchor tags
  - Applied across ALL 3 files: BarristerView, ReportView, ReportsSection
  - Backend export endpoints tested: PDF and DOCX both return 200 with proper Content-Disposition headers
  - Cookie-based auth works for direct URL access
- **Context limits restored** to original full values for report quality
- **Deployment check PASSED** — no blockers
- **Australian English verified** — no remaining American English in user-facing text
- **Testing**: iteration_65 passed 100%, manual curl testing of all 3 report types + PDF/DOCX exports

## 2026-03-19 — Session 13 (Deployment Readiness)
- Deployment readiness check passed
- emergentintegrations installed, subprocess python path fixed
- Initial retry + model fallback added

## 2026-03 — Sessions 1-12 (See previous changelog entries)
- Full app built: Auth, cases, documents, timeline, grounds, notes, reports
- PayID-only payment system
- Barrister View, legal resources, admin dashboard
- Mobile responsive, Australian English
