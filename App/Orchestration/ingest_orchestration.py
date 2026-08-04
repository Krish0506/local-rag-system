from app.ingestion.parser import parse_document
from app.ingestion.chunker import chunk_text


def ingest_document(path: str):

    text = parse_document(path)

    chunks = chunk_text(text)

    for index, chunk in enumerate(chunks):

        print(f"Chunk {index}")

        # Generate embedding
        # Store metadata
        # Store vector