import json
import os
from pathlib import Path

json_data_dir = Path("data")

questions = []
for file in json_data_dir.glob("*.json"):
    print(file)

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        qs = data["questions"]
        questions.extend(qs)


print(f"Total questions: {len(questions)}")
with open("questions.json", "w", encoding="utf-8") as f:
    json.dump({"questions": questions}, f, ensure_ascii=False, indent=4)
