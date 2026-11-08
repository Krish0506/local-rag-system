import importlib

import pytest


MODULES = [
    "app.config.settings",
    "app.health",
    "app.ingestion.chunker",
    "app.ingestion.cleaner",
    "app.ingestion.loaders",
    "app.ingestion.parser",
    "app.ingestion.pipeline",
    "app.llm.chat",
    "app.llm.embeddings",
    "app.orchestration.ingest_orchestration",
    "app.retrieval.generator",
    "app.retrieval.prompts",
    "app.retrieval.retriever",
    "app.storage.faiss_store",
    "app.storage.models",
    "app.storage.postgres",
    "app.storage.repository",
]


@pytest.mark.parametrize("module_name", MODULES)
def test_application_modules_import(module_name):
    assert importlib.import_module(module_name) is not None
