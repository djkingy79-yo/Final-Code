# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Criminal appeals management tool for Australian jurisdictions. Features secure document management, AI-powered case analysis, and tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) → $150 (2x depth) → $200 (3x depth). Barrister View locked until all 3 generated/paid.
- **Report Language:** STRICT third-person educational tool. No "we/us/our/you/your".
- **Branding:** Forced light mode. High contrast. No amber/brown. Blue action buttons.
- **Australian English:** analyse, organise, barrister, defence, offence throughout.
- **Payment:** PayID only (djkingy79@gmail.com, NAB). Stripe/PayPal permanently removed.
- **Trial Pricing:** First-time users get Grounds of Merit for $5.00 AUD (regular $99). One-time per user lifetime. Free Case Summary included.

## Tech Stack
React + Tailwind + Shadcn/UI | FastAPI + MongoDB | OpenAI GPT-4o via Emergent LLM | Capacitor 7 (iOS + Android) | Resend (Email) | reportlab + python-docx (Exports)

## Completed This Session (Feb 2026)
- Font size standardisation (reports, prints, exports)
- PayID email typo fix, Export Package crash fix
- Terms of Service font reduction, Dashboard cards enlarged, Case heading enlarged
- Native Mobile App build (Capacitor 7, camera scanning, offline, notifications, haptics, share)
- Payment unlock bug fix (feature type aliases, admin bypass, auto-refresh)
- Sticky investigation timer banner (always visible during AI analysis)
- **Trial Pricing System:** $5 Grounds of Merit trial for first-time users. Backend validates eligibility (0 completed payments). Frontend shows blue gradient banner with yellow badge, strikethrough on regular price. PaymentModal passes use_trial flag.

## Backlog
- P1: Deploy fixes to production
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat for Notes
- P2: Case sharing between users

## Critical Guards
- DO_NOT_UNDO comments protect key functions
- DOMPurify: `{ WHOLE_DOCUMENT: true, ADD_TAGS: ['style'] }`
- FEATURE_TYPE_ALIASES must include grounds_unlock → grounds_of_merit
- PayID email: djkingy79@gmail.com
- TRIAL_PRICE = 5.00, TRIAL_FEATURE = "grounds_of_merit"
