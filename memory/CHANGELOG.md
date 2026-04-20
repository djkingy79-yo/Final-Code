# Appeal Case Manager — Changelog


## 20 Apr 2026 — CTA Conversion Source Tracking
- **What's new:** Every Google sign-in CTA across the app now tags itself with a unique source label. When a new user first signs up, that label is written to the user document as `signup_source` — giving Deb visibility into which pages/buttons actually convert visitors into registered users.
- **Frontend:**
  - `startGoogleLogin(source)` in `/app/frontend/src/lib/oauthState.js` now accepts an optional source string. Defaults to `window.location.pathname`. Stored in `localStorage` under key `signup_source` before the redirect to Google.
  - `consumeSignupSource()` helper reads + clears the value.
  - `App.js` AuthCallback consumes the source and includes it in the `POST /api/auth/google/callback` body.
  - Explicit source labels applied to the 5 page CTAs: `about-get-started`, `how-to-use-get-started`, `success-stories-get-started`, `statistics-get-started`, `appeal-stats-signin`. `PageCTA` variants self-tag as `pagecta-{variant}`. AuthModal's Google button tags `modal-{pathname}` (e.g. `modal-landing`).
- **Backend:**
  - `/api/auth/google/callback` (`routers/auth.py`) now accepts optional `signup_source` in the request body. Persisted on **NEW user documents only** (never overwrites existing users). Truncated to 128 chars, stripped, skipped if empty.
  - New admin endpoint `GET /api/admin/signup-sources` (`routers/admin.py`) returns aggregated counts grouped by source: `{total_users, users_with_source, sources: [{source, count, first, last}]}` sorted by count desc. Admin-gated via `ADMIN_EMAILS`.
- **Tests:** 4 new pytest regression tests in `backend/tests/test_signup_source_tracking.py` — all passed (callback accepts new field, callback backwards-compatible without it, admin endpoint requires auth, admin endpoint rejects non-admin). Live endpoint verified returning `{total_users: 553, users_with_source: 0, sources: []}` as expected (no post-deploy sign-ups yet).
- **Frontend smoke:** Playwright-verified `about-get-started` label correctly written to localStorage on CTA click.
- **Mobile bundle resynced** (yarn build ✔ + cap sync ✔ for both iOS + Android).

### How to read the analytics later
Once users start signing up, Deb can curl:
```
GET /api/admin/signup-sources
Authorization: Bearer <her session token>
```
And see something like:
```
{ "total_users": 612, "users_with_source": 59,
  "sources": [
    {"source": "success-stories-get-started", "count": 23, "first": "...", "last": "..."},
    {"source": "modal-landing",               "count": 18, ...},
    {"source": "pagecta-default",             "count": 11, ...},
    ...
  ] }
```


## 20 Apr 2026 — Clarification: Preview OAuth 403 / Fix: Appeal Stats Edge-to-Edge Hero
- **Preview Google OAuth 403 is NOT a bug** — user clicked CTAs from the Emergent preview URL (`*.preview.emergentagent.com`), which is correctly rejected by Google Cloud Console because only `criminallawappealmanagement.com.au` is registered as an authorised origin. This is Google's security working as designed. Buttons will work perfectly once deployed to production.
- **Fixed edge-to-edge blue hero banner** on AppealStatisticsPage. The "Australian Appeal Statistics" section was spilling full viewport width (`py-12 px-6 bg-blue-800`) while the logo above (contained `max-w-4xl`) and content below (contained `max-w-5xl`) were properly boxed. Visually jarring after the logo was added. Wrapped it in `max-w-5xl mx-auto rounded-2xl` so it's now a contained rounded card matching the rest of the page (1024 px wide, 448 px margin each side on 1920 viewport). All other added-logo pages use `bg-white` heroes which blend with page background — no further changes needed.


