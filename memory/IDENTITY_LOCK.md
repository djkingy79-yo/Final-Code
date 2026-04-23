# DO_NOT_UNDO — IDENTITY LOCK

**Permanent rules for Appeal Case Manager. Verified 22 Apr 2026.**

This file exists so that no future agent (or fork, or deploy script) can silently re-introduce third-party identity leaks into the app. Every rule below is non-negotiable.

---

## 1. Domain

The ONLY domain this app targets for production is:

```
https://criminallawappealmanagement.com.au
https://www.criminallawappealmanagement.com.au
```

- `REACT_APP_BACKEND_URL` in `frontend/.env` MUST be `https://criminallawappealmanagement.com.au`.
- `FRONTEND_URL` in `backend/.env` MUST be `https://criminallawappealmanagement.com.au`.
- `CORS_ORIGINS` in `backend/.env` MUST include both the www and non-www variants of the domain above. Localhost is allowed for dev; nothing else.
- The hardcoded CORS allow-list in `backend/server.py` contains ONLY the two prod domains + localhost. Any other hosting-platform preview URL is a leak — remove it.
- No code file may contain `preview.emergentagent.com`, `emergent.sh`, `emergent.host`, or any other deploy-platform hostname except in (a) legacy build artefacts under `frontend/ios/`, `frontend/android/`, `frontend/build/` (regenerated automatically) or (b) .pyc files / generated output.

## 2. LLM

The ONLY OpenAI key this app uses is the one Deb paid for. It lives in `backend/.env` as:

```
OPENAI_API_KEY=sk-proj-...
```

- Code MUST read this exclusively via `os.environ.get("OPENAI_API_KEY")` (see `backend/services/llm_service.py :: _get_openai_client`).
- There is NO "universal key" / "Emergent LLM key" / `EMERGENT_LLM_KEY` fallback. Anywhere. Ever. If a PR reintroduces one, reject the PR.
- `emergentintegrations`, `litellm`, `google-genai`, `google-generativeai` MUST NOT appear in `backend/requirements.txt`. All LLM traffic goes through the direct `openai` SDK.

## 3. Branding / UI

- The app name is **Appeal Case Manager**.
- Bundle ID (iOS + Android) is **com.debking.criminalappeals**.
- `frontend/src/index.css` hides any platform-injected badge (selector `#emergent-badge` + the generic `a[href*="emergentagent"]` family). Do not remove.

## 4. Mobile release build

- `frontend/.env` is the source of truth for the mobile build — the REACT_APP_BACKEND_URL value is baked into the bundle at `yarn build` time and shipped inside the Capacitor native shell.
- Native shells (`capacitor://localhost`, `file://`) have no runtime origin to fall back to, so `frontend/src/App.js :: BACKEND_URL` is written to detect native shells and use the env var directly. Do not simplify.

## 5. Verification one-liners

Before committing / deploying / submitting to App Store:

```bash
# No emergent hostnames anywhere in active source
grep -rEn "preview\.emergentagent|emergent\.host|emergent\.sh" \
  /app/backend /app/frontend/src /app/frontend/public /app/frontend/.env /app/backend/.env \
  2>/dev/null | grep -v node_modules | grep -v tests/ | grep -v \.pyc

# No emergent LLM key references anywhere
grep -rEn "EMERGENT_LLM_KEY|emergentintegrations" \
  /app/backend /app/frontend/src 2>/dev/null | grep -v node_modules

# .env files not gitignored (Emergent deploy needs them committed)
cd /app && git check-ignore backend/.env frontend/.env && echo "FAIL — .env is ignored"
```

All three MUST return empty (or exit 1 for the last one).
