"""Hibrit arama motoru: Türkçe uyumlu Okapi BM25 + Sıralama Füzyonu (RRF / Weighted Score)."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Sequence

from rag.db import StoredChunk

TURKISH_STOP_WORDS: set[str] = {
    "nasil", "ne", "nedir", "nelerdir", "icin", "ile", "ve", "veya", "bir", "bu", "su", "o",
    "gibi", "kadar", "mi", "mu", "mu?", "mi?", "mı", "mı?", "mü", "mü?", "de", "da", "ise", "ya", "ki", "daha",
    "var", "yok", "olan", "olarak", "ben", "sen", "biz", "siz", "onlar", "bana", "sana", "size", "bize",
    "bunu", "sunu", "onu", "bunun", "sunun", "onun", "ama", "fakat", "lakin", "ancak",
    "gore", "karsi", "sonra", "once", "dolayi", "diye", "hem", "her", "tum", "bazi",
    "etmek", "yapmak", "olmak", "yapilir", "edilir", "olur", "eden", "yapan",
    "tarifi", "tarif", "verir", "misin", "musun", "misiniz", "musunuz",
    "hangi", "tarihte", "tarihinde", "gerceklesti", "olacak", "bugun", "yarin",
    "lutfen", "anlat", "yaz", "ver", "soyle", "midir", "mudur",
    "hava", "havalar", "durumu", "haber", "haberler", "fiyat", "fiyati", "dolar", "euro", "borsa", "sinema", "film", "muzik", "sarki", "futbol", "mac",
    "cok", "az", "fazla", "asiri", "disarida", "disarisi", "iceride", "icerisi", "suan", "simdi",
    "yagiyor", "yagacak", "yagar", "yagmur", "kar", "derece", "kac", "sicak", "soguk", "gunes", "bulut", "ruzgar",
}


def normalize_turkish(text: str) -> str:
    """Türkçe karakterleri ve noktalama işaretlerini normalize eder."""
    if not text:
        return ""
    mapping = {
        "İ": "i",
        "I": "i",
        "ı": "i",
        "i": "i",
        "Ğ": "g",
        "ğ": "g",
        "Ü": "u",
        "ü": "u",
        "Ş": "s",
        "ş": "s",
        "Ö": "o",
        "ö": "o",
        "Ç": "c",
        "ç": "c",
    }
    chars = [mapping.get(c, c.lower()) for c in text]
    normalized = "".join(chars)
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def tokenize_text(text: str, filter_stopwords: bool = True) -> list[str]:
    """Metni normalize edip token listesine böler ve isteğe bağlı durak kelimeleri eler."""
    norm = normalize_turkish(text)
    if not norm:
        return []
    tokens = norm.split()
    cleaned = [t for t in tokens if len(t) > 1 or t.isdigit()]
    if filter_stopwords:
        filtered = [t for t in cleaned if t not in TURKISH_STOP_WORDS]
        return filtered if filtered else cleaned
    return cleaned


class BM25Index:
    """Saf Python ile çalışan optimize Okapi BM25 dizini."""

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        self.k1 = k1
        self.b = b
        self.corpus_size: int = 0
        self.avg_doc_len: float = 0.0
        self.doc_lens: list[int] = []
        self.doc_freqs: dict[str, int] = {}
        self.inverted_index: dict[str, list[tuple[int, int]]] = {}
        self._is_indexed: bool = False

    def index_documents(self, documents: Sequence[str]) -> None:
        """Doküman listesini BM25 dizinine ekler."""
        self.corpus_size = len(documents)
        self.doc_lens = []
        self.doc_freqs = {}
        self.inverted_index = {}

        if self.corpus_size == 0:
            self.avg_doc_len = 0.0
            self._is_indexed = True
            return

        total_len = 0
        for doc_id, doc_text in enumerate(documents):
            tokens = tokenize_text(doc_text, filter_stopwords=True)
            doc_len = len(tokens)
            self.doc_lens.append(doc_len)
            total_len += doc_len

            tf_map: dict[str, int] = {}
            for token in tokens:
                tf_map[token] = tf_map.get(token, 0) + 1

            for token, tf in tf_map.items():
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1
                if token not in self.inverted_index:
                    self.inverted_index[token] = []
                self.inverted_index[token].append((doc_id, tf))

        self.avg_doc_len = total_len / self.corpus_size if self.corpus_size > 0 else 0.0
        self._is_indexed = True

    def _idf(self, term: str) -> float:
        df = self.doc_freqs.get(term, 0)
        if df == 0:
            return 0.0
        return math.log(1.0 + (self.corpus_size - df + 0.5) / (df + 0.5))

    def search(self, query: str) -> list[tuple[int, float]]:
        """Sorgu için her dokümanın BM25 skorunu hesaplar ve (doc_id, score) sıralı döner."""
        if not self._is_indexed or self.corpus_size == 0:
            return []

        q_tokens = tokenize_text(query, filter_stopwords=True)
        if not q_tokens:
            return []

        scores: dict[int, float] = {}

        for token in q_tokens:
            idf = self._idf(token)
            if idf <= 0.0:
                continue

            postings = self.inverted_index.get(token, [])
            for doc_id, tf in postings:
                doc_len = self.doc_lens[doc_id]
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_len or 1.0)))
                term_score = idf * (numerator / denominator)
                scores[doc_id] = scores.get(doc_id, 0.0) + term_score

        results = [(doc_id, score) for doc_id, score in scores.items() if score > 0.0]
        results.sort(key=lambda x: x[1], reverse=True)
        return results


def fuse_hybrid_ranks(
    vector_hits: list[tuple[int, float]],
    bm25_hits: list[tuple[int, float]],
    chunks: Sequence[StoredChunk],
    top_k: int = 3,
    alpha: float = 0.5,
    min_score: float = 0.35,
    vector_only_min_cosine: float = 0.45,
) -> list[tuple[StoredChunk, float]]:
    """
    Vektör ve BM25 skorlarını tutarlı normalizasyonla harmanlar.
    Alakasız / kapsam dışı sorgularda sıfır anahtar kelime ve düşük kosinüs varsa doküman döndürmez.
    """
    if not chunks:
        return []

    v_dict = dict(vector_hits)
    bm_dict = dict(bm25_hits)

    max_b = max(bm_dict.values()) if bm_dict else 0.0
    bm_norm_base = max(12.0, max_b)

    all_doc_ids = set(v_dict.keys()).union(set(bm_dict.keys()))
    combined: list[tuple[StoredChunk, float]] = []

    for doc_id in all_doc_ids:
        if doc_id < 0 or doc_id >= len(chunks):
            continue

        raw_v = max(0.0, min(1.0, v_dict.get(doc_id, 0.0)))  # Mutlak kosinüs benzerliği
        raw_b = bm_dict.get(doc_id, 0.0)  # BM25 skoru

        # Eğer hiç anahtar kelime eşleşmediyse (BM25 = 0), mutlak kosinüs eşiği zorunludur
        if raw_b == 0.0 and raw_v < vector_only_min_cosine:
            continue

        # Eğer anahtar kelime zayıf ve anlamsal kosinüs çok düşükse (kapsam dışı tekil kelime), reddet
        if raw_b > 0.0 and raw_v < 0.32 and raw_b < 12.0:
            continue

        norm_b = max(0.0, min(1.0, raw_b / bm_norm_base)) if bm_norm_base > 0 else 0.0

        if raw_b > 0.0 and raw_v >= 0.20:
            # Hem anahtar kelime hem semantik uyum
            hybrid_score = alpha * raw_v + (1.0 - alpha) * norm_b
        elif raw_b > 0.0:
            # Yalnızca anahtar kelime (zayıf semantik)
            hybrid_score = (1.0 - alpha) * norm_b
        else:
            # Yalnızca yüksek semantik benzerlik
            hybrid_score = alpha * raw_v

        if hybrid_score >= min_score:
            combined.append((chunks[doc_id], round(hybrid_score, 4)))

    combined.sort(key=lambda item: item[1], reverse=True)
    return combined[: max(top_k, 0)]
