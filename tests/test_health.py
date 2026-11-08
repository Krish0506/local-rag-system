from urllib.error import URLError

import app.health as health


class FakeResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def test_ollama_health_returns_true_when_endpoint_responds(monkeypatch):
    monkeypatch.setattr(health, "urlopen", lambda *args, **kwargs: FakeResponse())

    assert health.ollama_health() is True


def test_ollama_health_returns_false_when_endpoint_is_unreachable(monkeypatch):
    def raise_error(*args, **kwargs):
        raise URLError("unreachable")

    monkeypatch.setattr(health, "urlopen", raise_error)

    assert health.ollama_health() is False


def test_database_health_delegates_to_connection_check(monkeypatch):
    monkeypatch.setattr(health, "check_connection", lambda: True)

    assert health.database_health() is True
