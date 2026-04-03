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

## Credentials
- Email: djkingy79@gmail.com / Password: Grubbygrub88
