# Deployment Guide — Appeal Case Manager

## Architecture

```
                     ┌─────────────────────┐
                     │   Reverse Proxy      │
                     │  (Nginx / Cloudflare)│
                     └──────────┬───────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                  │
     /api/* routes      Static frontend      WebSocket
              │                 │               /ws
              ▼                 ▼                 │
     ┌────────────────┐  ┌──────────┐            │
     │  FastAPI (8001) │  │  React   │◄───────────┘
     │  + Uvicorn      │  │  (build) │
     └───────┬─────────┘  └──────────┘
             │
     ┌───────▼─────────┐
     │    MongoDB       │
     │  (Atlas / Local) │
     └─────────────────┘
```

## Prerequisites

- Python 3.11+
- Node.js 18+ and Yarn
- MongoDB 6+ (local or Atlas)
- Domain: `criminallawappealmanagement.com.au`

## Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. Fill in all required variables (see `.env.example` for list)

3. Set `FRONTEND_URL` to your production domain:
   ```
   FRONTEND_URL=https://criminallawappealmanagement.com.au
   ```

## Option 1: Docker Deployment (Recommended)

```bash
# Build
docker build \
  --build-arg REACT_APP_BACKEND_URL=https://criminallawappealmanagement.com.au \
  -t appeal-case-manager .

# Run
docker run -d \
  --name appeal-case-manager \
  --env-file backend/.env \
  -p 8001:8001 \
  --restart unless-stopped \
  appeal-case-manager
```

### Docker Compose (with MongoDB)

```yaml
version: '3.8'
services:
  app:
    build:
      context: .
      args:
        REACT_APP_BACKEND_URL: https://criminallawappealmanagement.com.au
    ports:
      - "8001:8001"
    env_file:
      - backend/.env
    depends_on:
      - mongo
    restart: unless-stopped

  mongo:
    image: mongo:7
    volumes:
      - mongo_data:/data/db
    restart: unless-stopped

volumes:
  mongo_data:
```

## Option 2: PaaS Deployment (Railway / Render)

The included `Procfile` supports PaaS platforms:

```bash
# Railway
railway deploy

# Render (recommended): use the included `render.yaml` Blueprint
# See: /DEPLOYMENT_RENDER.md
```

If Railway deploys from the repository root, it will detect the root `Dockerfile`.
That container now honors Railway's `$PORT` and can build the web frontend
without a separate `REACT_APP_BACKEND_URL` build arg for same-origin web deploys
(mobile builds still require it).

## Option 3: VPS / Manual

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001 --workers 2

# Frontend (build and serve via Nginx)
cd frontend
yarn install && yarn build
# Copy build/ to Nginx web root
```

## Nginx Configuration

```nginx
server {
    listen 443 ssl;
    server_name criminallawappealmanagement.com.au;

    ssl_certificate /etc/letsencrypt/live/criminallawappealmanagement.com.au/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/criminallawappealmanagement.com.au/privkey.pem;

    # Frontend
    location / {
        root /var/www/appeal-case-manager/build;
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
    }
}
```

## Health Checks

- **Liveness**: `GET /api/health` — Returns `{"status": "healthy"}` if the server is running
- **Readiness**: `GET /api/ready` — Returns `{"ready": true}` only when MongoDB is connected and the app is fully initialised
- **Deep check**: `GET /api/health/deep` — Checks MongoDB, LLM key, and email service connectivity

## Backup Strategy

See `BACKUP.md` for MongoDB backup procedures and schedule.

## Post-Deployment Checklist

1. Verify `GET /api/health` returns healthy
2. Verify `GET /api/ready` returns ready
3. Test login flow
4. Test report generation
5. Test PDF/DOCX export
6. Test PayID payment flow
7. Verify CORS only allows production domain
8. Check security headers with securityheaders.com
9. Verify SSL certificate is valid
10. Monitor error logs for first 24 hours