## 20 Apr 2026 — "Founded by Deb King" Caption + Broken CTA Buttons Fixed
- **"Founded by Deb King"** small-caps red caption added under the page logo on all 14 info/stats pages (inside the reusable `<PageLogo />` component). Consistent authorship visibility + SEO signal on every page. Test IDs: `page-logo-top`, `page-logo-founder-caption`.
- **Broken CTA buttons fixed.** Deb reported via screenshots that several "Get Started" / "Sign In" / "Contact Us" buttons incorrectly bounced to the landing page instead of performing their intended action. Root cause: these CTAs used `<Link to="/">` or `navigate('/', { state: { openAuth: true } })` — but the landing page never honoured the `openAuth` state flag, so users just ended up stranded on the home page.
- **New atomic helper** `startGoogleLogin()` in `/app/frontend/src/lib/oauthState.js` — generates OAuth state, saves to localStorage + cookie, builds URL, navigates to `https://accounts.google.com/o/oauth2/v2/auth` — all in a single synchronous event handler (same proven pattern that fixed the AuthModal render-time bug).
- **CTAs now wired via `startGoogleLogin()`:** `AboutPage` "Get Started Free", `HowToUsePage` "Get Started Now", `SuccessStories` "Get Started Free", `Statistics` "Get Started Free", `AppealStatisticsPage` header "Sign In", and `PageCTA` component (which powers the "Ready to Build Your Case?" banner, the sticky bottom CTA, the inline CTA, and the default banner — appearing on multiple pages).
- **`FAQPage` "Contact Us"** now opens a `mailto:` to `REACT_APP_SUPPORT_EMAIL` (fallback `djkingy79@gmail.com`) with subject "Question from FAQ page" — was previously linking to `/contact` which redirected to `/legal-resources` (wrong target).
- **"Back" buttons on all pages** (LegalGlossary, HowItWorksPage, Statistics, FormTemplates, TermsOfService, SuccessStories) intentionally left pointing to `/` — they genuinely should return to landing.
- **Verified live on preview:** all 5 fixed CTAs hit `accounts.google.com` on click; FAQ Contact Us href = `mailto:djkingy79@gmail.com?subject=Question%20from%20FAQ%20page` ✓.
- **Mobile bundle resynced** (yarn build ✔ + cap sync ✔ for both iOS and Android).


## 20 Apr 2026 — Logo on All Public/Info Pages + Welcome-Back Toast
- **New reusable component** `/app/frontend/src/components/PageLogo.jsx` — centred, 320px/400px (mobile/desktop), `/logo.png`, matches the landing-page hero logo exactly, `data-testid="page-logo-top"`.
- **Logo added to 14 pages** right after the site header and before any content/heading: AppealStatisticsPage, SuccessStories, LegalFrameworkPage, ResourcesPage, LegalResourcesPage, FAQPage, HowItWorksPage, HowToUsePage, HelpPage, LegalGlossary, FormTemplates, LawyerDirectory, CompareCasesPage, Statistics.
- **Verified on preview** — Playwright confirms logo renders at 400×541 px on all 10 public pages (appeal-statistics, success-stories, legal-framework, legal-resources, faq, how-it-works, how-to-use, glossary, forms, lawyers). The 4 auth-gated pages (Help, Resources, CompareCases, Statistics) have the component inserted — will appear once signed in.
- **Welcome-back toast** on successful Google OAuth callback (`App.js`). Fires `toast.success('Welcome back, {firstName} — redirecting to your dashboard…')` with 1.5s duration immediately before the navigate-to-dashboard, so the user sees tangible confirmation sign-in worked (previously the redirect was silent and felt jarring on mobile). First name derived from `response.data.name` (fallback to email local-part, then 'there').
- **Mobile bundle resynced** (`yarn build` ✔ + `npx cap sync` ✔ for both iOS + Android).


