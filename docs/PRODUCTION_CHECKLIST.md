# Production Checklist — Appeal Case Manager

## Pre-Deployment

- [ ] All environment variables set in production `.env` (see `.env.example`)
- [ ] `FRONTEND_URL` set to `https://criminallawappealmanagement.com.au`
- [ ] CORS configured to allow only production domain
- [ ] MongoDB connection string points to production database (Atlas recommended)
- [ ] `OPENAI_API_KEY` configured and tested (your personal OpenAI key — billing goes to your account)
- [ ] `RESEND_API_KEY` configured for transactional emails
- [ ] SSL/TLS certificate installed and valid
- [ ] Domain DNS configured (A record → server IP)

## Security

- [ ] All test credentials rotated / removed from codebase
- [ ] `.env` file NOT committed to version control
- [ ] `.env` file has restrictive permissions (`chmod 600`)
- [ ] Security headers verified (use securityheaders.com)
- [ ] CORS tested — only production domain allowed
- [ ] Rate limiting active on auth endpoints
- [ ] Session cookies set to `Secure`, `HttpOnly`, `SameSite=Lax`
- [ ] No debug `console.log` statements in production frontend build

## Build & Deploy

- [ ] Frontend built with production REACT_APP_BACKEND_URL
- [ ] Backend runs with `--workers 2` (or more based on traffic)
- [ ] Docker image builds successfully
- [ ] Health check: `GET /api/health` returns `{"status": "healthy"}`
- [ ] Readiness check: `GET /api/ready` returns `{"ready": true}`
- [ ] Deep health: `GET /api/health/deep` all checks pass

## Functional Testing

- [ ] User registration works
- [ ] User login works (email/password + Google OAuth)
- [ ] Case creation works
- [ ] Document upload works
- [ ] Timeline generation works
- [ ] Report generation works (all 4 tiers)
- [ ] PDF export works (including iOS)
- [ ] DOCX export works
- [ ] PayID payment flow works
- [ ] Barrister View unlocks after all 3 reports
- [ ] Password reset email sends

## Monitoring

- [ ] Application logs accessible (stdout/stderr or log file)
- [ ] Error alerting configured (email or monitoring service)
- [ ] Database backup schedule configured (see `BACKUP.md`)
- [ ] Disk space monitoring for uploaded documents

## Post-Launch

- [ ] Verify real user can register and login
- [ ] Verify real report generation end-to-end
- [ ] Monitor error rates for first 48 hours
- [ ] Verify email delivery (check spam folders)
- [ ] Test from mobile device (iOS Safari, Android Chrome)
- [ ] Review backup restore procedure
