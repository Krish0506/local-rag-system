from urllib.error import URLError
from urllib.request import urlopen

from app.config.settings import settings
from app.storage.postgres import check_connection


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