## 20 Apr 2026 — OAuth State Mismatch ROOT CAUSE Found & Fixed
- **Bug reproduced on live domain** (Deb tested with the new diagnostics panel on iPhone Safari). Diagnostics confirmed: `hostname=criminallawappealmanagement.com.au`, `localStorage_has_state=true`, `cookie_has_state=true`, `returned_state_present=true`, `code_present=true` — **yet state mismatch still occurred**. Belt-and-braces storage was not the root cause.
- **Actual root cause:** `AuthModal.jsx` line 53 was calling `const googleLoginUrl = buildGoogleLoginUrl();` **at component render time**. Because `buildGoogleLoginUrl()` both generates a new state AND writes it to storage, every re-render (modal open, form typing, focus events, parent re-renders, Radix dialog animation) regenerated and overwrote the stored state. This created a race: by the time Google redirected back, the state in storage was no longer the state that had been sent.
- **Fix:** Moved `buildGoogleLoginUrl()` invocation from render time into the onClick handler of the `google-signin-btn` button. State is now generated + stored + embedded in the URL atomically inside a single synchronous event handler, with zero opportunity for intermediate re-renders to overwrite storage.
- **Tests (iteration_206):** 13/13 passed. Verified state is NOT written on page load, modal open, typing, or modal toggle — only on button click. Storage value matches URL state parameter. Multiple rapid clicks always end with matching state (no race). Retry button, diagnostics panel, email-to-support button, email/password login all intact.
- **Mobile bundle resynced** with the fix.


## 20 Apr 2026 — "4th Report" Rename + Email-to-Support + README Overhaul
- **Renamed all remaining user-visible "Barrister Brief / View / Quick Brief" strings** to the canonical **"Appellate Research Brief"**. Code touchpoints:
  - `backend/routers/reports.py` — 2-page PDF title `"BARRISTER QUICK BRIEF"` → `"APPELLATE RESEARCH BRIEF — QUICK BRIEF"`.
  - `backend/services/barrister_generator.py` — output heading `## Final Barrister Briefing Note` → `## Final Appellate Research Briefing Note` (6 occurrences across required_headings, prompt instructions, and section budgets).
  - `backend/models/__init__.py` — checklist title `"Generate Barrister View report"` → `"Generate Appellate Research Brief report"`.
  - `README.md` — Tier 4 table row, Section 7 ("Appellate Research Brief — Counsel-Ready Synthesis"), Section 8 ("Appellate Research Brief — Quick Brief (2-Page PDF)"), Section 14 bullet, service layer doc, and frontend markdown table reference.
  - Left untouched (intentional): internal DB key `barrister_view`, endpoint URLs (`/reports/barrister-quick-brief`), service filename `barrister_generator.py`, page component `BarristerView.jsx`, generic references to the *profession* (Bar Associations, Find a Barrister, lawyer-directory firm names).
- **Email-to-support button** added to the sign-in diagnostics panel (`App.js`). Opens `mailto:` with pre-filled subject and body (full diagnostics JSON) to `REACT_APP_SUPPORT_EMAIL`. Button only renders when the env var is set — graceful fallback for self-hosted forks. `data-testid="auth-email-diagnostics-btn"`. Verified live on preview.
- **Env vars added:** `REACT_APP_SUPPORT_EMAIL` in `frontend/.env` (defaults to `djkingy79@gmail.com`).
- **README overhauled end-to-end** — zero Emergent references remain (grep-verified), all recent features documented (direct Google OAuth, belt-and-braces CSRF state, background polling for bulk extract, live pass-by-pass progress, 27 recent Acts, 5-gate CI pipeline with MongoDB service container, Capacitor 7 mobile, sign-in diagnostics panel). `EMERGENT_LLM_KEY` removed from env table; `OPENAI_API_KEY`, `GOOGLE_CLIENT_ID/SECRET`, `REACT_APP_GOOGLE_CLIENT_ID`, `REACT_APP_SUPPORT_EMAIL`, mobile App Store/Play URLs added.
- **Mobile bundle resynced** (`yarn build` + `npx cap sync` — iOS + Android, 12 plugins synced).


