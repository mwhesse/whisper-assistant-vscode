from faster_whisper import WhisperModel
import tempfile
import os
import logging
from typing import Dict, List, Any
from config import config

logger = logging.getLogger(__name__)

class TranscriptionService:
    """Service for handling audio transcription using Whisper model"""
    
    def __init__(self):
        """Initialize the Whisper model"""
        logger.info(f"Initializing with default Whisper model: {config.DEFAULT_WHISPER_MODEL}")
        self.current_model_name = config.DEFAULT_WHISPER_MODEL
        self.model = WhisperModel(
            config.DEFAULT_WHISPER_MODEL, 
            device=config.WHISPER_DEVICE, 
            compute_type=config.WHISPER_COMPUTE_TYPE
        )
        logger.info("Whisper model initialized successfully")
    
    async def transcribe_audio(self, audio_content: bytes, language: str = None, model_name: str = None, device: str = None) -> Dict[str, Any]:
        """
        Transcribe audio content to text
        
        Args:
            audio_content: Raw audio file content
            language: Language code for transcription (optional)
            model_name: Whisper model name to use for transcription (optional)
            
        Returns:
            Dictionary containing transcription results
        """

        logger.info(f"TranscriptionService transcribe_audio called with (model='{model_name}' lang='{language}')")

        if language is None:
            language = config.DEFAULT_LANGUAGE
        
        # Use provided model_name or fall back to config default
        if model_name is None:
            model_name = config.DEFAULT_WHISPER_MODEL

        if device is None:
            device = config.WHISPER_DEVICE
        
        # Check if we need to switch models
        if model_name != self.current_model_name:
            logger.info(f"Switching from model '{self.current_model_name}' to '{model_name}'")
            self.current_model_name = model_name
            self.model = WhisperModel(
                model_name,
                device=device,
                compute_type=config.WHISPER_COMPUTE_TYPE
            )
            
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=config.TEMP_FILE_SUFFIX) as temp_file:
            temp_file.write(audio_content)
            temp_file.flush()
            
            try:
                logger.info(f"Transcribing audio file: {temp_file.name}")
                
                # Transcribe the audio
                segments, info = self.model.transcribe(
                    temp_file.name,
                    language=language,
                    vad_filter=True
                )
                
                # Format response to match OpenAI API
                formatted_segments = []
                for i, segment in enumerate(segments):
                    formatted_segments.append({
                        "id": i,
                        "seek": 0,
                        "start": segment.start,
                        "end": segment.end,
                        "text": segment.text,
                        "tokens": [],
                        "temperature": 0.0,
                    })
                
                result = {
                    "text": " ".join(seg["text"] for seg in formatted_segments),
                    "segments": formatted_segments,
                    "language": info.language
                }
                
                logger.info(f"Transcription completed. Language: {info.language}, Segments: {len(formatted_segments)}")
                return result
                
            except Exception as e:
                logger.error(f"Error during transcription: {str(e)}")
                raise
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file.name)
                except OSError as e:
                    logger.warning(f"Failed to delete temp file {temp_file.name}: {str(e)}")

# Global instance
transcription_service = TranscriptionService()