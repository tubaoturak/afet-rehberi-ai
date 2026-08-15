"""SQLite vektör / chunk depolama katmanı ve anlık artımlı önbellekleme (Cache)."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class StoredChunk:
    id: int
    source: str
    content: str
    chunk_index: int
    embedding: list[float]


SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source);

CREATE TABLE IF NOT EXISTS embedding_cache (
    content_hash TEXT PRIMARY KEY,
    embedding TEXT NOT NULL
);
"""


class KnowledgeStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def clear(self) -> None:
        self._conn.execute("DELETE FROM chunks")
        self._conn.commit()

    def count(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS c FROM chunks").fetchone()
        return int(row["c"])

    def get_cached_embeddings(self, hashes: Sequence[str]) -> dict[str, list[float]]:
        """Önceden hesaplanmış embeddingleri hafızadan anında getirir."""
        if not hashes:
            return {}
        placeholders = ",".join(["?"] * len(hashes))
        rows = self._conn.execute(
            f"SELECT content_hash, embedding FROM embedding_cache WHERE content_hash IN ({placeholders})",
            list(hashes),
        ).fetchall()
        return {r["content_hash"]: json.loads(r["embedding"]) for r in rows}

    def save_cached_embeddings(
        self, hashes: Sequence[str], embeddings: Sequence[Sequence[float]]
    ) -> None:
        """Yeni üretilen embeddingleri önbelleğe kaydeder."""
        if not hashes:
            return
        rows = [
            (h, json.dumps(list(emb)))
            for h, emb in zip(hashes, embeddings, strict=True)
        ]
        self._conn.executemany(
            "INSERT OR REPLACE INTO embedding_cache (content_hash, embedding) VALUES (?, ?)",
            rows,
        )
        self._conn.commit()

    def insert_chunks(
        self,
        sources: Sequence[str],
        contents: Sequence[str],
        chunk_indices: Sequence[int],
        embeddings: Sequence[Sequence[float]],
    ) -> int:
        if not (len(sources) == len(contents) == len(chunk_indices) == len(embeddings)):
            raise ValueError("insert_chunks: tüm listeler aynı uzunlukta olmalı")
        rows = [
            (src, content, idx, json.dumps(list(emb)))
            for src, content, idx, emb in zip(
                sources, contents, chunk_indices, embeddings, strict=True
            )
        ]
        self._conn.executemany(
            "INSERT INTO chunks (source, content, chunk_index, embedding) VALUES (?, ?, ?, ?)",
            rows,
        )
        self._conn.commit()
        return len(rows)

    def all_chunks(self) -> list[StoredChunk]:
        rows = self._conn.execute(
            "SELECT id, source, content, chunk_index, embedding FROM chunks ORDER BY id"
        ).fetchall()
        return [
            StoredChunk(
                id=int(r["id"]),
                source=r["source"],
                content=r["content"],
                chunk_index=int(r["chunk_index"]),
                embedding=json.loads(r["embedding"]),
            )
            for r in rows
        ]

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "KnowledgeStore":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
