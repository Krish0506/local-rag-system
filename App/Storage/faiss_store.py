from pathlib import Path
import pickle

import faiss
import numpy as np

from app.config.settings import settings


class FAISSStore:

    def __init__(self):

        self.dimension = 1024

        self.index_path = Path(
            settings.VECTOR_STORE_PATH
        ).resolve()

        self.index_directory = self.index_path.parent

        self.metadata_path = self.index_path.with_suffix(".pkl")

        self.index = None

        self.metadata = []

        self.load()

    def load(self):

        self.index_directory.mkdir(

            parents=True,

            exist_ok=True

        )

        if self.index_path.exists():

            self.index = faiss.read_index(

                str(self.index_path)

            )

            if self.metadata_path.exists():

                with open(

                    self.metadata_path,

                    "rb"

                ) as file:

                    self.metadata = pickle.load(file)

        else:

            self.index = faiss.IndexFlatL2(

                self.dimension

            )

    def add(

        self,

        embedding,

        metadata

    ):

        vector = np.array(

            [embedding],

            dtype=np.float32

        )

        self.index.add(vector)

        self.metadata.append(metadata)

    def save(self):

        faiss.write_index(

            self.index,

            str(self.index_path)

        )

        with open(

            self.metadata_path,

            "wb"

        ) as file:

            pickle.dump(

                self.metadata,

                file

            )

    def search(

        self,

        embedding,

        top_k=5

    ):

        if self.index.ntotal == 0:

            return []

        vector = np.array(

            [embedding],

            dtype=np.float32

        )

        distances, indices = self.index.search(

            vector,

            top_k

        )

        results = []

        for idx in indices[0]:

            if idx == -1:

                continue

            results.append(

                {

                    "chunk_id":

                        self.metadata[idx]["chunk_id"],

                    "document_id":

                        self.metadata[idx]["document_id"],

                    "content":

                        self.metadata[idx]["content"]

                }

            )

        return results