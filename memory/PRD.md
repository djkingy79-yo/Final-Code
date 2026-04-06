# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Criminal appeals management tool for Australian jurisdictions. Features secure document management, AI-powered case analysis, and tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) -> $150 (2x depth) -> $200 (3x depth). Barrister View locked until all 3 generated/paid.
- **Report Language:** STRICT third-person educational tool. No "we/us/our/you/your".
- **Branding:** Forced light mode. High contrast. No amber/brown. Blue action buttons. Red Scale navbar icon (DO NOT change).
- **Australian English:** analyse, organise, barrister, defence, offence throughout.
- **Payment:** PayID only (djkingy79@gmail.com, NAB).
- **Disclaimers:** ALL print/export disclaimers MUST have bright red bg (#dc2626), white bold text, yellow hazard icon (#facc15). DO NOT revert.
- **Notes export:** Bright blue theme (#2563eb), NOT yellow/amber. Note cards: blue bg, white bold text.

## Tech Stack
React + Tailwind + Shadcn/UI | FastAPI + MongoDB | OpenAI GPT-4o via Emergent LLM | Capacitor 7 (iOS + Android) | Resend (Email) | reportlab + python-docx (Exports)

## Completed (Feb-Apr 2026)
- Font size standardisation (reports, prints, exports)
- PayID email typo fix, Export Package crash fix
- Native Mobile App build (Capacitor 7, camera scanning, offline, notifications)
- Payment unlock bug fix (feature type aliases, admin bypass, auto-refresh)
- Sticky investigation timer banner
- Trial Pricing System ($5 Grounds trial)
- Barrister View visible in main reports list
- Admin manual-unlock endpoint
- Custom branded app icons/splash screens (iOS, Android, Web/PWA)
- Print view font size reduction (Timeline h1: 18px, h2: 15px. Grounds h1: 18px, body: 13px)
- Disclaimer styling overhaul (ALL: bright red bg, white bold text, yellow hazard icon)
- EvidenceSummary garbage filter (filters key-concatenated strings)
- iOS PDF export auth fix (session_token as query param)
- Notes export: yellow→bright blue theme, note cards blue bg white text
- AustLII button: white→dark blue with white border
- About Deb bio: single block→3 columns
- Admin "How to verify" box: pale blue→bright blue bg, white bold text

## Backlog
- P0: Deploy all fixes to production
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat for Notes
- P2: Case sharing between users

## Critical Guards
- DO_NOT_UNDO comments protect key functions
- Navbar brand icon is RED bg-red-600 — DO NOT change
- `unlocked_features` check ALWAYS takes priority over `latestPaymentStatus`
- Disclaimers: bright red (#dc2626) bg + white text + yellow hazard icon — DO NOT revert
- Notes export: blue theme (#2563eb) — DO NOT change to yellow/amber
