# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features: secure document management, AI-powered case analysis, tiered reporting system (Free Quick Summary, $150 Full Detailed, $200 Extensive Log, locked Barrister View).

## Core Requirements
- **Report Tiers:** Strictly scale in depth. Barrister View is capstone synthesis.
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
- `/app/frontend/src/pages/BarristerView.jsx` — Barrister Brief view + custom export builder
- `/app/frontend/src/pages/ReportView.jsx` — Standard report view + custom export builder
- `/app/frontend/src/pages/CaseDetail.jsx` — Case detail with Print All/PDF All/Word All + Progress export

## What's Been Implemented

### Completed (Previous Sessions)
- Full multi-tier report generation pipeline (Quick Summary, Full Detailed, Extensive Log, Barrister View)
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
- Barrister View PDF export rewritten with inline Tailwind CSS
- Quick Brief blank page fixed

### Completed (11 April 2026 — Current Session)
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
  - Tested: 10-chunk German translation completed in ~2 minutes via polling (130K chars)

## Remaining / Backlog
- **P2**: Add second attachment for counsel conference prep (key questions, weak points, likely prosecution answers, document references) to Barrister View

## Test Credentials
- Email: djkingy79@gmail.com
- Password: Grubbygrub88
