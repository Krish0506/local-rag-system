from pathlib import Path

from app.config.settings import settings

from app.ingestion.pipeline import IngestionPipeline


class IngestOrchestrator:

    def __init__(self):

        self.pipeline = IngestionPipeline()

    def run(self):

        files = list(

            Path(

                settings.raw_directory

            ).glob("*")
        )

        print(

            f"Found {len(files)} files."
        )

        for file in files:

            print(

                f"Ingesting {file.name}"
            )

            self.pipeline.ingest(file)

        print(

            "\nFinished."
        )


if __name__ == "__main__":

    IngestOrchestrator().run()