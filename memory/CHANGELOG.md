# Changelog

## 2 Apr 2026 — Login Lag Fix + 502 Resilience + All 4 Reports Generated

### Fixed: Invisible Loading Spinner After Google Login
- The ProtectedRoute loading spinner used `text-slate-100`/`text-slate-300` — nearly invisible on white background
- User saw blank white screen and thought login was lagging
- Fixed to visible `text-slate-700` with clear "Loading your dashboard..." message

### Fixed: Report Generation 502 Resilience (DO_NOT_UNDO)
- Added pass-level retry in `_subprocess_llm()` (3 attempts with 30/60s exponential backoff)
- Added 502-specific backoff in `call_llm_structured()` (15-45s instead of 2-5s)
- Reports now fight through upstream proxy 502 storms instead of failing immediately

### All 4 Reports Generated Successfully for "Hom vs R"
- Quick Summary: Completed
- Full Detailed: 83,987 chars / ~11,302 words (8 passes)
- Extensive Log: 123,614 chars / ~16,637 words (8 passes)  
- Barrister View: 78,165 chars / ~10,247 words (auto-generated)


## 2 Apr 2026 — Report Recovery Bug Fix + Full Detailed Regenerated

### Fixed: Stuck "Generating..." Report (Full Detailed)
- **Root cause**: Backend restart killed the LLM generation mid-Pass 2/8, leaving report stuck in "generating" status
- **Bug found**: `cleanup_orphaned_reports()` restore logic used `>5000 chars` threshold instead of the per-type minimum (70k for Full Detailed). This would have restored a 9,462-char partial report as "completed" — giving users a shallow report
- **Fix**: Changed restore threshold from `>5000` to `>= min_chars` (70k for Full Detailed, 120k for Extensive Log). Reports below target now correctly stay as "failed" so users can regenerate
- **Regenerated**: Full Detailed report for "Hom vs R" (case_927d110878e7) — 83,987 chars / ~11,302 words across 8 passes. Status: completed.
- Added to DO_NOT_UNDO.md


## 2 Apr 2026 — Database Normalisation + Dedup Badge

### Database Normalisation Script (P3)
- Created `/app/backend/scripts/normalise_db.py` — idempotent script fixing missing fields across 6 collections
- Fixed: 66 cases (missing state/offence fields), 142 grounds (missing source_mode/verification_status), 37 reports (missing status), 117 documents (missing created_at, using uploaded_at)
- Added `POST /api/admin/normalise-db` admin endpoint for on-demand runs
- Includes stale session cleanup (>30 days) and full ground dedup sweep
- Safe to run repeatedly — second run shows 0 updates

### Dedup Protection Badge
- Added green badge to Grounds of Merit showing "Dedup Protection Active — X unique grounds verified (12-topic classification)"
- Visible when grounds are unlocked and count > 0 (data-testid="dedup-protection-badge")
- Uses CheckCircle icon with emerald colour scheme


## 2 Apr 2026 — Grounds Dedup Nuclear Fix (FINAL)

### LEGAL_TOPICS Expanded (11 → 12 categories)
- Added `unreasonable_verdict` topic: catches "unreasonable verdict", "unsafe verdict", "unsatisfactory verdict", "verdict cannot be supported", "witness inconsistency", "eyewitness", "identification evidence"
- Added `procedural_error` topic: catches "procedural error", "procedural irregularity", "procedural unfairness", "refusal of", "trial application refused"
- Expanded `ineffective_counsel`: added "ineffective assistance", "incompetence", "failure to call", "failure to object", "failure to adduce", "inadequate legal"
- Expanded `evidence_admissibility`: added "improper admission", "chain of custody", "dna evidence", "forensic evidence", "expert evidence"
- Expanded `judicial_direction`: added "prejudicial comments", "judge conduct", "judicial conduct", "unfair trial", "fair trial", "trial judge"
- Expanded `sentencing_error`: added "double-counting", "aggravating features", "moral culpability", "sentence: ", "adequacy of reasons"
- Removed overly broad "key witness" from `unreasonable_verdict` (was causing false positives with ineffective_counsel)

