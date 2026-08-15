"""Gradio web arayüzü."""

from __future__ import annotations

from rag.pipeline import RagPipeline


def build_gradio_app(pipeline: RagPipeline):
    import gradio as gr

    def respond(message: str, history: list) -> tuple[str, list]:
        result = pipeline.ask(message)
        citation_lines = []
        for c in result.citations:
            citation_lines.append(
                f"- **{c['source']}** (benzerlik: {c['score']})\n  > {c['excerpt']}"
            )
        citations_md = "\n".join(citation_lines) if citation_lines else "_Kaynak bulunamadı._"
        reply = (
            f"{result.answer}\n\n---\n"
            f"**Getirilen kaynaklar**\n{citations_md}\n\n"
            f"_Süre: {result.elapsed_seconds:.2f} sn_"
        )
        history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": reply},
        ]
        return "", history

    with gr.Blocks(title="AfetRehberi RAG") as demo:
        gr.Markdown(
            "# AfetRehberi AI\n"
            "Yerel Foundry Local + SQLite RAG asistanı. "
            "İnternet gerektirmeden (modeller önbellekteyse) çalışır."
        )
        chatbot = gr.Chatbot(type="messages", height=480)
        msg = gr.Textbox(
            label="Sorunuz",
            placeholder="Örn: Deprem anında bina içinde ne yapmalıyım?",
        )
        clear = gr.Button("Temizle")
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        clear.click(lambda: ([], ""), outputs=[chatbot, msg])
        gr.Examples(
            examples=[
                "Deprem anında bina içinde ne yapmalıyım?",
                "Enkaz altındayken sesimi nasıl duyurmalıyım?",
                "Burun kanamasında ne yapılmalı?",
                "Bugün hava nasıl olacak?",  # kapsam dışı
            ],
            inputs=msg,
        )
    return demo
