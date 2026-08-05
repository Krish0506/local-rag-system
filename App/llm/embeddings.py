from langchain_ollama import OllamaEmbeddings

from app.config.settings import settings


class EmbeddingService:

    def __init__(self):

        self.model = OllamaEmbeddings(

            model=settings.EMBEDDING_MODEL,

            base_url=settings.OLLAMA_BASE_URL

        )

    def embed(self, text: str):

        return self.model.embed_query(text)

    def embed_documents(self, documents):

        return self.model.embed_documents(documents)