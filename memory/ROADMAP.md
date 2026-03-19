# Appeal Case Manager — Roadmap

## P0 (Immediate) — COMPLETED
- ✅ Deployment readiness check passed
- ✅ Report generation reliability fixed (retry + model fallback)
- ✅ Australian English verification
- ✅ Print buttons verified

## P1 (Next)
- Multi-user case sharing model so realtime notes support cross-account collaboration
- Mention notifications and branch/thread discussion improvements in notes
- Barrister View: bind comparative sentencing/options panels to parsed report tables dynamically
- Monitor Claude 502 errors — consider upgrading to a more reliable model when available

## P2 (Technical / Platform)
- Refactor monolithic `backend/server.py` into dedicated routers/services (cases, documents, reports, notes, timeline, grounds)
- Harden websocket auth + add reconnect metrics/monitoring

## P3 (Release)
- Build signed Android/iOS binaries and complete store metadata/submission workflow
- Marketing launch plan finalisation