### Safety Net Dedup (Triple Protection)
1. `startup_dedup_grounds` — runs `cleanup_duplicate_grounds()` and `cleanup_duplicate_issues()` on EVERY server start across ALL cases
2. `_ensure_pipeline_identification` (grounds.py) — runs dedup cleanup AFTER every pipeline sync
3. `_refresh_pipeline_for_reporting` (server.py) — runs dedup cleanup AFTER every report generation sync
4. New endpoint `POST /cases/{case_id}/grounds/cleanup-duplicates` for manual cleanup

### Cleanup Functions Added to ground_dedup.py
- `cleanup_duplicate_grounds()`: Scans, merges (preserves evidence from investigated duplicates), and deletes duplicate grounds
- `cleanup_duplicate_issues()`: Scans and deletes duplicate issue_classifications

### Test Suite: /app/backend/tests/test_ground_dedup.py
- 6 comprehensive tests: Topic Coverage (48 titles), Duplicate Detection (12 pairs), Non-Duplicate Protection (5 pairs), Australian Spelling, DB Cleanup Function, Idempotent Sync (8 consecutive runs stay at 3 grounds)
- ALL TESTS PASS



## 1 Apr 2026 — Landing Page UI Fixes

### Australian Appeal Statistics Repositioned
- Moved from hero section to its own section with proper heading
- Positioned directly above "How Many Appeals In Your State" (StateAppealStats)

### Sentence Word Wrap Fixed
- Added `break-words` class to sentence text in Case Identity Card
- Long sentences now wrap properly on mobile

### Types of Crimes — 3 Column Grid
- Changed from `grid-cols-2 sm:grid-cols-3` to `grid-cols-3` on all screen sizes
- Text reduced to `text-xs sm:text-sm` to fit 3 columns on mobile

## 1 Apr 2026 — Report Depth Loss + Google Auth Fix

### Full Detailed Reports Regenerated
- Root cause: `cleanup_orphaned_reports()` was marking half-generated reports as "completed" (5k threshold instead of 70k+).
- Fixed with proper per-type minimum targets. Reports below target marked "failed" for resume.
- Added startup migration to flag existing undersized reports (non-destructive).
- Regenerated Full Detailed reports for BOTH cases: Homann v R (85,768 chars) and Hom vs R (94,653 chars).

### Google Auth ConnectTimeout Fixed
- `auth.py` `create_session` was using httpx without a timeout, causing crashes when Emergent auth server was slow.
- Added 30s timeout and proper error handling (504 for timeout, 502 for connection error).

## 1 Apr 2026 — Report Recovery Fix + Grounds Dedup Final Fix

### Report Depth Loss — Root Cause Fixed
- `cleanup_orphaned_reports()` was marking half-generated Full Detailed reports as "completed" (threshold was only 5,000 chars vs the 80,000+ needed).
- Now uses proper minimum targets per report type: quick_summary=10k, full_detailed=70k, extensive_log=120k.
- Partial reports below target are now marked "failed" (not "completed"), preserving partial content for resume on regeneration.

### Grounds Dedup — Last Bypass Fixed (grounds.py)
- `_classify_pipeline_issues()` and `_sync_pipeline_issues_to_grounds()` in `routers/grounds.py` were using exact-title-match upserts.
- Rewrote both to use `is_ground_duplicate()` from `ground_dedup.py`.
- Expanded LEGAL_TOPICS with 4 new categories: evidence_admissibility, fresh_evidence, prosecutorial_misconduct, judicial_direction.
- All 5 ground creation paths now use fuzzy dedup.

### HowItWorksPage Restored + HowToUsePage Fixed
- Restored HowItWorksPage text from text-xs (accidentally reduced by previous agent) back to text-sm baseline.
- Fixed HowToUsePage: reduced mobile text sizes, changed "PDF documents" to "PDF and Word (DOCX) documents".

## 1 Apr 2026 — Grounds Dedup Final Fix + HowToUse Page Fix

