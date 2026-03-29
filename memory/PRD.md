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
React (CRA + Craco) + FastAPI 0.135.2 + MongoDB + OpenAI GPT-4o (Emergent LLM Key)

## Auth
- Emergent Google OAuth + Email/Password login
- Bearer token via localStorage (NOT cookies — proxy CORS conflict)

## Build & Install Config
- `.eslintrc.json` — Extends CRA config, disables problematic ESLint rules for CI builds
- `.yarnrc.yml` — Forces nodeLinker: node-modules for Yarn 2/3/4 compat
- `CI=true npx craco build` passes with zero errors

## Security Audit (29 Mar 2026)
14 of 15 CVEs fixed. Remaining: Pygments CVE-2026-4539 (no fix available).
- ecdsa 0.19.1 → 0.19.2 (CVE-2024-23342, CVE-2026-33936)
- cryptography 46.0.4 → 46.0.6
- starlette 0.37.2 → 1.0.0, fastapi 0.110.1 → 0.135.2
- pymongo 4.5.0 → 4.16.0, motor 3.3.1 → 3.7.1
- requests 2.32.5 → 2.33.0
- pillow 12.1.0 → 12.1.1
- pyasn1 0.6.2 → 0.6.3
- PyJWT 2.11.0 → 2.12.1
- pyOpenSSL 25.3.0 → 26.0.0
- black 26.1.0 → 26.3.1

## Completed Features
- Multi-pass AI report generation (4 tiers)
- Document upload with auto-metadata extraction
- PDF/Word/Print exports with branding footers
- Barrister Issue Matrix attachment
- Case chat (WebSocket)
- "Print All Documents" utility
- Appeal statistics page
- Legal resources, glossary, FAQ, lawyer directory
- Case sharing, admin dashboard, payments

## Pending
- P1: "How It Works" page images
- P1: Native Mobile App (Capacitor build)
- P2: Counsel conference prep for Barrister View
- P3: server.py monolith refactoring
