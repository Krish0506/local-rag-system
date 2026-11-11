import sys

from pathlib import Path

from app.config.settings import settings

from app.ingestion.pipeline import IngestionPipeline


def main():
    requested_directory = Path(sys.argv[1]) if len(sys.argv) > 1 else None

    if requested_directory is not None:
        directory = requested_directory
    else:
        directory = settings.raw_directory

    pipeline = IngestionPipeline()
    results = pipeline.ingest_directory(directory)

    if not results:
        print(f"No supported documents found in {directory}.")
        return

    for result in results:
        print(f"{result['filename']}: {result['status']}")


if __name__ == "__main__":
    main()
