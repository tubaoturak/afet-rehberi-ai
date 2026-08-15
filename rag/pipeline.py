"""RAG boru hattı: Hibrit Retrieval (Vektör + BM25) → Kompakt Prompt → Üretim."""

from __future__ import annotations

import time
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rag.config import (
    DATA_DIR,
    DB_PATH,
    CHAT_MODEL,
    EMBEDDING_MODEL,
    ENABLE_FAQ_FASTPATH,
    ENABLE_QUERY_EXPANSION,
    HYBRID_ALPHA,
    MIN_SIMILARITY,
    TOP_K,
)
from rag.db import KnowledgeStore, StoredChunk
from rag.faq import match_fast_faq
from rag.foundry_runtime import FoundryRuntime
from rag.hybrid import BM25Index, normalize_turkish
from rag.ingest import ingest_documents
from rag.prompts import (
    OUT_OF_SCOPE_ANSWER,
    build_messages,
    clean_chunk_for_llm,
    clean_llm_response,
    format_citations,
    get_source_title,
)
from rag.query import expand_query
from rag.retrieval import RetrievalHit, search_hybrid


def is_conversational_out_of_scope(query: str, lang: str = "tr") -> bool:
    """
    Hava durumu, sohbet, tarih, yemek ve genel geyik gibi afet/ilk yardım dışı soruları tespit eder.
    Acil durum ve tıbbi terimler içeriyorsa False döner.
    """
    norm = normalize_turkish(query).lower()

    # 1. Acil durum/tıbbi/afet koruma anahtar kelimeleri (kesinlikle engellenmez)
    emergency_pattern = r"\b(carpma|carpmasi|ilk\s*yardim|tedavi|ne\s*yapil|mudahale|kurtarma|belirti|acil|afet|hastane|112|doktor|donma|hipotermi|bayil|kanama|kriz|deprem|yangin|zehir|turnike|cpr|atel|kirik|cikik|bogul|soluk|nefes|tikan|lokma|kacti|cisim|yutma|pansuman|ambulans|sok|fast|felc|koma|yanik)\w*"
    if re.search(emergency_pattern, norm):
        return False

    # 2. Günlük hava durumu, sıcaklık, kar, yağmur vb. sohbet soruları
    weather_pattern = r"(^(bugun|yarin|suan|simdi|disarida|disarisi)?\s*hava\s*(nasil|cok\s+sicak|cok\s+soguk|sicak\s*mi|soguk\s*mu|durumu|kac\s+derece|yagmurlu|kar\s*yagiyor|yagacak|yagar|guzel\s*mi|bozuk\s*mu)|^d[ıi][şs]ar[ıi]da\s+(kar|ya[ğg]mur)\s+ya[ğg][ıi]yor\s*mu|^hava\s+cok\s+sicak$|^hava\s+cok\s+soguk$|^hava\s+sicak$|^hava\s+soguk$)"
    if re.search(weather_pattern, norm):
        return True

    # 3. Yemek tarifleri, tarih, dedikodu, spor sohbeti
    general_chat_pattern = r"\b(tarif|tarifi|sufle|borek|kek|corba|pilav|makarna|fethedildi|fethi|sampiyon|futbol|mac|fiyat|dolar|euro|borsa|sinema|film|muzik|sarki)\b|yemek\s+tarifi"
    if re.search(general_chat_pattern, norm):
        return True

    return False


@dataclass
class RagResult:
    answer: str
    citations: list[dict[str, Any]] = field(default_factory=list)
    hits: list[RetrievalHit] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    out_of_scope: bool = False
    is_fast_faq: bool = False


