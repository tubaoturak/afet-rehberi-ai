"""Küçük modeller (Phi-3.5-mini, Phi-4-mini, 0.5B-3B) için optimize edilmiş istemler ve kurallar."""

from __future__ import annotations

import re
from typing import Sequence

from rag.retrieval import RetrievalHit

SOURCE_TITLES: dict[str, str] = {
    "kizilay_ozel_ilkyardim.txt": "Türk Kızılayı Özel İlk Yardım Rehberi",
    "kizilay_ilkyardim.txt": "Türk Kızılayı Temel İlk Yardım Rehberi",
    "kizilay_kalp_cpr.txt": "Türk Kızılayı CPR (Temel Yaşam Desteği) Rehberi",
    "kizilay_kanamalar_sok.txt": "Türk Kızılayı Kanama ve Şok Rehberi",
    "kizilay_kemik_eklem.txt": "Türk Kızılayı Kırık ve Çıkık Rehberi",
    "kizilay_goz_kulak_burun.txt": "Türk Kızılayı Duyu Organları İlk Yardım Rehberi",
    "afad_deprem.txt": "AFAD Deprem ve Enkaz Rehberi",
    "afad_yangin_sel.txt": "AFAD Yangın ve Sel Rehberi",
    "afad_cevresel_aciller.txt": "AFAD Çevresel Aciller Rehberi",
    "afad_kimyasal.txt": "AFAD KBRN & Kimyasal Aciller Rehberi",
}


def get_source_title(source: str) -> str:
    """Dosya adını kullanıcı dostu resmi kurum kaynak başlığına dönüştürür."""
    clean_src = source.strip().lower()
    if clean_src in SOURCE_TITLES:
        return SOURCE_TITLES[clean_src]
    for key, title in SOURCE_TITLES.items():
        if key in clean_src:
            return title
    return source.replace(".txt", "").replace("_", " ").title()


SYSTEM_RULES_TR = (
    "Sen AfetRehberi acil durum ve ilk yardım asistanısın.\n"
    "Aşağıdaki BAĞLAM metnindeki bilgileri kullanarak soruya doğrudan Türkçe ve net maddeler (1), 2), 3) veya tire -) halinde yanıt ver.\n"
    "- Soru belirtilerle ilgiliyse doğrudan belirti maddelerini yaz.\n"
    "- Soru ilk yardım / ne yapılması gerektiği ile ilgiliyse doğrudan Adım Adım Müdahale adımlarını, Yapılmaması Gerekenleri ve 112 kriterini yaz.\n"
    "Giriş veya selamlama yapmadan doğrudan maddelerle başla, bağlam dışı bilgi uydurma."
)

SYSTEM_RULES_EN = (
    "You are DisasterGuide emergency and first aid AI assistant.\n"
    "Answer directly in clear English bullet points strictly using the CONTEXT below.\n"
    "- If asked about symptoms, list only the symptom points.\n"
    "- If asked about first aid / what to do, list the step-by-step actions and critical mistakes to avoid.\n"
    "Start directly with bullet points without greeting or preamble."
)


def clean_chunk_for_llm(content: str) -> str:
    """Doküman başlığını acil durum formatına dönüştürür ve arama senaryolarını ayıklar."""
    if not content:
        return ""
    # "## Kullanıcı Soruları ve Arama Senaryoları:" bölümünü çıkar
    cleaned = re.sub(
        r"## Kullanıcı Soruları ve Arama Senaryoları:.*?(?=## 📋|## ⚠️|## 🚨|## 🩺|$)",
        "",
        content,
        flags=re.DOTALL,
    ).strip()

    # Ham numaralı başlıkları (ör. '1. KALP KRİZİ...') '🚨 ACİL DURUM: Kalp Krizi İlk Yardımı' formatına çevir
    lines = cleaned.splitlines()
    if lines:
        first = lines[0].strip()
        if re.match(r"^\d+\.\s+[A-ZÇĞİÖŞÜ]", first):
            raw_title = re.sub(r"^\d+\.\s*", "", first).strip()
            raw_title = re.sub(r"\([^\)]*\)", "", raw_title).strip()
            raw_title = re.sub(r"\s+(PROTOKOL[ÜU]|REHBER[İI])$", "", raw_title, flags=re.IGNORECASE).strip()
            raw_title = re.sub(r"\s+", " ", raw_title).strip()
            title_str = raw_title.title().replace("Ve ", "ve ").replace("Ile ", "ile ").replace("Cpr", "CPR").replace("Aed", "AED").replace("Oed", "OED")
            title_str = title_str.replace("i̇", "i")
            lines[0] = f"🚨 ACİL DURUM: {title_str}"
            cleaned = "\n".join(lines)

    return cleaned.strip()


