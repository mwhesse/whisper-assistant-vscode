import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io

from main import app

client = TestClient(app)

class TestAPI:
    """Test cases for the main API endpoints"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health_check" in data
        assert "transcribe" in data
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "model" in data
        assert "device" in data
    
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