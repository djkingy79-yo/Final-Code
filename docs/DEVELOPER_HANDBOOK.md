# Appeal Case Manager — Developer Handbook

## Architecture Overview

```
/app/
├── backend/                    # FastAPI (Python 3.11)
│   ├── server.py               # Core API — report generation, case CRUD (~5800 lines)
│   ├── config.py               # Centralised env vars, DB connection, logger
│   ├── auth_utils.py           # Token verification, ownership checks
│   ├── services/
│   │   └── llm_service.py      # LLM abstraction (owner's OpenAI key → GPT-4o)
│   ├── routers/
│   │   ├── auth.py             # Registration, login, Google OAuth, password change
│   │   ├── payments.py         # PayID, Stripe, PayPal payment flows
│   │   ├── export.py           # Case Export Pack PDF, translation, ZIP package
│   │   ├── admin.py            # Admin-only endpoints
│   │   ├── analysis.py         # AI contradiction scanning
│   │   ├── pipeline.py         # Background pipeline tasks
│   │   └── password_reset.py   # Forgot-password email flow
│   ├── .env                    # Secrets (NEVER commit)
│   ├── .env.example            # Template for new deployments
│   └── requirements.txt        # Python dependencies (pip freeze)
│
├── frontend/                   # React 18 (Create React App)
│   ├── src/
│   │   ├── App.js              # Root — routing, auth state, AuthCallback
│   │   ├── components/
│   │   │   ├── AuthModal.jsx   # Login/register dialog + Google Auth
│   │   │   ├── QuickExport.jsx # Export dialog (PDF pack + ZIP)
│   │   │   ├── ReportTranslator.jsx # Multi-language translation UI
│   │   │   └── ui/             # Shadcn component library
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── CaseDetail.jsx
│   │   │   ├── ReportView.jsx
│   │   │   └── BarristerView.jsx
│   │   └── index.css           # Global styles (forced light mode)
│   ├── .env                    # Frontend env (REACT_APP_BACKEND_URL)
│   └── package.json
│
├── docker-compose.yml          # Local dev stack (mongo + backend + frontend)
├── .github/workflows/ci.yml   # GitHub Actions CI (lint, test, lockfile check)
└── memory/
    ├── PRD.md                  # Product requirements
    └── test_credentials.md     # Test account credentials
```

## Quick Start (Local Development)

```bash
# 1. Clone and install
cd /app/backend && pip install -r requirements.txt
cd /app/frontend && yarn install

# 2. Configure environment
cp backend/.env.example backend/.env   # Fill in secrets
cp frontend/.env.example frontend/.env # Set API URL

# If using docker-compose for MongoDB, set in backend/.env:
#   MONGO_URL=mongodb://mongo:27017
# If running MongoDB locally on your machine, use:
#   MONGO_URL=mongodb://localhost:27017
#
# 3. Start services
# Backend (auto-reload on save):
cd backend && uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Frontend (auto-reload on save):
cd frontend && yarn start

# Or use Docker:
docker compose up --build
```

## Key API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Email/password registration |
| POST | `/api/auth/login` | Email/password login → session_token |
| POST | `/api/auth/session` | Exchange Google OAuth session_id → token |
| GET | `/api/auth/me` | Current user profile (requires Bearer token) |
| POST | `/api/auth/logout` | Invalidate session |
| POST | `/api/auth/accept-terms` | Accept terms of service |

### Cases
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cases` | List user's cases |
| POST | `/api/cases` | Create new case |
| GET | `/api/cases/{case_id}` | Get case detail |
| PUT | `/api/cases/{case_id}` | Update case |
| DELETE | `/api/cases/{case_id}` | Delete case and all related data |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cases/{case_id}/reports` | List reports for case |
| POST | `/api/cases/{case_id}/reports/generate` | Generate report (type: quick_summary, full_detailed, extensive_log) |
| GET | `/api/cases/{case_id}/reports/barrister-view` | Get/generate Barrister View |
| GET | `/api/cases/{case_id}/reports/{report_id}/export-pdf` | Export single report as PDF |
| GET | `/api/cases/{case_id}/reports/{report_id}/export-docx` | Export single report as DOCX |

### Export & Translation
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cases/{case_id}/export/case-pack` | Full case export (formatted PDF) |
| GET | `/api/cases/{case_id}/export/preview` | Preview what's included in export |
| POST | `/api/cases/{case_id}/export/package` | ZIP archive with raw data + templates |
| GET | `/api/languages` | List 41 supported translation languages |
| POST | `/api/cases/{case_id}/translate` | Translate report `{language, report_id}` |
| GET | `/api/cases/{case_id}/translate/{report_id}/pdf?lang=xx` | Export translated report as PDF |

### Payments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/payments/prices` | Get feature prices |
| GET | `/api/cases/{case_id}/payments` | Payment status for case |
| POST | `/api/payments/payid/create-reference` | Create PayID payment reference |
| POST | `/api/payments/payid/verify` | Verify PayID payment |

