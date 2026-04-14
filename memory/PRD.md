# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features: secure document management, AI-powered case analysis, tiered reporting system (Free Quick Summary, $150 Full Detailed, $200 Extensive Log, locked Appellate Research Brief).

## Core Requirements
- **Report Tiers:** Strictly scale in depth. Appellate Research Brief is capstone synthesis.
- **Report Language:** STRICT third-person educational tool. No "we", "us", "our", "you", "your". Forensic appellate language.
- **Branding:** Forced light mode globally. High contrast only. No amber/brown (blue/slate/navy). Bright blue action buttons with white text.
- **Print/Export:** Exacting standards for footer, TOC, paragraph numbering, layout parity between on-screen and exported (PDF/Word/Print).
- **Australian English:** analyse, organise, judgement, offence throughout.

## Architecture
- Frontend: React + Tailwind + Shadcn/UI
- Backend: FastAPI + MongoDB
- AI: OpenAI GPT-4o via Emergent LLM Key
- Auth: Emergent Google Auth
- Email: Resend
- Payments: PayID (Stripe removed)
- Mobile: Capacitor (native app build finalised)

## Key Files
- `/app/frontend/src/utils/exportHtml.js` — Shared export CSS/HTML wrapper
- `/app/frontend/src/pages/BarristerView.jsx` — Appellate Research Brief view + custom export builder
- `/app/frontend/src/pages/ReportView.jsx` — Standard report view + custom export builder
- `/app/frontend/src/pages/CaseDetail.jsx` — Case detail with Print All/PDF All/Word All + Progress export

## What's Been Implemented

### Completed (Previous Sessions)
- Full multi-tier report generation pipeline (Quick Summary, Full Detailed, Extensive Log, Appellate Research Brief)
- Document upload & management
- Timeline generation & analysis
- Grounds of Merit identification & investigation
- Case metadata & jurisdiction warnings
- Google Auth via Emergent
- PayID payment system
- Report translation
- Case sharing
- Native Mobile App (Capacitor) build
- Print footer overlap fixed
- Word exports use preview mode for iOS compatibility
- Pipeline Progress tab overhaul
- TOC formats synchronised to 2-column grid
- Case Metadata warning styling updated
- Translation API DuplicateKeyError fixed
- Appellate Research Brief PDF export rewritten with inline Tailwind CSS
- Quick Brief blank page fixed

### Completed (11 April 2026)
- **FORENSIC AUDIT OF ALL EXPORTS**: Ensured 100% formatting parity across all 4 export code paths
  - Added `.section`, `.section-header`, `.section-number`, `.section-title`, `.section-body` CSS to `exportHtml.js`
  - Rewrote `buildPrintAllHtml` in CaseDetail.jsx: replaced plain `<h2>` tags with section-header pattern (numbered badge + left border + uppercase title + bordered body container)
  - Rewrote `buildProgressHtml` in CaseDetail.jsx: same section-header pattern replacement
  - Updated Print All metadata header: now uses coloured case info grid with DEFENDANT, OFFENCE, SENTENCE, DOCUMENTS, TIMELINE EVENTS (matching individual report exports)
  - Verified BarristerView and ReportView exports already use correct section pattern
  - All exports now produce consistent structure: Coloured Header -> TOC (2-col grid) -> Numbered Sections -> Disclaimer -> Branding -> Footer

- **TRANSLATOR FIX (502 Timeout)**: Root cause — Kubernetes proxy kills requests after 60s, large report translations take 2-3 minutes
  - Converted translation to background task pattern (same as grounds auto-identify)
  - POST `/api/cases/{case_id}/translate` now returns immediately with task_id
  - GET `/api/cases/{case_id}/translate/status?report_id=...&language=...` polls for completion
  - Frontend ReportTranslator.jsx updated to poll with progress updates ("3/10 sections complete")
  - Cached translations still return instantly

