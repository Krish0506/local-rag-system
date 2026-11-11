import functools
import json
import time
import urllib.request
from urllib.error import URLError

from langchain_ollama import ChatOllama

from app.config.settings import settings


def _request_models(base_url: str, timeout: float = 2.0) -> list[str]:
    try:
        url = f"{base_url.rstrip('/')}/api/tags"
        with urllib.request.urlopen(url, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return [item.get("name") for item in payload.get("models", []) if item.get("name")]
    except (URLError, OSError, ValueError, json.JSONDecodeError):
        return []


@functools.lru_cache(maxsize=1)
def resolve_model() -> str:
    """Return the configured model when it is available, else the fallback model."""
    models = _request_models(settings.OLLAMA_BASE_URL)

    if settings.LLM_MODEL in models:
        return settings.LLM_MODEL

    if settings.LLM_FALLBACK_MODEL in models:
        return settings.LLM_FALLBACK_MODEL

    return settings.LLM_MODEL


class ChatService:

    def __init__(self):
        self.model_name = resolve_model()
        self._build_llm(self.model_name)

    def _build_llm(self, model_name: str):
        self.llm = ChatOllama(
            model=model_name,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0,
            num_predict=settings.MAX_ANSWER_TOKENS,
            num_ctx=settings.MODEL_CONTEXT_CHARS,
            reasoning=settings.LLM_REASONING,
        )

    @staticmethod
    def _extract_content(response) -> str:
        content = response.content

        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and isinstance(block.get("text"), str):
                    parts.append(block["text"])
                elif isinstance(block, str):
                    parts.append(block)
            content = "".join(parts)

        return content.strip()

    def ask(self, prompt: str):
        try:
            response = self.llm.invoke(prompt)
        except Exception:
            fallback = settings.LLM_FALLBACK_MODEL
            if not fallback or self.model_name == fallback:
                raise

            self.model_name = fallback
            self._build_llm(self.model_name)
            response = self.llm.invoke(prompt)

        content = self._extract_content(response)

        if not content:
            raise RuntimeError("The chat model returned an empty response.")

        return content

    def warm_up(self) -> float:
        """Load the model and return the warm-up time in seconds."""
        start = time.time()
        self.llm.invoke("Reply with exactly: OK")
        return round(time.time() - start, 2)
