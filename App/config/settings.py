from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    CHROMA_PATH: str
    CHROMA_COLLECTION: str

    class Config:
        env_file = ".env"


settings = Settings()