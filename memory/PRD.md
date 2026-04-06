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
- Mobile: Capacitor (configured)

## What's Been Implemented
- Full report generation pipeline (4 tiers)
- Document upload & management
- Timeline analysis
- Grounds of merit tracking
- PDF/DOCX export with cover pages, disclaimers, footers
- Barrister View with Issue Matrix attachment
- Google Auth + email/password auth
- PayID payment flow
- DOMPurify XSS sanitisation (with style tag preservation)
- Lawyer Directory with verified links
- Appeal Statistics page
- How It Works tutorial page
- Sentence extraction normalisation across all reports
- Security audit (18-point checklist)
- Export Appeal Package (ZIP with all case materials and templates)
- Pipeline Portfolio Summary on Dashboard

## Completed This Session (Feb 2026)
- **Font Size Standardisation (P0):** Reduced all report body text from ~17-18px to 15.2px (0.95rem). Reduced headings from 1.6rem to 1.2rem. DOCX/PDF backend exports also reduced.
- **PayID Email Fix (P0):** Corrected typo `gmsil.com` → `gmail.com` in both frontend PaymentModal and backend payments router.
- **Export Package Fix (P0):** Fixed TypeError crash when supporting_evidence contains dicts (not strings). Export now generates valid ZIP files.
- **Terms of Service Font Reduction (P0):** All section content reduced from text-sm to text-xs across TermsOfService.jsx and TermsAcceptance.jsx.
- **Dashboard Overview Cards Enlarged (P1):** Stats cards increased to text-3xl numbers, w-14 h-14 icons, p-6 padding. Pipeline Portfolio Summary styled with border-2, text-2xl numbers.
- **Case Page Heading Enlarged (P1):** Title increased to text-2xl sm:text-3xl md:text-4xl font-extrabold. Identity card fields increased to text-lg sm:text-xl.

## Backlog
- P1: Deploy fixes to production (user must click "Deploy" in Emergent chat)
- P1: Build Native Mobile App (Capacitor configured)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat for Notes section
- P2: Case sharing between registered users

## Critical Guards
- DO_NOT_UNDO comments protect key functions
- DOMPurify must use `{ WHOLE_DOCUMENT: true, ADD_TAGS: ['style'] }`
- PDF export blob fallback for iOS must not be modified
- Grounds of merit hard cap: max 2 new per sync
- PayID email must remain djkingy79@gmail.com
