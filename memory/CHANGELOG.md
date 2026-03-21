# Appeal Case Manager — Changelog

## 2026-03-21 — Session 16
### Landing Page & Marketing Copy Audit (P0)
- **All report section counts corrected** across LandingPage, HowItWorksPage, FAQPage:
  - Quick Summary: "CASE SNAPSHOT" (was CASE OVERVIEW), "TOP POTENTIAL GROUNDS" (was GROUNDS IDENTIFIED), "APPEAL OUTLOOK" with text rating (was 72% percentage)
  - Full Detailed: TOC now shows "CONTENTS (15 Sections)" with all 15 correct section names (was 10)
  - Extensive Log: TOC now shows "COMPLETE TABLE OF CONTENTS (20 SECTIONS)" with all 20 names (was 14), 5 exclusive sections highlighted in purple
- **Badges corrected**: Extensive Log now shows "20 Sections", "15+ Precedent Cases", "12+ Sentencing Comparisons" (was 14/12/23)
- **Pricing descriptions updated**: Full Detailed mentions "15 sections: grounds portfolio, 8+ sentencing comparisons...", Extensive Log mentions "20 sections" with 5 exclusive features listed
- **AI feature card**: Changed "GPT-4 powered" to "AI-Powered"
- **Barrister View section**: Updated to "Extensive Log Advantage" with "20 sections with 5 exclusives"
- **FAQ answers**: All 3 report tier answers now list exact section names and counts
- **HowItWorksPage**: Report pricing features updated with accurate section counts and content descriptions
- **Testing**: iteration_71 — 100% frontend (19/19 tests passed)

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
- **Quick Summary**: 7 sections, 1500-2200 words (overview only)
- **Full Detailed**: 15 sections, 4500-6500 words (Analysis -> Strategy -> Practical -> Client Brief LAST)
- **Extensive Log**: 20 sections, 7000-10000 words. 5 unique sections: Hearing Prep, Conference Pack, Court Pathway, Similar Search, Risk Assessment. 300+ words/ground, 12+ sentencing, 15+ precedent. Context limits: 32K chars.
- **Aggressive Mode**: Restructured to double word count, 15+ sentencing, 20+ precedent, draft submissions
- **Barrister View**: Merges ALL reports for case (not just one). Keeps longest section version, deduplicates by title, sequential numbering, "Merged from N reports" badge.
- State-specific URLs for all 8 jurisdictions (AustLII, Legal Aid, court forms)
- Client Plain-English Brief always LAST in all reports
- Eliminated content doubling and scattered ordering

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
