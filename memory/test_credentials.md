# Test Credentials

## Main User Account
- Email: djkingy79@gmail.com
- Password: Grubbygrub88

## Current Cases (as of 31 Mar 2026)
- case_f8bf63e9dcbe: "Homann v R" (22 docs, 5 grounds, 5 timeline events)
- case_44b2047065b2: "Test Auto Detect" (0 docs, 0 grounds)

## Notes
- Auto-detect of state/offence/sentence requires at least one document with >200 chars
- Background LLM task takes ~20-25 seconds to populate metadata after upload
- Auth uses Bearer token from localStorage (cookies unreliable in deployed environment)
- Google OAuth redirects to /dashboard (not /auth/callback)
