from app.llm.embeddings import EmbeddingService
from app.storage.faiss_store import FAISSStore


class Retriever:

    def __init__(self):

        self.embedding_service = EmbeddingService()

        self.vector_store = FAISSStore()

    def retrieve(

        self,

        question,

        top_k=5

    ):

        question_embedding = self.embedding_service.embed(

            question

        )

        results = self.vector_store.search(

            question_embedding,

            top_k

        )

        return results