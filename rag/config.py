"""Uygulama yapılandırması (ortam değişkenleri + yollar)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent

# Proje kökündeki .env dosyasını yükle (varsa). Mevcut process env önceliklidir.
load_dotenv(ROOT_DIR / ".env", override=False)

DATA_DIR = Path(os.getenv("AFET_DATA_DIR", ROOT_DIR / "data"))
DB_PATH = Path(os.getenv("AFET_DB_PATH", ROOT_DIR / "knowledge.db"))

# Foundry Local model alias'ları (katalog adları)
CHAT_MODEL = os.getenv("AFET_CHAT_MODEL", "phi-3.5-mini")
EMBEDDING_MODEL = os.getenv("AFET_EMBEDDING_MODEL", "qwen3-embedding-0.6b")

# Retrieval (Hızlı CPU üretimi için TOP_K=1)
TOP_K = int(os.getenv("AFET_TOP_K", "1"))
MIN_SIMILARITY = float(os.getenv("AFET_MIN_SIMILARITY", "0.35"))
HYBRID_ALPHA = float(os.getenv("AFET_HYBRID_ALPHA", "0.50"))

# Generation ayarları (CPU dostu, odaklı ve 20-35s hızlı yanıt)
MAX_TOKENS = int(os.getenv("AFET_MAX_TOKENS", "260"))
TEMPERATURE = float(os.getenv("AFET_TEMPERATURE", "0.2"))

# Hızlı Refleks (Instant FAQ) ve Eş Anlamlı Sorgu Genişletme
ENABLE_FAQ_FASTPATH = os.getenv("AFET_ENABLE_FAQ_FASTPATH", "1").lower() in {"1", "true", "yes"}
ENABLE_QUERY_EXPANSION = os.getenv("AFET_ENABLE_QUERY_EXPANSION", "1").lower() in {"1", "true", "yes"}

# Chunking: Başlık duyarlı & 1–3 paragraf hedefi
MAX_PARAGRAPHS_PER_CHUNK = int(os.getenv("AFET_MAX_PARAS_PER_CHUNK", "3"))
MIN_CHUNK_CHARS = int(os.getenv("AFET_MIN_CHUNK_CHARS", "40"))

# Model indirme: False ise yalnızca önbellekteki modeller kullanılır
ALLOW_MODEL_DOWNLOAD = os.getenv("AFET_ALLOW_MODEL_DOWNLOAD", "1").lower() in {
    "1",
    "true",
    "yes",
}

APP_NAME = "afet_rehberi_rag"

# Foundry model önbelleği (Docker volume için)
_model_cache = os.getenv("AFET_MODEL_CACHE_DIR", "").strip()
MODEL_CACHE_DIR = Path(_model_cache) if _model_cache else None
