# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Deb King is building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. The app features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Scale in depth. Free (Base) -> $150 (2x depth) -> $200 (3x depth).
- **Barrister View:** Locked until all 3 standard reports generated/paid. Capstone synthesis.
- **Report Language:** STRICT third-person educational tool. Paragraphs, not bullet points.
- **Branding & Disclaimers:** All reports/exports: "NOT LEGAL ADVICE" disclaimers + branding footer (scales icon + Appeal Case Manager + Founded by Debra King).
- **UI/UX:** Forced light mode globally. High contrast. Blue/slate/navy palette. Bright blue action buttons.
- **Paywalls:** Grounds of Merit shows only count until $99 paid. Admin bypasses all paywalls.
- **Australian English:** All UI text, code, and AI outputs use Australian spelling.
- **Export Buttons:** Every report must have Print, PDF, and Word buttons.
- **Document Footers:** CSS counter(page) for page numbers, appellant name, date. No static "Page 1". Branding footer embedded.
- **Footer Layout:** 3-column layout on all screen sizes (Brand | Explore | Legal).
- **Legal Resources:** Default filter "All states" (not NSW-only). All resource cards display visible state badges.
- **Terms of Service:** References "Commonwealth of Australia" and all states/territories (not just NSW).

## What's Been Implemented
- User auth (JWT + Google social login)
- Case CRUD with AI auto-detection of metadata
- Document upload with text extraction + background auto-timeline generation
- Grounds of Merit with strict $99 paywall
- 4-tier report system with Print/PDF/Word exports
- Branding footer on all report views and exports
- Legal Resources page with state filter defaulting to "all"
- Terms of Service covering all Australian jurisdictions
- Chat button (bottom-left), Home+ScrollTop (bottom-right)
- PDF preview auto-sizes to content height
- 3-column footer layout on all screen sizes
- Resource card badges using inline styles (Tailwind-purge-proof)

## Prioritised Backlog
- **P1:** Build Native Mobile App (Capacitor configured)
- **P1:** Custom domain setup (criminallawappealmanagement.com.au via GoDaddy)
- **P2:** Counsel conference prep attachment for Barrister View
- **P3:** Break up server.py monolith (>7300 lines)
