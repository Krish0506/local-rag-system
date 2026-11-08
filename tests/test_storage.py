import os

import pytest

from app.storage.faiss_store import FAISSStore
from app.storage.postgres import check_connection


def test_faiss_store_round_trip(tmp_path):
    index_path = tmp_path / "faiss.index"

    store = FAISSStore(index_path=index_path, dimension=4)
    store.add(
        [1.0, 0.0, 0.0, 0.0],
        {
            "chunk_id": 1,
            "document_id": 1,
            "content": "sample",
        },
    )
    store.save()

    reloaded = FAISSStore(index_path=index_path, dimension=4)
    results = reloaded.search([1.0, 0.0, 0.0, 0.0], top_k=1)

    assert results[0]["chunk_id"] == 1
    assert results[0]["content"] == "sample"


def test_faiss_store_rejects_wrong_dimension(tmp_path):
    store = FAISSStore(index_path=tmp_path / "faiss.index", dimension=4)

    with pytest.raises(ValueError):
        store.add([1.0, 0.0], {})


def test_faiss_store_detects_missing_metadata(tmp_path):
    index_path = tmp_path / "faiss.index"

    store = FAISSStore(index_path=index_path, dimension=4)
    store.add(
        [1.0, 0.0, 0.0, 0.0],
        {
            "chunk_id": 1,
            "document_id": 1,
            "content": "sample",
        },
    )
    store.save()
    index_path.with_suffix(".pkl").unlink()

    with pytest.raises(RuntimeError, match="metadata file is missing"):
        FAISSStore(index_path=index_path, dimension=4)


@pytest.mark.integration
def test_database_connection():
    if os.getenv("RUN_DB_TESTS") != "1":
        pytest.skip("Set RUN_DB_TESTS=1 to run database integration tests")

    assert check_connection() is True
