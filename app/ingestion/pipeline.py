from pathlib import Path

from app.config.settings import settings
from app.ingestion.parser import SUPPORTED_EXTENSIONS, parse_document
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

    def ingest(self, file_path) -> bool:
        session = SessionLocal()

        try:
            repository = Repository(session)

            file = Path(file_path)

            if repository.document_exists(file.name):
                print(f"{file.name} already ingested; skipped.")
                return False

            text = parse_document(file)

            cleaned = clean_text(text)

            chunks = chunk_text(cleaned)

            document = repository.save_document(
                filename=file.name,
                document_type=file.suffix,
                source=str(file),
            )

            for index, chunk in enumerate(chunks):
                chunk_row = repository.save_chunk(
                    document_id=document.id,
                    chunk_index=index,
                    text=chunk,
                    embedding_model=settings.EMBEDDING_MODEL,
                )

                embedding = self.embedding.embed(chunk)

                self.vector_store.add(
                    embedding,
                    {
                        "chunk_id": chunk_row.id,
                        "document_id": document.id,
                        "content": chunk,
                        "filename": file.name,
                        "location": f"part {index + 1}",
                    },
                )

            self.vector_store.save()
        finally:
            session.close()

        print(f"{file.name} ingested successfully.")
        return True

    def ingest_directory(self, directory) -> list[dict]:
        directory = Path(directory)

        files = sorted(
            path
            for path in directory.glob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )

        results = []

        for file in files:
            try:
                ingested = self.ingest(file)
                results.append(
                    {
                        "filename": file.name,
                        "status": "ingested" if ingested else "skipped",
                        "detail": "",
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "filename": file.name,
                        "status": "error",
                        "detail": str(exc),
                    }
                )

        return results
