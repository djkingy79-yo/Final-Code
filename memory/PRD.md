# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The app features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $99 Grounds Unlock, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) -> $99 Grounds Unlock -> $150 Full Detailed -> $200 Extensive Log -> Barrister View (after all 3)
- **Report Language:** STRICT third-person educational tool. No first/second person pronouns.
- **Branding:** Forced light mode. High contrast. Blue/slate/navy palette. Bright blue action buttons with white text.
- **Australian English:** analyse, organise, barrister, defence, offence throughout.
- **Ground Identification:** Must find ALL distinct grounds (8-15 per case). Dedup only merges near-identical titles.

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
│   │   ├── email_service.py   # Payment emails + admin PayID alerts with one-click confirm
│   │   ├── ground_dedup.py    # Dedup logic (fuzzy 85 + word overlap 60% only, NO topic merging)
│   │   ├── pipeline/classify.py  # AI ground identification (thorough, 8-15 grounds)
│   ├── routers/
│   │   ├── payments.py        # ACTIVE payment router (PayID with email-confirm endpoint)
│   │   ├── grounds.py         # Ground management and sync
├── frontend/src/
│   ├── pages/
│   ├── components/
│       ├── AuthModal.jsx      # Login/Register with Forgot Password link
│       ├── PaymentModal.jsx
├── DO_NOT_UNDO.md
```

## What's Been Implemented
- Full auth flow (Google + email/password + forgot password)
- Case CRUD, document upload with OCR
- Multi-pass AI report generation (section-by-section expansion)
- Ground identification (thorough, all distinct grounds preserved)
- Ground deduplication (permissive — only merges near-identical titles)
- All 4 report tiers + Barrister View with Issue Matrix attachment
- PDF/DOCX export with proper footers
- PayID payment with one-click email confirmation (no login required)
- Landing page with "What This Tool Does" after hero states/crimes

## Recent Changes (April 2026)
- **Ground Identification Overhaul**: AI prompt now identifies ALL grounds (8-15) instead of merging to 3-8
- **Dedup Fix**: Removed aggressive topic-based merging. Now only merges titles with fuzzy score >= 85 or word overlap > 60%
- **Forgot Password**: Added link in AuthModal login form
- **PayID One-Click Email Confirm**: Admin confirms payments directly from Gmail
- **PayID Admin Notification**: Admin receives email when user submits payment
- **Landing Page**: "What This Tool Does" section moved after hero

## Pending Items
- P0: Verify AppFooter styling (bold white, dark bg, flowing font)
- P1: Verify How It Works page images (IMG_4323–IMG_4327)
- P1: Build Native Mobile App (Capacitor)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time Collaboration/Chat
- P2: Case Sharing

## Credentials
- Email: djkingy79@gmail.com / Password: Grubbygrub88
