# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The app features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Scale in depth. Free (Base) -> $150 (2x depth) -> $200 (3x depth).
- **Barrister View:** Locked until all 3 reports generated/paid. Capstone synthesis.
- **Report Language:** STRICT third-person educational tool. Paragraphs, not bullet points.
- **Branding & Disclaimers:** "NOT LEGAL ADVICE" disclaimers + branding footer (scales + Appeal Case Manager + Founded by Debra King).
- **UI/UX:** Forced light mode. High contrast. Blue/slate/navy. Bright blue action buttons.
- **Paywalls:** Grounds $99 paywall. Admin bypasses all.
- **Australian English:** All text uses Australian spelling.
- **Export Buttons:** Every report: Print, PDF, Word.
- **Document Footers:** CSS counter(page), appellant name, date. Branding footer embedded.
- **PDF Preview:** Must match on-screen view quality with responsive CSS for mobile.
- **Footer Layout:** 3-column on all screen sizes.
- **Legal Resources:** Default "All states". Inline-style badges.
- **Terms of Service:** "Commonwealth of Australia".
- **Chat:** Real-time messaging per case (WebSocket + REST).

## What's Been Implemented
- User auth (JWT + Google social login)
- Case CRUD with AI auto-detection
- Document upload + background auto-timeline generation
- Grounds of Merit with $99 paywall
- 4-tier report system with Print/PDF/Word exports
- Responsive PDF preview (CSS @media 768px breakpoints in ReportView + BarristerView)
- Branding footer on all views/exports
- CaseChat with backend endpoints
- Chat button (bottom-left), Home+ScrollTop (bottom-right)
- /login redirect route
- All resource card badges using inline styles

## Code Audit Fixes (March 2026)
- Fixed undefined LlmChat/UserMessage (missing import)
- Added missing chat backend (GET/POST /messages, WS /chat/ws)
- Added /login redirect route
- Fixed resource card badges (Tailwind purge → inline styles)
- Added responsive CSS to PDF preview HTML templates
- State filter default → "all", Terms → "Commonwealth of Australia"

## Prioritised Backlog
- **P1:** Build Native Mobile App (Capacitor)
- **P1:** Custom domain (criminallawappealmanagement.com.au via GoDaddy)
- **P2:** Counsel conference prep attachment for Barrister View
- **P3:** Break up server.py monolith (>7400 lines)