### CRITICAL: Grounds Dedup — Last Bypass Fixed (grounds.py)
- Root cause: `_classify_pipeline_issues()` and `_sync_pipeline_issues_to_grounds()` in `routers/grounds.py` 
  were still using **exact-title-match upserts** — the exact pattern that caused 4→27+ multiplication.
  These two functions are called every time the user clicks "Analyse Grounds" on the frontend.
- Fix: Rewrote both functions to use `is_ground_duplicate()` from `ground_dedup.py` (topic + fuzzy + overlap).
- Now ALL FIVE ground creation paths use fuzzy dedup: grounds.py (2), pipeline_staged.py (3), pipeline.py (1), server.py (1).
- Expanded LEGAL_TOPICS with 4 new categories: evidence_admissibility, fresh_evidence, prosecutorial_misconduct, judicial_direction.
- Added keywords to media_coverage: "media influence", "media on jury", "jury media", etc.
- Verified: "Media Influence on Jury" now correctly matches "Prejudicial Media Coverage".

### HowToUsePage.jsx — Typography + Copy Fix
- Reduced mobile text sizes: headings text-lg md:text-xl, body text-xs sm:text-sm, tips text-xs sm:text-sm.
- Changed "Reports are generated as PDF documents" → "Reports are generated as PDF and Word (DOCX) documents".

### HowItWorksPage.jsx — Text Sizes Restored
- Previous agent accidentally reduced text to text-xs on HowItWorksPage (wrong file). 
- Restored descriptions, list items, captions, and tips back to text-sm baseline.

## 1 Apr 2026 — Grounds Deduplication Overhaul v2 + UI Fixes

### Grounds Deduplication — Topic-Based Classification (41 → 6 grounds)
- Root cause v2: fuzzywuzzy alone scored titles like "Sentencing Error Related to Non-Parole Period" vs 
  "Sentencing Error Due to Misapplication of Psychological Evidence" at only 59 (below 65 threshold)
- Fix: Created `backend/services/ground_dedup.py` with THREE matching methods:
  1. Legal Topic Classification (maps "psychiatric", "sentencing", "jury", etc. to topic buckets)
  2. fuzzywuzzy token_set_ratio (threshold lowered to 55)
  3. Bidirectional word overlap (> 0.45)
- Applied to ALL 4 ground creation paths: pipeline.py, grounds.py, pipeline_staged.py (classify + sync)
- Added batch-awareness: new grounds are added to in-memory list during sync so subsequent issues see them
- Cleaned issue_classifications from 41 → 6 unique entries
- Verified: 2 consecutive syncs produce 0 new grounds (6 → 6 → 6)

### UI Fixes
- Case Summary: added "Case Summary" heading, text reduced from text-base → text-xs/text-sm
- Grounds description: reduced from text-base → text-xs/text-sm, tighter line spacing
- Grounds buttons: flex-wrap for mobile (Search, Investigate, Delete stack vertically)
- Deep Analysis dialog: added Search AustLII button + quick search links (JADE, NSW CaseLaw, QLD Judgments, Google Scholar)
- Extensive Log report: LazySection with IntersectionObserver (renders sections on scroll, prevents browser choking)

### Report Quality (continued)
- Barrister View regenerated: 3,519 → 12,585 words
- Final verified counts: Quick 1,550 / Full 13,122 / Extensive 15,467 / Barrister 12,585

## 31 Mar 2026 — Report Quality Engine Overhaul
- Fixed over-aggressive dedup (0.82 → 0.97 for multi-pass, 0.90 for single-pass)
- Full Detailed restructured from 5 → 8 generation passes
- Removed conflicting "cautious language" guardrail from report generation
- Section-by-section expansion for thin sections
- In-place report regeneration (no more duplicate reports)

## 31 Mar 2026 (earlier session)
- Google Auth Redirect Loop Fix
- PDF/Word Preview Mode, LLM "Case name" Fix, Deep Analysis, UI Badge Cleanup
- Report Colour Coding, Case Identity Card Protection, Print View Inline CSS Fix
