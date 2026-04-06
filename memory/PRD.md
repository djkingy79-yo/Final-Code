# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Criminal appeals management tool for Australian jurisdictions. Features secure document management, AI-powered case analysis, and tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) -> $150 (2x depth) -> $200 (3x depth). Barrister View locked until all 3 generated/paid.
- **Report Language:** STRICT third-person educational tool. No "we/us/our/you/your".
- **Branding:** Forced light mode. High contrast. No amber/brown. Blue action buttons. Red Scale navbar icon (DO NOT change).
- **Australian English:** analyse, organise, barrister, defence, offence throughout.
- **Disclaimers:** ALL print/export disclaimers MUST have bright red bg (#dc2626), white bold text, yellow hazard icon (#facc15). DO NOT revert.
- **Notes export:** Bright blue theme (#2563eb), NOT yellow/amber.
- **Export fonts:** Body 12px, H1 18-20px, H2 14px, H3 13px. DO NOT increase.

## Tech Stack
React + Tailwind + Shadcn/UI | FastAPI + MongoDB | OpenAI GPT-4o via Emergent LLM | Capacitor 7 (iOS + Android) | Resend (Email) | reportlab + python-docx (Exports)

## Completed (Feb-Apr 2026)
- Font size standardisation (reports, prints, exports) — all reduced to 12px body
- PayID email typo fix, Export Package crash fix
- Native Mobile App build (Capacitor 7, camera scanning, offline, notifications)
- Payment unlock bug fix (feature type aliases, admin bypass, auto-refresh)
- Custom branded app icons/splash screens (iOS, Android, Web/PWA)
- Disclaimer styling overhaul (ALL: bright red bg, white bold text, yellow hazard icon)
- EvidenceSummary garbage filter (filters key-concatenated strings)
- iOS PDF export auth fix (session_token as query param)
- Notes export: yellow→bright blue, note cards blue bg white text
- AustLII button: white→dark blue with white border
- About Deb bio: single block→3 columns
- Admin "How to verify" box: pale blue→bright blue bg, white bold text
- **Legal Framework:** Fixed [object Object] in forms, raw JSON in legislation sections, underscore keys in time_limits
- **Grounds/Print All:** ground_type now capitalized with spaces (Sentencing Error not sentencing_error)
- **Print All:** law_sections handles both JSON strings and objects
- **Print All:** evidence properly filters garbage strings
- **Barrister View:** removed duplicate BARRISTER BRIEF badge, offence capitalized (Murder not murder)
- **Case Readiness Score:** heading enlarged (text-xl/2xl)
- **Export fonts:** body 12px, h1 20px, h2 14px across all exportHtml/buildTabPreviewHtml/buildPrintAllHtml
- **Legal Framework Typography:** subheadings 18px bold (h4) / 16px bold (h5), body text 12px/11px — clear hierarchy
- **iOS Mobile Menu:** converted from inline dropdown to full-screen fixed overlay with scroll support, X close button, WebkitOverflowScrolling
- **Dashboard Sidebar:** added iOS scroll support (WebkitOverflowScrolling: touch, overscrollBehavior: contain)

- **Statistics Data Update (April 2026):** All stats updated to latest verified sources — NSW (Jan 2026 provisional), VIC (2024-25 annual report), QLD (2024-25 annual report, 294 filings not 60), SA (DPP 2023-24, 74 appeals), WA (2024-25, 243 finalised), ABS (515,460 defendants 2023-24). Landing page and Stats page now show consistent success rates (24-32% range). Removed unverifiable "8,700 national appeals" and "684,138 cases" figures. Added proper source citations.
- **FAQ Forms & Filing:** Added 9 comprehensive questions about filling in appeal forms (Notice of Intention, Notice of Appeal, transcript requests, Case Stated, exhibit access, time limits, online filing, serving documents, correcting errors)

## Backlog
- P0: Deploy all fixes to production (user must click Deploy in Emergent chat)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat for Notes
- P2: Case sharing between users

## Critical Guards
- DO_NOT_UNDO comments protect key functions
- Navbar brand icon is RED bg-red-600 — DO NOT change
- Disclaimers: bright red (#dc2626) bg + white text + yellow hazard icon — DO NOT revert
- Notes export: blue theme (#2563eb) — DO NOT change to yellow/amber
- Export font sizes: body 12px, h1 18-20px — DO NOT increase
- LegalFrameworkViewer typography: h4=18px bold, subheadings=16px bold, body=12px/11px — DO NOT revert
- Mobile menu: full-screen fixed overlay (z-[100]) — DO NOT revert to inline dropdown
- LegalFrameworkViewer: must handle both string and object forms/sections
- EvidenceSummary: must filter garbage key-concatenated strings
