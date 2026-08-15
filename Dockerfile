# --- Frontend build ---
FROM node:20-bookworm-slim AS frontend
WORKDIR /ui
COPY package.json package-lock.json* ./
RUN npm install
COPY index.html vite.config.ts tsconfig.json metadata.json ./
COPY src ./src
COPY public* ./public/
RUN npm run build

# --- Python runtime (Foundry Local + FastAPI + mobil UI) ---
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    AFET_DATA_DIR=/app/data \
    AFET_DB_PATH=/app/db/knowledge.db \
    AFET_MODEL_CACHE_DIR=/models \
    AFET_ALLOW_MODEL_DOWNLOAD=1 \
    PORT=8000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
      curl \
      libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./
COPY rag ./rag
COPY data ./data
COPY tests ./tests
COPY pytest.ini ./
COPY --from=frontend /ui/dist ./dist
COPY docker/entrypoint.sh /entrypoint.sh
COPY knowledge.db* /app/db/
RUN chmod +x /entrypoint.sh \
    && mkdir -p /models /app/db

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/api/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
