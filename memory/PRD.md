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
React (CRA + Craco) + FastAPI + MongoDB + OpenAI GPT-4o (Emergent LLM Key)

## Auth
- Emergent Google OAuth + Email/Password login
- Bearer token via localStorage (NOT cookies — proxy CORS conflict)
- Session tokens stored in user_sessions collection

## Build & Install Config
- `.eslintrc.json` — Extends CRA config, disables `no-unused-vars`, `react-hooks/exhaustive-deps`, `no-useless-escape`, `no-empty-pattern`, `no-control-regex`. Keeps `no-dupe-keys` as warn.
- `.yarnrc.yml` — Forces `nodeLinker: node-modules` for Yarn 2/3/4 compatibility
- `packageManager: yarn@1.22.22` in package.json (clean, no SHA hash)
- `CI=true npx craco build` passes with zero errors

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
- Removed axios.defaults.withCredentials=true (proxy CORS conflict)
- Backend CORS changed to allow_origin_regex
- Register endpoint returns session_token

### Build Fix (CRITICAL)
- 204 ESLint errors fixed — unused imports (Moon/Sun/theme/toggleTheme from removed dark mode), missing toast import, bare confirm() calls
- Created .eslintrc.json for proper ESLint config
- Created .yarnrc.yml for Yarn compatibility
- CI=true build now passes clean

### Code Quality
- WebSocket memory leak fixed (CaseChat.jsx)
- Dead auth_old.py removed

## Pending
- P1: "How It Works" page images
- P1: Native Mobile App (Capacitor build)
- P2: Counsel conference prep attachment for Barrister View
- P3: server.py monolith refactoring (>7400 lines)
- P3: Real-time collaboration on Notes
- P3: Case sharing enhancements
