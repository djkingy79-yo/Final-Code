# Appeal Case Manager — PRD

## Product Overview
Criminal appeals case management application for Australian jurisdictions.

## Architecture
React frontend + FastAPI backend + MongoDB. 29 routers, 16 services.

## Environment Variable Validation (Production Readiness)

### Tier 1: FATAL (app won't start)
| Variable | Purpose |
|----------|---------|
| `MONGO_URL` | MongoDB connection string |
| `DB_NAME` | Database name |
| `FRONTEND_URL` | Frontend URL for CORS/redirects |
| `ADMIN_EMAILS` | Comma-separated admin emails |
| `CONTACT_EMAIL` | Support/contact email |
| `EMERGENT_LLM_KEY` | AI/LLM key for report generation |

### Tier 2: REVENUE (payments fail without)
| Variable | Purpose |
|----------|---------|
| `STRIPE_API_KEY` | Stripe secret key — guard returns 503 if missing |

### Tier 3: EMAIL (notifications/password-reset fail)
| Variable | Purpose |
|----------|---------|
| `RESEND_API_KEY` | Resend email service key |

### Tier 4: SECURITY
| Variable | Purpose |
|----------|---------|
| `CORS_ORIGINS` | Restrict to specific origins (warn if `*`) |

### Tier 5: OPTIONAL (sensible defaults)
| Variable | Purpose | Default |
|----------|---------|---------|
| `PAYID_EMAIL` | PayID bank transfer email | Falls back to CONTACT_EMAIL |
| `RESEND_FROM_EMAIL` | Email sender address | Falls back |

### Diagnostic Endpoint
`GET /api/health/env` — Admin-only. Returns status of all env vars without exposing values.

## Implemented Features
- Multi-tier AI report generation (Free → $150 → $200 → Barrister View)
- 9-jurisdiction routing (NSW, VIC, QLD, SA, WA, TAS, NT, ACT, Federal)
- Download token security (short-lived, single-use)
- Standardised print/export footer across all document types
- Find Case Law with AI-suggested authorities
- 41-language translation with PDF export
- Stripe + PayID payment integration

## Test Coverage
- Environment validation: Tier 1–5 all verified on startup
- `/api/health/env` admin-only endpoint: auth guard verified

## Backlog
- P1: "How It Works" page screenshots verification
- P2: Success Stories page compliance
- P2: Native Mobile App (Capacitor v7)
- P2: Counsel conference prep attachment for Barrister View
- P2: Real-time collaboration/chat, Case sharing
