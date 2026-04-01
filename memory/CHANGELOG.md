# Changelog

## 31 Mar 2026 — Report Quality Engine Overhaul
- Fixed over-aggressive dedup (0.82 → 0.97 for multi-pass, 0.90 for single-pass)
- Full Detailed restructured from 5 → 8 generation passes (7,890 → 12,309 words, +56%)
- Extensive Log: 13,050 → 15,830 words (+21%) with section expansion
- Barrister View: 3,934 → 6,333 words (+61%) with task_type="report_generation" and ground-by-ground expansion
- Quick Summary: expansion enabled (1,417 → 1,486 words)
- Removed conflicting "cautious language" guardrail from report generation
- Section-by-section expansion for thin sections (replaces broken full-report expansion that hit 502 errors)
- In-place report regeneration (no more duplicate reports)
- Cleaned 4 duplicate reports from database
- Added comprehensive DO_NOT_UNDO protections for entire report engine
- Added inline code comments (DO_NOT_UNDO) on all critical thresholds and pass counts

## 31 Mar 2026 (earlier session)
- Google Auth Redirect Loop Fix
- PDF/Word Preview Mode
- LLM "Case name" Hallucination Fix
- Deep Analysis Generation (investigate endpoint)
- UI Badge Cleanup (Draft → Generated)
- Report Colour Coding (Green/Blue/Purple/Teal)
- Grounds Deduplication (fuzzy matching, 13 → 6 grounds)
- DO_NOT_UNDO Guards Added
- Case Identity Card Protection
- Print View Inline CSS Fix
