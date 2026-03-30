# Appeal Case Manager - Roadmap

## P0 - Critical (Completed)
- [x] Multi-pass LLM report generation (word count targets hit)
- [x] All 6 reports generated with content tier hierarchy (no repetition)
- [x] Barrister Views verified for all report types

## P0 - Critical (Recently Completed)
- [x] Barrister Acceptance Pack PDF generation & frontend button
- [x] Pipeline Progress widget integration in CaseDetail

## P1 - High Priority
- [ ] **Backend Refactoring** - Decompose server.py (~4,884 lines)
  - [x] cases.py router extracted
  - [ ] Extract notes.py router
  - [ ] Extract documents.py router
  - [ ] Extract timeline.py router
  - [ ] Extract reports.py router
  - [ ] Extract grounds.py router

- [ ] **Native Mobile App** - Capacitor configured, needs build and test

## P2 - Medium Priority
- [ ] Real-time Collaboration/Chat for Notes section
- [ ] Case Sharing between registered users
- [ ] Verified Case Law Database integration
- [ ] Finalise marketing launch plan (/app/memory/mobile_app_launch_plan.md)

## Maintenance
- [ ] Database normalisation script for legacy records (convert old loose dicts to strict Pydantic structures)

## Backlog
- [ ] Minor: Reduce aggressive-mode overlap between Full Detailed and Quick Summary
- [ ] Report regeneration UX improvements
- [ ] Performance optimisation for large case files
