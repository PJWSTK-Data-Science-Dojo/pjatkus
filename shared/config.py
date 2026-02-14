from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path

class Settings(BaseSettings):
    openai_api_key: str

    stt_service_url: str = "http://localhost:8001"
    llm_service_url: str = "http://localhost:8002"
    gateway_service_url: str  = "http://localhost:8000"

    openai_model: str = "gpt-4o-mini"
    nemo_model: str = "nvidia/stt_pl_fastconformer_hybrid_large_pc"

    max_audio_size_mb: int = 10
    request_timeout: int = 30

    class Config:
        env_file = os.path.join(Path(__file__).parent.parent, '.env')
        env_file_encoding = 'utf-8'
        extra = 'allow'

@lru_cache
def get_settings():
    return Settings()