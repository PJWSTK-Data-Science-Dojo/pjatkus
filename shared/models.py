from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TranscriptionRequest(BaseModel):
    """Request do serwisu Text-to-Speech"""
    audio_base64: str = Field(..., description="Audio w base64 (WAV na razie, potem do ustalenia XD)")
    language: str = Field(default="pl", description="Język audio")

class TranscriptionResponse(BaseModel):
    """Odpowiedź z serwisu Text-to-Speech"""
    text: str
    processing_time: float
    confidence: Optional[float] = None

class ChatRequest(BaseModel):
    """Request do LLM service"""
    message: str
    session_id: str
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    """Odpowiedź z LLM service"""
    response: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ConversationRequest(BaseModel):
    """Request od robota z Gateway"""
    audio_base64: str
    session_id: str
    metadata: Optional[dict] = None

class ConversationResponse(BaseModel):
    """Odpowiedź od robota z Gateway"""
    transcription: str
    response: str
    session_id: str
    processing_time: float