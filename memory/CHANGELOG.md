# Appeal Case Manager — Changelog


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
