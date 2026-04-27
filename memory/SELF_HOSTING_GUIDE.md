# Self-Hosting Deployment Guide — Appeal Case Manager

This guide covers deploying the backend onto infrastructure under your own
control so that every part of the pipeline — frontend, backend, LLM,
authentication, and domain — is owned by you.

> **Status:** Both frontend and backend run on
> `criminallawappealmanagement.com.au` / `api.criminallawappealmanagement.com.au`.
> Use this guide when migrating to a new hosting provider.

---

## 0. Pre-migration checklist

Collect these before you start:

- [ ] Domain DNS access (GoDaddy) — you already have this.
- [ ] Your **OpenAI API key** (stored as `OPENAI_API_KEY`).
- [ ] Your **Google OAuth client** (`GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`)
      configured for `criminallawappealmanagement.com.au` in Google Cloud Console.
- [ ] Your **Resend API key** (`RESEND_API_KEY`) for transactional email.
- [ ] Your **MongoDB Atlas** cluster URI (or another managed Mongo) — the
      current Kubernetes-hosted Mongo is not portable between providers.
- [ ] The current `/app/backend/.env` contents as a reference (do NOT commit
      it to git; copy the values into the new provider's secrets panel).

---

## 1. Recommended hosting providers

All three support Python 3.11 + FastAPI + persistent disk + HTTPS certificates
for a custom subdomain.

| Provider | Monthly cost for this app | Pros | Cons |
| --- | --- | --- | --- |
| **Railway** | ~US$5–20 | Easiest setup. Built-in Dockerfile detection. Push-to-deploy from GitHub. Free managed PostgreSQL and Mongo add-ons. | Cold starts on the cheapest tier. |
| **Render** | ~US$7–25 | Very clean UI, persistent disk built in, background workers supported. | Slightly slower deploys than Railway. |
| **AWS Lightsail / Fly.io** | US$5–15 | Full control, cheapest at scale. | More ops work — you manage the container, logs, TLS. |

**Recommended for a single-practitioner legal app: Railway.** Setup takes
under 30 minutes and is point-and-click.

---

## 2. Railway deployment walkthrough

### Step 1 — Prepare the backend for deployment

The backend already has everything it needs:

- `/app/backend/requirements.txt` — Python dependencies.
- `/app/backend/server.py` — FastAPI app (module path `server:app`).
- `/app/backend/.env` — environment variables (do NOT commit).

Create one new file in `/app/backend/` called `Procfile`:

```
web: uvicorn server:app --host 0.0.0.0 --port $PORT
```

Railway will detect this and run the FastAPI app with the port it exposes.

### Step 2 — Push to GitHub

Push the repository to GitHub using `git push`.

### Step 3 — Create the Railway project

1. Sign in at https://railway.app with GitHub.
2. New Project → **Deploy from GitHub repo** → pick your Appeal Case Manager repo.
3. Railway detects the Python project. In Settings → **Root directory** set `backend`.
4. Start command will auto-fill from the `Procfile`.

### Step 4 — Add environment variables (Railway → Variables tab)

Copy each variable from your local `/app/backend/.env`:

- `MONGO_URL` → point this at your **MongoDB Atlas** cluster URI, not the
  local Kubernetes Mongo (which Railway cannot reach).
- `DB_NAME` → same value as today.
- `OPENAI_API_KEY` → your OpenAI key.
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` → your Google OAuth credentials.
- `RESEND_API_KEY` → your Resend key.
- `FRONTEND_URL` → `https://criminallawappealmanagement.com.au`
- `CORS_ORIGINS` → `https://criminallawappealmanagement.com.au,https://www.criminallawappealmanagement.com.au`
- `ADMIN_EMAILS` → `djkingy79@gmail.com`
- `CONTACT_EMAIL` → `djkingy79@gmail.com`
- `PAYID_EMAIL` → `djkingy79@gmail.com`
- `RESEND_FROM_EMAIL` → `Appeal Case Manager <djkingy79@gmail.com>`

### Step 5 — Set the custom domain

1. Railway project → Settings → **Domains** → Custom Domain.
2. Enter `api.criminallawappealmanagement.com.au`.
3. Railway gives you a CNAME target. Go to **GoDaddy → DNS → Records** and
   add a CNAME for `api` pointing at the Railway target.
4. Wait 1–5 minutes for DNS propagation. Railway automatically provisions
   a TLS cert once the CNAME resolves.

### Step 6 — Flip the frontend

The frontend already builds against `REACT_APP_BACKEND_URL`. Update it:

1. Edit `/app/frontend/.env`:
   ```
   REACT_APP_BACKEND_URL=https://api.criminallawappealmanagement.com.au
   ```
2. Trigger a frontend rebuild / redeploy. Once live, the frontend will call
   your new backend directly.

### Step 7 — Google Cloud Console update

Add the new backend origin to your OAuth client:

1. Google Cloud Console → **APIs & Services → Credentials**.
2. Edit your OAuth 2.0 Client ID for Appeal Case Manager.
3. **Authorised JavaScript origins** must include
   `https://criminallawappealmanagement.com.au`.
4. **Authorised redirect URIs** must include
   `https://criminallawappealmanagement.com.au/auth/callback`.
5. Save.

(The backend origin is not a redirect URI — only the frontend origin is —
so Railway's URL does NOT need to be listed here.)

---

## 3. MongoDB Atlas quick-start

If you haven't already:

1. Sign in at https://cloud.mongodb.com.
2. Create a free M0 cluster (shared tier is plenty for a small practice).
3. Database Access → create a DB user with a strong password.
4. Network Access → allow access from anywhere (`0.0.0.0/0`) OR restrict to
   Railway's egress IPs (Railway → Settings → Networking).
5. Connect → Connect your application → copy the `mongodb+srv://...` URI
   and paste it into Railway's `MONGO_URL` variable.
6. **Migrate existing data** from the current Kubernetes Mongo:
   ```
   mongodump --uri="<old_mongo_url>" --out=/tmp/backup
   mongorestore --uri="<atlas_uri>" /tmp/backup
   ```

---

## 4. Post-migration verification

After the DNS flip, run these checks:

```
curl https://api.criminallawappealmanagement.com.au/api/health
```
Expected: `{"status":"healthy","database":"connected",...}`.

1. Sign in with Google OAuth from the live frontend.
2. Generate a Quick Summary report — confirms OpenAI integration is live.
3. Translate a section — confirms the parallel chunker is working.
4. Upload a document — confirms file storage + extract pipeline.
5. Admin → Legislation Currency → pick one Act and run the AI check —
   confirms admin endpoints and guardrails are active.

If any of the above fails, Railway's **Logs** tab will show the exact
FastAPI error with a stack trace. The most common post-migration issues are:

- `MONGO_URL` pointing at the old internal host (symptom: 502 on `/api/health`).
- `CORS_ORIGINS` not including your frontend origin (symptom: browser
  Network tab shows `No 'Access-Control-Allow-Origin'` on every request).
- Google OAuth redirect URI not updated (symptom: Google login hangs or
  returns `redirect_uri_mismatch`).

---

## 5. Ongoing operations

- **Logs** — Railway's Logs tab streams stdout + stderr live.
- **Restart** — Railway → Deployments → ⋮ → Restart.
- **Rollback** — every deploy keeps a snapshot; Railway → Deployments →
  click any previous deploy → **Redeploy**.
- **Secrets rotation** — rotate `OPENAI_API_KEY`, `RESEND_API_KEY`, and
  Google OAuth client secret every 6 months at minimum. Update the values
  in Railway → Variables; the container auto-restarts.
- **Cost** — at the 79-Act registry + the current 18 offence categories,
  monthly OpenAI spend runs around US$30–80 depending on report volume.
  The `/admin/analytics` dashboard tracks this live.

---

## 6. Verification

Once the frontend is pointing at your new backend and the above
verification passes, there is zero third-party dependency between you,
your data, and your barrister users — the application runs end-to-end
on infrastructure you own.

---

_Written 14 February 2026. If any step ever 404s, refer to the provider's
current docs — this document captures the flow and the rationale; the
exact UI button names may drift over time._
