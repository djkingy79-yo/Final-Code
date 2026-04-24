# Security Policy — Appeal Case Manager

## Supported Versions

| Version | Supported |
|---------|-----------|
| Current | Yes       |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Email**: djkingy79@gmail.com
2. **Subject**: `[SECURITY] Appeal Case Manager — Vulnerability Report`
3. **Include**: Description, steps to reproduce, potential impact
4. **Do NOT** disclose publicly until the issue is resolved

Expected response time: 48 hours.

## Security Measures

### Authentication
- Password hashing: PBKDF2-SHA256 with 100,000 iterations and random 128-bit salt
- Session tokens: Cryptographically random 128-bit hex (UUID4)
- Session expiry: 7 days with automatic cleanup
- Cookie settings: `HttpOnly`, `Secure`, `SameSite=Lax`
- Rate limiting on login/register endpoints (5 attempts per minute)

### Data Protection
- All data encrypted in transit (TLS/SSL)
- MongoDB access restricted to application server
- No credit card data stored (PayID bank transfers only)
- Document uploads processed server-side, not stored in public directories
- AI processing via OpenAI API (data not used for training per API ToS)

### CORS
- Restricted to production domain (`criminallawappealmanagement.com.au`)
- Credentials allowed only for same-origin requests
- Methods and headers explicitly whitelisted

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: default-src 'self'`

### Input Validation
- All user inputs validated server-side via Pydantic models
- URL parameters whitelisted (e.g., tab values)
- File uploads restricted by type and size
- HTML content sanitised before rendering

## Secrets Management

### Required Secrets
| Secret | Purpose | Rotation |
|--------|---------|----------|
| `MONGO_URL` | Database connection | On compromise |
| `OPENAI_API_KEY` | AI report generation (your OpenAI account) | On compromise |
| `RESEND_API_KEY` | Transactional email | On compromise |

### Rotation Procedure
1. Generate new key/credential from the provider
2. Update `.env` on the production server
3. Restart the application (`supervisorctl restart backend`)
4. Verify service is healthy (`GET /api/health`)
5. Revoke the old key from the provider
6. Document rotation date

## Incident Response

1. **Detect**: Monitor application logs and error rates
2. **Contain**: Disable affected feature or endpoint
3. **Assess**: Determine scope and impact
4. **Remediate**: Apply fix and deploy
5. **Notify**: Inform affected users if personal data was exposed
6. **Review**: Post-incident review and documentation
