# Appeal Case Manager — PRD

## Original Problem Statement
Build "Appeal Case Manager" to assist with criminal appeals across Australian jurisdictions. Features: secure document management, AI-powered case analysis, tiered reporting system (Free, Paid), Barrister View, and PayID integration.

## UI/UX Rule
Forced light mode globally. High contrast only. No dark mode toggle. No grey/muted text. Australian spelling. White backgrounds, black body text, coloured headings.

## Tech Stack
React + Tailwind + Shadcn UI / FastAPI + MongoDB / OpenAI GPT-4o via Emergent LLM Key / Emergent Google Auth

## Case Tabs (CORRECT ORDER)
Documents, Timeline, Grounds, Notes, Reports, Legal Framework, Progress — **NO Contradictions tab**

## What's Been Implemented (26 Mar 2026)
- Full CRUD for cases, documents, reports
- AI-powered grounds identification (Free + $99 tier)
- 3 report tiers: Quick Summary, Full Detailed, Extensive Log
- Barrister View (unlocks after 3 reports)
- Dark mode toggle removed from ALL 30+ pages
- ALL CSS variables replaced with explicit light-mode colours
- 7 mobile-width (390px) mockup screenshots with real case data for How It Works page
- Mockup tabs corrected: no Contradictions, shows Legal Framework
- Report Snapshot cards deleted from Landing Page
- How It Works FAQ answers reduced to text-xs
- Legal Resources: all text sizes reduced, ResourceCard made compact, intro text deleted, banner removed, Innocence heading made bigger
- LandingPage footer fixed with explicit colours
- PageCTA inline variant fixed for light mode
- SuccessStories footer CTA and Share My Story button fixed
- CaseDetail gradient button replaced with solid blue
- **Report language sanitisation**: "we/us/our" eliminated from AI prompts + post-processing in backend (_strip_report_placeholders) and frontend (cleanAIContent). Replaced with "the applicant", "the legal professional", "this analysis".
- **Print/PDF preview rebuilt**: Professional layout matching on-screen view — coloured headers, numbered sections, styled borders, table of contents, disclaimer footer.
- **CLIENT PLAIN-ENGLISH BRIEF** prompts updated across all 3 report tiers to enforce educational tool third-person language.
- **Extensive Log timeout fix**: Reduced per-pass LLM timeout from 420s to 180s, cut retries from 6 to 4 with gpt-4o-mini fallback. Skipped expansion step for extensive_log (7 passes already produce 70k+ chars). Added partial-save after each pass so server restarts don't lose work. Added startup cleanup for orphaned "generating" reports.
- **Progress indicator improved**: Shows contextual messages during generation ("Reading documents..." -> "Writing analysis..." -> "Completing final sections...").
- **Report content depth enforced**: Full Detailed target 10k-15k words, Extensive Log target 25k-35k words. MATERIAL COUNTS (doc/timeline/ground counts) added to all prompts.
- **ALL grounds enforcement**: Every report prompt now has GROUNDS TO COVER with "MUST INCLUDE ALL" and explicit counts.
- **Comparison table**: Added to end of ALL report views and print/PDF — 3 columns (FREE / $150 / $200) with 24 subject matter rows and checkmarks.
- **Disclaimer with hazard symbol**: Present on all on-screen reports AND print/PDF views.
- **Prompt instruction stripping**: Headings like "OUTCOME OPTIONS — keep ALL pathways in this ONE section" cleaned in both backend and frontend.
- **Pricing updated**: $150 AUD Full Detailed, $200 AUD Extensive Log throughout all prompts and UI.

## Prioritised Backlog
### P1
- Backend refactoring (decompose server.py — >5000 lines)
- Native mobile app build (Capacitor configured)

### P2
- Real-time collaboration/chat
- Case sharing between registered users
