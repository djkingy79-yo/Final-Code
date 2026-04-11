# Appeal Case Manager — PRD

## Product Overview
Criminal appeals case management application for Australian jurisdictions. Features secure document management, AI-powered case analysis, and tiered reporting (Free, $150 Full Detailed, $200 Extensive Log, Barrister View).

## Core Requirements
- **Report Tiers:** Strictly scale in depth. Free -> $150 (2x) -> $200 (3x). Barrister View locked until all 3 are generated/paid.
- **Report Language:** STRICT third-person educational tool. Forensic appellate language. Australian English only.
- **UI:** Forced light mode. Blue/slate/navy palette. Bright blue action buttons with white text.
- **Legal Accuracy:** Cite current, state-specific, and federal Australian legislation with correct section numbers. NO NSW defaults.
- **Print Format:** All exported/printed documents: h1=18pt, h3=14pt, h4=14pt, body=12pt, Times New Roman. Footer: "Documented from the Criminal Law /Appeal Management Application - [Doc Type] - For [Case Name] DD/MM/YYYY Page X of Y" in Times New Roman, italic, 10pt.

## Architecture
- React frontend + FastAPI backend + MongoDB
- Emergent Google Auth, OpenAI GPT-4o (Emergent LLM Key), Resend emails
- Payment methods: Stripe (card/Apple Pay/Google Pay) + PayID (bank transfer)
- Capacitor v7 configured for native mobile

## What's Been Implemented

### Session 4 (Apr 2026) — Print, Security, Acceptance Pack, Case Law
- **Print All Fix:** Raw `##` markdown headings now converted to proper HTML headings via `mdToHtml()` helper
- **Font Sizes Fixed:** Title h1=18pt (was 22pt), h4 subheadings=14pt (was 12pt), body=12pt
- **Table of Contents:** Added to Complete Case Bundle (Print All / Word All / PDF All)
- **Australian English in Print:** `auSpelling()` applied to all text in buildPrintAllHtml
- **Barrister Quick Brief iOS Fix:** Changed from `window.location.assign()` to `window.open()` in new tab
- **Acceptance Pack Enhanced:** Increased font sizes (body 11pt, was 9pt), added Case Summary section, full ground descriptions + deep analysis + appellate pathway + similar cases + legislation, Notes section, standardised footer
- **Find Case Law Upgrade:** Tab renamed, API now returns AI-suggested authorities (cases + legislation) from grounds data, copy-to-clipboard for citations, AustLII search links for each authority
- **Download Token Security:** Short-lived (5-min), single-use tokens replace session_token in download URLs
- **Standardised Footer:** Exact format across all PDF, DOCX, and browser print views

### Session 3 (Apr 2026) — Footers, Download Token Security
- Backend shared footer logic (`export_footer.py`)
- Download token endpoint and auth integration

### Session 2 (Apr 2026) — iOS Safari, Pipeline, Translation
- `auSpelling.js` iOS-safe rewrite (zero regex)
- `created_at` KeyError fixes, duplicate index fixes
- Translation formatting (ReactMarkdown)
- Service worker cache strategy to network-first

### Session 1 (Apr 2026) — Jurisdiction Validation
- 9-jurisdiction end-to-end validation (all PASS)
- Citation anti-hallucination post-processing

### Previously Completed
- Stripe + PayID payment integration
- Payment History Dashboard with PDF receipts
- Federal jurisdiction routing
- Metadata soft warnings
- Security hardening (rate limiting, bcrypt)
- Barrister View deep synthesis + Issue Matrix
- PDF/DOCX exports with legal disclaimers

## Test Coverage
- Session 4: iteration_187 — 14/14 backend, 100% frontend
- Session 3: iteration_186 — 12/13 backend, 100% frontend
- Session 2: iterations 184-185 — 100% pass
- 9-jurisdiction matrix: 9/9 PASS

## Backlog
- P1: "How It Works" page screenshots verification (user-uploaded IMG_4323-4327)
- P1: `server.py` monolith refactor (user approved multi-session)
- P2: Verify "Success Stories" page content compliance
- P2: Native Mobile App (Capacitor v7)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat, Case sharing
