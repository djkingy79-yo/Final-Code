# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The app features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $99 Grounds Unlock, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Free (Base) -> $99 Grounds Unlock -> $150 Full Detailed -> $200 Extensive Log -> Barrister View (after all 3)
- **Report Language:** STRICT third-person educational tool. No first/second person pronouns.
- **Branding:** Forced light mode. High contrast. Blue/slate/navy palette. Bright blue action buttons with white text.
- **Australian English:** analyse, organise, barrister, defence, offence throughout.
- **Ground Identification:** Must find ALL distinct grounds (8-15 per case). Dedup only merges near-identical titles.

## Tech Stack
- React (Frontend) + FastAPI (Backend) + MongoDB
- OpenAI GPT-4o via Emergent LLM Key
- Emergent Auth (Google social login)
- Resend (Emails), Stripe/PayPal/PayID (Payments)

## What's Been Implemented (ALL COMPLETE)
- Full auth flow (Google + email/password + forgot password)
- Case CRUD, document upload with OCR
- Multi-pass AI report generation (section-by-section expansion)
- Ground identification (thorough, all distinct grounds preserved)
- Ground deduplication (permissive — only merges near-identical titles)
- All 4 report tiers + Barrister View with Issue Matrix attachment
- PDF/DOCX export with proper footers and legal disclaimers
- iOS-safe PDF preview via /document-preview route
- PayID payment with one-click email confirmation (no login required)
- Case Chat (CaseChat.jsx + messages router)
- Notes Section (NotesSection.jsx + notes router)
- Case Sharing (ShareCaseModal.jsx + AcceptShareLink.jsx + collaboration router)
- Notification Bell
- Activity Feed
- Document Bundler
- Timeline (enhanced, auto-updates on new doc upload)
- Deadline Tracker
- Legal Framework Viewer
- Landing page with states, crimes, statistics, pricing, tier comparison
- "What This Tool Does" section positioned after hero states/crimes
- Legal resources, glossary, forms, FAQ, success stories, lawyer directory
- Appeal statistics page
- Auto-detection on doc upload (metadata, timeline, summary, pipeline extraction)
- Admin Dashboard with PayID pending payments management

## Pending Items
- P1: Build Native Mobile App (Capacitor)
- P2: Add counsel conference prep attachment to Barrister View

## Recent Changes (April 2026)
- Fixed "How To Use" page: removed ZIP reference, added Chat & Collaboration step, zoomed in all screenshots (edge-to-edge, wider container), fixed broken Barrister View image path
- Fixed grounds multiplying ROOT CAUSE: re-enabled topic matching in dedup, added cleanup to ALL 4 sync paths, only skip re-classification when 8+ issues already exist
- Fixed report content protection: new content must be >50% of backup length or backup is restored
- Fixed Full Detailed report only covering ~5 grounds: line multiplier `* 3` was wrong (grounds_enumerated is 1 line per ground, not 3)
- Fixed DOCX export: was reopening PDF preview instead of downloading Word file from backend API
- Fixed raw data in supporting evidence: added extractEvidenceText() parser across all views
- Fixed placeholder cases: "R v [Surname] [Year]" and variations filtered out
- Fixed font sizes across ALL print/PDF/Word views: info box labels bigger, ground titles smaller, body text bigger, consistent across ReportView, BarristerView, GroundsOfMerit, CaseDetail tab export, Print All bundle, and shared exportHtml utility
- Expanded Australian English: backend _AU_REPLACEMENTS 13→33 patterns, frontend auSpelling() expanded, classify+verify prompts now enforce Australian English explicitly
- Increased LLM retry resilience: 6 model slots (was 4), backoff 8-25s (was 5-14s)

## Credentials
- Email: djkingy79@gmail.com / Password: Grubbygrub88
