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
- "How To Use" page with live populated screenshots (8 steps + 3 individual report views + Barrister unlock info)
- Payment integration (PayPal/PayID/Stripe)
- Deployment config audit (centralised FRONTEND_URL)
- Notes system with categories and pinning

## Completed This Session (28 Mar 2026)
- Re-captured all 8 step screenshots exclusively from the demo case (Dummy Murder Appeal Demonstration / Alex Carter)
- Generated 3 reports on the demo case (Quick Summary, Full Detailed, Extensive Log) and captured individual report screenshots showing colour headings + table of contents
- Reports tab screenshot now shows 3 colourful cards: purple ($200 Extensive Log), blue ($150 Full Detailed), green (Free Quick Summary)
- Progress tab screenshot shows Appeal Checklist with 8/22 items ticked
- Added "Each Report Type" section to Step 8 with 3-column grid of individual report screenshots
- Added "Unlock Requirement" notice to Step 9 (Barrister View) — all 3 reports must be generated first
- Populated demo case with 8 documents, 8 timeline events, 4 grounds, 3 notes, and 3 completed reports
- Testing agent confirmed 100% pass rate (iteration_101.json)

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