## 20 Apr 2026 — Sign-in Diagnostics Panel + Mobile Bundle Resync
- **Diagnostics panel** on the OAuth failure card (`App.js`). New collapsible "Show sign-in diagnostics" link reveals a JSON dump of: timestamp, hostname, protocol, referrer, `navigator.cookieEnabled`, whether state exists in localStorage, whether state exists in cookie, whether a returned `state`/`code` is in the URL, the `errorDetail`, and userAgent. A "Copy diagnostics to clipboard" button lets any user forward the payload to Deb in one click. Test IDs: `auth-toggle-diagnostics-btn`, `auth-diagnostics-panel`, `auth-copy-diagnostics-btn`. Verified via screenshot on preview — panel renders correctly with real values.
- **Mobile bundle resynced** to include both the OAuth state fix and the diagnostics feature. `yarn build` ✔ (24 s, build OK), `npx cap sync` ✔ for both iOS + Android (12 Capacitor plugins in sync). CocoaPods/xcodebuild steps deferred to Deb's Mac as documented in `MOBILE_BUILD.md`.


## 20 Apr 2026 — OAuth CSRF State — Belt-and-Braces Fix (GoDaddy DNS hop resilience)
- **Bug:** Google sign-in on `criminallawappealmanagement.com.au` failed with "Security check failed (state mismatch)". Root cause: GoDaddy's DNS-level forwarding between `www.` and the bare domain changes the storage origin mid-OAuth-flow, wiping `sessionStorage`. The previous agent had partially moved the state to `localStorage` in `AuthModal.jsx` but left `App.js` still reading from `sessionStorage`, so storage and read never matched.
- **Fix:** New helper `/app/frontend/src/lib/oauthState.js` exposing `generateState`, `saveOAuthState`, `readOAuthState`, `clearOAuthState`. State is now written to **BOTH** `localStorage` **AND** a parent-domain-scoped cookie (`Domain=.criminallawappealmanagement.com.au` in prod, host-only in preview/localhost). Read falls back from localStorage → cookie, so either storage layer alone is sufficient to survive the `www.` ↔ bare-domain hop.
- **Files touched:** new `frontend/src/lib/oauthState.js`; `frontend/src/App.js` (AuthCallback state verification + retry-button state regeneration now use the helper); `frontend/src/components/AuthModal.jsx` (buildGoogleLoginUrl uses the helper).
- **Tests (iteration_205):** 11/11 passed. Verified: OAuth URL construction, dual-location storage, matching-state passes, wrong-state fails, cookie-only fallback works (simulates localStorage wipe by DNS hop), post-check cleanup of both stores, retry-button regenerates state, email/password regression intact, backend `/api/auth/google/callback` returns clean 400/401 on bad input.
- **Deb's real-world test still required:** Sign in from `criminallawappealmanagement.com.au` (bare domain preferred). The CSRF mismatch screen should no longer appear.


