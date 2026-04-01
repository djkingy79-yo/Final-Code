# Changelog

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
