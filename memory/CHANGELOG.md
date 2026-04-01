# Appeal Case Manager — Changelog

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
