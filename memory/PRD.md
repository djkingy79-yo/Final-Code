# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Criminal appeals management tool for Australian jurisdictions. Features secure document management, AI-powered case analysis, and tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) → $150 (2x depth) → $200 (3x depth). Barrister View locked until all 3 standard reports generated/paid.
- **Report Language:** STRICT third-person educational tool. No "we/us/our/you/your".
- **Branding:** Forced light mode. High contrast. No amber/brown. Blue action buttons.
- **Australian English:** analyse, organise, barrister, defence, offence throughout.
- **Payment:** PayID only (djkingy79@gmail.com, NAB). Stripe/PayPal permanently removed.

## Tech Stack
- Frontend: React + Tailwind + Shadcn/UI
- Backend: FastAPI + MongoDB
- AI: OpenAI GPT-4o via Emergent LLM Key (LiteLLM)
- Auth: Emergent Google Auth + JWT
- Email: Resend
- Exports: reportlab (PDF), python-docx (DOCX)
- Mobile: Capacitor 7 (iOS + Android)

## What's Been Implemented

### Core Features
- Full report generation pipeline (4 tiers)
- Document upload & management with camera scanning (native)
- Timeline analysis
- Grounds of merit tracking with payment unlock
- PDF/DOCX export with cover pages, disclaimers, footers
- Barrister View with Issue Matrix attachment
- Google Auth + email/password auth
- PayID payment flow with admin approval
- DOMPurify XSS sanitisation (with style tag preservation)
- Lawyer Directory with verified links
- Appeal Statistics page, How It Works tutorial page
- Export Appeal Package (ZIP)
- Pipeline Portfolio Summary on Dashboard

### Native Mobile App (Capacitor)
- Camera document scanning, offline access, push/local notifications
- Haptic feedback, native share, biometric auth permissions
- iOS & Android projects generated at /app/frontend/ios and /app/frontend/android

## Completed This Session (Feb 2026)
- **Font Size Standardisation:** All reports, prints, and exports
- **PayID Email Fix:** gmsil.com → gmail.com
- **Export Package Fix:** TypeError on supporting_evidence dicts
- **Terms of Service Font Reduction**
- **Dashboard Overview Cards Enlarged**
- **Case Page Heading Enlarged**
- **Native Mobile App Build:** Full Capacitor 7 setup with 11 plugins
- **Payment Unlock Bug Fix (P0):**
  - Added `grounds_unlock` to FEATURE_TYPE_ALIASES (legacy data support)
  - Made grounds endpoint use `canonical_feature_type` for unlock check
  - Added admin bypass to grounds endpoint (admin can view any case)
  - Fixed payment query to use case owner's user_id (not admin's)
  - Added "Refresh Status" button on paywall banner
  - Added "Check Status" button in PaymentModal after submission
  - PaymentModal auto-refreshes case data on close
  - Fixed legacy bad data in DB (normalised non-canonical feature names)

## Backlog
- P1: Deploy fixes to production (user must click "Deploy" in Emergent chat)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat for Notes section
- P2: Case sharing between registered users

## Critical Guards
- DO_NOT_UNDO comments protect key functions
- DOMPurify must use `{ WHOLE_DOCUMENT: true, ADD_TAGS: ['style'] }`
- PDF export blob fallback for iOS must not be modified
- Grounds of merit hard cap: max 2 new per sync
- PayID email must remain djkingy79@gmail.com
- All native calls wrapped in isNativePlatform() checks
- FEATURE_TYPE_ALIASES must include grounds_unlock → grounds_of_merit
