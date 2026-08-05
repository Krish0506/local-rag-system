from pathlib import Path

from app.config.settings import settings
from app.ingestion.parser import parse_document
from app.ingestion.cleaner import clean_text
from app.ingestion.chunker import chunk_text

from app.llm.embeddings import EmbeddingService

from app.storage.faiss_store import FAISSStore

from app.storage.postgres import SessionLocal

from app.storage.repository import Repository


class IngestionPipeline:

    def __init__(self):

        self.embedding = EmbeddingService()

        self.vector_store = FAISSStore()

    def ingest(

        self,

        file_path

    ):

        session = SessionLocal()

        repository = Repository(session)

        file = Path(file_path)

        text = parse_document(file)

        cleaned = clean_text(text)

        chunks = chunk_text(cleaned)

        document = repository.save_document(

            filename=file.name,

            document_type=file.suffix,

            source=str(file)

        )

        for index, chunk in enumerate(chunks):

            chunk_row = repository.save_chunk(

               document_id = document.id,

                chunk_index = index,

                text=chunk,

                embedding_model=settings.EMBEDDING_MODEL

            )

            embedding = self.embedding.embed(

                chunk

            )

            self.vector_store.add(

                embedding,

                {

                    "chunk_id": chunk_row.id,

                    "document_id": document.id,

                    "content": chunk

                }

            )

        self.vector_store.save()

        session.close()

        print(

            f"{file.name} ingested successfully."
        )