def contextualize_query(query: str, history: list[dict[str, str]] | None) -> str:
    """Ardışık takip sorularında bağlamı bir önceki soruyla birleştirir."""
    if not history:
        return query
    
    q_lower = query.lower().strip()
    follow_up_triggers = [
        "peki", "o zaman", "bu durumda", "bunda", "kriz aninda", "krizde", "kriz anında",
        "aspirin", "kusturulmali", "kusturmalı", "ne yapmali", "ne yapmalı",
        "during an attack", "in this case", "what next", "what to do then", "what should i do",
        "then what", "how to treat", "and then"
    ]
    is_follow_up = any(q_lower.startswith(t) or t in q_lower for t in follow_up_triggers)
    
    if is_follow_up:
        last_user_query = ""
        for msg in reversed(history):
            if msg.get("role") == "user":
                last_user_query = msg.get("content", "")
                break
        if last_user_query:
            norm_last = last_user_query.lower()
            topic = ""
            for t in [
                "kalp krizi", "heart attack", "kalp", "deprem", "earthquake", "enkaz", "rubble",
                "burun kanamasi", "nosebleed", "burun", "yanik", "burn", "zehirlenme", "poisoning",
                "bogulma", "drowning", "heimlich", "choking", "inme", "stroke", "cikik", "kirik",
                "yilan", "snake", "akrep", "scorpion", "goz", "eye"
            ]:
                if t in norm_last:
                    topic = t
                    break
            if topic:
                clean_q = re.sub(r"^(peki|o zaman|bu durumda|then|and then)\s*", "", query, flags=re.IGNORECASE).strip()
                return f"{topic} {clean_q}".strip()
                
    return query


