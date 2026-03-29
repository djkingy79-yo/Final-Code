# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The app features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Scale in depth. Free (Base) -> $150 (2x depth) -> $200 (3x depth).
- **Barrister View:** Locked until all 3 standard reports generated/paid. Capstone synthesis.
- **Report Language:** STRICT third-person educational tool. Paragraphs, not bullet points.
- **Branding & Disclaimers:** "NOT LEGAL ADVICE" disclaimers + branding footer (scales icon + Appeal Case Manager + Founded by Debra King).
- **UI/UX:** Forced light mode. High contrast. Blue/slate/navy palette. Bright blue action buttons.
- **Paywalls:** Grounds of Merit shows only count until $99 paid. Admin bypasses all paywalls.
- **Australian English:** All UI text, code, and AI outputs use Australian spelling.
- **Export Buttons:** Every report must have Print, PDF, and Word buttons.
- **Document Footers:** CSS counter(page) for page numbers. No static "Page 1". Branding footer embedded.
- **Footer Layout:** 3-column layout on all screen sizes.
- **Legal Resources:** Default filter "All states". All resource cards display visible state badges (inline styles).
- **Terms of Service:** References "Commonwealth of Australia" and all states/territories.
- **Chat:** CaseChat feature with real-time messaging per case (WebSocket + REST endpoints).

## What's Been Implemented
- User auth (JWT + Google social login)
- Case CRUD with AI auto-detection of metadata
- Document upload with text extraction + background auto-timeline generation
- Grounds of Merit with strict $99 paywall
- 4-tier report system with Print/PDF/Word exports
- Branding footer on all report views and exports
- Legal Resources page with "all" state default filter
- Terms of Service covering all Australian jurisdictions
- CaseChat with backend endpoints (GET/POST /messages, WebSocket /chat/ws)
- Chat button (bottom-left), Home+ScrollTop (bottom-right)
- PDF preview auto-sizes to content height
- 3-column footer layout on all screen sizes
- Resource card badges using inline styles (Tailwind-purge-proof)
- /login redirect route

## Code Audit Fixes (March 2026)
- **CRITICAL:** Fixed undefined `LlmChat`/`UserMessage` in server.py auto-detect function (missing import)
- **CRITICAL:** Added missing chat backend endpoints (GET/POST /messages, WS /chat/ws)
- **MEDIUM:** Added missing /login redirect route in App.js
- **MEDIUM:** Fixed resource card badges (bg-slate-700 purged by Tailwind → inline styles)
- **LOW:** State filter default changed from NSW to "all"
- **LOW:** Terms of Service updated to "Commonwealth of Australia"

## Prioritised Backlog
- **P1:** Build Native Mobile App (Capacitor configured)
- **P1:** Custom domain setup (criminallawappealmanagement.com.au via GoDaddy)
- **P2:** Counsel conference prep attachment for Barrister View
- **P3:** Break up server.py monolith (>7400 lines)

## Architecture
```
/app/
├── backend/
│   ├── server.py           # Core logic, LLM generation, chat, exports
│   ├── routers/            # Extracted API routes (auth, payments, export, analytics)
│   └── .env
└── frontend/
    └── src/
        ├── components/     # GroundsOfMerit, Timeline, CaseChat, Documents, ReportsSection
        ├── pages/          # CaseDetail, ReportView, BarristerView, LegalResources, Terms
        └── App.js
```
