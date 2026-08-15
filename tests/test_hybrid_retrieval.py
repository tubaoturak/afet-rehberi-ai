"""Hibrit arama, BM25, sorgu genişletme, başlık duyarlı chunking ve hızlı FAQ testleri."""

import pytest
from rag.chunking import chunk_text, is_heading
from rag.db import StoredChunk
from rag.faq import match_fast_faq
from rag.hybrid import BM25Index, fuse_hybrid_ranks, normalize_turkish, tokenize_text
from rag.prompts import build_messages
from rag.query import expand_query
from rag.retrieval import RetrievalHit, search_hybrid


def test_turkish_normalization():
    raw = "ÇÖK - KAPAN - TUTUN! Şok ve Ilk Yardım?"
    norm = normalize_turkish(raw)
    assert norm == "cok kapan tutun sok ve ilk yardim"


def test_bm25_exact_keyword_retrieval():
    docs = [
        "Deprem anında çök kapan tutun pozisyonu alınmalıdır.",
        "Yangın durumunda acil çıkış kapılarına yönelin ve asansör kullanmayın.",
        "Burun kanamasında baş hafifçe öne eğilerek burun kanatları sıkılır.",
        "Şiddetli atardamar kanamasında tek kemikli bölgeye turnike uygulanır.",
    ]
    bm25 = BM25Index()
    bm25.index_documents(docs)

    # "turnike" araması 3. dokümanı bulmalı
    results = bm25.search("turnike nasıl yapılır")
    assert len(results) > 0
    best_doc_id, best_score = results[0]
    assert best_doc_id == 3
    assert best_score > 0

    # "çök kapan tutun" araması 0. dokümanı bulmalı
    results = bm25.search("çök kapan tutun nedir")
    assert len(results) > 0
    assert results[0][0] == 0


def test_hybrid_rank_fusion_favors_both_vector_and_keyword():
    chunks = [
        StoredChunk(1, "afad_deprem.txt", "Deprem anında çök kapan tutun yapın.", 0, [0.9, 0.1]),
        StoredChunk(2, "yangin.txt", "Yangın tüpü kullanımı...", 0, [0.1, 0.9]),
        StoredChunk(3, "ilkyardim.txt", "Genel ilk yardım bilgileri...", 0, [0.5, 0.5]),
    ]

    bm25 = BM25Index()
    bm25.index_documents([c.content for c in chunks])

    # Sadece cosine benzerliği ve sorgu "çök kapan"
    hits = search_hybrid(
        query_embedding=[0.85, 0.15],
        query_text="çök kapan",
        chunks=chunks,
        bm25_index=bm25,
        top_k=2,
        alpha=0.5,
    )

    assert len(hits) == 2
    assert hits[0].chunk.source == "afad_deprem.txt"
    assert hits[0].score > hits[1].score


def test_query_expansion():
    expanded = expand_query("zelzele anında ne yapmalı")
    assert "deprem" in expanded
    assert "çök" in expanded or "tutun" in expanded

    expanded_cpr = expand_query("kalbi durdu ne yapmalıyım")
    assert "cpr" in expanded_cpr or "kalp masajı" in expanded_cpr


def test_fast_faq_matching():
    # Deprem anı
    res = match_fast_faq("deprem anında ne yapılmalı")
    assert res is not None
    answer, source = res
    assert "ÇÖK-KAPAN-TUTUN" in answer
    assert "afad" in source.lower()

    # Burun kanaması
    res2 = match_fast_faq("Burnum kanıyor")
    assert res2 is not None
    answer2, source2 = res2
    assert "ÖNE" in answer2
    assert "kizilay" in source2.lower()

    # CPR
    res3 = match_fast_faq("kalp masajı nasıl yapılır")
    assert res3 is not None
    answer3, source3 = res3
    assert "30" in answer3 and "2" in answer3

    # Alakasız sorgu
    assert match_fast_faq("yarın hava nasıl olacak") is None


def test_heading_aware_chunking_with_overlap():
    text = (
        "1. DEPREM ANI PROTOKOLÜ:\n"
        "Sarsıntı anında çök kapan tutun yapın.\n\n"
        "Pencerelerden ve camlardan uzak durun.\n\n"
        "2. ENKAZ ALTI PROTOKOLÜ:\n"
        "Enkaz altındayken ritmik vuruşlar yapın.\n\n"
        "Düdük çalarak yerinizi belli edin."
    )
    chunks = chunk_text(text, source="afad_deprem.txt", max_paragraphs=2, min_chars=10, overlap_paragraphs=1)
    assert len(chunks) >= 2
    assert "DEPREM" in chunks[0].content or "afad_deprem" in chunks[0].content


def test_small_model_prompt_structure():
    chunk = StoredChunk(1, "afad_deprem.txt", "Çök-kapan-tutun uygulayın.", 0, [1.0])
    hit = RetrievalHit(chunk=chunk, score=0.95)
    messages = build_messages("Depremde ne yapmalı?", [hit])
    sys_prompt = messages[0]["content"]

    assert "1)" in sys_prompt or "1." in sys_prompt
    assert "BAĞLAM" in sys_prompt
    assert "112" in sys_prompt
    assert "uydurma" in sys_prompt.lower()
