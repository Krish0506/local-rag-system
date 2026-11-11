from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Root of the project
PROJECT_ROOT = Path(__file__).resolve().parents[2]


# Project version (displayed in the UI footer and System Settings page)
APP_VERSION = "1.2.0"


class Settings(BaseSettings):
    # -------------------------------
    # Environment
    # -------------------------------
    APP_ENV: Literal["development", "test", "production"] = "development"

    # -------------------------------
    # PostgreSQL
    # -------------------------------
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = Field(default=5432, ge=1, le=65535)
    POSTGRES_DB: str = "ragdb"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"

    # -------------------------------
    # Data Directories
    # -------------------------------
    RAW_DATA_DIR: str = "data/raw"
    PROCESSED_DATA_DIR: str = "data/processed"

    # -------------------------------
    # Vector Store
    # -------------------------------
    VECTOR_STORE_PATH: str = "data/vectors/demo.index"

    # -------------------------------
    # Chunking
    # -------------------------------
    CHUNK_SIZE: int = Field(default=1000, gt=0)
    CHUNK_OVERLAP: int = Field(default=200, ge=0)

    # -------------------------------
    # Retrieval
    # -------------------------------
    RETRIEVAL_TOP_K: int = Field(default=5, ge=1, le=20)
    MAX_CONTEXT_CHARS: int = Field(default=6000, gt=0)

    # -------------------------------
    # Ollama
    # -------------------------------
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "bge-m3"
    LLM_MODEL: str = "qwen3.5:4b"
    LLM_FALLBACK_MODEL: str = "mistral:7b-instruct"
    MAX_ANSWER_TOKENS: int = Field(default=512, gt=0)
    MODEL_CONTEXT_CHARS: int = Field(default=4096, gt=0)
    # Reasoning models (e.g. qwen3.5) otherwise spend the token budget on
    # thinking before answering; disabled by default for concise grounded answers.
    LLM_REASONING: bool = False

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @model_validator(mode="after")
    def validate_settings(self):
        if self.CHUNK_OVERLAP >= self.CHUNK_SIZE:
            raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")

        if self.APP_ENV == "production" and self.POSTGRES_PASSWORD in {"", "postgres"}:
            raise ValueError(
                "POSTGRES_PASSWORD must be changed when APP_ENV=production"
            )

        return self

    @property
    def raw_directory(self):
        return PROJECT_ROOT / self.RAW_DATA_DIR

    @property
    def processed_directory(self):
        return PROJECT_ROOT / self.PROCESSED_DATA_DIR

    @property
    def vector_store(self):
        return PROJECT_ROOT / self.VECTOR_STORE_PATH


settings = Settings()
