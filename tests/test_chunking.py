"""Chunking birim testleri."""

from rag.chunking import chunk_text, split_paragraphs


def test_split_paragraphs():
    text = "Birinci paragraf.\n\nİkinci paragraf.\n\n\nÜçüncü."
    parts = split_paragraphs(text)
    assert parts == ["Birinci paragraf.", "İkinci paragraf.", "Üçüncü."]


def test_chunk_groups_paragraphs():
    text = "\n\n".join([f"Paragraf {i} içeriği buradadır ve yeterince uzundur." for i in range(6)])
    chunks = chunk_text(text, source="ornek.txt", max_paragraphs=3, min_chars=20)
    assert len(chunks) >= 2
    assert all(c.source == "ornek.txt" for c in chunks)
    assert chunks[0].chunk_index == 0


def test_empty_text():
    assert chunk_text("   ", source="x.txt") == []
