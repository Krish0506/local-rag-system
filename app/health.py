from urllib.error import URLError
from urllib.request import urlopen
import json

from sqlalchemy import func, select

from app.config.settings import settings
from app.storage.models import Chunk, Document
from app.storage.postgres import check_connection, engine


def database_health() -> bool:
    """Return True when PostgreSQL is reachable."""
    return check_connection()


def ollama_health(timeout: float = 2.0) -> bool:
    """Return True when the configured Ollama endpoint responds."""
    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags"

    try:
        with urlopen(url, timeout=timeout) as response:
            return 200 <= response.status < 300
    except (URLError, OSError, ValueError):
        return False


def knowledge_base_counts() -> tuple[int, int]:
    """Return document and chunk counts from PostgreSQL."""
    with engine.connect() as connection:
        documents = connection.scalar(select(func.count()).select_from(Document)) or 0
        chunks = connection.scalar(select(func.count()).select_from(Chunk)) or 0

    return int(documents), int(chunks)


def loaded_models(timeout: float = 2.0) -> list[str]:
    """Return the model names currently loaded in Ollama memory."""
    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/ps"

    try:
        with urlopen(url, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, OSError, ValueError):
        return []

    names = []
    for item in payload.get("models", []):
        name = item.get("Model") or item.get("Name") or item.get("model") or item.get("name")
        if not name:
            continue
        names.append(str(name).split("@", 1)[0])

    return names


def model_ready() -> bool:
    """Return True when the resolved chat model is loaded in Ollama memory."""
    active = f"{settings.LLM_MODEL}".split("@", 1)[0]
    fallback = f"{settings.LLM_FALLBACK_MODEL}".split("@", 1)[0]

    for name in loaded_models():
        if name == active or name == fallback:
            return True

    return False
