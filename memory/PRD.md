# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Strictly scale in depth. Free (Base) -> $150 (2x depth) -> $200 (3x depth)
- **Barrister View:** Locked until all 3 standard reports are generated/paid
- **Report Language:** STRICT third-person educational tool. No "we", "us", "our", "you", "your"
- **Branding:** Forced light mode. High contrast. Blue/slate/navy only. Action buttons bright blue with white text
- **Legal Accuracy:** Must cite current, state-specific, and federal Australian legislation
- **Unified Document Styling:** Times New Roman, 12pt body, bold headings, indented bullets, legal footers
- **Australian English:** ALL user-facing text must use Australian spelling. auSpelling utility applied to all AI-generated content.

## Architecture
- React frontend + FastAPI backend + MongoDB
- AI: OpenAI GPT-4o via Emergent LLM Key
- Auth: Emergent-managed Google Auth + email/password
- Payments: PayPal/PayID/Stripe
- Emails: Resend

## Completed This Session (10 Apr 2026)
- Fixed Grounds of Merit UI: Reduced mobile fonts, displayed actual Legal Framework text
- Applied auSpelling to ALL AI-generated content (deep analysis, evidence, appellate pathway, timeline)
- Expanded auSpelling utility with 15+ additional Australian English conversions
- Fixed Barrister report card: forced inline `style={{color:'#ffffff'}}` for bright white text on teal
- Fixed Google Sign In: Changed from `<button onClick>` to `<a href>` for iOS webview compatibility
- **Full forensic audit completed:**
  - Removed 1,689 lines dead frontend code (5 orphaned components)
  - Removed 2 dead backend router files (messages.py, reports.py)
  - Deduplicated `is_admin_user` (was in 3 files, now in config.py)
  - Deduplicated `hash_password` (was in 2 files, now imported from auth.py)
  - Deduplicated `get_frontend_url` (was in 2 files, now imported from config.py)
  - Removed 4 unused frontend imports (Badge, useCallback, PlayCircle, useTheme)
  - Zero lint errors (Python + JavaScript)
  - All LLM calls verified wrapped in try/except
  - All MongoDB queries verified with _id exclusion
  - No hardcoded URLs, API keys, or credentials

## Pending Tasks
### P1
- Verify "How It Works" page images (IMG_4323.png to IMG_4327.png)
- Build Native Mobile App (Capacitor v7 configured)

### P2
- Backend refactoring: decompose server.py (~6000 lines)
- Camera/Share native device features
- Counsel conference prep attachment for Barrister View
