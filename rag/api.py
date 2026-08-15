"""FastAPI: mobil React UI ile uyumlu /api/chat, /api/ingest + statik build sunumu."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from rag.pipeline import RagPipeline

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

FOLLOW_UPS = [
    "Deprem anında bina içinde ne yapmalıyım?",
    "Enkaz altındayken sesimi nasıl duyurmalıyım?",
    "Burun kanamasında ne yapılmalı?",
    "Kalp masajı (CPR) nasıl yapılır?",
    "Yangın sırasında ne yapmalıyım?",
    "Sel uyarısı gelince ne yapılmalı?",
]


class ChatRequest(BaseModel):
    query: str = Field(default="")
    lang: str = Field(default="tr")
    is_button: bool = Field(default=False)
    history: list[dict[str, str]] = Field(default_factory=list)


def detect_lang(query: str, client_lang: str = "tr") -> str:
    """Sorgunun dilini tespit eder; kullanıcı TR seçse bile soru İngilizce ise 'en' döner."""
    q = query.lower().strip()
    
    # Türkçe özel karakterler varsa direkt Türkçe'dir
    if re.search(r"[çğışöüÇĞİŞÖÜ]", query):
        return "tr"
        
    # İngilizce belirteçler
    en_patterns = [
        r"\b(how|what|why|when|where|which|who|whom|whose)\b",
        r"\b(is|are|am|was|were|be|been|being)\b",
        r"\b(can|could|should|would|must|might|may|shall)\b",
        r"\b(do|does|did|done|have|has|had)\b",
        r"\b(the|this|that|these|those|my|your|his|her|its|our|their|i|you|he|she|we|they|me|him|us|them)\b",
        r"\b(if|in|on|at|to|for|with|by|from|about|into|through|during|after|before|under|above)\b",
        r"\b(nosebleed|earthquake|bleeding|burn|burns|poison|poisoning|drowning|choking|fire|shock|cpr|heart|attack|faint|fainting|stroke|fracture|wound|injury|emergency|first\s*aid|hospital|ambulance|call|help)\b"
    ]
    en_matches = sum(1 for p in en_patterns if re.search(p, q))
    
    # Türkçe soru kalıpları kontrolü
    tr_matches = bool(re.search(r"\b(ne|nelerdir|nasıl|nedir|yapmalı|yapılır|nerede|kim|kaç|mı|mi|mu|mü|bir|ve|veya|için|olan|ile|ben|sen|o|biz|siz|onlar|kanama|deprem|yanık|zehirlenme|kalp|kriz|bayılma)\b", q))
    
    if en_matches >= 1 and not tr_matches:
        return "en"
        
    if client_lang == "en":
        return "en"
        
    return "tr"


def create_app(pipeline: RagPipeline | None = None) -> FastAPI:
    app = FastAPI(title="AfetRehberi RAG API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    state: dict[str, Any] = {"pipeline": pipeline}

    @app.on_event("startup")
    def _startup() -> None:
        if state["pipeline"] is None:
            pipe = RagPipeline()
            pipe.setup()
            state["pipeline"] = pipe

    @app.on_event("shutdown")
    def _shutdown() -> None:
        pipe = state.get("pipeline")
        if pipe is not None:
            pipe.close()

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/ingest")
    def trigger_ingest() -> dict[str, Any]:
        """Tek tıkla / sıfır RAM yüküyle mevcut model üzerinden verileri hızlıca yeniden indeksler."""
        pipe: RagPipeline = state["pipeline"]
        from rag.ingest import ingest_documents

        total = ingest_documents(runtime=pipe.runtime)
        if pipe._store is not None:
            pipe._chunks_cache = pipe._store.all_chunks()
            pipe._bm25_index.index_documents([c.content for c in pipe._chunks_cache])
        return {"status": "ok", "total_chunks": total}

    @app.post("/api/chat")
    def chat(body: ChatRequest) -> dict[str, Any]:
        query = (body.query or "").strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        effective_lang = detect_lang(query, body.lang)
        pipe: RagPipeline = state["pipeline"]
        result = pipe.ask(query, is_button=body.is_button, lang=effective_lang, history=body.history)

        sources = [
            {
                "source": c["source"],
                "content": c.get("excerpt") or "",
            }
            for c in result.citations
        ]

        return {
            "answer": result.answer,
            "sources": sources,
            "suggestedFollowUps": [],
            "detectedLang": effective_lang,
            "elapsedSeconds": round(result.elapsed_seconds, 3),
            "outOfScope": result.out_of_scope,
            "isFastFaq": result.is_fast_faq,
        }

    @app.post("/api/chat/stream")
    def chat_stream(body: ChatRequest):
        query = (body.query or "").strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        effective_lang = detect_lang(query, body.lang)
        pipe: RagPipeline = state["pipeline"]

        from fastapi.responses import StreamingResponse

        def event_generator():
            for chunk in pipe.ask_stream(
                query,
                is_button=body.is_button,
                lang=effective_lang,
                history=body.history,
            ):
                yield f"data: {chunk}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @app.post("/api/upload")
    async def upload_document(file: UploadFile = File(...)) -> dict[str, Any]:
        """Kullanıcının yüklediği .txt / .md dokümanını kaydeder ve bilgi tabanını yeniden başlatmadan anında günceller."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="Dosya adı bulunamadı.")

        allowed_extensions = {".txt", ".md"}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Yalnızca .txt veya .md dosyaları desteklenir. Gelen uzantı: {file_ext}",
            )

        from rag.config import DATA_DIR

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^\w\-.]", "_", file.filename)
        dest_path = DATA_DIR / safe_name

        content = await file.read()
        dest_path.write_bytes(content)

        pipe: RagPipeline = state["pipeline"]
        from rag.ingest import ingest_documents

        total = ingest_documents(data_dir=DATA_DIR, db_path=pipe.db_path, runtime=pipe.runtime)

        if pipe._store is not None:
            pipe._chunks_cache = pipe._store.all_chunks()
            pipe._bm25_index.index_documents([c.content for c in pipe._chunks_cache])

        return {
            "status": "ok",
            "filename": safe_name,
            "total_chunks": total,
            "message": f"'{safe_name}' başarıyla indekslendi. Toplam bilgi bloğu: {total}",
        }

    # Production: Vite build çıktısını sun (mobil UI)
    if DIST.exists() and (DIST / "index.html").exists():
        assets = DIST / "assets"
        if assets.exists():
            app.mount("/assets", StaticFiles(directory=str(assets)), name="assets")

        @app.get("/{full_path:path}")
        def spa(full_path: str = "") -> FileResponse:
            candidate = DIST / full_path
            if full_path and candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(DIST / "index.html")

    return app
