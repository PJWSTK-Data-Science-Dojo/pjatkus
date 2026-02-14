from fastapi import FastAPI, HTTPException
from openai import OpenAI
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from shared import ChatRequest, ChatResponse, get_settings

app = FastAPI(title="LLM service")
settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """Jesteś PJATKuS - przyjazny robot studencki działający na PJATK (Polsko-Japońska Akademia Technik Komputerowych).

Twoja rola:
- Pomagasz studentom z informacjami o uczelni
- Odpowiadasz krótko i konkretnie (max 2-3 zdania)
- Mówisz po polsku
- Jesteś pomocny, ale nie przesadnie formalny
- Jeśli czegoś nie wiesz, powiedz to wprost

Pamiętaj: jesteś robotem, ale sympatycznym!"""

conversation_history = {}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if request.session_id not in conversation_history:
            conversation_history[request.session_id] = []
        
        history = conversation_history[request.session_id]

        history.append({"role": "user", "content": request.message})

        if len(history) > 10:
            history = history[-10:]

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )

        assistant_message = response.choices[0].message.content

        history.append({"role": "assistant", "content": assistant_message})
        conversation_history[request.session_id] = history

        return ChatResponse(
            response=assistant_message,
            session_id=request.session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")
    
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "llm"}

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    if session_id in conversation_history:
        del conversation_history[session_id]
    
    return {"status": "cleared", "session_id": session_id}