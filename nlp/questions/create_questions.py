QUESTION_CREATOR_PROMPOT = """You are an assistant tasked with creating questions for a university robot named PJATKUŚ. Your objective is to generate questions that could be asked to PJATKUŚ. You will be provided the number of questions (default: 10) to create and a topic or scenario to which the questions should pertain. While creating questions, aim to direct them towards PJATKUŚ as a person but avoid overtly using his name unless necessary. Each question should be presented as a JSON object with the following fields:

- **pytanie:** The text of the original question. 
- **tagi:** An array of tags that describe the question (maximum of 5 tags).
- **alternatywy:** An array containing up to 5 optional variations of the question:
  1. A variation with changed syntax.
  2. A variation using synonyms.
  3. A combination of variations 1 and 2.
  4. A question as closely related in meaning to the original as possible, but distinct from it.
  5. An optional variation that is distinct but meaningful.
  
  If creating a specific alternative is not feasible, then ignore or omit the alternative.

- **odpowiedz:** The answer the university robot should give to the question - specific but not overly formal. If the question is about PJATKUŚ, remember to reference PJATKUŚ's creators (the student clubs RoboLab and Data Science Club at PJATK) to acknowledge them in the responses.

# Notes

- Responses must be in Polish!
- No emoticons allowed.

## About PJATKUŚ

PJATKUŚ is a robot created in collaboration with the student clubs RoboLab and Data Science Club at PJATK, and is used by them as creators. PJATKUŚ can only respond to questions about himself and the college. The college is an academy, not a university.

Anyone can ask PJATKUŚ a question, and you are to propose these questions.

# Output Format

The response should be a correctly formatted JSON array containing 10 objects that adhere to the structure outlined above. Ensure every field is correctly formatted without syntax errors.

# Examples

**Questions:** 5
**Topic:** First question about PJATKUŚ

```json
[
  {
    "pytanie": "Kim jesteś?",
    "tagi": ["PJATKUŚ", "twórcy", "o mnie"],
    "alternatywy": [
      "Kim jest PJATKUŚ?",
      "Czym jesteś?",
      "Co to jest PJATKUŚ?"
    ],
    "odpowiedz": "Jestem robotem stworzonym przez studentów z RoboLab i Data Science Club PJATK, który ma na celu wspieranie studentów i odpowiadanie na ich pytania."
  }
  // ... 4 additional objects
]
```

**Questions:** 10
**Topic:** Kierunki studiów

```json
[
  {
    "pytanie": "Jakie kierunki studiów oferuje PJATK?",
    "tagi": ["kierunki studiów", "oferta edukacyjna"],
    "alternatywy": [
      "Które kierunki studiów można wybrać?",
      "jakie kierunki są dostępne?",
      "Jakie opcje studiów są dostępne na PJATK?",
      "Jakie programy nauki są dostępne na tej uczelni?"
    ],
    "odpowiedz": "PJATK oferuje szeroką gamę kierunków studiów w różnych dziedzinach takich jak informatyka, grafika, czy zarządzanie."
  }
  // ... 9 additional objects
]
```"""


import json
import os
from openai import OpenAI
from dotenv import load_dotenv
import tqdm

load_dotenv()
client = OpenAI()


def new_questions(topic: str, n=20):

    prompts = [
        {
            "role": "system",
            "content": f"{QUESTION_CREATOR_PROMPOT}",
        },
        {
            "role": "user",
            "content": f"QUESTIONS: {n}\nTOPIC: {topic}",
        },
    ]
    model = os.getenv("QUESTION_CREATOR_MODEL")
    response = client.chat.completions.create(
        model=model,
        messages=prompts,
        response_format={"type": "json_object"},
        temperature=0.000001,
    )

    questions_str = response.choices[0].message.content

    try:
        questions_list: dict = json.loads(questions_str)
    except json.JSONDecodeError:
        print(questions_str)
        raise

    return questions_list


if __name__ == "__main__":
    topics = [
        "O uczelnie",
        "Kierunki studiów",
        "Wydziały",
        "Rekrutacja",
        "Studenci",
        "Współpraca",
        "Wydarzenia",
        "Kontakt",
        "Pomoc",
        "Humorystyczne",
        "O PJATKUŚ",
        "Koła naukowe",
        "O PJATK",
        "Inne",
    ]
    questions = []
    for topic in tqdm.tqdm(topics):

        qs = new_questions(topic)
        questions.extend(qs["questions"])
        with open(f"data/questions_{topic}.json", "w", encoding="utf-8") as f:
            json.dump(qs, f, indent=2, ensure_ascii=False)

    with open("questions.json", "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
