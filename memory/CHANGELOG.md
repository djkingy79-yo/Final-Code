# Appeal Case Manager — Changelog

## 2026-03-19 — Session 13 (Deployment Readiness + Report Reliability Fix)
- **Deployment readiness check PASSED** — No blockers found:
  - Auth redirect uses `window.location.origin` (not hardcoded)
  - All env vars properly configured
  - Backend/frontend supervisor configs correct
- **Report generation reliability FIXED** (P0 critical recurring issue):
  - Root cause 1: `emergentintegrations` module not installed in environment — fixed with pip install
  - Root cause 2: Subprocess used `python3` which didn't resolve to venv — fixed with `sys.executable`
  - Root cause 3: No retry or model fallback — added 3-attempt chain: Claude Sonnet 4 (x2) → gpt-4o-mini
  - Reports now complete successfully (~3 min with fallback)
  - Claude hits 502 errors intermittently, gpt-4o-mini fallback works reliably
- **Australian English verified** — No remaining American English in user-facing text
- **Print buttons verified** — All use `window.print()` (BarristerView, ReportView, CaseDetail)
- **Testing**: iteration_65 — 100% backend (9/9) + 100% frontend
  - Full polling flow verified: Generate → Poll → Complete (~174s)
  - Mobile responsive verified at 390px
  - All case tabs working

## 2026-03 — Session 12 (Unfinished Tasks Execution Sweep)
- Realtime notes collaboration upgraded:
  - Added WebSocket collaboration endpoint: `/api/cases/{case_id}/notes/ws`
  - Presence + typing events implemented
  - Mentions extraction for notes/comments
  - Threaded note comments (add/delete)
  - Pin/unpin alignment fixed (`PATCH /notes/{note_id}/pin`, compatibility fields: `is_pinned` + `pinned`)
- Report generation upgraded with **Aggressive Mode**:
  - `aggressive_mode` added to report request
  - Prompt directives updated for assertive primary/fallback orders
  - `content.aggressive_mode` persisted in saved report
- Barrister View expanded:
  - Comparative sentencing panel
  - Full relief options matrix (quash/retrial/substitute/reduce/dismiss)
- Deadline tracker calendar integration completed:
  - Google Calendar deep-link action
  - ICS export per deadline
- Contacts page ambiguity resolved:
  - Canonical route `/legal-contacts`
  - Redirect `/contacts -> /legal-contacts`
  - Cross-links between contact form and directory
- Mobile packaging progress:
  - `yarn build` completed
  - `npx cap sync` completed successfully
- Validation:
  - Testing report: `/app/test_reports/iteration_35.json`
  - Frontend sanity pass: success

## 2026-03 — Session 11 (AU English + Legal Background Images)
- Australian English pass (~20 corrections): "analyze" → "analyse", "organize" → "organise", "favor" → "favour"
- 4 AI-generated legal-themed background images added to landing page
- Testing: iteration_31 (95% pass)

## 2026-03 — Session 10 (PayID Email Notifications)
- Automatic email notifications for PayID and PayPal payment confirmations
- Professional HTML email templates with branding
- Sent via Resend API

## 2026-03 — Session 9 (Visitor Counter)
- Public visitor counter on landing page
- Backend analytics endpoints for tracking unique visitors

## 2026-03 — Session 8 (PayPal & PayID Integration)
- Full PayPal REST API integration
- PayID manual bank transfer support with unique reference codes
- Admin dashboard for verifying pending payments

## 2026-03 — Session 7 (Stripe Removal & Barrister View Overhaul)
- Stripe completely removed per user request
- Barrister View redesigned with premium gradient header and case strength score

## 2026-03 — Session 6 (Super Reports & Stripe)
- Report prompts massively upgraded (Quick Summary, Full Detailed, Extensive Log)
- Stripe payment integration (later removed)

## 2026-03 — Sessions 1-5 (Foundation)
- Core features: Auth, cases, documents, timeline, grounds, notes, reports
- UI/UX redesign with blue/white/red colour scheme
- All Australian states coverage
- Legal framework viewer with AustLII links
- Mobile responsive design
- Backend refactoring into routers