### Completed (14 April 2026)
- **BACK TO REPORTS NAVIGATION FIX**: "Back to Case" buttons in ReportView.jsx and BarristerView.jsx now navigate to `/cases/${caseId}?tab=reports` (landing on Reports tab instead of default Documents tab). Button text updated to "Back to Reports". CaseDetail.jsx correctly parses the `?tab=reports` query parameter. Verified working.
- **DEPLOYMENT INDEX CRASH FIX**: Wrapped all `create_index` calls in `startup_tasks.py` with a safe helper (`_safe_create_index`) that catches `OperationFailure`, drops the conflicting index by name, then recreates it. Fixes crash on line 39 where a non-unique `document_extracts` index conflicted with the new unique version.
- **QUICK NAVIGATE BETWEEN REPORTS**: Added a "Jump to:" navigation bar below the sticky header in both ReportView.jsx and BarristerView.jsx. Shows all completed reports as clickable buttons (Quick Summary, Full Detailed, Extensive Log, Appellate Research Brief). Current report is highlighted (blue for standard, teal for Appellate Research Brief). Clicking navigates directly to that report without returning to the Reports tab.
- **SERVER-SIDE LLM SYNTHESIS VERIFICATION**: Confirmed the existing Appellate Research Brief generation is 100% server-side LLM synthesis via `barrister_generator.py`. Multi-pass GPT-4o synthesis fetches all 3 completed reports, runs 4 section groups + expansion passes + tables + attachments. No frontend JS/regex merging. Requires all 3 reports completed and paid before unlocking.
- **GROUNDS: APPELLATE PATHWAY RESTORED**: Moved the blue Appellate Pathway box to appear after Supporting Evidence and before Legal Framework. Fixed the investigate endpoint to generate `appellate_pathway` via LLM when missing. Created backfill endpoint (`POST /api/cases/{id}/grounds/backfill-pathways`) and ran it on the Homann case — all 9 grounds now show correct NSW appellate pathway provisions.
- **GROUNDS: DISCLAIMER MESSAGE RESTORED**: Added the disclaimer at the bottom of every ground card: "This analysis identifies potential appellate issues based on available material. It does not determine that the appeal will succeed. All grounds require refinement and verification by a qualified legal practitioner."
- **LEGAL FRAMEWORK HARDENING (14 Apr 2026)**:
  - Added Federal Criminal Code s.4.4 (absolute liability), s.4.1, s.5.2, s.5.4, s.5.6 (fault elements), s.9.1/9.2/9.3 (mistake of fact), s.10.1 (insanity), s.10.2 (intoxication) to FEDERAL_CRIMINAL_FRAMEWORK
  - Fixed appeal time limit extraction to support both `time_limit` string and `time_limits` dict formats — NSW and WA now correctly report their time limits in system prompts
  - Added `last_verified: "2026-04-14"` to all 9 state/federal criminal frameworks for currency tracking
  - Created comprehensive self-test suite (`tests/test_legal_framework.py`) — 202 tests covering all frameworks, offence categories, anti-hallucination, forensic language, citation validation, jurisdiction completeness
- **PIPELINE 500 FIX (14 Apr 2026)**: Added missing `extract_id`, `status` fields to `DocumentExtract` model and `case_extract_id`, `status`, `metadata`, `document_extract_ids` to `CaseExtract` model — fixes AttributeError crash on Extract All Documents, Refresh Case Extract, and Refresh Pipeline.
- **BLANK PIPELINE BUTTONS FIX**: Changed "Refresh Pipeline Now", "Refresh + Verify Top 3", "Refresh + Verify Top 6" buttons from invisible `bg-slate-700` to bright blue `bg-blue-700`.
- **METADATA BANNER FIX**: Red "Case Metadata — Action Required" banner no longer shows when the only warning is an appeal time limit (which is informational, not an action item).

## Remaining / Backlog
- **P2**: Add second attachment for counsel conference prep (key questions, weak points, likely prosecution answers, document references) to Appellate Research Brief

## Test Credentials
- Email: djkingy79@gmail.com
- Password: Grubbygrub88
