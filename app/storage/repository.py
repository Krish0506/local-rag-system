from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.storage.models import Document
from app.storage.models import Chunk


class Repository:

    def __init__(self, session: Session):
        self.session = session

    # ------------------------
    # Documents
    # ------------------------

    def document_exists(self, filename: str) -> bool:
        statement = select(Document.id).where(Document.filename == filename)
        return self.session.scalar(statement) is not None

    def list_documents_with_chunk_counts(self) -> list[dict]:
        """Return all documents with their chunk counts, newest first."""
        statement = (
            select(
                Document.id,
                Document.filename,
                Document.document_type,
                Document.source,
                Document.created_at,
                func.count(Chunk.id),
            )
            .outerjoin(Chunk, Chunk.document_id == Document.id)
            .group_by(Document.id)
            .order_by(Document.created_at.desc(), Document.id.desc())
        )

        rows = self.session.execute(statement).all()

        return [
            {
                "id": row[0],
                "filename": row[1],
                "document_type": row[2],
                "source": row[3],
                "created_at": row[4],
                "chunk_count": int(row[5] or 0),
            }
            for row in rows
        ]

    # ------------------------
    # Documents
    # ------------------------

    def save_document(
        self,
        filename: str,
        document_type: str,
        source: str
    ) -> Document:

        document = Document(
            filename=filename,
            document_type=document_type,
            source=source
        )

        self.session.add(document)

        self.session.commit()

        self.session.refresh(document)

        return document

    # ------------------------
    # Chunks
    # ------------------------

    def save_chunk(
        self,
        document_id: int,
        chunk_index: int,
        text: str,
        embedding_model: str
    ) -> Chunk:

        chunk = Chunk(
            document_id=document_id,
            chunk_index=chunk_index,
            text=text,
            embedding_model=embedding_model
        )

        self.session.add(chunk)

        self.session.commit()

        self.session.refresh(chunk)

        return chunk