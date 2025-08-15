import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io

from main import app

client = TestClient(app)

class TestAPI:
    """Test cases for the main API endpoints"""
    
    def test_root_endpoint_dashboard(self):
        """Test the root endpoint serves HTML dashboard"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "WhisperX Assistant API" in response.text
        assert "Available Models" in response.text
    
    def test_api_info_endpoint(self):
        """Test the API info endpoint returns JSON"""
        response = client.get("/api/info")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert "current_model" in data
        assert "available_models" in data
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "model" in data
        assert "device" in data
        assert "version" in data
        assert "available_models" in data
        assert isinstance(data["available_models"], list)
    
    def test_models_endpoint(self):
        """Test the models endpoint"""
        response = client.get("/v1/models")
        assert response.status_code == 200
        data = response.json()
        assert "current_model" in data
        assert "available_models" in data
        assert "current_model_info" in data
        assert isinstance(data["available_models"], list)
        assert len(data["available_models"]) > 0
        
        # Check model structure
        for model in data["available_models"]:
            assert "name" in model
            assert "size" in model
            assert "description" in model
            assert "downloaded" in model
    
    def test_downloaded_models_endpoint(self):
        """Test the downloaded models endpoint"""
        response = client.get("/v1/models/downloaded")
        assert response.status_code == 200
        data = response.json()
        assert "downloaded_models" in data
        assert "total_available" in data
        assert isinstance(data["downloaded_models"], list)
        assert isinstance(data["total_available"], int)
    
    @patch('models_service.models_service.download_model')
    def test_download_model_success(self, mock_download):
        """Test successful model download"""
        mock_download.return_value = {
            "success": True,
            "message": "Model downloaded successfully",
            "downloaded": True
        }
        
        response = client.post("/v1/models/base/download")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["model"] == "base"
        assert data["downloaded"] == True
        
        mock_download.assert_called_once()
    
    @patch('models_service.models_service.download_model')
    def test_download_model_failure(self, mock_download):
        """Test failed model download"""
        mock_download.return_value = {
            "success": False,
            "message": "Download failed",
            "downloaded": False
        }
        
        response = client.post("/v1/models/nonexistent/download")
        assert response.status_code == 400
        
        mock_download.assert_called_once()
    
    @patch('transcription_service.transcription_service.transcribe_audio')
    def test_transcribe_audio_success(self, mock_transcribe):
        """Test successful audio transcription"""
        # Mock the transcription service response
        mock_transcribe.return_value = {
            "text": "Hello world",
            "segments": [
                {
                    "id": 0,
                    "seek": 0,
                    "start": 0.0,
                    "end": 2.0,
                    "text": "Hello world",
                    "tokens": [],
                    "temperature": 0.0,
                }
            ],
            "language": "en"
        }
        
        # Create a mock audio file
        audio_content = b"fake audio content"
        files = {"file": ("test.wav", io.BytesIO(audio_content), "audio/wav")}
        
        response = client.post("/v1/audio/transcriptions", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Hello world"
        assert data["language"] == "en"
        assert len(data["segments"]) == 1
        
        # Verify the service was called
        mock_transcribe.assert_called_once()
    
    def test_transcribe_audio_empty_file(self):
        """Test transcription with empty file"""
        files = {"file": ("test.wav", io.BytesIO(b""), "audio/wav")}
        
        response = client.post("/v1/audio/transcriptions", files=files)
        
        assert response.status_code == 400
        assert "Empty file provided" in response.json()["detail"]
    
    @patch('transcription_service.transcription_service.transcribe_audio')
    def test_transcribe_audio_service_error(self, mock_transcribe):
        """Test transcription when service raises an error"""
        mock_transcribe.side_effect = Exception("Transcription failed")
        
        audio_content = b"fake audio content"
        files = {"file": ("test.wav", io.BytesIO(audio_content), "audio/wav")}
        
        response = client.post("/v1/audio/transcriptions", files=files)
        
        assert response.status_code == 500
        assert "Transcription failed" in response.json()["detail"]
    
    @patch('transcription_service.transcription_service.transcribe_audio')
    def test_transcribe_audio_with_language(self, mock_transcribe):
        """Test transcription with specific language"""
        mock_transcribe.return_value = {
            "text": "Bonjour le monde",
            "segments": [],
            "language": "fr"
        }
        
        audio_content = b"fake audio content"
        files = {"file": ("test.wav", io.BytesIO(audio_content), "audio/wav")}
        data = {"language": "fr"}
        
        response = client.post("/v1/audio/transcriptions", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["text"] == "Bonjour le monde"
        assert result["language"] == "fr"
    
    @patch('transcription_service.transcription_service.transcribe_audio')
    def test_transcribe_audio_with_model_name(self, mock_transcribe):
        """Test transcription with specific model name"""
        mock_transcribe.return_value = {
            "text": "Hello from large model",
            "segments": [],
            "language": "en"
        }
        
        audio_content = b"fake audio content"
        files = {"file": ("test.wav", io.BytesIO(audio_content), "audio/wav")}
        data = {"model_name": "large", "language": "en"}
        
        response = client.post("/v1/audio/transcriptions", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["text"] == "Hello from large model"
        assert result["language"] == "en"
        
        # Verify the service was called with the correct parameters
        mock_transcribe.assert_called_once()
        call_args = mock_transcribe.call_args
        assert len(call_args[0]) == 3  # audio_content, language, model_name
        assert call_args[0][1] == "en"  # language
        assert call_args[0][2] == "large"  # model_name