import h5py
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import hnswlib
import time


class QuestionsDB:
    def __init__(self, compression="gzip"):
        self.compression = compression
        self.questions_file: h5py.File = None
        self.questions_group: h5py.Group = None
        self.embedding_model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

    def get(self, qid) -> h5py.Dataset:
        return self.questions_group[qid]

    def init_db(self):
        self.questions_file = h5py.File("questions.hdf5", "a")
        self.questions_group = self.questions_file.require_group("questions")

    def vectorize_questions(self, questions):
        return self.embedding_model.encode(questions)

    def vectorize_question(self, question):
        embeddings = self.embedding_model.encode([question])
        return embeddings[0]

    def open(self):
        self.init_db()

    def close(self):
        self.questions_file.close()

    def __enter__(self):
        # Open the questions file in read mode
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Close the questions file
        self.close()

    def add_question(self, question, answer, qid=None):
        if qid is None:
            qid = str(len(self.questions_group))

        if qid in self.questions_group:
            return False

        # Add the question to the questions group
        embed = self.vectorize_question(question)
        # Add the question to the questions file

        ds = self.questions_group.create_dataset(
            qid, data=embed, compression=self.compression
        )

        ds.attrs["question"] = question
        ds.attrs["answer"] = answer

        return True

    def get_all_embeddings(self):
        embeddings = []
        keys = []
        for key in self.questions_group.keys():
            keys.append(key)
            embeddings.append(self.questions_group[key][()])
        embeddings = np.stack(embeddings)
        return keys, embeddings

    def find_closest(self, query_embedding, ef_construction=200, M=16, k=1):
        """ """
        # Load stored embeddings and keys.
        keys, embeddings = self.get_all_embeddings()
        num_elements, dim = embeddings.shape

        # Initialize hnswlib index with cosine metric.
        index = hnswlib.Index(space="cosine", dim=dim)
        index.init_index(
            max_elements=num_elements, ef_construction=ef_construction, M=M
        )
        index.add_items(embeddings)
        # Set ef for search (trade-off between speed and accuracy)
        index.set_ef(50)

        # Query for the nearest neighbor.
        # hnswlib expects query_embedding as a 2D array.
        labels, distances = index.knn_query(np.array([query_embedding]), k=k)

        # For cosine metric, the distance is (1 - cosine similarity).
        closest_index = labels[0][0]
        similarity = 1 - distances[0][0]

        return keys[closest_index], similarity

    def get_similarity(self, emb1, emb2):
        """Calculate the cosine similarity between two embeddings."""
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)

        # Avoid division by zero
        if norm1 == 0 or norm2 == 0:
            return 0.0

        # Cosine similarity: dot / (norm1 * norm2)
        similarity = dot_product / (norm1 * norm2)
        return similarity


if "__main__" == __name__:
    with QuestionsDB() as db:
        base_question = "Jak się studiuje na tej uczelni?"
        similar_question = [
            "Jak się na tej uczelni studiuje?",
            "How is studying at this university?",
            "How is studying at this college?",
            "Co lubisz na tej uczelni?",
            "Długo już studiujesz na tej uczelni?",
            "Jakie są kierunki studiów na tej uczelni?",
            "Czy na tej uczelni jest trudno?",
            "Czy na tej uczelni jest łatwo?",
            "Czy na tej uczelni jest dużo nauki?",
            "Czy na tej uczelni jest dużo zabawy?",
            "Czy na tej uczelni jest dużo imprez?",
            "Ile się płaci za studia na tej uczelni?",
            "Czy na tej uczelni są stypendia?",
        ]

        for q in similar_question:
            start = time.perf_counter()
            print(
                f"Similarity between '{base_question}' and '{q}':",
                db.get_similarity(
                    db.vectorize_question(base_question), db.vectorize_question(q)
                ),
            )
            print(f"Time elapsed: {time.perf_counter() - start:.4f} seconds")
