# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Strictly scale in depth. Free (Base) -> $150 (2x depth) -> $200 (3x depth)
- **Barrister View:** Locked until all 3 standard reports are generated/paid
- **Report Language:** STRICT third-person educational tool. No "we", "us", "our", "you", "your". Must use forensic appellate language.
- **Branding:** Forced light mode. High contrast. Blue/slate/navy only. Action buttons bright blue with white text
- **Legal Accuracy:** Must cite current, state-specific, and federal Australian legislation
- **Australian English:** ALL user-facing text must use Australian spelling. auSpelling utility applied to all AI-generated content.

## Architecture
- React frontend + FastAPI backend + MongoDB
- AI: OpenAI GPT-4o via Emergent LLM Key
- Auth: Emergent-managed Google Auth + email/password
- Payments: PayID (sole payment method)
- Emails: Resend
- **CRITICAL:** API calls always go to preview URL (REACT_APP_BACKEND_URL), NOT window.location.origin. Custom domain Cloudflare proxy returns 520 for /api/* routes.

## Completed — Previous Sessions
- All prior work (forensic audit, backend refactor, native features, etc.)

## Completed — Current Session (10 Apr 2026)
- **auSpelling Safari Crash Fix:** Changed `const corrected` to `let corrected` — Safari throws "Attempted to assign to readonly property" for const reassignment
- **Forensic Language Varied Prefixes:** 9 rotating prefixes ("It is arguable that", "It may be contended that", "There is a tenable argument that", etc.) in both frontend auSpelling.js and backend offence_helpers.py. Includes judge possessive patterns and broad catch-all regex.
- **Generated Badge UI:** Bold white text on teal (#00B09E) background for report card badges
- **Google Auth Backend Retry:** 5 server-side retries with delays [0,1,2,3,5s] for Emergent session-data API
- **Google Auth Auto-Retry:** Frontend auto-redirects to fresh Google Sign In on failure (up to 3x), session_id validation (skip <32 chars), URL cleaned immediately
- **CRITICAL FIX — Custom Domain API Routing:** Custom domain Cloudflare proxy returns 520 for /api/* routes. Changed BACKEND_URL from window.location.origin to always use REACT_APP_BACKEND_URL (preview URL). Cross-origin works via CORS Access-Control-Allow-Origin: *. Auth uses Bearer tokens from localStorage.

## Pending Tasks
### P1
- Verify "How It Works" page images (IMG_4323.png to IMG_4327.png)
- Build Native Mobile App (Capacitor v7 configured)

### P2
- Counsel conference prep attachment for Barrister View
