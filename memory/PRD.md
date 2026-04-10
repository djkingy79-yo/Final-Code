# Appeal Case Manager — Product Requirements Document

## Original Problem Statement
Building "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features secure document management, AI-powered case analysis, and a tiered reporting system (Free, $150 Full Detailed, $200 Extensive Log, and a locked Barrister View).

## Core Requirements
- **Report Tiers:** Strictly scale in depth. Free (Base) -> $150 (2x depth) -> $200 (3x depth)
- **Barrister View:** Locked until all 3 standard reports are generated/paid
- **Report Language:** STRICT third-person educational tool. No "we", "us", "our", "you", "your"
- **Branding:** Forced light mode. High contrast. Blue/slate/navy only. Action buttons bright blue with white text
- **Legal Accuracy:** Must cite current, state-specific, and federal Australian legislation
- **Unified Document Styling:** Times New Roman, 12pt body, bold headings, indented bullets, legal footers
- **Australian English:** ALL user-facing text must use Australian spelling. auSpelling utility applied to all AI-generated content.

## Architecture
- React frontend + FastAPI backend + MongoDB
- AI: OpenAI GPT-4o via Emergent LLM Key
- Auth: Emergent-managed Google Auth + email/password
- Payments: PayID (sole payment method — PayPal/Stripe fully removed)
- Emails: Resend

## Completed — Previous Session (10 Apr 2026)
- Fixed Grounds of Merit UI: Reduced mobile fonts, displayed actual Legal Framework text
- Applied auSpelling to ALL AI-generated content (deep analysis, evidence, appellate pathway, timeline)
- Expanded auSpelling utility with 15+ additional Australian English conversions
- Fixed Barrister report card: forced inline `style={{color:'#ffffff'}}` for bright white text on teal
- Fixed Google Sign In: Changed from `<button onClick>` to `<a href>` for iOS webview compatibility
- Full forensic codebase audit (dead code, lint, duplication, MongoDB _id fixes)
- Removed PayPal/Stripe completely; PayID is sole payment method

## Completed — Current Session (10 Apr 2026)
- **Full Forensic Legal Framework Audit (`offence_framework.py`):**
  - Cross-referenced all legislation codes against real Australian law via web search
  - **20 corrections applied** (zero hallucinations now):
    - NSW: s.23 (was "Self-defence" → now "Extreme provocation"), s.23A (was "Excessive self-defence" → now "Substantial impairment by mental health impairment"), s.24 (was "Provocation" → now "Punishment for manslaughter"), s.25 REMOVED (repealed), s.19B (was "Punishment for manslaughter" → now "Mandatory life sentence for murder of police officers")
    - VIC: s.3A (was "Manslaughter defined" → now "Constructive murder"), s.5 (was "Abolition of year and a day rule" → now "Punishment for manslaughter"), s.31 in Assault (was s.31 → now s.16 "Intentionally causing serious injury")
    - QLD: s.300 (was "Definition of murder" → now "Unlawful homicide"), s.302 (was "Definition of manslaughter" → now "Definition of murder")
    - WA: s.280 (was "Unlawful homicide" → now "Manslaughter"), s.281 (was "Killing on provocation" → now "Unlawful assault causing death"), s.283/s.259 REMOVED (incorrect)
    - TAS: s.156 (was "Murder defined" → now "Culpable homicide"), s.157 (was "Punishment for murder" → now "Murder")
    - ACT: s.54-56 (corrected from "1st/2nd/3rd degree" to actual ACT offence titles), s.55A corrected
    - SA: Updated RECENT_LEGISLATION_UPDATES — Coercive Control Act passed Sept 2025 (not still "debated"), commencing ~2027
  - All verified via web search against AustLII, state legislation sites, and legal practitioner resources
  - Python lint: zero errors. Backend validated and running

## Pending Tasks
### P0
- (none — legal audit complete)

### P1
- Verify "How It Works" page images (IMG_4323.png to IMG_4327.png)
- Build Native Mobile App (Capacitor v7 configured)

### P2
- Backend refactoring: decompose server.py (~6000 lines)
- Camera/Share native device features
- Counsel conference prep attachment for Barrister View
