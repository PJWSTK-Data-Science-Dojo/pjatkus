import httpx
import sys
import os
import time

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from shared import get_settings, ConversationResponse, ConversationRequest

app = FastAPI(title="Gateway service")
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/conversation", response_model=ConversationResponse)
async def conversation(audio: UploadFile = File(...), session_id: str = "default"):
    """
    Na razie flow jest następujące:
    1. Obiera audio
    2. Wysyła do STT, dostaje tekst
    3. Wysyła tekst do LLM, dostaje odpowiedź
    4. Zwraca odpowiedź do klienta
    """
    start_time = time.time()

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            # Transcribe audio
            audio_content = await audio.read()
            files = {'audio_file': (audio.filename, audio_content, audio.content_type)}
            
            stt_response = await client.post(
                f"{settings.stt_service_url}/transcribe",
                files=files
            )
            stt_response.raise_for_status()
            transcription = stt_response.json()["text"]

            print(f"Transcribed text: {transcription}")

            # Get LLM response
            llm_response = await client.post(
                f"{settings.llm_service_url}/chat",
                json={
                    "message": transcription,
                    "session_id": session_id
                }
            )
            llm_response.raise_for_status()
            response_text = llm_response.json()["response"]

            print(f"LLM response: {response_text}")

            processing_time = time.time() - start_time

            return ConversationResponse(
                transcription=transcription,
                response=response_text,
                session_id=session_id,
                processing_time=processing_time
            )
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"Service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")
    
@app.post("/api/v1/conversation-base64", response_model=ConversationResponse)
async def conversation_base64(request: ConversationRequest):
    """
    Na razie flow jest następujące:
    1. Obiera audio
    2. Wysyła do STT, dostaje tekst
    3. Wysyła tekst do LLM, dostaje odpowiedź
    4. Zwraca odpowiedź do klienta
    """
    start_time = time.time()

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            # Transcribe audio
            stt_response = await client.post(
                f"{settings.stt_service_url}/transcribe-base64",
                json={"audio_base64": request.audio_base64, "language": "pl"}
            )
            stt_response.raise_for_status()
            transcription = stt_response.json()["text"]

            print(f"Transcribed text: {transcription}")

            # Get LLM response
            llm_response = await client.post(
                f"{settings.llm_service_url}/chat",
                json={
                    "message": transcription,
                    "session_id": request.session_id
                }
            )
            llm_response.raise_for_status()
            response_text = llm_response.json()["response"]

            print(f"LLM response: {response_text}")

            processing_time = time.time() - start_time

            return ConversationResponse(
                transcription=transcription,
                response=response_text,
                session_id=request.session_id,
                processing_time=processing_time
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")
    
@app.get("/health")
async def health():
    health_status = {"service": "gateway", "status": "healthy", "downstream": {}}

    async with httpx.AsyncClient(timeout=5) as client:
        try:
            stt_health = await client.get(f"{settings.stt_service_url}/health")
            health_status["downstream"]["stt"] = stt_health.json()
        except:
            health_status["downstream"]["stt"] = {"status": "unreachable"}
        
        try:
            llm_health = await client.get(f"{settings.llm_service_url}/health")
            health_status["downstream"]["llm"] = llm_health.json()
        except:
            health_status["downstream"]["llm"] = {"status": "unreachable"}
    
    return health_status