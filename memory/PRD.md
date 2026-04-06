# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Criminal appeals management tool for Australian jurisdictions. Features secure document management, AI-powered case analysis, and tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) -> $150 (2x depth) -> $200 (3x depth). Barrister View locked until all 3 generated/paid.
- **Report Language:** STRICT third-person educational tool. No "we/us/our/you/your".
- **Branding:** Forced light mode. High contrast. No amber/brown. Blue action buttons. Red Scale navbar icon (DO NOT change).
- **Australian English:** analyse, organise, barrister, defence, offence throughout.
- **Payment:** PayID only (djkingy79@gmail.com, NAB).
- **Trial Pricing:** First-time users get Grounds of Merit for $5.00 AUD (regular $99).
- **Disclaimers:** ALL print/export disclaimers MUST have bright red bg (#dc2626), white bold text, yellow hazard icon (#facc15). DO NOT revert to pale pink/red border style.

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
- **Print view font size reduction** — Timeline h1: 28px→18px, h2: 20px→15px. Grounds h1: 22px→18px, body: 14px→13px
- **Disclaimer styling overhaul** — ALL print/export disclaimers now: bright red bg (#dc2626), white bold text, yellow hazard icon (&#9888;). Applied to: Timeline, Grounds (single + full export), ReportView (print + on-screen), BarristerView (print + on-screen), CaseDetail (tab export), exportHtml.js (Word/PDF exports)
- **EvidenceSummary garbage filter** — Filters key-concatenated strings like "document_idfilenamequotepage_referenceroleconfidence"
- **iOS PDF export auth fix** — Timeline PDF export now appends session_token as query param for iOS devices

## Backlog
- P0: Deploy all fixes to production (user's live domain is out of sync)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat for Notes
- P2: Case sharing between users

## Critical Guards
- DO_NOT_UNDO comments protect key functions
- Navbar brand icon is RED bg-red-600 — user rejected generated icon replacement
- `unlocked_features` check ALWAYS takes priority over `latestPaymentStatus`
- PayID email: djkingy79@gmail.com
- TRIAL_PRICE = 5.00, TRIAL_FEATURE = "grounds_of_merit"
- Disclaimers MUST be bright red (#dc2626) bg + white text + yellow hazard icon — DO NOT revert
