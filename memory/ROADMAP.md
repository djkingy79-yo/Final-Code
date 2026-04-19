# Appeal Case Manager - Roadmap

## P0 - Critical (Completed)
- [x] Multi-pass LLM report generation (word count targets hit)
- [x] All 6 reports generated with content tier hierarchy (no repetition)
- [x] Barrister Views verified for all report types

## P0 - Critical (Recently Completed)
- [x] Barrister Acceptance Pack PDF generation & frontend button
- [x] Pipeline Progress widget integration in CaseDetail

## P1 - High Priority
- [x] **Backend Refactoring** - Decompose server.py (verified 19 Apr 2026, server.py = 183 lines thin app factory)
  - [x] cases.py router (145 lines)
  - [x] notes.py router (287 lines)
  - [x] documents.py router (649 lines)
  - [x] timeline.py router (762 lines)
  - [x] reports.py router (850 lines)
  - [x] grounds.py router (1277 lines)
  - [x] 23 other domain routers extracted (auth, admin, payments, collaboration, exports, pipeline, translate, etc.)

- [ ] **Native Mobile App** - Capacitor configured, needs build and test

## P2 - Medium Priority
- [ ] Verified Case Law Database integration
- [ ] Counsel conference prep attachment for Barrister View
- [x] Real-time Collaboration/Chat for Notes section (DONE — collaboration.py, messages.py, NotesSection.jsx)
- [x] Case Sharing between registered users (DONE — ShareCaseModal.jsx, NotificationBell.jsx, collaboration.py)

## Maintenance
- [ ] Database normalisation script for legacy records (convert old loose dicts to strict Pydantic structures)

## Backlog
- [ ] Minor: Reduce aggressive-mode overlap between Full Detailed and Quick Summary
- [ ] Report regeneration UX improvements
- [ ] Performance optimisation for large case files
