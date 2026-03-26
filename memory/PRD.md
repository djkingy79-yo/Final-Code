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

## Prioritised Backlog
### P1
- Backend refactoring (decompose server.py — >5000 lines)
- Native mobile app build (Capacitor configured)

### P2
- Real-time collaboration/chat
- Case sharing between registered users
