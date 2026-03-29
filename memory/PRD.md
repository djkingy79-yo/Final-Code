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
- **Landing Page Pricing & Comparison Table:** Fixed report title mismatches ("Quick Summary Report" → "Quick Summary", "Full Detailed" → "Full Detailed Report", "Extensive Log" → "Extensive Log Report"). Applied tier-specific colours to pricing cards (Green, Blue, Purple, Teal) and comparison table headers (emerald-600, blue-600, purple-600). Added teal Barrister View note below comparison table. Testing agent confirmed 100% pass (iteration_102.json).
- **Global Footer Legal Disclaimer:** Added a full, bold, red-background "NOT LEGAL ADVICE" disclaimer banner at the very bottom of every page via AppFooter.jsx. Includes warning icon, full disclaimer text (educational tool, not legal advice, creator is not a lawyer, must be verified by qualified Australian legal professional, no solicitor-client relationship), and link to Terms & Privacy.
- **Full Disclaimer in All Reports:** Updated ALL disclaimer instances across ReportView (on-screen, PDF, print), BarristerView (banner, footer, PDF, print), and backend exports (PDF via reportlab, DOCX via python-docx) to use the same full-length disclaimer text: "educational research tool only, does NOT constitute legal advice, creator is not a lawyer, must be independently verified, Australian law only, no solicitor-client relationship".
- **Case Sharing & Real-Time Collaboration (28 Mar 2026):** Full feature implementation including:
  - Share by email + shareable link (view & comment permissions)
  - Real-time chat panel (WebSocket + polling fallback) with message history
  - Activity feed tracking (shares, messages, notes)
  - In-app notification bell with unread badge + email notifications (Resend)
  - Shared Cases section on Dashboard with teal-accented cards
  - Collaboration tab in Case Detail with activity feed
  - Share modal with email input, link generation, copy, and revoke
  - AcceptShareLink page for link-based sharing
  - Backend: New collaboration router with 14 API endpoints (tested 100%)
  - Frontend: 5 new components (ShareCaseModal, CaseChat, NotificationBell, ActivityFeed, AcceptShareLink)
  - Testing agent confirmed 100% pass rate (iteration_103.json)
- **Stats Page Blue Theme Fix (29 Mar 2026):** Restored bright blue background across entire Appeal Statistics page. Fixed blank white boxes (stat cards, snapshot section, important note all now blue-themed). Made bullets white (marker:text-white) for visibility. Enlarged all section headings (text-3xl) and sub-headings (text-xl/text-2xl) so they stand out from body text. Updated StateDetailCard, Complaints, Common Grounds, Historical Trends, and Data Sources sections to blue theme.
- **Chat Typing Indicators:** Added real-time typing indicators to CaseChat — shows "[name] is typing..." when other participants are composing a message, sent via WebSocket.

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