## 19 Apr 2026 — Direct Google OAuth Wired (replaces Emergent-managed auth)
- **Backend (`routers/auth.py` + `config.py` + `.env`):** New `POST /api/auth/google/callback` endpoint. Exchanges Google `code` at `https://oauth2.googleapis.com/token`, verifies `id_token` with `google.oauth2.id_token.verify_oauth2_token` against `GOOGLE_CLIENT_ID`, upserts user by verified email, issues session_token + sets secure httponly cookie. Returns 400 on missing fields, 401 on invalid code, 503 if OAuth env not configured, 504 on Google unreachable, 403 if email not verified.
- **Frontend (`AuthModal.jsx` + `App.js`):** `buildGoogleLoginUrl()` now builds direct Google authorize URL (`https://accounts.google.com/o/oauth2/v2/auth`) with OpenID scopes + CSRF `state` param stored in `sessionStorage`. `AuthCallback` component reads `code` from query, verifies `state` match, POSTs to new backend endpoint. Legacy `session_id` path kept briefly for users mid-redirect.
- **Env vars added:** backend `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`; frontend `REACT_APP_GOOGLE_CLIENT_ID`.
- **Last Emergent auth touchpoint removed from app** — `auth.emergentagent.com` no longer referenced anywhere in frontend source. Users matched by verified email preserve all existing accounts.
- **Tests (iteration_204):** 15/15 passed (missing code → 400, invalid code → 401, config loaded, id_token verification correct, Emergent fallback works, all regression tests pass for `/login`, `/register`, `/me`, `/logout`).
- **⚠️ Deb must rotate the client secret** — the secret `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` was pasted in chat. Reset it via Google Cloud Console → Credentials → OAuth client → Reset Secret, then update `/app/backend/.env` `GOOGLE_CLIENT_SECRET`.
- **⚠️ Deb must fix Google Console JavaScript origin** from `http://criminallawappealmanagement.com.au` to `https://...` or mobile login will fail.


