# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The app features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $99 Grounds Unlock, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) -> $99 Grounds Unlock -> $150 Full Detailed (15 sections) -> $200 Extensive Log (20 sections) -> Barrister View (unlocked after all 3)
- **Report Language:** STRICT third-person educational tool. No first/second person pronouns.
- **Branding:** Forced light mode. High contrast. Blue/slate/navy palette. Bright blue action buttons with white text.
- **Australian English:** analyse, organise, barrister, defence, offence throughout.

## Tech Stack
- React (Frontend) + FastAPI (Backend) + MongoDB
- OpenAI GPT-4o via Emergent LLM Key
- Emergent Auth (Google social login)
- Resend (Emails), Stripe/PayPal/PayID (Payments)

## Architecture
```
/app/
├── backend/
│   ├── server.py              # Core LLM generation engine (DO NOT TOUCH)
│   ├── config.py              # Centralised env vars
│   ├── services/
│   │   ├── email_service.py   # Payment emails + admin PayID alerts
│   │   ├── ground_dedup.py
│   ├── routers/
│   │   ├── payments.py        # ACTIVE payment router (PayID + PayPal)
│   │   ├── payments_new.py    # Legacy/unused payment router
│   │   ├── auth.py, cases.py, analytics.py, etc.
├── frontend/src/
│   ├── pages/                 # LandingPage, ReportView, BarristerView, HowItWorksPage, etc.
│   ├── components/            # PaymentModal, AppFooter, FastScrollTop, ReportsSection, etc.
├── DO_NOT_UNDO.md             # Critical protection rules
```

## What's Been Implemented
- Full auth flow (Google + email/password)
- Case CRUD, document upload with OCR
- Multi-pass AI report generation (section-by-section expansion to avoid 502s)
- Ground deduplication logic
- All 4 report tiers + Barrister View with Issue Matrix attachment
- PDF/DOCX export with proper footers and legal disclaimers
- iOS-safe PDF preview via /document-preview route
- PayID payment flow with admin email notifications on payment submission
- Landing page with states, crimes, statistics, pricing, tier comparison
- "What This Tool Does" section positioned after hero states/crimes
- Legal resources, glossary, forms, FAQ, success stories, lawyer directory pages
- Appeal statistics page (bright blue background, vibrant red text)
- Floating scroll buttons (bright blue, repositioned above Emergent badge)
- DO NOT UNDO markers across 75+ critical lines

## Recent Changes (April 2026)
- **PayID Admin Notification**: Added `send_admin_payid_alert()` — admin now receives email when user submits PayID payment with user details, amount, reference, and link to Admin Dashboard
- Moved "What This Tool Does" section to appear right after hero states/crimes on landing page
- Barrister View depth overhaul (section-by-section expansion)
- Frontend report visibility bug fix
- Ground deduplication keyword mapping fix
- Floating button overlap fix

## Pending Items
- P0: Verify AppFooter styling (bold white, dark bg, flowing font)
- P1: Verify How It Works page images (IMG_4323–IMG_4327)
- P1: Build Native Mobile App (Capacitor)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time Collaboration/Chat
- P2: Case Sharing

## Credentials
- Email: djkingy79@gmail.com / Password: Grubbygrub88
