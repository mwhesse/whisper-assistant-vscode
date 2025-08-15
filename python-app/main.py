from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from config import config
from transcription_service import transcription_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description="A FastAPI service for audio transcription using Whisper"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/v1/audio/transcriptions")
async def transcribe_audio(
    file: UploadFile = File(...),
    model_name: str = "whisper-1",  # Renamed parameter to avoid conflict
    language: str = config.DEFAULT_LANGUAGE
):
    """Transcribe audio file to text"""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith(('audio/', 'video/')):
            logger.warning(f"Invalid content type: {file.content_type}")
            # Allow anyway as some clients might not set proper content type
        
        # Read file content
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file provided")
        
        logger.info(f"Processing file: {file.filename}, size: {len(content)} bytes")
        
        # Transcribe using the service
        result = await transcription_service.transcribe_audio(content, language)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing transcription request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.get("/v1/health")
async def health_check():
    """Check if the API is running"""
    return {
        "status": "ok",
        "model": config.WHISPER_MODEL,
        "device": config.WHISPER_DEVICE
    }

@app.get("/")
async def root():
    """Get API information and available endpoints"""
    return {
        "message": config.API_TITLE,
        "version": config.API_VERSION,
        "docs": "/docs",
        "health_check": "/v1/health",
        "transcribe": "/v1/audio/transcriptions"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4445)