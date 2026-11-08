import pytest
from pydantic import ValidationError

from app.config.settings import Settings


def make_settings(**overrides):
    values = {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": 5432,
        "POSTGRES_DB": "ragdb",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "postgres",
        "CHUNK_SIZE": 1000,
        "CHUNK_OVERLAP": 200,
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_default_configuration_loads():
    settings = make_settings()

    assert settings.APP_ENV == "development"
    assert settings.POSTGRES_PORT == 5432
    assert settings.CHUNK_SIZE == 1000
    assert settings.CHUNK_OVERLAP == 200
    assert settings.EMBEDDING_MODEL == "bge-m3"


def test_environment_variables_override_defaults(monkeypatch):
    monkeypatch.setenv("CHUNK_SIZE", "512")

    settings = Settings(_env_file=None)

    assert settings.CHUNK_SIZE == 512


def test_chunk_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ValidationError):
        make_settings(CHUNK_SIZE=100, CHUNK_OVERLAP=100)


def test_invalid_postgres_port_is_rejected():
    with pytest.raises(ValidationError):
        make_settings(POSTGRES_PORT=70000)


def test_production_rejects_default_password():
    with pytest.raises(ValidationError):
        make_settings(APP_ENV="production")
