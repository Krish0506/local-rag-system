from app.config.settings import settings
from app.retrieval.generator import Generator
from app.retrieval.retriever import Retriever


def test_retriever_initializes_with_empty_vector_store(tmp_path, monkeypatch):
    monkeypatch.setattr(
        settings,
        "VECTOR_STORE_PATH",
        str(tmp_path / "faiss.index"),
    )

    retriever = Retriever()

    assert retriever.embedding_service.model is not None
    assert retriever.vector_store.index.ntotal == 0


def test_generator_initializes_ollama_client():
    generator = Generator()

    assert generator.chat.llm is not None
