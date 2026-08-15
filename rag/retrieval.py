"""Vektör ve Hibrit arama (Cosine Similarity + BM25 + Top-K)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from rag.db import StoredChunk
from rag.hybrid import BM25Index, fuse_hybrid_ranks


@dataclass(frozen=True)
class RetrievalHit:
    chunk: StoredChunk
    score: float


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """İki vektör arasındaki kosinüs benzerliğini hesaplar."""
    if len(a) != len(b) or not a:
        return 0.0
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for x, y in zip(a, b, strict=True):
        dot += x * y
        norm_a += x * x
        norm_b += y * y
    if norm_a <= 0.0 or norm_b <= 0.0:
        return 0.0
    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))


def search_similar(
    query_embedding: Sequence[float],
    chunks: Sequence[StoredChunk],
    top_k: int = 3,
    min_score: float = 0.0,
) -> list[RetrievalHit]:
    """Sorgu vektörüne en yakın top-K chunk'ı saf kosinüs benzerliğiyle döndürür."""
    scored: list[RetrievalHit] = []
    for chunk in chunks:
        score = cosine_similarity(query_embedding, chunk.embedding)
        if score >= min_score:
            scored.append(RetrievalHit(chunk=chunk, score=round(score, 4)))
    scored.sort(key=lambda h: h.score, reverse=True)
    return scored[: max(top_k, 0)]


def search_hybrid(
    query_embedding: Sequence[float],
    query_text: str,
    chunks: Sequence[StoredChunk],
    bm25_index: BM25Index,
    top_k: int = 3,
    min_score: float = 0.0,
    alpha: float = 0.5,
) -> list[RetrievalHit]:
    """
    Vektör benzerliği ve BM25 anahtar kelime eşleşmesini harmanlayarak en iyi chunk'ları seçer.
    """
    if not chunks:
        return []

    # 1. Vektör skorları
    vector_hits: list[tuple[int, float]] = []
    for idx, chunk in enumerate(chunks):
        score = cosine_similarity(query_embedding, chunk.embedding)
        vector_hits.append((idx, score))

    # 2. BM25 skorları
    bm25_hits = bm25_index.search(query_text)

    # 3. Hibrit sıralama füzyonu
    fused = fuse_hybrid_ranks(
        vector_hits=vector_hits,
        bm25_hits=bm25_hits,
        chunks=chunks,
        top_k=top_k,
        alpha=alpha,
        min_score=min_score,
    )

    return [RetrievalHit(chunk=c, score=s) for c, s in fused]