## Database Schema (MongoDB)

### Core Collections
- **users**: `{user_id, email, name, password_hash, password_salt, google_id, terms_accepted}`
- **user_sessions**: `{session_token, user_id, expires_at}` (TTL index on expires_at)
- **cases**: `{case_id, user_id, title, defendant_name, case_number, court, sentence, state, offence_type}`
- **reports**: `{report_id, case_id, user_id, report_type, status, content, generated_at}`
- **documents**: `{document_id, case_id, user_id, filename, content, file_type}`
- **grounds_of_merit**: `{ground_id, case_id, user_id, title, ground_type, strength, description, analysis, law_sections, similar_cases}`
- **timeline_events**: `{event_id, case_id, title, event_date, event_category, significance}`
- **notes**: `{note_id, case_id, user_id, content, created_at}`
- **payments**: `{payment_id, case_id, user_id, amount, status, payment_method, feature}`
- **report_translations**: `{report_id, case_id, user_id, language, language_name, translated_content, translated_at}` (unique index: report_id+language)

### Report Types
1. `quick_summary` — Free base analysis
2. `full_detailed` — $150 AUD, 2× depth
3. `extensive_log` — $200 AUD, 3× depth
4. `barrister_view` — Locked until all 3 above are generated. Counsel-grade synthesis.

## Security Configuration

### Authentication
- **Password hashing**: PBKDF2-HMAC-SHA256 with 100,000 iterations + random salt
- **Session tokens**: UUID4, stored in MongoDB with TTL expiry
- **Google OAuth**: Owner's own Google Cloud OAuth client (`GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`) — redirects directly between Google and `criminallawappealmanagement.com.au`, no third-party auth hop

### Rate Limiting
- Auth endpoints (login, register, forgot-password): 10 requests/minute/IP
- Implemented via `SecurityHeadersMiddleware` in `server.py`

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Cache-Control: no-store, no-cache, must-revalidate`
- `Strict-Transport-Security` (via Cloudflare)

### CORS
- Configured via `CORS_ORIGINS` env var (comma-separated domains)
- **Never use `*` in production** — always list explicit domains

## Environment Variables Reference

### Backend (.env)
| Variable | Required | Description |
|----------|----------|-------------|
| `MONGO_URL` | Yes | MongoDB connection string |
| `DB_NAME` | Yes | Database name |
| `CORS_ORIGINS` | No | Allowed frontend origins (comma-separated) |
| `OPENAI_API_KEY` | Yes | Owner's OpenAI API key (drives all LLM features) |
| `GOOGLE_CLIENT_ID` | No | Google Cloud OAuth client ID (required only for Google Sign-In) |
| `GOOGLE_CLIENT_SECRET` | No | Google Cloud OAuth client secret (required only for Google Sign-In) |
| `RESEND_API_KEY` | No | Resend.com API key (required only for password reset / notifications) |
| `RESEND_FROM_EMAIL` | No | Sender email address (required only if using Resend) |
| `CONTACT_EMAIL` | Yes | Admin contact email |
| `FRONTEND_URL` | Yes | Frontend URL for email links |
| `ADMIN_EMAILS` | Yes | Comma-separated admin emails |
| `PAYID_EMAIL` | No | PayID payment email |

### Frontend (.env)
| Variable | Required | Description |
|----------|----------|-------------|
| `REACT_APP_BACKEND_URL` | Yes | Backend API base URL |

## Testing

```bash
# Run backend tests
cd /app/backend && python -m pytest tests/ -v

# Run linters
cd /app/backend && ruff check .
cd /app/frontend && npx eslint src/

# Manual API test
API_URL="https://your-url.com"
TOKEN=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['session_token'])")
curl -s "$API_URL/api/cases" -H "Authorization: Bearer $TOKEN"
```

## Deployment Notes

1. **MongoDB**: Ensure indexes are created on startup (handled automatically by `server.py` startup event)
2. **Static files**: Backend serves `/static/` for uploaded documents
3. **PDF generation**: Requires `reportlab` and `python-docx` — included in requirements.txt
4. **File uploads**: Stored on the backend disk under `/app/backend/uploads/` (persistent volume on the production host)
5. **Email**: Requires valid Resend API key and verified sender domain
6. **Payments**: PayID (manual verification), Stripe, and PayPal supported

## Common Issues

| Issue | Solution |
|-------|----------|
| Google Auth fails on custom domain | Verify `criminallawappealmanagement.com.au` is listed as an authorised JavaScript origin and redirect URI in your Google Cloud Console OAuth 2.0 client |
| PDF export blank on iOS | Uses `/document-preview?mode=pdf` route (not blob URLs) |
| Report stuck in "generating" | Startup cleanup auto-recovers or fails stuck reports |
| Translation timeout | Large reports are chunked (12KB per chunk). Increase `timeout_seconds` if needed |
| CORS errors | Check `CORS_ORIGINS` includes the exact frontend origin (with protocol, no trailing slash) |
, no trailing slash) |
