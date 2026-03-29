# Appeal Case Manager — PRD

## Problem Statement
Criminal appeals management tool for Australian jurisdictions. Features secure document management, AI-powered case analysis, and tiered reporting (Free, $150 Full Detailed, $200 Extensive Log, locked Barrister View).

## Core Requirements
- Report tiers scale in depth: Free → $150 (2x) → $200 (3x) → Barrister (synthesis)
- Barrister View locked until all 3 standard reports generated/paid
- Strict third-person language — no "we/us/our/you/your"
- Legal disclaimers on all reports/exports
- Forced light mode, high contrast, blue/slate/navy only, bright blue buttons

## Tech Stack
React + FastAPI + MongoDB + OpenAI GPT-4o (Emergent LLM Key)

## Auth
- Emergent Google OAuth + Email/Password login
- Bearer token via localStorage (NOT cookies — proxy CORS conflict)
- Session tokens stored in user_sessions collection

## Completed Features
- Multi-pass AI report generation (4 tiers)
- Document upload with auto-metadata extraction
- PDF/Word/Print exports with branding footers
- Barrister Issue Matrix attachment
- Case chat (WebSocket)
- "Print All Documents" utility
- Appeal statistics page
- Legal resources, glossary, FAQ, lawyer directory
- Case sharing between users
- Admin dashboard
- PayID/Stripe payments
- Mobile-responsive UI

## Bug Fixes (29 Mar 2026)

### Auth CORS Fix
- Root cause: K8s/Cloudflare proxy overwrites Access-Control-Allow-Origin to "*" while backend sets Access-Control-Allow-Credentials: true — browsers reject this combo
- Fix: Removed axios.defaults.withCredentials=true, auth uses Bearer tokens from localStorage exclusively
- Backend CORS changed to allow_origin_regex for proper origin reflection
- Register endpoint now returns session_token in body
- Verified: 15/15 backend + 8/8 frontend tests (iteration 115), 12/12 live browser CORS tests (iteration 116)

### Code Audit Bug Fixes
- WebSocket memory leak: CaseChat.jsx reconnection loop continued after component unmount. Fixed with mountedRef guard.
- ESLint warnings: 9 components had missing useEffect deps. Fixed with eslint-disable-next-line comments for intentional mount-only effects.
- Dead code: Removed duplicate auth_old.py router file.
- Verified: 17/17 backend + all frontend tests passed, 0 compile warnings (iteration 117)

## Pending
- P1: "How It Works" page images (IMG_4323-IMG_4327) — page has text captions only, no actual screenshots
- P1: Native Mobile App (Capacitor build)
- P2: Counsel conference prep attachment for Barrister View
- P3: server.py monolith refactoring (>7400 lines)
- P3: Real-time collaboration on Notes
- P3: Case sharing enhancements