## 19 Apr 2026 — Mobile CTA + Emergent Reference Cleanup (Partial)
- **Mobile CTA added** to `HelpPage.jsx` → new "Get the iOS & Android App" section between "What is Criminal Appeal AI?" and "Step 1: Sign In". App Store + Google Play buttons are greyed-out placeholders showing "Coming soon" by default, and **auto-activate** when `REACT_APP_IOS_APP_STORE_URL` and/or `REACT_APP_GOOGLE_PLAY_URL` env vars are set (will open in new tab once live). Uses inline Apple/Google logo SVGs (no external CDN). `data-testid`s: `help-mobile-cta-section`, `help-app-store-cta`, `help-google-play-cta`.
- **Emergent CDN image purged.** Landing page hero image (`static.prod-images.emergentagent.com/...png`) downloaded to `/app/frontend/public/images/court-custody-hero.png` (1.28 MB). `LandingPage.jsx` now references the local asset via `${PUBLIC_URL}/images/court-custody-hero.png`.
- **Cosmetic cleanup.** Removed "Emergent badge" code comment from LandingPage.jsx.
- **Remaining Emergent touchpoints documented for Deb** (can't auto-remove — require her input):
  - `auth.emergentagent.com` Google OAuth redirect — needs Deb's own Google Cloud OAuth app (`client_id` + `client_secret`) for me to rewire to direct Google OAuth.
  - `EMERGENT_LLM_KEY` — needs Deb's own OpenAI/Anthropic/Gemini API key to swap off the universal key.
  - `REACT_APP_BACKEND_URL` preview URL — goes away when backend is deployed to Deb's own host (Vercel/Railway/VPS).
- **Refund / billing concern** (user said she paid >$3k): explicitly NOT handled by main agent. Must be routed via `support_agent` if she requests again.


## 19 Apr 2026 — P1 Mobile Prep + P2 Attachment B Verification
- **P2 — Counsel Conference Prep (Attachment B) verified COMPLETE.** Feature was already shipped in `services/barrister_generator.py` (lines 846–911). Verified present in all 5 most recent barrister reports (rpt_1d3ddfc9c595, rpt_3ef5f8797fdb, rpt_a976824bd035, rpt_35c073a0c8f8, rpt_e0300749db58). Contains B.1 Key Questions, B.2 Weak Points (markdown table), B.3 Likely Prosecution Responses, B.4 Document References (checklist table), B.5 Suggested Conference Agenda. Parsed by `parseBarristerSections` in `BarristerView.jsx` and rendered via ReactMarkdown+remarkGfm (tables render correctly).
- **P1 — Mobile build prep COMPLETE.**
  - Re-ran `yarn build` (18 s) + `npx cap sync` (both iOS + Android) — 12 Capacitor plugins synced.
  - Updated `capacitor.config.json` → `allowNavigation` now whitelists `*.emergentagent.com`, `criminallawappealmanagement.com.au`, `*.criminallawappealmanagement.com.au` (stops mobile CORS failures on custom domain).
  - Created `/app/frontend/MOBILE_BUILD.md` with step-by-step Xcode + Android Studio build instructions, signing notes, keystore commands, release-bundle upload steps, and re-sync workflow.
  - Native `.ipa` and `.aab` production builds must be completed on Deb's Mac / with Android Studio (Linux container has no JDK/Xcode) — all project state is deploy-ready.


## 19 Apr 2026 — Full Critical Triage & CI Parity Sweep
- **Triage result: zero critical backend/frontend/security/build blockers.** Production code was already clean.
- **Fixes applied (minimal, test-scaffolding only):**
  - Ran `ruff --fix` on `backend/tests/` (58 F541/F841/F811 auto-fixed).
  - Replaced 2 bare `except:` → `except Exception:` in `tests/test_export_endpoints_iteration201.py` (E722).
  - Added `backend/pyproject.toml` with `[tool.ruff] extend-exclude = ["tests/legacy"]` so archived scripts never noise-block CI again.
- **CI parity verification (all green):**
  - `ruff check backend/` → All checks passed.
  - `eslint frontend/src/` → No issues found.
  - `pytest` offline suite (396 tests across offence/state/legal/dedup/legislation frameworks) → 396 passed in 1.91 s.
  - `yarn build` with `REACT_APP_BACKEND_URL` → built cleanly in 20 s, all chunks generated, ready for deploy.
  - `pip check` → no broken requirements.
  - `/api/health` → 200, DB connected. Frontend on port 3000 → 200.
- **Security scan (zero findings):** no hardcoded secrets (sk-/AKIA/AIza/ghp_), no `os.system`, no `subprocess(shell=True)`, no `eval/exec`, no bare `except:` in production code, no raw `innerHTML` (only `dangerouslySetInnerHTML` via `DOMPurify.sanitize`), all API keys read from `os.environ`.
- **Dependency health:** `emergentintegrations==0.1.1` properly gated with `--extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/` at the top of `requirements.txt`.


## 19 Apr 2026 — Real Backend-Fed Pass-by-Pass Report Progress
- **New feature on request:** Multi-pass report generation now emits real progress per pass instead of time-based estimates. Applies to Full Detailed (8 passes, 15 sections) and Extensive Log (10 passes, 24 sections).
- **Backend (`services/report_generator.py`):** Added `PASS_TITLES` dict mapping each pass label to a human-readable section title (e.g. `PASS 3/8` → "Grounds of Merit — Part 1"). Added `_update_report_pass_progress()` helper that persists `{current_pass, total_passes, pass_label, pass_title}` to `reports.generation_progress` before each pass runs. Helper wrapped in try/except so it cannot break generation.
- **Backend (`routers/reports.py`):** Extended `GET /cases/{case_id}/reports/{report_id}/status` to return `progress` sub-object when `status='generating'`. Added `$unset: {generation_progress: 1}` to all 3 completion/failure DB writes (success, backup restore, failure) to prevent stale progress leaking.
- **Frontend (`components/ReportsSection.jsx`):** Added `genProgress` state; `pollForCompletion` captures it every 3 s; in-flight banner now displays `PASS 3/8 — Grounds of Merit — Part 1` with a pill per pass (completed / active-pulsing / pending) and a real progress bar driven by `current_pass / total_passes`. Falls back to the existing time-based labels before the first poll returns.
- **Regression:** 7/7 backend tests pass (`test_report_progress_iteration203.py`). Existing elapsed timer, PipelineProgress widget, and document-extract ticker all intact.


## 19 Apr 2026 — "Request timed out" + "Failed to extract text" — Permanent Fix
- **Root cause:** Frontend `axios.defaults.timeout = 30000` was too tight, AND the synchronous `/api/cases/{case_id}/extract-all-text` endpoint made an LLM metadata-detect call that regularly took 60–90 seconds. Any case load while the backend was saturated by upload-triggered background work would timeout on the frontend even though the backend eventually succeeded.
- **Permanent fix — background polling (same pattern as `/investigate`):**
  - Converted `/api/cases/{case_id}/extract-all-text` to return a `task_id` immediately (~180 ms).
  - Added `GET /api/cases/{case_id}/extract-all-text/status?task_id=...` polling endpoint that returns `running` (with progress string) → `completed` (with result payload) → `not_found` if task expired.
  - Worker `_run_extract_all_text()` runs as `asyncio.create_task`, updates progress at each stage (Loading docs → Extracting text (i/n) → Analysing for metadata).
- **Frontend hardening:**
  - `axios.defaults.timeout`: 30 000 → 60 000 ms (still bounded; LLM paths now use polling).
  - `DocumentsSection.handleExtractAllText` rewired to start task + poll every 3 s with 20 s per-poll timeout; graceful "taking longer than expected" fallback.
  - `CaseDetail.fetchCaseData` now uses explicit 90 s timeout for the main case GET + documents GET, 60 s for the 5 other parallel fetches.
- **Regression:** 12/12 backend tests pass (`test_extract_all_text_iteration202.py`). Auto-detect metadata (offence category / state / court / case number) confirmed persisted on task completion.


## 18 Apr 2026 — Backend PDF/Word Export Formatting Parity
- **Font sizing reduced to match frontend print CSS** (`exportHtml.js`): Body 11pt, H1 16pt, H2 15pt, H3 13pt, tables 9pt, cover meta 10pt, cover disclaimer 9pt, body disclaimer 8pt. Applied across both ReportLab PDF and python-docx DOCX in `/app/backend/routers/report_exports.py`.
- **Footer label standardised** in `/app/backend/services/export_footer.py` → `Criminal Law Appeal Management / {Document Name} — {Defendant} — {Date}`. Footer font now 7pt Times-Italic (matches HTML print footer). Propagates to all export endpoints using `build_footer_label` (reports, timeline, translate, barrister pack, case export).
- **NumberedCanvas double-page bug fixed** — `showPage()` now calls `self._startPage()` instead of `_Canvas.showPage(self)`, so pages are committed exactly once in `save()`. PDFs previously produced 2× page count with alternating blank pages; now correct. 10-page Case Summary went from 20 pages/40KB → 10 pages/22KB.
- **Cover page tightened** — removed duplicate header block, reduced top spacer (18mm→6mm), cover table padding (10→5), margins (20mm→18mm) to eliminate wasted whitespace.
- **Regression:** 12/12 backend export endpoint tests pass (`test_export_endpoints_iteration201.py`) — reports, timeline, barrister-pack, and case export all produce valid PDFs with correct footer + font sizing.

## 9 Apr 2026 (Session 5) — Comprehensive Legal Framework Update
- **RECENT_LEGISLATION_UPDATES:** Added 27 verified recently commenced Australian Acts (2022-2026) to `offence_framework.py`, covering all jurisdictions.
- **Key Acts Added:** NSW Coercive Control (s 54D, 1 Jul 2024), Jury Amendment Act 2024 (10 Mar 2025), Knife Crime Act 2024, Racial and Religious Hatred Act 2025, Bail Act 2013 amendments, Child Protection Amendment Act 2024, Animal Sexual Abuse Act 2025, Good Character Bill 2026 (pending), Surveillance Devices Regulation updates; VIC Youth Justice Act 2024, Non-Fatal Strangulation Act, Performance Crime Act 2025, Anti-vilification Act 2025; QLD Coercive Control (s 334C, 26 May 2025), Making Queensland Safer Act 2024; SA Coercive Control (s 20A), High Risk Offenders Amendment; WA Family Violence Legislation Reform Act 2024; TAS Jari's Law; Federal Hate Crimes Act 2025, Wage Theft Act 2024.
- **Complete Criminal Frameworks for ALL jurisdictions:** Built 9 comprehensive criminal legislative frameworks (NSW, VIC, QLD, SA, WA, TAS, NT, ACT + Federal/Commonwealth). Each framework contains Primary Legislation (with key provisions/sections), Key Regulations, and Specialised Legislation. All 11 primary Criminal Codes/Acts verified per user's law guide: Crimes Act 1914 (Cth), Crimes Act 1900 (ACT), Crimes Act 1900 (NSW), Criminal Code 1899 (QLD), Criminal Code 1924 (Tas), Criminal Code Act Compilation Act 1913 (WA), Criminal Code Act 1995 (Cth), Criminal Code 2002 (ACT), Criminal Code Act 1983 (NT), Criminal Law Consolidation Act 1935 (SA), Crimes Act 1958 (Vic).
- **NSW Complete Criminal Framework:** Primary Acts (Crimes Act 1900 No 40, Criminal Procedure Act 1986 No 209, Crimes (Sentencing Procedure) Act 1999 No 92, LEPRA 2002 No 103, Evidence Act 1995 No 25), Key Regulations (Crimes Regulation 2020, Criminal Procedure Regulation 2017, Sentencing Procedure Regulation 2017, LEPRA Regulation 2016), Specialised Legislation (DV Act 2007, Bail Act 2013, Drug Misuse Act 1985, Summary Offences Act 1988, Mental Health Forensic Provisions Act 2020, Forensic Procedures Act 2000, Criminal Appeal Act 1912, Jury Act 1977).
- **Prompt Injection System:** `_build_state_framework_context()` auto-injects the correct state framework. `_build_federal_framework_context()` always injects Commonwealth framework. `_build_recent_legislation_context()` filters recent Acts by state + offence category. All three inject into standard reports AND Barrister View.
- **Anti-Hallucination Guardrails:** RECENT LEGISLATION AWARENESS in system prompts, LEGISLATION ACCURACY rules in report guardrails (cite FULL Act name + year, use current versions, flag uncertainty).
- **Regression Tests:** 81 pytest tests in `tests/test_legislation_framework.py` — all passing. Fresh reports generated on Homann v R (NSW) and R v JE (WA) confirming legislation cited in output.

## 1 Apr 2026 (Session 3) — Extensive Log Fix
- **Extensive Log (3rd Report) Generation Fixed:** Triggered and monitored a fresh `extensive_log` generation for case `case_927d110878e7`. All 8 passes completed successfully using `condensed_prompt` logic. Report: 117,184 chars, ~15,710 words, 25 sections. Multiple 502 errors were handled by pass-level retry with exponential backoff.
- **Condensed Prompt Protection:** Added DO_NOT_UNDO entry protecting the condensed_prompt approach.

## 1 Apr 2026 (Session 2) — Dedup & Resilience
- Grounds of Merit Deduplication — 12-topic fuzzy dedup with startup and post-sync safety nets
- Dedup Visual Badge (green "Dedup Active" UI badge)
- Database Normalisation Script (normalise_db.py)
- Orphaned Report Bug Fix (strict thresholds 70k/120k)
- 502 Proxy Timeout Resilience (pass-level retry + exponential backoff)
- Condensed Prompts for 8-Pass Engine (134k → ~20k for passes 2+)
- Google Login Blank Screen Fix (visible loading spinners)
- Google OAuth Redirect Loop Fix (3x retry before logout)

## Previous Sessions
- Full case management, documents, timeline, grounds, notes
- 4-tier report generation, PDF/DOCX export
- Barrister View with Issue Matrix attachment
- Chat collaboration, Case sharing
- Statistics page, Legal resources, Form templates
- Stripe/PayPal/PayID payments
- Mobile-responsive UI
