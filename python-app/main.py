from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import logging
import time
import json
from typing import Dict, Any, Optional
from config import config
from transcription_service import transcription_service
from models_service import ModelsService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize models service
models_service = ModelsService()

# Initialize templates
templates = Jinja2Templates(directory="templates")


app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description="A FastAPI service for audio transcription using OpenAI Whisper with support for external model storage"
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
    model: str = Form("base"),  # OpenAI standard parameter name
    language: str = Form(config.DEFAULT_LANGUAGE)
):
    """Transcribe audio file to text"""
    
    # Log all parameters received
    print(f"\n🔍 TRANSCRIBE_AUDIO FUNCTION CALLED:")
    print(f"   📁 file.filename: {file.filename}")
    print(f"   📁 file.content_type: {file.content_type}")
    print(f"   📁 file.size: {getattr(file, 'size', 'unknown')}")
    print(f"   🤖 model: {model}")
    print(f"   🌍 language: {language}")
    print(f"   ⚙️  config.DEFAULT_LANGUAGE: {config.DEFAULT_LANGUAGE}")
    
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith(('audio/', 'video/')):
            logger.warning(f"Invalid content type: {file.content_type}")
            # Allow anyway as some clients might not set proper content type
        
        # Read file content
        content = await file.read()
        actual_size = len(content)
        print(f"   📊 Actual file content size: {actual_size} bytes")
        
        if not content:
            error_msg = "Empty file provided"
            print(f"   ❌ ERROR: {error_msg}")
            logger.error(f"TRANSCRIPTION ERROR: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info(f"Processing file: {file.filename}, size: {actual_size} bytes, language: {language}, model: {model}")
        
        # Log what we're passing to the transcription service
        print(f"   🔄 Calling transcription_service.transcribe_audio(content_size={actual_size}, language='{language}', model_name='{model}')")
        
        # Transcribe using the service
        result = await transcription_service.transcribe_audio(content, language, model)
        
        print(f"   ✅ Transcription successful: {len(result.get('text', ''))} characters")
        logger.info(f"Transcription successful: {len(result.get('text', ''))} characters")
        return result
        
    except HTTPException as he:
        # Re-raise HTTP exceptions (these are expected errors)
        print(f"   ❌ HTTP Exception: {he.status_code} - {he.detail}")
        logger.error(f"TRANSCRIPTION HTTP ERROR {he.status_code}: {he.detail}")
        raise he
    except Exception as e:
        error_msg = f"Transcription failed: {str(e)}"
        print(f"   ❌ Unexpected Exception: {error_msg}")
        logger.error(f"TRANSCRIPTION UNEXPECTED ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/v1/health")
async def health_check():
    """Check if the API is running"""
    return {
        "status": "ok",
        "device": config.WHISPER_DEVICE,
        "version": config.API_VERSION,
        "available_models": [model["name"] for model in models_service.get_available_models()],
        "storage": {
            "external_storage_enabled": config.ENABLE_EXTERNAL_STORAGE,
            "effective_cache_dir": config.get_effective_cache_dir() if config.ENABLE_EXTERNAL_STORAGE else None
        }
    }

@app.get("/v1/models")
async def get_models():
    """Get information about available Whisper models with download status"""
    return {
        "available_models": models_service.get_models_with_status(),
        "downloaded_models": models_service.get_downloaded_models()
    }

@app.post("/v1/models/{model_name}/download")
async def download_model(model_name: str):
    """Download a specific Whisper model"""
    try:
        result = await models_service.download_model(
            model_name,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "model": model_name,
                "downloaded": result["downloaded"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error(f"Error in download endpoint for model {model_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download model: {str(e)}")

@app.get("/v1/models/downloaded")
async def get_downloaded_models():
    """Get list of models that are downloaded locally"""
    return {
        "downloaded_models": models_service.get_downloaded_models(),
        "total_available": len(models_service.get_available_models())
    }

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the dashboard with API information and available models"""
    try:
        # Get available models with download status
        available_models = models_service.get_models_with_status()
        
        # Prepare template context
        context = {
            "request": request,
            "api_title": config.API_TITLE,
            "version": config.API_VERSION,
            "status": "Online",
            "device": config.WHISPER_DEVICE.upper(),
            "port": config.PORT,
            "available_models": available_models
        }
        
        return templates.TemplateResponse("dashboard.html", context)
        
    except Exception as e:
        logger.error(f"Error serving dashboard: {str(e)}")
        # Fallback to JSON response if template fails
        return {
            "message": config.API_TITLE,
            "version": config.API_VERSION,
            "status": "Online",
            "device": config.WHISPER_DEVICE,
            "docs": "/docs",
            "health_check": "/v1/health",
            "transcribe": "/v1/audio/transcriptions"
        }

@app.get("/api/info")
async def api_info():
    """Get API information in JSON format (for programmatic access)"""
    return {
        "message": config.API_TITLE,
        "version": config.API_VERSION,
        "status": "Online",
        "device": config.WHISPER_DEVICE,
        "available_models": models_service.get_available_models(),
        "docs": "/docs",
        "health_check": "/v1/health",
        "transcribe": "/v1/audio/transcriptions"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4445)