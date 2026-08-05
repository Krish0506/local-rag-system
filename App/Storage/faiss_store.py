import os
import pickle

import faiss
import numpy as np


class FAISSStore:

    def __init__(self, dimension=1024):

        self.dimension = dimension

        self.index = faiss.IndexFlatL2(dimension)

        self.metadata = []

    def add(self, embedding, metadata):

        vector = np.array([embedding]).astype("float32")

        self.index.add(vector)

        self.metadata.append(metadata)

    def search(self, embedding, k=5):

        vector = np.array([embedding]).astype("float32")

        distances, indices = self.index.search(vector, k)

        results = []

        for idx in indices[0]:

            if idx != -1:

                results.append(self.metadata[idx])

        return results

    def save(self, path):

        os.makedirs(os.path.dirname(path), exist_ok=True)

        faiss.write_index(self.index, path)

        with open(path + ".meta", "wb") as f:

            pickle.dump(self.metadata, f)

    def load(self, path):

        self.index = faiss.read_index(path)

        with open(path + ".meta", "rb") as f:

            self.metadata = pickle.load(f)