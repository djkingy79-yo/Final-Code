# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Strictly scale in depth. Free (Base) -> $150 (2x depth) -> $200 (3x depth)
- **Barrister View:** Locked until all 3 standard reports are generated/paid
- **Report Language:** STRICT third-person educational tool. No "we", "us", "our", "you", "your". Must use forensic appellate language.
- **Branding:** Forced light mode. High contrast. Blue/slate/navy only. Action buttons bright blue with white text
- **Legal Accuracy:** Must cite current, state-specific, and federal Australian legislation
- **Unified Document Styling:** Times New Roman, 12pt body, bold headings, indented bullets, legal footers
- **Australian English:** ALL user-facing text must use Australian spelling. auSpelling utility applied to all AI-generated content.

## Architecture
- React frontend + FastAPI backend + MongoDB
- AI: OpenAI GPT-4o via Emergent LLM Key
- Auth: Emergent-managed Google Auth + email/password
- Payments: PayID (sole payment method)
- Emails: Resend

## Completed — Previous Sessions
- Fixed Grounds of Merit UI, applied auSpelling to all AI content
- Fixed Google Sign In iOS compatibility (changed from button onClick to a href)
- Full forensic codebase audit, dead code removal
- Removed PayPal/Stripe; PayID is sole payment method
- Full Forensic Legal Framework Audit (29 corrections across offence_framework.py)
- Backend Refactoring: server.py 6,068 -> 426 lines (93% reduction)
- Camera/Share Native Features verified
- Forensic Australian English Audit (52 new AU spelling conversions)
- Forensic Appellate Language Audit (90+ sentence-start replacement patterns)

## Completed — Current Session (10 Apr 2026)
- **Google Auth Permanent Fix:** Added backend-side retry logic (5 attempts with delays [0,1,2,3,5s]) for Emergent Auth session-data API call. Frontend now makes single call with 30s timeout. Error UI with "Try Google Sign In Again" and "Back to Home" buttons replaces infinite spinner. 100% test pass rate (iteration_179).
- **auSpelling Safari Crash Fix:** Changed `const corrected` to `let corrected` in `auSpelling.js`. The forensic language enforcement loop (added in previous session) reassigns this variable. Safari throws "Attempted to assign to readonly property" for const reassignment, crashing Timeline and GroundsOfMerit components.

## Pending Tasks
### P0
- (none)

### P1
- Verify "How It Works" page images (IMG_4323.png to IMG_4327.png)
- Build Native Mobile App (Capacitor v7 configured)

### P2
- Counsel conference prep attachment for Barrister View
