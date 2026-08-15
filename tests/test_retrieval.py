"""SQLite + cosine retrieval testleri (Foundry gerektirmez)."""

from pathlib import Path

from rag.db import KnowledgeStore, StoredChunk
from rag.retrieval import cosine_similarity, search_similar


def test_cosine_identical():
    v = [1.0, 0.0, 0.0]
    assert abs(cosine_similarity(v, v) - 1.0) < 1e-9


def test_cosine_orthogonal():
    assert abs(cosine_similarity([1, 0], [0, 1])) < 1e-9


def test_store_and_search(tmp_path: Path):
    db = tmp_path / "t.db"
    store = KnowledgeStore(db)
    store.insert_chunks(
        sources=["a.txt", "b.txt", "c.txt"],
        contents=["deprem çök kapan tutun", "yangın merdiven kullanma", "sel yüksek yer"],
        chunk_indices=[0, 0, 0],
        embeddings=[
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
    )
    assert store.count() == 3
    chunks = store.all_chunks()
    hits = search_similar([0.9, 0.1, 0.0], chunks, top_k=2, min_score=0.1)
    assert hits[0].chunk.source == "a.txt"
    assert hits[0].score > hits[1].score
    store.close()


def test_top_k_and_threshold():
    chunks = [
        StoredChunk(1, "a.txt", "x", 0, [1.0, 0.0]),
        StoredChunk(2, "b.txt", "y", 0, [0.0, 1.0]),
        StoredChunk(3, "c.txt", "z", 0, [0.7, 0.7]),
    ]
    hits = search_similar([1.0, 0.0], chunks, top_k=2, min_score=0.5)
    assert len(hits) == 2
    assert hits[0].chunk.source == "a.txt"
