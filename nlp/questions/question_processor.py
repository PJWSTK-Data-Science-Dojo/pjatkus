import time
import nltk
from nltk.tokenize import sent_tokenize
import h5py
from db import QuestionsDB

# If not already downloaded, uncomment the next line to download the necessary NLTK data.
nltk.download("punkt_tab")


class QuestionProcessor:
    def __init__(self):
        self.db = QuestionsDB()

    def __enter__(self):
        self.db.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()
        pass

    def is_question(self, text: str):
        return text.endswith("?")

    def process(self, text: str, treshold=0.9):
        sentences = sent_tokenize(text)
        questions = [sentence for sentence in sentences if self.is_question(sentence)]
        embeddings = self.db.vectorize_questions(questions)
        answers = []
        for emb in embeddings:
            start = time.perf_counter()
            qid, sim = self.db.find_closest(emb)
            print(f"Time: {time.perf_counter() - start}")
            ds = self.db.get(qid)

            print(f"Question: {ds.attrs['question']}")
            print(f"Answer: {ds.attrs['answer']}")
            print(f"Similarity: {sim}")

            if sim < treshold:
                continue

            question = ds.attrs["question"]
            answer = ds.attrs["answer"]
            answers.append((question, answer))

        return answers


if __name__ == "__main__":
    with QuestionProcessor() as qp:
        text = "Kto stworzył PJATKUSIA?"
        answers = qp.process(text)
        for question, answer in answers:
            print(f"Question: {question}")
            print(f"Answer: {answer}")
            print()
