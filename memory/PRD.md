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

## User
- **Language:** Australian English (analyse, organise, offence, defence, barrister)
- **Admin:** djkingy79@gmail.com

## Architecture
- React frontend + FastAPI backend + MongoDB
- AI: OpenAI GPT-4o via Emergent LLM Key
- Auth: Emergent-managed Google Auth + email/password
- Payments: PayPal/PayID/Stripe
- Emails: Resend

## What's Been Implemented
- Full authentication (Google + email/password)
- Case CRUD with document upload and management
- AI-powered timeline generation
- AI-powered grounds of merit classification with 12-topic dedup
- Deep investigation analysis per ground
- Appellate Viability Assessment scoring (9-point scale)
- Law sections and appellate pathway extraction from verify.py
- Legal Framework display showing actual legislation text (not just counts)
- Tiered report generation (Free, $150, $200, Barrister View)
- Document exports (PDF, DOCX, Print)
- Unified Times New Roman legal formatting across all tabs and exports
- Dashboard with pipeline portfolio summary
- Landing page with CTAs
- Stats page
- How It Works page
- Mobile-optimised Grounds of Merit UI with reduced fonts
- Evidence card filtering (removes "optional" filenames and "Page: None")

## Completed This Session (10 Apr 2026)
- Fixed Grounds of Merit UI: Reduced mobile font sizes for evidence cards, Supporting Evidence heading, and Appellate Viability Assessment
- Replaced "X law sections identified" count-only display with actual Legal Framework text showing legislation (e.g. "s 18 Crimes Act 1900 (NSW)")
- Fixed duplicate jurisdiction display (no more "(NSW) (NSW)")
- Filtered out "optional" filename and "Page: None" garbage from evidence cards
- Updated export template law sections to match (no duplicate jurisdiction)

## Pending Tasks
### P1
- Verify "How It Works" page images (IMG_4323.png to IMG_4327.png)
- Build Native Mobile App (Capacitor v7 configured)

### P2
- Backend refactoring: decompose server.py (~6000 lines)
- Camera/Share native device features
- Counsel conference prep attachment for Barrister View
- Real-time collaboration/chat
- Case sharing between users
