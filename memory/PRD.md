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
- **Stats Page Final UI Fixes (29 Mar 2026):** Fixed three issues on /appeal-statistics: (1) Replaced custom blue header with standard white site header matching all other pages, (2) Reverted footer to white background with dark text matching all other pages, (3) Added CSS rule to force white bullet markers on blue backgrounds (force-light was overriding to dark navy). Also fixed hero section white/blank area by replacing broken dark gradient (from-black via-slate-950 — overridden by force-light CSS) with bg-blue-800. CTA button changed from invisible white to visible red-600.
- **Universal Disclaimer & Bug Fixes (29 Mar 2026):** Added "NOT LEGAL ADVICE" disclaimer to all remaining print/export views: tab print previews, timeline print HTML, timeline PDF export, and document bundle PDF. Fixed document bundle PDF crash (variable shadowing — `doc` SimpleDocTemplate overwritten by MongoDB dict in for loop). Fixed timeline delete buttons invisible on mobile (opacity-0 → opacity-100 on mobile).
- **AI Auto-Detection of Case Metadata (29 Mar 2026):** Critical fix — new cases were defaulting to "Homicide" regardless of uploaded document content. Added AI auto-detection that runs: (1) on document upload, (2) after "Extract All Text to Case", and (3) at the start of report generation as fallback. The LLM reads document text and identifies offence_category, offence_type, sentence, state, court, and case_number. Case metadata is automatically updated in the database. Frontend shows toast with detected info and refreshes the case view. Case creation form now defaults to "Auto-detect from documents" instead of "Homicide".
- **Grounds of Merit Paywall (29 Mar 2026):** Enforced strict paywall — before $99 payment, ONLY the count is shown ("X Grounds Found! Unlock for $99"). No titles, descriptions, badges, investigate buttons, or search buttons are visible. The backend returns an empty grounds array with just the count when locked. Admin bypass removed. After payment, full ground cards with titles, investigate button, deep analysis are available.

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
