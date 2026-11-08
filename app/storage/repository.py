from sqlalchemy.orm import Session

from app.storage.models import Document
from app.storage.models import Chunk


class Repository:

    def __init__(self, session: Session):
        self.session = session

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