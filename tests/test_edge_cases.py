"""Prompt, boş sorgu ve kapsam dışı senaryoları (Foundry gerektirmez)."""

from rag.db import StoredChunk
from rag.pipeline import RagPipeline
from rag.prompts import OUT_OF_SCOPE_ANSWER, build_messages, format_citations
from rag.retrieval import RetrievalHit


def test_prompt_forbids_hallucination():
    chunk = StoredChunk(1, "afad_deprem.txt", "Çök-kapan-tutun uygulayın.", 0, [1.0])
    hit = RetrievalHit(chunk=chunk, score=0.91)
    messages = build_messages("Depremde ne yapayım?", [hit])
    system = messages[0]["content"]
    assert "uydurma" in system.lower() or "ASLA uydurma" in system
    assert "AFAD" in system or "afad_deprem" in system
    assert messages[1]["content"] == "Depremde ne yapayım?"


def test_citations_include_source():
    chunk = StoredChunk(1, "kizilay_ilkyardim.txt", "ABC protokolü...", 0, [1.0])
    cites = format_citations([RetrievalHit(chunk=chunk, score=0.88)])
    assert "Kızılay" in cites[0]["source"] or "kizilay" in cites[0]["source"].lower()
    assert cites[0]["score"] == 0.88


def test_empty_query_without_models():
    """Boş sorgu model yüklemeden yanıtlanır."""
    pipeline = RagPipeline()
    result = pipeline.ask("   ")
    assert result.out_of_scope is True
    assert "Boş sorgu" in result.answer


def test_out_of_scope_message_content():
    assert "112" in OUT_OF_SCOPE_ANSWER
    assert "bulunamadı" in OUT_OF_SCOPE_ANSWER.lower() or "bulunamadı" in OUT_OF_SCOPE_ANSWER
