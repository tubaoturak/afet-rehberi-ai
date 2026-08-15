"""Doküman parçalama: Başlık duyarlı (Heading-aware) ve Örtüşmeli (Overlap) chunking."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from rag.config import MAX_PARAGRAPHS_PER_CHUNK, MIN_CHUNK_CHARS


@dataclass(frozen=True)
class TextChunk:
    source: str
    content: str
    chunk_index: int


def split_paragraphs(text: str) -> list[str]:
    """Metni boş satırlara göre paragraflara böler."""
    parts = [p.strip() for p in text.replace("\r\n", "\n").split("\n\n")]
    return [p for p in parts if p]


def is_heading(line: str) -> bool:
    """Satırın bir ana başlık veya bölüm başlığı olup olmadığını belirler."""
    line = line.strip()
    if not line:
        return False
    # Numaralı başlıklar: "1. DEPREM ANI", "2. ENKAZ...", "A. İLK YARDIM"
    if re.match(r"^(\d+\.|\b[A-Z]\.)\s+[A-ZÇĞİÖŞÜ0-9\s\(\)\-\:\,\.]+$", line):
        return True
    # Markdown başlıkları: "### Başlık"
    if line.startswith("#"):
        return True
    # Bölüm ayracı çizgileri: "======", "------"
    if line.startswith("===") or line.startswith("---"):
        return True
    return False


def extract_clean_heading(para: str) -> str:
    """Paragrafın ilk satırından başlık metnini ayıklar."""
    lines = [line.strip() for line in para.split("\n") if line.strip()]
    if not lines:
        return ""
    first_line = lines[0]
    if first_line.startswith("===") or first_line.startswith("---"):
        if len(lines) > 1:
            return lines[1]
    return first_line.lstrip("#").strip()


def chunk_text(
    text: str,
    source: str,
    max_paragraphs: int = MAX_PARAGRAPHS_PER_CHUNK,
    min_chars: int = MIN_CHUNK_CHARS,
    overlap_paragraphs: int = 1,
) -> list[TextChunk]:
    """
    Protokol duyarlı ve başlık korumalı anlamsal parçalama.
    Her acil durum protokolü (başlık + sorular + adımlar + yapılmayacaklar + 112 kriteri)
    bütünlüğünü koruyarak tek parça halinde indekslenir.
    """
    raw_sections = [s.strip() for s in re.split(r'\n---+\n|\n={5,}\n', text) if s.strip()]
    
    merged_sections: list[str] = []
    curr_heading = ""
    for s in raw_sections:
        if s.startswith('#') and len(s) < 120 and "REHBERİ" in s:
            continue
        if re.match(r'^\d+\.\s+[A-ZÇĞİÖŞÜ]', s) and len(s) < 180:
            curr_heading = s
        else:
            if curr_heading:
                merged_sections.append(f"{curr_heading}\n\n{s}".strip())
                curr_heading = ""
            else:
                merged_sections.append(s.strip())
                
    final_sections: list[str] = []
    for sec in merged_sections:
        paras = split_paragraphs(sec)
        if len(paras) > max_paragraphs and len(raw_sections) <= 1:
            step = max_paragraphs - max(0, overlap_paragraphs)
            step = max(1, step)
            for i in range(0, len(paras), step):
                chunk_paras = paras[i : i + max_paragraphs]
                chunk_content = "\n\n".join(chunk_paras).strip()
                if chunk_content:
                    final_sections.append(chunk_content)
        else:
            final_sections.append(sec)

    chunks: list[TextChunk] = []
    for idx, sec in enumerate(final_sections):
        if len(sec) >= min_chars:
            chunks.append(TextChunk(source=source, content=sec, chunk_index=idx))

    return chunks


def load_documents(data_dir: Path) -> list[tuple[str, str]]:
    """data_dir altındaki .txt dosyalarını (kaynak_adı, metin) olarak yükler."""
    docs: list[tuple[str, str]] = []
    if not data_dir.exists():
        return docs
    for path in sorted(data_dir.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        if text:
            docs.append((path.name, text))
    return docs


def chunk_directory(data_dir: Path) -> list[TextChunk]:
    """Klasördeki tüm dokümanları parçalara ayırır."""
    all_chunks: list[TextChunk] = []
    for source, text in load_documents(data_dir):
        all_chunks.extend(chunk_text(text, source=source))
    return all_chunks
