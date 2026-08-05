from sqlalchemy import text

from app.storage.postgres import engine
from app.storage.faiss_store import FAISSStore


def test_postgres():

    print("Testing PostgreSQL...")

    with engine.connect() as conn:

        result = conn.execute(text("SELECT version();"))

        print(result.fetchone())


def test_faiss():

    print("Testing FAISS...")

    store = FAISSStore()

    embedding = [0.0] * 1024

    store.add(
        embedding,
        {
            "document": "sample.pdf",
            "chunk": 0
        }
    )

    results = store.search(embedding)

    print(results)


if __name__ == "__main__":

    test_postgres()

    print()

    test_faiss()

    print()

    print("Storage layer working successfully.")