# Appeal Case Manager — Changelog

## 9 Apr 2026 (Session 5) — Comprehensive Legal Framework Update
- **RECENT_LEGISLATION_UPDATES:** Added 23 verified recently commenced Australian Acts (2022-2025) to `offence_framework.py`, covering all jurisdictions (NSW, VIC, QLD, SA, WA, TAS + Federal/Commonwealth).
- **Key Acts Added:** NSW Coercive Control (s 54D, 1 Jul 2024), Jury Amendment Act 2024 (10 Mar 2025), Knife Crime Act 2024, Racial and Religious Hatred Act 2025, Bail Act 2013 amendments, Child Protection Amendment Act 2024; VIC Youth Justice Act 2024, Non-Fatal Strangulation Act, Performance Crime Act 2025, Anti-vilification Act 2025; QLD Coercive Control (s 334C, 26 May 2025), Making Queensland Safer Act 2024; SA Coercive Control (s 20A), High Risk Offenders Amendment; WA Family Violence Legislation Reform Act 2024; TAS Jari's Law; Federal Hate Crimes Act 2025, Wage Theft Act 2024.
- **NSW Complete Criminal Framework:** Added NSW_CRIMINAL_FRAMEWORK — Primary Acts (Crimes Act 1900 No 40, Criminal Procedure Act 1986 No 209, Crimes (Sentencing Procedure) Act 1999 No 92, LEPRA 2002 No 103, Evidence Act 1995 No 25), Key Regulations (Crimes Regulation 2020, Criminal Procedure Regulation 2017, Sentencing Procedure Regulation 2017, LEPRA Regulation 2016), Specialised Legislation (DV Act 2007, Bail Act 2013, Drug Misuse Act 1985, Summary Offences Act 1988, Mental Health Forensic Provisions Act 2020, Forensic Procedures Act 2000, Criminal Appeal Act 1912, Jury Act 1977). Also added: Animal Sexual Abuse Act 2025, Good Character Bill 2026 (pending), Surveillance Devices Regulation updates.
- **Prompt Injection:** New `_build_recent_legislation_context()` function auto-injects relevant recent legislation into every LLM report generation prompt (filtered by state + offence category). `_build_nsw_framework_context()` injects foundational NSW framework for all NSW cases.
- **Anti-Hallucination Guardrails:** Added RECENT LEGISLATION AWARENESS block to system prompts, LEGISLATION ACCURACY rules to report guardrails, and transitional provision checks.
- **Inline Updates:** Updated domestic_violence (coercive control for NSW/QLD/SA/VIC), firearms_weapons (Knife Crime Act), terrorism (Hate Crimes Act) categories with new section references.
- **Regression Tests:** 43 pytest tests in `tests/test_legislation_framework.py` — all passing. Fresh report generated on Homann v R confirming Crimes Act 1900, Criminal Procedure Act 1986, Evidence Act 1995, Mental Health Forensic Provisions Act 2020 cited in output.

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
