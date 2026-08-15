"""Doküman ingestion: chunk → önbellek kontrolü → eksik chunk'ları embed et → SQLite."""

from __future__ import annotations

import hashlib
import time
from pathlib import Path

from rag.chunking import chunk_directory
from rag.config import DATA_DIR, DB_PATH
from rag.db import KnowledgeStore
from rag.foundry_runtime import FoundryRuntime


def _hash_content(text: str) -> str:
    """Metin için SHA256 içerik parmak izi oluşturur."""
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def _embed_with_retry(
    runtime: FoundryRuntime, texts: list[str], max_retries: int = 3
) -> list[list[float]]:
    """Olası yoğunluk/zaman aşımına karşı embedding üretimini güvenli şekilde dener."""
    for attempt in range(max_retries):
        try:
            return runtime.embed_texts(texts)
        except Exception as e:
            if attempt == max_retries - 1:
                results: list[list[float]] = []
                for t in texts:
                    results.append(runtime.embed_query(t))
                return results
            time.sleep(2)
    return []


def ingest_documents(
    data_dir: Path | None = None,
    db_path: Path | None = None,
    runtime: FoundryRuntime | None = None,
    batch_size: int = 16,
) -> int:
    """
    data/ altındaki .txt dosyalarını parçalar.
    Daha önce hesaplanan parçaları önbellekten (0.01 saniyede) çeker,
    yalnızca YENİ veya DEĞİŞMİŞ parçaları modelden geçirerek saniyeler içinde tamamlar.
    """
    data_dir = Path(data_dir or DATA_DIR)
    db_path = Path(db_path or DB_PATH)

    chunks = chunk_directory(data_dir)
    if not chunks:
        raise FileNotFoundError(f"Doküman bulunamadı: {data_dir}")

    store = KnowledgeStore(db_path)
    own_runtime = False

    try:
        # 1. Tüm chunk'ların içerik hash'lerini çıkar
        chunk_hashes = [_hash_content(c.content) for c in chunks]

        # 2. Önbellekte olanları anında sorgula
        cached_map = store.get_cached_embeddings(chunk_hashes)

        # 3. Yalnızca eksik/yeni olan chunk'ları bul
        missing_indices = [
            i for i, h in enumerate(chunk_hashes) if h not in cached_map
        ]

        print(
            f"[*] Toplam {len(chunks)} parça: {len(cached_map)} önbellekten yüklendi, "
            f"{len(missing_indices)} yeni parça hesaplanacak."
        )

        if missing_indices:
            if runtime is None:
                own_runtime = True
                runtime = FoundryRuntime()
                runtime.initialize()
                runtime.load_models()

            # Yeni parçaları batchler halinde hesapla ve önbelleğe kaydet
            for start in range(0, len(missing_indices), batch_size):
                batch_idxs = missing_indices[start : start + batch_size]
                batch_texts = [chunks[i].content for i in batch_idxs]
                batch_hashes = [chunk_hashes[i] for i in batch_idxs]

                new_embs = _embed_with_retry(runtime, batch_texts)
                if len(new_embs) != len(batch_texts):
                    raise RuntimeError(
                        f"Embedding sayısı uyuşmuyor: {len(new_embs)} != {len(batch_texts)}"
                    )

                store.save_cached_embeddings(batch_hashes, new_embs)
                for h, emb in zip(batch_hashes, new_embs, strict=True):
                    cached_map[h] = emb

                print(f"[*] Yeni hesaplanan: {min(start + batch_size, len(missing_indices))}/{len(missing_indices)}")

        # 4. Veritabanını güncel chunk ve embedding listesiyle doldur
        store.clear()
        all_embeddings = [cached_map[h] for h in chunk_hashes]

        total = store.insert_chunks(
            sources=[c.source for c in chunks],
            contents=[c.content for c in chunks],
            chunk_indices=[c.chunk_index for c in chunks],
            embeddings=all_embeddings,
        )

        print(f"[✓] {total} parça başarıyla veritabanına yazıldı.")
        return total

    finally:
        store.close()
        if own_runtime and runtime is not None:
            runtime.unload()
