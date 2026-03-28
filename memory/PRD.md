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
- **2026-03-26:** Completed full app health check (`/app/test_reports/iteration_92.json`) with public routes, auth protection, navigation, and backend APIs passing
- **2026-03-26:** Deployment-readiness check passed with no blockers detected for the current FastAPI + React + MongoDB configuration
- **2026-03-26:** Completed authenticated UI verification (`/app/test_reports/iteration_93.json`) using email/password login on case `case_76056187ad4f`; all core authenticated flows passed
- **2026-03-26:** Fixed the final Barrister hero overlap by constraining the summary grid width so the title no longer collapses vertically on the live authenticated screen
- **2026-03-26:** Completed final pre-deploy sweep (`/app/test_reports/iteration_94.json`) across all public pages, authentication, case tabs, report views, Barrister View, grounds exports, progress tab, admin dashboard, and backend health with no critical issues found
- **2026-03-26:** Fixed Google auth callback redirect to hard-redirect into `/dashboard` after successful session exchange instead of falling back to landing-page navigation
- **2026-03-26:** Fixed PayID `Payment Received Refresh` flow so user verification now marks payment as submitted for admin review, admin refresh sees it, admin confirmation completes it, and subsequent user refresh unlocks the feature correctly
- **2026-03-27:** Re-normalised report tables across full-page, Barrister, preview, and grounds surfaces using a fixed-layout 640px baseline with stable wrapping to stop columns jumping and stretching unpredictably
- **2026-03-27:** Added live PayID notice emails to the active payment routes in `server.py`, so user verification and admin confirmation now send payment-status emails to the user inbox
- **2026-03-27:** Updated remaining low-contrast dashboard/case-note action buttons to the bright blue with white text treatment, including New Case, create-case submit, Add Note, comment submit, and note submit buttons
- **2026-03-27:** Audited and fixed all report payment flows end-to-end: canonicalised legacy report payment feature types, made report unlock checks alias-safe, and verified notify → user refresh → admin pending refresh → admin confirm → user refresh across both Full Detailed and Extensive Log payments
- **2026-03-27:** Added visible payment-status badges to the paid report tier cards using live payment state data (`Pending`, `Awaiting confirmation`, `Unlocked`)
- **2026-03-27:** Fixed unlocked paid report cards so they generate directly instead of reopening payment, and updated remaining client-view white buttons (Help, Quick Export, Bundle Docs, Compare Cases dashboard) to bright blue with white text
- **2026-03-27:** Completed the remaining dialog/secondary action button restyle in core case flows, including Cancel buttons, event/ground submit buttons, export dialog buttons, and report dialog buttons
- **2026-03-27:** Hardened Barrister generation against timeouts by increasing stale-job tolerance to 15 minutes, adding per-stage partial-save/resume support, and verifying a full rerun that survived an expansion-stage 502 and still completed successfully
- **2026-03-26:** Updated all report/Barrister table headers to the bright blue brand colour with bold white text and stopped header text from stacking vertically on mobile
- **2026-03-26:** Updated Case File and Admin action buttons to the bright blue/white button treatment and restored the document action as `Extract All Text to Case`
- **2026-03-26:** Reduced report table minimum width from 720px to 560px across report, Barrister, preview, and grounds analysis tables to stop over-stretching
- **2026-03-26:** Added Grounds tab export actions for unlocked users: Print View, PDF View, and Word View, including full deep investigation analysis in the generated grounds export document
- **2026-03-26:** Added the requested acknowledgement quote above the About page footer for Renee Yates and Nigel Willett
- **2026-03-26:** Restyled the About page acknowledgement card to the bright blue background with white text treatment
- **2026-03-28:** Fixed stale case/report state bleed in `CaseDetail.jsx`, `ReportView.jsx`, and `BarristerView.jsx` by resetting view state on route changes and ignoring late async responses from older case/report requests
- **2026-03-28:** Corrected offence display fallback so report and barrister headers prefer case-specific extracted offence text before generic offence-category labels
- **2026-03-28:** Reworked report, barrister, and grounds preview navigation to use same-tab `/document-preview` routing with stored `returnTo` paths; preview back buttons now return to the originating report/case screen instead of the landing page
- **2026-03-28:** Updated preview and print surfaces with dynamic footer text (document name + appellant + date), Deb King branding, thank-you sign-off, and visible preview page numbering; tightened print-table wrapping to prevent stretched or overlapping columns
- **2026-03-28:** Added PDF footer/page numbering in `server.py` and DOCX footer/page field output with the requested dynamic footer label and Deb King closing message
- **2026-03-28:** Increased long-report tolerance by extending report polling/generation timeouts for Extensive Log and Barrister generation so large runs are less likely to fail prematurely
- **2026-03-28:** Restyled PayID purchase buttons to the bright-blue/white treatment with clearer vertical spacing
- **2026-03-28:** Verified the full fix set with smoke testing plus rigorous automated coverage in `/app/test_reports/iteration_96.json` (backend and frontend both passed)
- **2026-03-28:** Reduced Grounds of Merit print/export typography and table sizing so more content fits on each page without removing detail
- **2026-03-28:** Changed the floating home button above the Top of Page button to the bright-blue treatment with a white home icon
- **2026-03-28:** Added a Timeline Print button that opens `/document-preview` with full expanded event details (description, source, participants, linked documents, related grounds, contested and inconsistency notes) included in the printout
- **2026-03-28:** Wired timeline preview returns back to `/cases/:caseId?tab=timeline` so leaving the print preview lands on the Timeline tab instead of resetting the case view
- **2026-03-28:** Verified these frontend updates with browser smoke tests plus `auto_frontend_testing_agent` and backend sanity checks; all passed with no regressions
- **2026-03-28:** Fixed the Generate Report dialog footer buttons so they no longer overlap on narrow/mobile widths and both remain bright blue with white text
- **2026-03-28:** Fixed the top report-page Back to Case buttons by switching them to direct case-route navigation for Report View and Barrister View
- **2026-03-28:** Corrected the sentence-summary extraction so case cards no longer pull appeal outcome junk (for example “dismissed/upheld”) instead of the actual sentence
- **2026-03-28:** Tightened full-screen report table rendering for mobile by using scrollable wrappers with auto table layout and smaller mobile table typography
- **2026-03-28:** Added title-page cover sheets to report print previews plus PDF/DOCX export generation, covering all report tiers through the shared export pipeline
- **2026-03-28:** Verified the latest report fixes on desktop and mobile, including the cover sheet, via responsive frontend testing and export sanity checks; all passed
- **2026-03-28:** Fixed Barrister availability when all 3 standard reports exist by recovering incomplete empty barrister records and auto-retrying generation when the three prerequisite reports are completed
- **2026-03-28:** Standardised full detailed report preview/export tables to a consistent smaller 11pt-style table font treatment and unified table font family handling across preview/PDF/DOCX paths
- **2026-03-28:** Reworked Barrister synthesis prompts so the brief now explicitly includes a 3-part source-report synthesis (`Quick Summary`, `Full Detailed`, `Extensive Log`) before the integrated counsel analysis, rather than treating the inputs as one blurred summary source
- **2026-03-28:** Regenerated the live Barrister brief for case `case_76056187ad4f` after the prompt rewrite so the current live brief now uses the new 3-report synthesis structure
- **2026-03-28:** Replaced speculative sentence fallbacks with sentence resolution from the case’s completed report history across Report View, Barrister View, and backend exports so the live case now shows the exact sentence wording everywhere
- **2026-03-28:** Normalised sentence wording to remove offence text (`for murder`), remove `minimum` from non-parole wording, and remove the stray comma after `imprisonment`
- **2026-03-28:** Verified exact sentence wording across all 4 report types plus Print/PDF/DOCX outputs in `/app/test_reports/iteration_99.json` — all passed
- **2026-03-28:** Removed the extra `Created and Designed by Deb King` report-layout blocks from the live report/preview/export flows so the footer now stops at the disclaimer + footer label/page treatment the user requested
- **2026-03-28:** Changed report PDF buttons to open the real backend-generated PDF output instead of the HTML pseudo-PDF preview; added Barrister export alias endpoints for `/reports/barrister-view/export-pdf` and `/export-docx` to stop the Barrister PDF 404 path
- **2026-03-28:** Re-verified standard report PDF export, Barrister PDF export alias, and Barrister DOCX export alias — all now return 200 successfully

## Verified Status
- P0 Barrister View backend synthesis: implemented and verified
- P0 Print/PDF presentation fixes: implemented and verified
- P0 stale case/report data bleed guards: implemented and verified
- P1 preview/export back-button routing: implemented and verified
- P1 grounds print density improvement: implemented and verified
- P1 timeline print preview with expanded details: implemented and verified
- P0 report sentence-summary bug: implemented and verified
- P1 generate-report modal mobile button overlap: implemented and verified
- P1 report cover sheet for print/PDF/Word: implemented and verified
- P0 barrister unlock/recovery bug: implemented and verified
- P0 barrister synthesis rewrite from all 3 source reports: implemented and live-regenerated for current case
- P0 exact sentence wording across 4 reports + exports: implemented and verified
- P0 real PDF view + footer cleanup across report flows: implemented and verified
- Latest rigorous verification: `/app/test_reports/iteration_99.json` — backend 100%, frontend 100%

## Prioritised Next Actions
### P1
- Run user review on live Barrister brief quality with real completed cases and refine prompt depth if needed
- Monitor large Extensive Log/Barrister runs on fresh non-homicide matters to confirm the timeout changes hold under real long-form generation
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
