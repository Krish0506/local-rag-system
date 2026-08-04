from sqlalchemy import text

from app.storage.postgres import engine
from app.storage.chroma_store import get_collection


def test_postgres():

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT version();")
        )

        print(result.fetchone())


def test_chroma():

    collection = get_collection()

    print("Collection Name:", collection.name)


if __name__ == "__main__":

    print("Testing PostgreSQL...")

    test_postgres()

    print()

    print("Testing ChromaDB...")

    test_chroma()

    print()

    print("Storage layer is working!")