class RagPipeline:
    def __init__(
        self,
        data_dir: Path = DATA_DIR,
        db_path: Path = DB_PATH,
        chat_model_alias: str = CHAT_MODEL,
        embedding_model_alias: str = EMBEDDING_MODEL,
        top_k: int = TOP_K,
        min_similarity: float = MIN_SIMILARITY,
        hybrid_alpha: float = HYBRID_ALPHA,
        enable_faq: bool = ENABLE_FAQ_FASTPATH,
        enable_query_expansion: bool = ENABLE_QUERY_EXPANSION,
    ) -> None:
        self.data_dir = data_dir
        self.db_path = db_path
        self.top_k = top_k
        self.min_similarity = min_similarity
        self.hybrid_alpha = hybrid_alpha
        self.enable_faq = enable_faq
        self.enable_query_expansion = enable_query_expansion

        self.runtime = FoundryRuntime(
            chat_model_alias=chat_model_alias,
            embedding_model_alias=embedding_model_alias,
        )
        self._store: KnowledgeStore | None = None
        self._bm25_index = BM25Index()
        self._chunks_cache: list[StoredChunk] | None = None
        self._ready = False

    def setup(self) -> None:
        if self._ready:
            return
        self.runtime.initialize()
        self.runtime.load_models()

        self._store = KnowledgeStore(self.db_path)

        self._chunks_cache = self._store.all_chunks()
        if not self._chunks_cache:
            ingest_documents(
                data_dir=self.data_dir,
                db_path=self.db_path,
                runtime=self.runtime,
            )
            self._chunks_cache = self._store.all_chunks()

        # BM25 dizinini hafızada hazırla
        self._bm25_index.index_documents([c.content for c in self._chunks_cache])
        self._ready = True

    def ask(
        self,
        query: str,
        is_button: bool = False,
        lang: str = "tr",
        history: list[dict[str, str]] | None = None,
    ) -> RagResult:
        started = time.perf_counter()
        query = (query or "").strip()
        if not query:
            return RagResult(
                answer="Empty query." if lang == "en" else "Boş sorgu gönderildi. Lütfen bir soru yazın.",
                elapsed_seconds=time.perf_counter() - started,
                out_of_scope=True,
            )

        # 0. Takip sorusu bağlam genişletmesi
        effective_query = contextualize_query(query, history)

        # 1. Hızlı Refleks / Hayati FAQ Kontrolü (YALNIZCA acil durum butonlarında anında 0 ms yanıt)
        if self.enable_faq and is_button:
            faq_match = match_fast_faq(effective_query, lang=lang) or match_fast_faq(query, lang=lang)
            if faq_match:
                faq_answer, faq_source = faq_match
                friendly_source = get_source_title(faq_source)
                dummy_chunk = StoredChunk(
                    id=0,
                    source=friendly_source,
                    content=faq_answer,
                    chunk_index=0,
                    embedding=[],
                )
                hit = RetrievalHit(chunk=dummy_chunk, score=1.0)
                return RagResult(
                    answer=faq_answer,
                    citations=[
                        {
                            "source": friendly_source,
                            "score": 1.0,
                            "excerpt": faq_answer[:240] + ("…" if len(faq_answer) > 240 else ""),
                        }
                    ],
                    hits=[hit],
                    elapsed_seconds=time.perf_counter() - started,
                    out_of_scope=False,
                    is_fast_faq=True,
                )

        if not self._ready:
            self.setup()

        assert self._chunks_cache is not None

        # Kapsam dışı günlük sohbet / hava durumu kontrolü (tıbbi/afet içermiyorsa doğrudan ret)
        if is_conversational_out_of_scope(effective_query, lang=lang):
            out_of_scope_text = "The answer to this question was not found in the local disaster guide. In case of emergency, call 112 / 911." if lang == "en" else OUT_OF_SCOPE_ANSWER
            return RagResult(
                answer=out_of_scope_text,
                citations=[],
                hits=[],
                elapsed_seconds=time.perf_counter() - started,
                out_of_scope=True,
            )

        # 2. Afet / İlk Yardım Eş Anlamlı Genişletme
        search_query = expand_query(effective_query) if (self.enable_query_expansion and lang == "tr") else effective_query

        # 3. Hibrit Arama (İngilizce sorgularda vektör ağırlıklı, Türkçe'de dengeli)
        query_vec = self.runtime.embed_query(search_query)
        eff_alpha = 0.90 if lang == "en" else self.hybrid_alpha
        eff_min_score = 0.25 if lang == "en" else self.min_similarity

        hits = search_hybrid(
            query_embedding=query_vec,
            query_text=search_query,
            chunks=self._chunks_cache,
            bm25_index=self._bm25_index,
            top_k=self.top_k,
            min_score=eff_min_score,
            alpha=eff_alpha,
        )

        if not hits:
            out_of_scope_text = "The answer to this question was not found in the local disaster guide. In case of emergency, call 112 / 911." if lang == "en" else OUT_OF_SCOPE_ANSWER
            return RagResult(
                answer=out_of_scope_text,
                citations=[],
                hits=[],
                elapsed_seconds=time.perf_counter() - started,
                out_of_scope=True,
            )

        # Yüksek güven skorlu doğrudan protokol eşleşmelerinde alakasız konuların promptu kirletmesini filtrele
        top_hit = hits[0]
        clean_doc = clean_chunk_for_llm(top_hit.chunk.content)

        # Doğrulanmış Kızılay / AFAD protokolü tespit edildiğinde doğrudan eksiksiz formatlı protokol sunulur
        if lang == "tr" and top_hit.score >= 0.45 and any(h in clean_doc for h in ["ADIM ADIM", "YAPILMAMASI", "BELİRTİ", "112", "PROTOKOL"]):
            answer = clean_doc
        else:
            messages = build_messages(effective_query, hits, lang=lang)
            raw_answer = self.runtime.chat(messages)
            answer = clean_llm_response(raw_answer)
            if not answer:
                answer = clean_doc

        citations = format_citations(hits)

        return RagResult(
            answer=answer,
            citations=citations,
            hits=hits,
            elapsed_seconds=time.perf_counter() - started,
            out_of_scope=False,
            is_fast_faq=False,
        )

    def ask_stream(
        self,
        query: str,
        is_button: bool = False,
        lang: str = "tr",
        history: list[dict[str, str]] | None = None,
    ):
        """
        SSE Streaming generator: JSON formatında meta, delta ve done olayları üretir.
        """
        import json
        started = time.perf_counter()
        query = (query or "").strip()
        if not query:
            yield json.dumps({
                "type": "meta",
                "sources": [],
                "detectedLang": lang,
                "outOfScope": True,
                "isFastFaq": False,
            }) + "\n"
            yield json.dumps({
                "type": "delta",
                "delta": "Boş sorgu gönderildi. Lütfen bir soru yazın." if lang == "tr" else "Empty query.",
            }) + "\n"
            yield json.dumps({
                "type": "done",
                "elapsedSeconds": round(time.perf_counter() - started, 3),
            }) + "\n"
            return

        effective_query = contextualize_query(query, history)

        # 1. Hızlı Refleks / Hayati FAQ Kontrolü
        if self.enable_faq and is_button:
            faq_match = match_fast_faq(effective_query, lang=lang) or match_fast_faq(query, lang=lang)
            if faq_match:
                faq_answer, faq_source = faq_match
                friendly_source = get_source_title(faq_source)
                yield json.dumps({
                    "type": "meta",
                    "sources": [{"source": friendly_source, "content": faq_answer[:240]}],
                    "detectedLang": lang,
                    "outOfScope": False,
                    "isFastFaq": True,
                }) + "\n"
                words = faq_answer.split(" ")
                for i in range(0, len(words), 4):
                    chunk = " ".join(words[i:i+4]) + (" " if i+4 < len(words) else "")
                    yield json.dumps({"type": "delta", "delta": chunk}) + "\n"
                yield json.dumps({
                    "type": "done",
                    "elapsedSeconds": round(time.perf_counter() - started, 3),
                }) + "\n"
                return

        if not self._ready:
            self.setup()

        assert self._chunks_cache is not None

        # Kapsam dışı günlük sohbet / hava durumu kontrolü (tıbbi/afet içermiyorsa doğrudan ret)
        if is_conversational_out_of_scope(effective_query, lang=lang):
            out_of_scope_text = "The answer to this question was not found in the local disaster guide. In case of emergency, call 112 / 911." if lang == "en" else OUT_OF_SCOPE_ANSWER
            yield json.dumps({
                "type": "meta",
                "sources": [],
                "detectedLang": lang,
                "outOfScope": True,
                "isFastFaq": False,
            }) + "\n"
            yield json.dumps({"type": "delta", "delta": out_of_scope_text}) + "\n"
            yield json.dumps({
                "type": "done",
                "elapsedSeconds": round(time.perf_counter() - started, 3),
            }) + "\n"
            return

        search_query = expand_query(effective_query) if (self.enable_query_expansion and lang == "tr") else effective_query
        query_vec = self.runtime.embed_query(search_query)
        eff_alpha = 0.90 if lang == "en" else self.hybrid_alpha
        eff_min_score = 0.25 if lang == "en" else self.min_similarity

        hits = search_hybrid(
            query_embedding=query_vec,
            query_text=search_query,
            chunks=self._chunks_cache,
            bm25_index=self._bm25_index,
            top_k=self.top_k,
            min_score=eff_min_score,
            alpha=eff_alpha,
        )

        if not hits:
            out_of_scope_text = "The answer to this question was not found in the local disaster guide. In case of emergency, call 112 / 911." if lang == "en" else OUT_OF_SCOPE_ANSWER
            yield json.dumps({
                "type": "meta",
                "sources": [],
                "detectedLang": lang,
                "outOfScope": True,
                "isFastFaq": False,
            }) + "\n"
            yield json.dumps({"type": "delta", "delta": out_of_scope_text}) + "\n"
            yield json.dumps({
                "type": "done",
                "elapsedSeconds": round(time.perf_counter() - started, 3),
            }) + "\n"
            return

        citations = format_citations(hits)
        top_hit = hits[0]
        clean_doc = clean_chunk_for_llm(top_hit.chunk.content)

        yield json.dumps({
            "type": "meta",
            "sources": [{"source": c["source"], "content": c.get("excerpt") or ""} for c in citations],
            "detectedLang": lang,
            "outOfScope": False,
            "isFastFaq": False,
        }) + "\n"

        if lang == "tr" and top_hit.score >= 0.45 and any(h in clean_doc for h in ["ADIM ADIM", "YAPILMAMASI", "BELİRTİ", "112", "PROTOKOL"]):
            lines = clean_doc.split("\n")
            for line in lines:
                yield json.dumps({"type": "delta", "delta": line + "\n"}) + "\n"
        else:
            messages = build_messages(effective_query, hits, lang=lang)
            for token in self.runtime.chat_stream(messages):
                yield json.dumps({"type": "delta", "delta": token}) + "\n"

        yield json.dumps({
            "type": "done",
            "elapsedSeconds": round(time.perf_counter() - started, 3),
        }) + "\n"

    def close(self) -> None:
        if self._store is not None:
            self._store.close()
            self._store = None
        self.runtime.unload()
        self._ready = False
