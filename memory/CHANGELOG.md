# Changelog

## 1 Apr 2026 — Grounds Deduplication Overhaul + Report Timeout Fix

### Grounds Deduplication (39 → 9 grounds)
- Root cause: one-directional word overlap (only checked new→existing) missed cases where existing title was shorter
- Fix: bidirectional fuzzy matching using fuzzywuzzy token_set_ratio (≥65) AND max(new/existing overlap ratio) > 0.45
- Applied to ALL three ground creation paths: pipeline.py, grounds.py, pipeline_staged.py
- Cleaned database: 39 duplicate grounds → 9 unique grounds
- DO_NOT_UNDO protections added

### Extensive Log Report Timeout Fix
- Root cause: 117K+ chars of markdown rendered all at once, choking mobile browsers
- Fix: LazySection component with IntersectionObserver — only renders sections as they scroll into view
- First 3 sections render immediately; rest load on scroll with 400px margin
- Print/export forces all sections to render before building HTML

### Report Quality Engine (continued from 31 Mar)
- Barrister View: 3,519 → 12,585 words (258% increase) — now properly uses task_type="report_generation"
- Cleaned up 5 duplicate reports (including partial interrupted generations)
- Final verified counts: Quick 1,550 / Full 13,122 / Extensive 15,467 / Barrister 12,585

## 31 Mar 2026 — Report Quality Engine Overhaul
- Fixed over-aggressive dedup (0.82 → 0.97 for multi-pass, 0.90 for single-pass)
- Full Detailed restructured from 5 → 8 generation passes
- Removed conflicting "cautious language" guardrail from report generation
- Section-by-section expansion for thin sections
- In-place report regeneration (no more duplicate reports)

## 31 Mar 2026 (earlier session)
- Google Auth Redirect Loop Fix
- PDF/Word Preview Mode
- LLM "Case name" Hallucination Fix
- Deep Analysis Generation (investigate endpoint)
- UI Badge Cleanup (Draft → Generated)
- Report Colour Coding (Green/Blue/Purple/Teal)
- Grounds Deduplication initial fix (fuzzy matching)
- Case Identity Card Protection
- Print View Inline CSS Fix
