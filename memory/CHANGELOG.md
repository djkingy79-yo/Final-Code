# Appeal Case Manager — Changelog

## 2026-03-21 — Session 15 (AI Endpoint Fallback + Content Quality + Edit Case + Print Fix)
- **All secondary AI endpoints now use `call_llm_with_fallback`** (P0):
  - `investigate_ground_of_merit` and `auto_identify_grounds`: Replaced hardcoded Claude-only calls with model fallback
- **PRINT BUTTONS FIXED ACROSS ALL VIEWS** (P0 — asked 4 times):
  - Print button now appears on ALL 7 tabs in CaseDetail (was missing from Documents, Reports, Legal)
  - iOS Safari fix: BarristerView/ReportView Print opens PDF export in new tab instead of unreliable `window.print()`
  - iOS Safari fix: CaseDetail Print uses iframe-based content extraction for reliable printing
  - Desktop: `window.print()` continues to work as before
- **AI Report Content Quality Fixes** (P0):
  - `cleanAIContent` strips AI preamble and bracket placeholder notes
  - Section filtering threshold increased from 30 to 80 chars — removes thin/useless sections like "Authority Sequence"
  - Backend guardrails updated with anti-preamble/anti-bracket instructions
- **Sentence Field Fix** (P1):
  - Added `sentence` field to Case model + Dashboard/CaseDetail forms
  - Stricter regex prevents wrong sentence extraction ("12 years, reduced due to mental health evidence effects on intent")
  - Fallback text: "Not specified — edit case to add sentence"
- **Edit Case Details** (P1):
  - "Edit" button on Case Detail page with full dialog for all fields
  - Sentence displayed as amber badge
- **iOS Safari PDF Export Fix** (P1):
  - Timeline PDF export now uses anchor tag approach
- **Testing**: iterations 66 (13/13), 67 (21/21), 68 (all code + build verified)

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
