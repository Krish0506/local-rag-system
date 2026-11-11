from urllib.error import URLError
from urllib.request import urlopen

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
