from pathlib import Path

from app.ingestion.parser import parse_document
from app.ingestion.cleaner import clean_text
from app.ingestion.chunker import chunk_text


def process_document(path):

    print("Loading...")

    text = parse_document(path)

    print("Cleaning...")

    cleaned = clean_text(text)

    print("Chunking...")

    chunks = chunk_text(cleaned)

    print(f"Generated {len(chunks)} chunks.")

    return {

        "filename": Path(path).name,

        "chunks": chunks
    }