from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import func


class Base(DeclarativeBase):
    pass


class Document(Base):

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)

    filename: Mapped[str]

    document_type: Mapped[str]

    source: Mapped[str]

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now()
    )


class Chunk(Base):

    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id")
    )

    chunk_index: Mapped[int]

    text: Mapped[str]

    embedding_model: Mapped[str]

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now()
    )