def clean_llm_response(text: str) -> str:
    """Küçük modellerin üretebileceği döngü tekrarlarını, meta ibareleri veya yabancı karakterleri temizler."""
    if not text:
        return ""
    
    cleaned = text.strip()
    
    # 1. Yabancı (Asya vb.) bozuk token kalıntılarını temizle
    cleaned = re.sub(r"[\u4e00-\u9fff\u3040-\u30ff]", "", cleaned)
    
    # 2. Döngüye giren tekrarlayan öbekleri (loop repetition) teke indir
    pattern = r"(.{10,80}?)(?:\s*,?\s*\1){2,}"
    cleaned = re.sub(pattern, r"\1", cleaned, flags=re.DOTALL)
    
    # 3. 'Yanıt: Bu bilgi yerel afet rehberinde bulunamadı' gibi kalıntıları ayıkla
    cleaned = re.sub(
        r"(?i)\n*yanıt\s*:\s*bu\s+bilgi\s+yerel\s+afet\s+rehberinde\s+bulunamad[ıi]\.?.*$",
        "",
        cleaned,
    ).strip()
    
    # 4. Ardışık birebir aynı satırları tekilleştir
    lines = cleaned.splitlines()
    deduped: list[str] = []
    for line in lines:
        l_str = line.strip()
        if not l_str:
            continue
        if deduped and deduped[-1] == l_str:
            continue
        deduped.append(l_str)
    cleaned = "\n".join(deduped).strip()
    
    # Sadece soruyu tekrarlayan boş yanıtları düzelt
    if cleaned.endswith("?") and len(cleaned.splitlines()) == 1:
        return ""
        
    return cleaned


def build_context_block(hits: Sequence[RetrievalHit]) -> str:
    """Küçük modelleri yormayan, soru başlıklarından arındırılmış temiz bağlam bloğu oluşturur."""
    if not hits:
        return "(Bağlam bulunamadı.)"
    parts: list[str] = []
    for i, hit in enumerate(hits, start=1):
        title = get_source_title(hit.chunk.source)
        clean_content = clean_chunk_for_llm(hit.chunk.content)
        parts.append(f"--- BİLGİ {i} (Kaynak: {title}) ---\n{clean_content}")
    return "\n\n".join(parts)


def build_messages(query: str, hits: Sequence[RetrievalHit], lang: str = "tr") -> list[dict[str, str]]:
    """Model için sistem ve kullanıcı mesajlarını hazırlar."""
    context = build_context_block(hits)
    rules = SYSTEM_RULES_EN if lang == "en" else SYSTEM_RULES_TR
    system = f"{rules}\n\nBAĞLAM:\n{context}"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": query},
    ]


def format_citations(hits: Sequence[RetrievalHit]) -> list[dict[str, str | float]]:
    """Arayüz için kaynak alıntılarını kurum isimleriyle formatlar."""
    return [
        {
            "source": get_source_title(hit.chunk.source),
            "score": round(hit.score, 4),
            "excerpt": hit.chunk.content[:240]
            + ("…" if len(hit.chunk.content) > 240 else ""),
        }
        for hit in hits
    ]


OUT_OF_SCOPE_ANSWER_TR = (
    "Bu sorunun cevabı yerel bilgi tabanındaki dokümanlarda bulunamadı. "
    "Lütfen sorunuzu afet / ilk yardım kapsamında yeniden sorun.\n\n"
    "🚨 Hayati tehlike varsa derhal 112 Acil Çağrı Merkezi'ni arayın."
)

OUT_OF_SCOPE_ANSWER_EN = (
    "The answer to this question was not found in the local disaster guide knowledge base. "
    "Please ask an emergency or first aid related question.\n\n"
    "🚨 In case of immediate life threat, call 112 / Emergency Services."
)

OUT_OF_SCOPE_ANSWER = OUT_OF_SCOPE_ANSWER_TR
