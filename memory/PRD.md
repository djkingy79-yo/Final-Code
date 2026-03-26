# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The product combines secure document management, AI-powered case analysis, tiered report generation, and a locked Barrister View intended to act as the capstone synthesis of all three standard reports.

## Core Product Requirements
- **Report tiers:** Free (Base), $150 Full Detailed, and $200 Extensive Log must scale materially in depth.
- **Barrister View:** Must remain locked until all 3 standard reports are completed; output must be one cohesive barrister-ready brief with no duplicated or scattered analysis.
- **Report language:** Strict third-person educational tone only. No "we", "us", "our", "you", or "your".
- **Branding:** All report surfaces and exports must display "Created and Designed by Deb King" plus a strong legal disclaimer.
- **UI/UX:** Forced light mode, high contrast, Australian spelling, and a blue/slate/navy palette only.

## Tech Stack
- React frontend + FastAPI backend + MongoDB
- OpenAI GPT-4o via Emergent LLM Key
- Emergent-managed Google Auth

## Current Architecture
```
/app/backend/server.py                     # Core API, AI prompt engine, exports, barrister synthesis
/app/frontend/src/pages/CaseDetail.jsx     # Main case workspace
/app/frontend/src/pages/ReportView.jsx     # Standard report viewing, print, PDF/DOCX actions
/app/frontend/src/pages/BarristerView.jsx  # Rebuilt barrister brief page driven by backend synthesis
/app/frontend/src/components/ReportsSection.jsx
/app/frontend/src/index.css                # Global + print styling
```

## What Has Been Implemented
- Full case CRUD with document upload/OCR, timeline, grounds, and notes
- Multi-pass AI generation for the three standard report tiers with partial DB saving
- Export header improvements including Grounds count and Sentence
- Strong backend/frontend stripping of forbidden first/second-person report language
- FAQ and supporting public pages in the updated light visual system
- **2026-03-26:** Barrister View rewritten so it no longer merges content in the frontend
- **2026-03-26:** New backend Barrister synthesis flow added at `GET /api/cases/{case_id}/reports/barrister-view`
- **2026-03-26:** Barrister brief is now generated and stored as a dedicated `barrister_view` report using backend LLM synthesis from the 3 latest completed standard reports
- **2026-03-26:** Barrister page rebuilt into a professional document-style layout with Deb King branding, disclaimer, clean section rendering, and export actions
- **2026-03-26:** ReportView print/table styling tightened for professional print/PDF presentation
- **2026-03-26:** Extensive Log visual theme corrected from purple to slate/navy
- **2026-03-26:** Download links opened in a new tab/window now support `session_token` query-param authentication
- **2026-03-26:** How It Works pricing-card header text forced to white bold for all report tiers on mobile and desktop
- **2026-03-26:** Fixed Barrister View backend generation crash caused by invalid Mongo projection in `generate_barrister_brief()`
- **2026-03-26:** Fixed Barrister endpoint loop so failed/stale jobs no longer recreate endless `generating` placeholders
- **2026-03-26:** Generated a completed Barrister Brief for case `case_db8d84fecfc4` as report `rpt_3b5271d6f2ab`
- **2026-03-26:** Reworked Barrister synthesis into grouped deep-generation passes plus expansion logic so the Barrister brief carries materially more detail from all 3 standard reports
- **2026-03-26:** Regenerated the Barrister Brief for case `case_db8d84fecfc4` as report `rpt_d707334d7843` with 25,019 characters and all 11 required sections
- **2026-03-26:** Strengthened Barrister generation again to force one dedicated subsection per ground and regenerated case `case_db8d84fecfc4` as report `rpt_703bad1e2169` with 31,131 characters and 5 explicit ground subsections
- **2026-03-26:** Tightened backend PDF export formatting for report headings and bullet/list rendering to improve readability and reduce broken PDF text flow
- **2026-03-26:** Reworked Barrister and ReportView mobile preview/export flows to use blob-based preview pages instead of `document.write` blank popups
- **2026-03-26:** Removed iOS blank-tab export behaviour by switching PDF/DOCX export paths to blob download/share handling
- **2026-03-26:** Compacted the Barrister top layout so the analysis starts higher on mobile and print-preview screens
- **2026-03-26:** Replaced popup/blob preview with a dedicated in-app `/document-preview` route using stored preview payloads, fixing the mobile blank PDF/print preview behaviour for Barrister and standard report pages
- **2026-03-26:** Added Barrister comparison-table enrichment and regenerated case `case_db8d84fecfc4` as report `rpt_d287912f2a53` with 40,923 characters, 4 comparison tables, and deeper all-report synthesis
- **2026-03-26:** Fixed failed multi-pass report recovery for the third report by resuming from saved partial passes instead of restarting from zero, splitting the heaviest pass, and replacing raw 502 UI errors with a user-friendly retry message
- **2026-03-26:** Updated the landing-page dropdown/mobile nav/footer to include the full public page set and refreshed How It Works styling so Step 6 is bright blue, Step 7 is bright teal, and the Barrister View pricing card uses the teal header treatment
- **2026-03-26:** Removed the public-page legal image additions after user rejection and restored the clean public-page layout
- **2026-03-26:** Fixed report/progress data linkage for case `case_76056187ad4f` by restoring the extensive report purple theme, improving sentence extraction, switching progress analysis to `grounds_of_merit`, and syncing all completed standard reports to the real 4-ground data
- **2026-03-26:** Fixed Barrister recovery for case `case_76056187ad4f` by hardening stale/failed generation handling and completing stuck report `rpt_dcb21f0efc62` successfully
- **2026-03-26:** Updated all report/Barrister table headers to the bright blue brand colour with bold white text and stopped header text from stacking vertically on mobile
- **2026-03-26:** Updated Case File and Admin action buttons to the bright blue/white button treatment and restored the document action as `Extract All Text to Case`
- **2026-03-26:** Reduced report table minimum width from 720px to 560px across report, Barrister, preview, and grounds analysis tables to stop over-stretching
- **2026-03-26:** Added Grounds tab export actions for unlocked users: Print View, PDF View, and Word View, including full deep investigation analysis in the generated grounds export document
- **2026-03-26:** Added the requested acknowledgement quote above the About page footer for Renee Yates and Nigel Willett
- **2026-03-26:** Restyled the About page acknowledgement card to the bright blue background with white text treatment

## Verified Status
- P0 Barrister View backend synthesis: implemented and verified
- P0 Print/PDF presentation fixes: implemented and verified
- Latest rigorous verification: `/app/test_reports/iteration_91.json` — backend 100%, frontend 100%

## Prioritised Next Actions
### P1
- Run user review on live Barrister brief quality with real completed cases and refine prompt depth if needed
- Continue export polish if any jurisdiction-specific formatting preferences emerge from review
- Resume deferred backend refactor to decompose `server.py`
- Progress Capacitor/native mobile wrapper once the web report presentation is signed off

### P2
- Real-time collaboration/chat enhancements in Notes
- Case sharing between registered users

## Notes for Next Agent
- Do **not** restore frontend report-merging logic for Barrister View.
- Barrister View now depends on backend synthesis and stores a dedicated `barrister_view` report record.
- Keep Australian spelling and strict tone constraints across UI and generated outputs.
