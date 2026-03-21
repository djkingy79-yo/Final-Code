# Appeal Case Manager - Roadmap

## P0 - Critical (Completed)
- [x] Multi-pass LLM report generation (word count targets hit)
- [x] All 6 reports generated with content tier hierarchy (no repetition)
- [x] Barrister Views verified for all report types

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
- [ ] Finalise marketing launch plan (/app/memory/mobile_app_launch_plan.md)

## Backlog
- [ ] Minor: Reduce aggressive-mode overlap between Full Detailed and Quick Summary
- [ ] Report regeneration UX improvements
- [ ] Performance optimisation for large case files
