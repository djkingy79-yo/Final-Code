# Deploying Appeal Case Manager to Render

This guide covers a zero-to-production deployment of Appeal Case Manager on
[Render](https://render.com) using the included Docker-based single-container setup.

The container bundles the React frontend (built at deploy time) and the
FastAPI backend into one image — no separate static-hosting service is needed.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| GitHub account | Repo must be connected to Render |
| Render account | Free tier works; Starter plan recommended for persistence |
| MongoDB Atlas | Free tier (M0) is fine to start. Get a connection string. |
| OpenAI API key | Personal key — billing goes to your own account |
| Google Cloud project | For OAuth 2.0 credentials |
| Resend account | For transactional email (password reset, notifications) |

---

## Step 1 — Set up MongoDB Atlas

1. Sign up at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas).
2. Create a free M0 cluster.
3. Under **Database Access** → Add a database user with password auth.
4. Under **Network Access** → Allow access from anywhere (`0.0.0.0/0`) for Render,
   or add Render's static outbound IP ranges if available on your Render plan.
5. Click **Connect** → **Drivers** → copy the connection string.
   It looks like:
   ```
   mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. Replace `<user>` and `<password>` with your database user credentials.
   **Keep this string secret — never commit it.**

---

## Step 2 — Create Google OAuth credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
2. Create a project (or use an existing one).
3. **APIs & Services** → **OAuth consent screen** → configure as External.
4. **Credentials** → **Create credentials** → **OAuth 2.0 Client ID**
   - Application type: **Web application**
   - Authorised JavaScript origins:
     ```
     https://<your-render-service-name>.onrender.com
     ```
     (add your custom domain here too if you have one)
   - Authorised redirect URIs:
     ```
     https://<your-render-service-name>.onrender.com/auth/callback
     ```
5. Copy the **Client ID** and **Client Secret**.

> **Note:** You will only know the exact Render URL after the first deploy (Step 4 below).
> You can deploy first with any placeholder URL, then update the OAuth credentials
> and re-deploy once you know the final URL.

---

## Step 3 — Set up Resend (email)

1. Sign up at [resend.com](https://resend.com).
2. Add and verify your sending domain (or use `onboarding@resend.dev` for testing).
3. **API Keys** → Create an API key and copy it.
4. Note the verified sender email address (e.g. `noreply@your-domain.com`).

---

## Step 4 — Deploy to Render via Blueprint

### Option A — Render Blueprint (recommended)

1. Fork or connect this repository to your Render account.
2. In Render Dashboard → **New** → **Blueprint**.
3. Select this repository. Render detects `render.yaml` automatically.
4. Render will prompt for all `sync: false` environment variables (marked as secrets).
   Fill in each value:

   | Variable | Value |
   |---|---|
   | `MONGO_URL` | Your Atlas connection string from Step 1 |
   | `OPENAI_API_KEY` | Your OpenAI key (`sk-...`) |
   | `GOOGLE_CLIENT_ID` | From Step 2 |
   | `GOOGLE_CLIENT_SECRET` | From Step 2 |
   | `ADMIN_EMAILS` | Comma-separated list of admin email addresses |
   | `CONTACT_EMAIL` | Primary support email |
   | `RESEND_API_KEY` | From Step 3 (`re_...`) |
   | `RESEND_FROM_EMAIL` | Your verified sender, e.g. `noreply@your-domain.com` |
   | `PAYID_EMAIL` | (Optional) PayID payment email; defaults to `CONTACT_EMAIL` |

5. Click **Apply**. The first build starts.

### Option B — Manual Web Service

1. Render Dashboard → **New** → **Web Service**.
2. Connect your repository.
3. Set **Runtime** to **Docker**.
4. Set **Dockerfile Path** to `./Dockerfile`.
5. Under **Environment**, add all the variables listed in the table above, plus:

   | Variable | Value |
   |---|---|
   | `DB_NAME` | `criminal_appeals` |
   | `FRONTEND_URL` | `https://<your-service-name>.onrender.com` |
   | `CORS_ORIGINS` | `https://<your-service-name>.onrender.com` |

6. **Health Check Path**: `/api/health`
7. Click **Create Web Service**.

> **Note:** For this repo's single-container deployment, you do **not** need
> `REACT_APP_BACKEND_URL` because the frontend calls the backend using the
> same origin it was loaded from. `REACT_APP_BACKEND_URL` is only required
> for native mobile builds (Capacitor) or split frontend/backend hosting.

