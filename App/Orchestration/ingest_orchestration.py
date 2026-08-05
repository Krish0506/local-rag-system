from pathlib import Path

from app.config.settings import settings
from app.ingestion.pipeline import process_document


def ingest_all_documents():

    raw_folder = settings.raw_directory

    files = list(Path(raw_folder).glob("*"))

    print(f"\nFound {len(files)} files.\n")

    for file in files:

        print("=" * 50)

        print("Processing:", file.name)

        process_document(file)

    print("\nAll documents processed.")