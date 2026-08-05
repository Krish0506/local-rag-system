from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Root of the project
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # -------------------------------
    # PostgreSQL
    # -------------------------------
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # -------------------------------
    # Data Directories
    # -------------------------------
    RAW_DATA_DIR: str = "data/raw"
    PROCESSED_DATA_DIR: str = "data/processed"

    # -------------------------------
    # Vector Store
    # -------------------------------
    VECTOR_STORE_PATH: str = "data/vectors/faiss.index"

    # -------------------------------
    # Chunking
    # -------------------------------
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    # -------------------------------
    # Ollama
    # -------------------------------
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "bge-m3"
    LLM_MODEL: str = "mistral:7b-instruct"

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