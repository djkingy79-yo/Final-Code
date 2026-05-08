# ─── Stage 1: Build Frontend ───
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --network-timeout 600000
COPY frontend/ ./
ARG REACT_APP_BACKEND_URL=http://localhost:8001
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
RUN yarn build

# ─── Stage 2: Backend + Serve Frontend ───
FROM python:3.11-slim-bookworm
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libmagic1 \
    tesseract-ocr \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ -r requirements.txt

# Copy backend
COPY backend/ ./

# Copy built frontend
COPY --from=frontend-build /app/frontend/build ./static

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD sh -c 'curl -f "http://localhost:${PORT:-8001}/api/health" || exit 1'

CMD ["sh", "-c", "exec uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001} --workers 1"]
