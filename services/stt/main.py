from fastapi import FastAPI, HTTPException, UploadFile, File
import nemo.collections.asr as nemo_asr
import base64
import tempfile
import sys
import os
import time
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from shared import TranscriptionRequest, TranscriptionResponse, get_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="STT service")
settings = get_settings()

asr_model = None

@app.on_event("startup")
async def load_model():
    global asr_model
    logger.info(f"Loading {settings.nemo_model} model...")

    try:
        asr_model = nemo_asr.models.EncDecHybridRNNTCTCBPEModel.from_pretrained(model_name=settings.nemo_model)
        asr_model.change_decoding_strategy(decoder_type="ctc")

        logger.info("Model loaded successfully.")
    
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        # raise e
    
@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(audio_file: UploadFile = File(...)):
    if asr_model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")
    
    start_time = time.time()

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        result = asr_model.transcribe([tmp_path])
        transcription = result[0].text
        os.unlink(tmp_path)

        processing_time = time.time() - start_time

        return TranscriptionResponse(
            text=transcription,
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during transcription: {str(e)}")

# Ten endpoint jeszcze nie przetestowany xd Na razie testy bazowej funkcjoności są na transcribe, ale potem można będzie przenieść testy na ten endpoint i usunąć ten poprzedni
@app.post("/transcribe_base64", response_model=TranscriptionResponse)
async def transcribe_base64(request: TranscriptionRequest):
    if asr_model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")
    
    start_time = time.time()

    try:
        audio_data = base64.b64decode(request.audio_base64)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_data)
            tmp_path = tmp_file.name
        
        transcription = asr_model.transcribe([tmp_path])[0]
        os.unlink(tmp_path)

        processing_time = time.time() - start_time

        return TranscriptionResponse(
            text=transcription,
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during transcription: {str(e)}")

@app.get("/health")
async def health():
    model_loaded = asr_model is not None
    return {
        "status": "healthy" if model_loaded else "loading",
        "service": "stt",
        "model_loaded": model_loaded
    }