# Appeal Case Manager — PRD

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The app features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) -> $150 (2x depth) -> $200 (3x depth). Barrister View locked until all 3 standard reports generated/paid.
- **Report Language:** Strict third-person educational tool. No "we/us/our/you/your".
- **Branding:** Legal disclaimers on all reports (on-screen, PDF, DOCX).
- **UI/UX:** Forced light mode. High contrast. Blue/slate/navy palette. Bright blue action buttons with white text.
- **Language:** Australian English throughout (analyse, organise, defence, offence).

## Architecture
- **Frontend:** React (Create React App) + Tailwind + Shadcn/UI
- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **AI:** OpenAI GPT-4o via Emergent LLM Key + LiteLLM
- **Auth:** Emergent-managed Google Auth + email/password
- **Payments:** PayPal, PayID, Stripe
- **Email:** Resend

## What's Implemented (Complete)
- User auth (Google + email/password)
- Case CRUD with document upload/management
- AI-powered timeline, grounds analysis
- Multi-pass AI report generation (Free, $150, $200)
- Barrister View with "Attachment A — Barrister Issue Matrix"
- PDF/DOCX export with proper footers and page numbering
- iOS-safe PDF preview via /document-preview route
- Legal Framework, Glossary, FAQ, Resources pages
- Appeal Statistics page (bright blue bg, white text, red emphasis)
- "How It Works" page with step-by-step walkthrough
- "How To Use" page with live populated screenshots (8 steps + Barrister View + Export)
- Payment integration (PayPal/PayID/Stripe)
- Deployment config audit (centralised FRONTEND_URL)
- Notes system with categories and pinning

## Completed This Session (28 Mar 2026)
- Captured 8 fresh live screenshots from a populated demo case for the How To Use page
- Created dummy case "Dummy Murder Appeal Demonstration" (Alex Carter) with 8 timeline events, 4 grounds, 3 notes
- All screenshots showing real app data: login, dashboard, documents, timeline, grounds, legal, progress, reports
- Verified all images serve correctly (HTTP 200, image/png content type)
- Testing agent confirmed 100% pass rate on frontend

## Backlog
### P1
- Build Native Mobile App (Capacitor configured, needs build + test)

### P2
- Add second Barrister View attachment (counsel conference prep)
- Real-time Collaboration/Chat for Notes
- Case Sharing between registered users

### Refactoring (Low Priority)
- Break up server.py monolith (>7000 lines)
- Frontend URL config consistency audit across export flows
