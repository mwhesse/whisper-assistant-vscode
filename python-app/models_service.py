"""
Service for managing Whisper model information
"""
from typing import List, Dict, Any
import logging
import os
import asyncio
from pathlib import Path
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

class ModelsService:
    """Service for handling Whisper model information"""
    
    # Available Whisper models with their approximate sizes and descriptions
    # Based on faster-whisper supported models: https://github.com/SYSTRAN/faster-whisper
    AVAILABLE_MODELS = [
        {
            "name": "tiny",
            "size": "~39 MB",
            "description": "Fastest, least accurate",
            "parameters": "39M",
            "relative_speed": "~10x",
            "vram_required": "~1 GB"
        },
        {
            "name": "base",
            "size": "~74 MB",
            "description": "Good balance of speed and accuracy",
            "parameters": "74M",
            "relative_speed": "~7x",
            "vram_required": "~1 GB"
        },
        {
            "name": "small",
            "size": "~244 MB",
            "description": "Better accuracy, slower",
            "parameters": "244M",
            "relative_speed": "~4x",
            "vram_required": "~2 GB"
        },
        {
            "name": "medium",
            "size": "~769 MB",
            "description": "High accuracy, moderate speed",
            "parameters": "769M",
            "relative_speed": "~2x",
            "vram_required": "~5 GB"
        },
        {
            "name": "large",
            "size": "~1550 MB",
            "description": "Highest accuracy, slowest",
            "parameters": "1550M",
            "relative_speed": "~1x",
            "vram_required": "~10 GB"
        },
        {
            "name": "large-v2",
            "size": "~1550 MB",
            "description": "Improved large model",
            "parameters": "1550M",
            "relative_speed": "~1x",
            "vram_required": "~10 GB"
        },
        {
            "name": "large-v3",
            "size": "~1550 MB",
            "description": "Latest large model with better performance",
            "parameters": "1550M",
            "relative_speed": "~1x",
            "vram_required": "~10 GB"
        }
    ]
    
    def __init__(self, current_model: str = "base"):
        """Initialize the models service with current model"""
        self.current_model = current_model
        logger.info(f"Models service initialized with current model: {current_model}")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of all available Whisper models"""
        return self.AVAILABLE_MODELS.copy()
    
    def get_current_model_info(self) -> Dict[str, Any]:
        """Get information about the currently loaded model"""
        for model in self.AVAILABLE_MODELS:
            if model["name"] == self.current_model:
                return model.copy()
        
        # If current model not found in predefined list, return basic info
        return {
            "name": self.current_model,
            "size": "Unknown",
            "description": "Custom model",
            "parameters": "Unknown",
            "relative_speed": "Unknown"
        }
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a model is available"""
        return any(model["name"] == model_name for model in self.AVAILABLE_MODELS)
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        for model in self.AVAILABLE_MODELS:
            if model["name"] == model_name:
                return model.copy()
        return None
    
    def get_recommended_model(self, use_case: str = "balanced") -> str:
        """Get recommended model based on use case"""
        recommendations = {
            "speed": "tiny",
            "balanced": "base",
            "accuracy": "large-v3",
            "development": "base",
            "production": "small"
        }
        return recommendations.get(use_case, "base")
    
    def _get_model_cache_paths(self, model_name: str) -> List[Path]:
        """Get possible cache paths for a model"""
        # HuggingFace cache directory
        hf_cache = os.environ.get("HF_HOME", os.path.expanduser("~/.cache/huggingface"))
        
        # Possible path structures for faster-whisper models
        # Based on actual cache structure: models--guillaumekln--faster-whisper-{model_name}
        possible_paths = [
            # Current actual structure (guillaumekln is the maintainer of faster-whisper)
            Path(hf_cache) / "hub" / f"models--guillaumekln--faster-whisper-{model_name}",
            # Legacy/alternative structures
            Path(hf_cache) / "hub" / f"models--Systran--faster-whisper-{model_name}",
            Path(hf_cache) / "hub" / f"models--openai--whisper-{model_name}",
            Path(hf_cache) / "transformers" / f"models--guillaumekln--faster-whisper-{model_name}",
            Path(hf_cache) / "transformers" / f"models--Systran--faster-whisper-{model_name}",
            Path(hf_cache) / "transformers" / f"models--openai--whisper-{model_name}",
            # Also check for direct model name in case of different caching
            Path(hf_cache) / model_name,
            Path(hf_cache) / f"faster-whisper-{model_name}",
        ]
        
        return possible_paths
    
    def is_model_downloaded(self, model_name: str) -> bool:
        """Check if a model is downloaded locally without triggering downloads"""
        try:
            # Only check file system paths - do NOT call any download functions
            # as they might trigger automatic downloads
            
            # Check possible cache paths
            for model_path in self._get_model_cache_paths(model_name):
                if model_path.exists():
                    # Look for model files
                    model_files = (
                        list(model_path.rglob("*.bin")) +
                        list(model_path.rglob("*.safetensors")) +
                        list(model_path.rglob("model.bin")) +
                        list(model_path.rglob("pytorch_model.bin")) +
                        list(model_path.rglob("*.ctranslate2"))  # CT2 format files
                    )
                    if len(model_files) > 0:
                        logger.debug(f"Found model {model_name} at {model_path}")
                        return True
            
            # Also check if there's a simple model directory with the model name
            # in common cache locations
            common_cache_dirs = [
                os.path.expanduser("~/.cache/huggingface"),
                os.path.expanduser("~/.cache/whisper"),
                os.path.expanduser("~/.local/share/whisper"),
                "/tmp/whisper",
                "./models"  # Local models directory
            ]
            
            for cache_dir in common_cache_dirs:
                cache_path = Path(cache_dir)
                if cache_path.exists():
                    # Look for model directories
                    possible_model_dirs = [
                        cache_path / model_name,
                        cache_path / f"whisper-{model_name}",
                        cache_path / f"faster-whisper-{model_name}"
                    ]
                    
                    for model_dir in possible_model_dirs:
                        if model_dir.exists() and model_dir.is_dir():
                            # Check if it has model files
                            model_files = (
                                list(model_dir.rglob("*.bin")) +
                                list(model_dir.rglob("*.safetensors")) +
                                list(model_dir.rglob("*.ctranslate2"))
                            )
                            if len(model_files) > 0:
                                logger.debug(f"Found model {model_name} at {model_dir}")
                                return True
            
            return False
        except Exception as e:
            logger.warning(f"Error checking if model {model_name} is downloaded: {str(e)}")
            return False
    
    def get_downloaded_models(self) -> List[str]:
        """Get list of models that are downloaded locally"""
        downloaded = []
        for model in self.AVAILABLE_MODELS:
            if self.is_model_downloaded(model["name"]):
                downloaded.append(model["name"])
        return downloaded
    
    async def download_model(self, model_name: str, device: str = "cpu", compute_type: str = "int8") -> Dict[str, Any]:
        """Download a model if not already available"""
        try:
            if not self.is_model_available(model_name):
                return {
                    "success": False,
                    "message": f"Model '{model_name}' is not available",
                    "downloaded": False
                }
            
            if self.is_model_downloaded(model_name):
                return {
                    "success": True,
                    "message": f"Model '{model_name}' is already downloaded",
                    "downloaded": True
                }
            
            logger.info(f"Starting download of model: {model_name}")
            
            # Download the model by initializing it
            # This will trigger the download if not already present
            def _download_sync():
                try:
                    # Initialize the model which will download it if not present
                    logger.info(f"Initializing WhisperModel for {model_name} with device={device}, compute_type={compute_type}")
                    model = WhisperModel(model_name, device=device, compute_type=compute_type)
                    logger.info(f"WhisperModel initialized successfully for {model_name}")
                    # Clean up the model to free memory
                    del model
                    return True
                except Exception as e:
                    logger.error(f"Error in _download_sync for {model_name}: {str(e)}")
                    raise e
            
            # Run the download in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, _download_sync)
            
            # Give it a moment for the files to be written
            await asyncio.sleep(2)
            
            # Verify download with more lenient checking after successful initialization
            if self.is_model_downloaded(model_name):
                logger.info(f"Successfully downloaded model: {model_name}")
                return {
                    "success": True,
                    "message": f"Model '{model_name}' downloaded successfully",
                    "downloaded": True
                }
            else:
                # If our file-based detection fails, but the model initialized successfully,
                # we can assume the download worked (the model is cached somewhere)
                logger.info(f"Model {model_name} initialized successfully but file verification failed - assuming download succeeded")
                return {
                    "success": True,
                    "message": f"Model '{model_name}' downloaded successfully (cached by faster-whisper)",
                    "downloaded": True
                }
                
        except Exception as e:
            logger.error(f"Error downloading model {model_name}: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"Error downloading model '{model_name}': {str(e)}",
                "downloaded": False
            }
    
    def get_models_with_status(self) -> List[Dict[str, Any]]:
        """Get all models with their download status"""
        models_with_status = []
        for model in self.AVAILABLE_MODELS:
            model_info = model.copy()
            model_info["downloaded"] = self.is_model_downloaded(model["name"])
            models_with_status.append(model_info)
        return models_with_status

# Global instance - will be initialized with actual current model in main.py
models_service = None