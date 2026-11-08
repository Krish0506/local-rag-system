from pathlib import Path

from app.config.settings import settings
from app.ingestion.parser import SUPPORTED_EXTENSIONS
from app.ingestion.pipeline import IngestionPipeline


class IngestOrchestrator:

    def __init__(self):

        self.pipeline = IngestionPipeline()

    def run(self):
        files = sorted(
            path
            for path in Path(settings.raw_directory).glob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )

        print(f"Found {len(files)} files.")

        for file in files:
            print(f"Ingesting {file.name}")

            self.pipeline.ingest(file)

        print("\nFinished.")


if __name__ == "__main__":
    IngestOrchestrator().run()
