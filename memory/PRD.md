# Appeal Case Manager — PRD

## Product Overview
Criminal appeals case management application for Australian jurisdictions. Features secure document management, AI-powered case analysis, and tiered reporting (Free, $150 Full Detailed, $200 Extensive Log, Barrister View).

## Architecture
```
/app/backend/
├── server.py                    # App factory (170 lines)
├── config.py                    # Env vars, DB, logger
├── auth_utils.py                # Session + download token auth
├── routers/
│   ├── __init__.py              # Router registry (29 routers)
│   ├── auth.py                  # Auth + download token
│   ├── cases.py                 # Case CRUD
│   ├── reports.py               # Reports + Quick Brief
│   ├── report_exports.py        # PDF/DOCX generation (981 lines)
│   ├── pipeline.py              # AI pipeline (1316 lines, was 1687)
│   ├── pipeline_staged.py       # Staged pipeline
│   ├── barrister_pack.py        # NEW: Acceptance Pack PDF (370 lines)
│   ├── export.py                # Export bundle (1273 lines, was 1674)
│   ├── translate.py             # NEW: Translation + PDF (474 lines)
│   ├── caselaw.py               # Case law search + authorities
│   ├── grounds.py               # Grounds of merit (1131 lines)
│   └── ... (29 routers total)
└── services/
    ├── startup_tasks.py         # DB indexes, orphan recovery, dedup
    ├── export_footer.py         # Shared footer rendering
    ├── report_generator.py      # Multi-pass AI reports (1833 lines)
    ├── barrister_generator.py   # Barrister View synthesis (1107 lines)
    └── ... (16 services total)
```

## Refactoring History
| Session | File | Before | After | Change |
|---------|------|--------|-------|--------|
| 5 | server.py | 432 | 170 | -61% (startup → services/startup_tasks.py) |
| 6 | pipeline.py | 1687 | 1316 | -22% (acceptance pack → barrister_pack.py) |
| 6 | export.py | 1674 | 1273 | -24% (translation → translate.py) |

## Test Coverage
- Session 6 regression: 6/6 key flows pass (health, languages, acceptance pack, quick brief, case law, cases)
- Session 5: iteration_187 — 14/14 backend, 100% frontend

## Backlog
- P1: "How It Works" page screenshots verification
- P2: Success Stories page compliance
- P2: Native Mobile App (Capacitor v7)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat, Case sharing
