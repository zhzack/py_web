# syntax=docker/dockerfile:1.6

# ---------- Stage 1: build Vue frontend ----------
FROM node:20-alpine AS frontend
WORKDIR /web
COPY vue-project/package*.json ./
RUN npm ci --no-audit --no-fund || npm install --no-audit --no-fund
COPY vue-project/ ./
RUN npm run build

# ---------- Stage 2: python runtime ----------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Shanghai

WORKDIR /app

# system deps for cryptography / bcrypt wheels are precompiled, but keep curl for healthcheck
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && pip install 'bcrypt<4.1'

# app source
COPY app/ ./app/
COPY deploy/ ./deploy/

# built frontend from stage 1 -> served by FastAPI (vue-project/dist)
COPY --from=frontend /web/dist/ ./vue-project/dist/

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
  CMD curl -fsS http://127.0.0.1:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
