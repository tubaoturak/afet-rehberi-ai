"""Microsoft Foundry Local runtime sarmalayıcısı."""

from __future__ import annotations

from typing import Any, Sequence

from rag.config import (
    ALLOW_MODEL_DOWNLOAD,
    APP_NAME,
    CHAT_MODEL,
    EMBEDDING_MODEL,
    MAX_TOKENS,
    MODEL_CACHE_DIR,
    TEMPERATURE,
)


class FoundryRuntimeError(RuntimeError):
    """Foundry Local ile ilgili çalıştırma hataları."""


class FoundryRuntime:
    """
    Yerel embedding + chat modellerini yönetir.

    Modeller bir kez indirilip önbelleğe alındıktan sonra tamamen offline çalışır.
    """

    def __init__(
        self,
        chat_model_alias: str = CHAT_MODEL,
        embedding_model_alias: str = EMBEDDING_MODEL,
        allow_download: bool = ALLOW_MODEL_DOWNLOAD,
    ) -> None:
        self.chat_model_alias = chat_model_alias
        self.embedding_model_alias = embedding_model_alias
        self.allow_download = allow_download
        self._manager: Any = None
        self._embedding_model: Any = None
        self._chat_model: Any = None
        self._embedding_client: Any = None
        self._chat_client: Any = None

    def initialize(self) -> None:
        try:
            from foundry_local_sdk import Configuration, FoundryLocalManager
        except ImportError as exc:
            raise FoundryRuntimeError(
                "foundry-local-sdk yüklü değil. "
                "macOS/Linux: pip install foundry-local-sdk\n"
                "Windows: pip install foundry-local-sdk-winml"
            ) from exc

        kwargs: dict[str, Any] = {"app_name": APP_NAME}
        if MODEL_CACHE_DIR is not None:
            MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
            kwargs["model_cache_dir"] = str(MODEL_CACHE_DIR)
        try:
            config = Configuration(**kwargs)
        except TypeError:
            # Eski SDK sürümleri model_cache_dir kabul etmeyebilir
            config = Configuration(app_name=APP_NAME)
        FoundryLocalManager.initialize(config)
        self._manager = FoundryLocalManager.instance

    def _get_model(self, alias: str) -> Any:
        assert self._manager is not None
        model = self._manager.catalog.get_model(alias)
        if model is None:
            raise FoundryRuntimeError(
                f"Model bulunamadı: '{alias}'. "
                "Katalogda mevcut alias'ları kontrol edin (ör. phi-3.5-mini, qwen3-embedding-0.6b)."
            )
        return model

    def _ensure_cached(self, model: Any, label: str) -> None:
        is_cached = bool(getattr(model, "is_cached", False))
        if is_cached:
            return
        if not self.allow_download:
            raise FoundryRuntimeError(
                f"{label} önbellekte yok ve AFET_ALLOW_MODEL_DOWNLOAD=0. "
                "Önce modelleri indirin veya indirmeye izin verin."
            )
        print(f"[*] {label} indiriliyor...")
        model.download(
            lambda p: print(f"\r    {label}: {p:.1f}%", end="", flush=True)
        )
        print()

    def load_models(self) -> None:
        if self._manager is None:
            self.initialize()

        self._embedding_model = self._get_model(self.embedding_model_alias)
        self._ensure_cached(self._embedding_model, f"Embedding ({self.embedding_model_alias})")
        self._embedding_model.load()
        self._embedding_client = self._embedding_model.get_embedding_client()

        self._chat_model = self._get_model(self.chat_model_alias)
        self._ensure_cached(self._chat_model, f"Chat ({self.chat_model_alias})")
        self._chat_model.load()
        self._chat_client = self._chat_model.get_chat_client()
        if hasattr(self._chat_client, "settings") and self._chat_client.settings is not None:
            try:
                self._chat_client.settings.max_tokens = MAX_TOKENS
                self._chat_client.settings.temperature = TEMPERATURE
            except Exception:
                pass

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if self._embedding_client is None:
            raise FoundryRuntimeError("Embedding modeli yüklü değil. load_models() çağırın.")
        if not texts:
            return []
        # API: generate_embeddings (batch) veya generate_embedding (tekil)
        if len(texts) == 1 and hasattr(self._embedding_client, "generate_embedding"):
            response = self._embedding_client.generate_embedding(texts[0])
            return [list(response.data[0].embedding)]
        response = self._embedding_client.generate_embeddings(list(texts))
        return [list(item.embedding) for item in response.data]

    def embed_query(self, query: str) -> list[float]:
        vectors = self.embed_texts([query])
        return vectors[0]

    def chat(self, messages: list[dict[str, str]]) -> str:
        if self._chat_client is None:
            raise FoundryRuntimeError("Chat modeli yüklü değil. load_models() çağırın.")

        # Streaming tercih edilir; yoksa non-stream complete_chat
        if hasattr(self._chat_client, "complete_streaming_chat"):
            parts: list[str] = []
            for chunk in self._chat_client.complete_streaming_chat(messages):
                try:
                    content = chunk.choices[0].delta.content
                except (AttributeError, IndexError):
                    content = None
                if content:
                    parts.append(content)
            return "".join(parts).strip()

        if hasattr(self._chat_client, "complete_chat"):
            response = self._chat_client.complete_chat(messages)
            try:
                return str(response.choices[0].message.content).strip()
            except (AttributeError, IndexError) as exc:
                raise FoundryRuntimeError("Chat yanıtı parse edilemedi.") from exc

        raise FoundryRuntimeError("Chat client API'si desteklenmiyor.")

    def chat_stream(self, messages: list[dict[str, str]]):
        """Streaming token üreticisi (SSE için)."""
        if self._chat_client is None:
            raise FoundryRuntimeError("Chat modeli yüklü değil. load_models() çağırın.")

        if hasattr(self._chat_client, "complete_streaming_chat"):
            for chunk in self._chat_client.complete_streaming_chat(messages):
                try:
                    content = chunk.choices[0].delta.content
                except (AttributeError, IndexError):
                    content = None
                if content:
                    yield content
            return

        if hasattr(self._chat_client, "complete_chat"):
            response = self._chat_client.complete_chat(messages)
            try:
                yield str(response.choices[0].message.content).strip()
            except (AttributeError, IndexError) as exc:
                raise FoundryRuntimeError("Chat yanıtı parse edilemedi.") from exc
            return

        raise FoundryRuntimeError("Chat client API'si desteklenmiyor.")

    def unload(self) -> None:
        for model in (self._embedding_model, self._chat_model):
            if model is not None and hasattr(model, "unload"):
                try:
                    model.unload()
                except Exception:
                    pass
        self._embedding_client = None
        self._chat_client = None
