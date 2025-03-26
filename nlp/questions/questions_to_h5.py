import json
from db import QuestionsDB

QUESTIONS_FILE = "questions.json"
QUESTIONS_DB = "questions.h5"


with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)
    questions = data["questions"]


with QuestionsDB() as db:
    for q in questions:
        db.add_question(q["pytanie"], q["odpowiedz"])
