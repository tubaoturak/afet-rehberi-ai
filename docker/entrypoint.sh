#!/bin/sh
set -e

mkdir -p "$(dirname "$AFET_DB_PATH")" "$AFET_MODEL_CACHE_DIR"

echo "[docker] AfetRehberi starting..."
echo "[docker] data=$AFET_DATA_DIR  DB=$AFET_DB_PATH  models=$AFET_MODEL_CACHE_DIR"

if [ ! -f "$AFET_DB_PATH" ] || [ "${AFET_FORCE_INGEST:-0}" = "1" ]; then
  echo "[docker] Running ingest..."
  python main.py ingest
else
  echo "[docker] Existing knowledge DB found — skipping ingest"
fi

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
echo "[docker] Mobil UI + RAG API → http://${HOST}:${PORT}"
exec python main.py serve --host "$HOST" --port "$PORT"
