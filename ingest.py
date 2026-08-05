from app.orchestration.ingest_orchestration import IngestOrchestrator


def main():

    orchestrator = IngestOrchestrator()

    orchestrator.run()


if __name__ == "__main__":

    main()