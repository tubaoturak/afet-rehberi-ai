#!/usr/bin/env python3
"""
AfetRehberi — Foundry Local Offline RAG

Aktif arayüz: mobil React (telefon görünümü)
Backend: Python Foundry Local RAG

Komutlar:
  python main.py ingest
  python main.py serve          # API (+ build varsa mobil UI)  :8000
  python main.py ask "soru"
  python main.py chat
  python main.py ui-gradio      # isteğe bağlı Gradio
"""

from __future__ import annotations

import argparse
import sys

from rag.config import CHAT_MODEL, DATA_DIR, DB_PATH, EMBEDDING_MODEL
from rag.ingest import ingest_documents
from rag.pipeline import RagPipeline


def cmd_ingest(_: argparse.Namespace) -> int:
    print(f"[*] Veri: {DATA_DIR}")
    print(f"[*] DB  : {DB_PATH}")
    print(f"[*] Embedding modeli: {EMBEDDING_MODEL}")
    n = ingest_documents()
    print(f"[✓] {n} chunk SQLite'a yazıldı → {DB_PATH}")
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    pipeline = RagPipeline()
    try:
        result = pipeline.ask(args.question)
        print(result.answer)
        if result.citations:
            print("\n--- Kaynaklar ---")
            for c in result.citations:
                print(f"* {c['source']} ({c['score']})")
        print(f"\n(Süre: {result.elapsed_seconds:.2f} sn)")
        return 0
    finally:
        pipeline.close()


def cmd_chat(_: argparse.Namespace) -> int:
    print(f"AfetRehberi CLI | chat={CHAT_MODEL} | embed={EMBEDDING_MODEL}")
    print("Çıkmak için: quit / exit\n")
    pipeline = RagPipeline()
    try:
        pipeline.setup()
        while True:
            try:
                q = input("Soru> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not q or q.lower() in {"quit", "exit", "q"}:
                break
            result = pipeline.ask(q)
            print(f"\n{result.answer}\n")
            if result.citations:
                print("Kaynaklar:", ", ".join(c["source"] for c in result.citations))
            print(f"(Süre: {result.elapsed_seconds:.2f} sn)\n")
    finally:
        pipeline.close()
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    from rag.api import create_app

    print("[*] Mobil UI API hazırlanıyor (Foundry Local RAG)...")
    print(f"[*] http://{args.host}:{args.port}")
    print("[*] Geliştirme: ayrı terminalde `npm run dev` → http://localhost:3000")
    app = create_app()
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    return 0


def cmd_ui_gradio(args: argparse.Namespace) -> int:
    from rag.ui_gradio import build_gradio_app

    pipeline = RagPipeline()
    pipeline.setup()
    demo = build_gradio_app(pipeline)
    demo.launch(server_name=args.host, server_port=args.port, share=False)
    pipeline.close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AfetRehberi — Microsoft Foundry Local Offline RAG"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="Dokümanları vektörleştirip SQLite'a yazar")
    p_ingest.set_defaults(func=cmd_ingest)

    p_ask = sub.add_parser("ask", help="Tek soru sor")
    p_ask.add_argument("question", type=str)
    p_ask.set_defaults(func=cmd_ask)

    p_chat = sub.add_parser("chat", help="Etkileşimli CLI")
    p_chat.set_defaults(func=cmd_chat)

    p_serve = sub.add_parser(
        "serve",
        help="API sunucusu (mobil React /api/chat). Build varsa UI da :8000'de",
    )
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)
    p_serve.set_defaults(func=cmd_serve)

    p_ui = sub.add_parser("ui-gradio", help="İsteğe bağlı Gradio arayüzü")
    p_ui.add_argument("--host", default="127.0.0.1")
    p_ui.add_argument("--port", type=int, default=7860)
    p_ui.set_defaults(func=cmd_ui_gradio)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
