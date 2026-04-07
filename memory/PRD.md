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

- **iOS Export Fix (April 2026):** Replaced ALL blob URL downloads (createObjectURL) across every export button with document-preview route navigation (window.location.assign). Fixes WebKitBlobResource error on iOS Safari. Fixed Word All button mode from 'pdf' to 'word'. Affected files: ReportView, BarristerView, CaseDetail, GroundsOfMerit, TimelineEnhanced.
- **Print/Export Font Sizes (April 2026):** Reduced body text across all print/export views — ReportView body 9pt, BarristerView body 9pt, Grounds body 11px, exportHtml body 10px. All heading sizes reduced proportionally.
- **Report Section Parser (April 2026):** Now handles both numbered (## 1. Title) and unnumbered (## TITLE) markdown section headers. Minimum content threshold reduced from 80 to 20 chars to prevent dropping short sections like Plain English Guide.
- **Landing Page Trial Banner (April 2026):** Card-style banner at top of page (after disclaimer), matching Dashboard styling. Sparkles icon in white circle. Compact, clickable (opens auth modal). Inline `style={{ color: '#ffffff' }}` forces white text.
- **Auto-Identify Background Task (April 2026):** Converted synchronous auto-identify endpoint to background task pattern. POST returns immediately with task_id. Frontend polls GET /status every 5s. Document extraction now runs concurrently (3 at a time). Fixes production timeout on cases with 16+ documents.
- **Case Creation Fix (April 2026):** Added field_validator to CaseCreate model that converts empty strings to None before enum validation. Fixes 422 error when form sends empty string for state/offence_category.
- **Sentence Auto-Detection Fix (April 2026):** Improved LLM prompt to extract HEAD SENTENCE + NPP only (no crime narrative). Added `_clean_sentence_candidate` to the LLM-detected path. Re-detection triggered when stored sentence contains crime narrative words.
- **Phase 1 Barrister Credibility Fixes (April 2026):**
  - Law sections: Frontend now filters out entries with "section not provided" or "unknown". Backend verify.py strips them post-LLM.
  - Similar cases: Renamed to "Comparable Authority". Filters placeholder citations ("[Surname]", "verification needed"). Backend strips them post-LLM.
  - Per-ground disclaimer: Added to every ground in print/PDF: "This analysis identifies potential appellate issues... All grounds require refinement and verification by a qualified legal practitioner."
  - Appellate pathway: New field per ground (classify.py generates, displayed in blue box). Maps to state-specific Criminal Appeal Act provisions.
  - Viability language: "Strong/Moderate/Weak" replaced with "Arguable — Strong / Arguable — Moderate / Requires Development".
  - Assertive language: AI prompts updated — "It is contended that..." not "may have". No percentage success rates anywhere.
  - Constitutional overreach: AI constrained to prioritise miscarriage of justice, unsafe verdict, misdirection, procedural unfairness over s 80 constitutional framing.
  - Deep analysis structure: Mandatory Trial Finding → Error Identified → Materiality → Consequence → Appellate Viability.

## Backlog
- P0: Deploy all fixes to production (user must click Deploy in Emergent chat)
- P1: Phase 2 Structural — appellate pathway enforcement, ground overlap merging, new ground structure
- P1: Phase 3 Report Differentiation — Quick (issue ID only), Full (appellate pathway analysis), Extensive (operations engine with checklists/evidence gaps/filing), Barrister View (pure synthesis, no repetition)
- P1: Phase 4 Advanced — full pipeline integration, three-axis viability scoring, operations engine
- P2: Build Native Mobile App (Capacitor configured, needs build + test)
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
- Auto-identify: background task pattern with polling — DO NOT revert to synchronous
- Landing page trial banner: card-style at top, NOT inside hero section
- Law sections: MUST filter "section not provided" / "unknown" — DO NOT display placeholders
- Similar cases: heading is "Comparable Authority" NOT "Similar Cases (AI-Suggested)" — DO NOT revert
- Strength labels: "Arguable — Strong / Arguable — Moderate / Requires Development" — DO NOT revert to "Strong/Moderate/Weak"
- AI prompts: assertive language ("It is contended that...") — DO NOT revert to "may have"
- Reports: NO percentage success rates — use appellate viability language only
