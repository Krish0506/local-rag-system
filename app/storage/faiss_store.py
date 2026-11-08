from pathlib import Path
import pickle

import faiss
import numpy as np

from app.config.settings import settings


class FAISSStore:

    def __init__(self, index_path=None, dimension: int = 1024):

        self.dimension = dimension

        configured_path = Path(index_path) if index_path else settings.vector_store

        self.index_path = Path(configured_path).resolve()

        self.index_directory = self.index_path.parent

        self.metadata_path = self.index_path.with_suffix(".pkl")

        self.index = None

        self.metadata = []

        self.load()

    def load(self):
        self.index_directory.mkdir(parents=True, exist_ok=True)

        if not self.index_path.exists():
            self.index = faiss.IndexFlatL2(self.dimension)
            return

        self.index = faiss.read_index(str(self.index_path))

        if self.index.d != self.dimension:
            raise RuntimeError(
                f"FAISS index dimension {self.index.d} does not match "
                f"configured dimension {self.dimension}"
            )

        if not self.metadata_path.exists():
            raise RuntimeError(
                "FAISS metadata file is missing for the existing index: "
                f"{self.metadata_path}"
            )

        with open(self.metadata_path, "rb") as file:
            self.metadata = pickle.load(file)

        if len(self.metadata) != self.index.ntotal:
            raise RuntimeError(
                "FAISS index and metadata are out of sync: "
                f"{self.index.ntotal} vectors, {len(self.metadata)} metadata entries"
            )

    def add(self, embedding, metadata):
        if len(embedding) != self.dimension:
            raise ValueError(
                f"Embedding dimension {len(embedding)} does not match "
                f"index dimension {self.dimension}"
            )

        vector = np.array([embedding], dtype=np.float32)

        self.index.add(vector)
        self.metadata.append(metadata)

    def save(self):
        faiss.write_index(self.index, str(self.index_path))

        with open(self.metadata_path, "wb") as file:
            pickle.dump(self.metadata, file)

    def search(self, embedding, top_k=5):
        if len(embedding) != self.dimension:
            raise ValueError(
                f"Embedding dimension {len(embedding)} does not match "
                f"index dimension {self.dimension}"
            )

        if self.index.ntotal == 0:
            return []

        vector = np.array([embedding], dtype=np.float32)

        distances, indices = self.index.search(vector, top_k)

        results = []

        for idx in indices[0]:
            if idx == -1:
                continue

            results.append(
                {
                    "chunk_id": self.metadata[idx]["chunk_id"],
                    "document_id": self.metadata[idx]["document_id"],
                    "content": self.metadata[idx]["content"],
                }
            )

        return results
