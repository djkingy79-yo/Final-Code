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