---

## Step 5 — Update URLs after first deploy

After the first successful deploy, Render assigns a URL like
`https://appeal-case-manager-xxxx.onrender.com`.

Update the following to use the actual URL:

1. **Render environment variables** (via Dashboard → your service → Environment):
   - `FRONTEND_URL` → actual Render URL
   - `CORS_ORIGINS` → actual Render URL

2. **Google Cloud Console** → OAuth 2.0 Client:
   - Authorised JavaScript origins → add actual URL
   - Authorised redirect URIs → add `<actual-url>/auth/callback`

3. **Trigger a redeploy** in Render so the new environment variables take effect.

---

## Step 6 — (Optional) Custom domain

1. Render Dashboard → your service → **Settings** → **Custom Domains**.
2. Add your domain and follow the DNS instructions.
3. Update `FRONTEND_URL`, `CORS_ORIGINS`, and `REACT_APP_BACKEND_URL` to use
   your custom domain, and update the Google OAuth credentials accordingly.
4. Redeploy.

---

## Environment variable reference

### Backend (required at runtime)

| Variable | Description | Example |
|---|---|---|
| `MONGO_URL` | MongoDB Atlas connection string | `mongodb+srv://user:pass@cluster...` |
| `DB_NAME` | MongoDB database name | `criminal_appeals` |
| `FRONTEND_URL` | Public URL of this service | `https://your-app.onrender.com` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `https://your-app.onrender.com` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `12345.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | `GOCSPX-...` |
| `ADMIN_EMAILS` | Comma-separated admin emails | `admin@example.com` |
| `CONTACT_EMAIL` | Contact/support email | `support@example.com` |

### Backend (optional)

| Variable | Description | Default |
|---|---|---|
| `PAYID_EMAIL` | PayID payment email | Falls back to `CONTACT_EMAIL` |
| `RESEND_API_KEY` | Resend API key used to enable email sending | Email features are disabled when unset |
| `RESEND_FROM_EMAIL` | Verified sender email used with Resend | Required only when `RESEND_API_KEY` is set |

### Frontend (Docker build argument — baked into bundle at build time)

| Variable | Description | Example |
|---|---|---|
| `REACT_APP_BACKEND_URL` | Backend API base URL (mobile/split hosting only) | `https://your-app.onrender.com` |

> **Important:** `REACT_APP_BACKEND_URL` is a Docker build argument consumed by
> the React build step (`yarn build`). You do **not** need it for same-origin
> web deployments. If you do set or change it, you need a full redeploy.

### Optional setup — when you **do** need `REACT_APP_BACKEND_URL` (mobile/split hosting)

Use one of these paths:

1. **Render Dashboard** → your service → **Settings** → **Build & Deploy** →
   **Build Arguments** → add:
   - Key: `REACT_APP_BACKEND_URL`
   - Value: `https://api.your-domain.com`
2. **Blueprint (`render.yaml`)** → uncomment the example `dockerBuildArgs` block
   under the service and set the same value.

Then redeploy so the new build arg is baked into the frontend bundle.

---

## Verifying the deployment

Once deployed, check:

```
https://your-app.onrender.com/api/health        → {"status":"healthy","database":"connected"}
https://your-app.onrender.com/api/ready         → {"ready":true}
```

Admin-only deep diagnostic (requires being logged in as an admin):
```
https://your-app.onrender.com/api/health/env    → env var status (no secret values exposed)
https://your-app.onrender.com/api/health/deep   → MongoDB + OpenAI + email checks
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| App fails to start — `FATAL: Missing required environment variables` | One or more required env vars not set | Check Render Dashboard → Environment |
| Google sign-in shows `redirect_uri_mismatch` | OAuth redirect URI not matching | Add `https://your-url.onrender.com/auth/callback` to Google Cloud Console |
| API calls fail from a separately-hosted frontend | Frontend and backend are on different origins | Set `REACT_APP_BACKEND_URL` to backend origin and ensure CORS allows the frontend |
| Email not sending | `RESEND_API_KEY` missing or sender not verified | Check Resend dashboard |
| `database: disconnected` on health check | `MONGO_URL` wrong or Atlas IP allowlist blocking Render | Fix connection string or allow `0.0.0.0/0` in Atlas |
