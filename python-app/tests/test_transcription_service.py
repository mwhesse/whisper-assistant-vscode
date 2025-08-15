import pytest
from unittest.mock import patch, MagicMock
import tempfile
import os

from transcription_service import TranscriptionService

class TestTranscriptionService:
    """Test cases for the TranscriptionService"""
    
    @patch('transcription_service.WhisperModel')
    def test_init(self, mock_whisper_model):
        """Test service initialization"""
        mock_model = MagicMock()
        mock_whisper_model.return_value = mock_model
        
        service = TranscriptionService()
        
        assert service.model == mock_model
        mock_whisper_model.assert_called_once_with("base", device="cpu", compute_type="int8")
    
    @patch('transcription_service.WhisperModel')
    @pytest.mark.asyncio
    async def test_transcribe_audio_success(self, mock_whisper_model):
        """Test successful audio transcription"""
        # Mock the Whisper model
        mock_model = MagicMock()
        mock_whisper_model.return_value = mock_model
        
        # Mock transcription results
        mock_segment = MagicMock()
        mock_segment.start = 0.0
        mock_segment.end = 2.0
        mock_segment.text = "Hello world"
        
        mock_info = MagicMock()
        mock_info.language = "en"
        
        mock_model.transcribe.return_value = ([mock_segment], mock_info)
        
        service = TranscriptionService()
        
        # Test transcription
        result = await service.transcribe_audio(b"fake audio content", "en")
        
        assert result["text"] == "Hello world"
        assert result["language"] == "en"
        assert len(result["segments"]) == 1
        assert result["segments"][0]["text"] == "Hello world"
        assert result["segments"][0]["start"] == 0.0
        assert result["segments"][0]["end"] == 2.0
    
    @patch('transcription_service.WhisperModel')
    @pytest.mark.asyncio
    async def test_transcribe_audio_default_language(self, mock_whisper_model):
        """Test transcription with default language"""
        mock_model = MagicMock()
        mock_whisper_model.return_value = mock_model
        
        mock_segment = MagicMock()
        mock_segment.start = 0.0
        mock_segment.end = 1.0
        mock_segment.text = "Test"
        
        mock_info = MagicMock()
        mock_info.language = "en"
        
        mock_model.transcribe.return_value = ([mock_segment], mock_info)
        
        service = TranscriptionService()
        
        # Test transcription without language parameter
        result = await service.transcribe_audio(b"fake audio content")
        
        # Verify the model was called with default language
        mock_model.transcribe.assert_called_once()
        call_args = mock_model.transcribe.call_args
        assert call_args[1]["language"] == "en"  # Default language from config
    
    @patch('transcription_service.WhisperModel')
    @patch('transcription_service.os.unlink')
    @pytest.mark.asyncio
    async def test_temp_file_cleanup(self, mock_unlink, mock_whisper_model):
        """Test that temporary files are cleaned up"""
        mock_model = MagicMock()
        mock_whisper_model.return_value = mock_model
        
        mock_segment = MagicMock()
        mock_segment.start = 0.0
        mock_segment.end = 1.0
        mock_segment.text = "Test"
        
        mock_info = MagicMock()
        mock_info.language = "en"
        
        mock_model.transcribe.return_value = ([mock_segment], mock_info)
        
        service = TranscriptionService()
        
        await service.transcribe_audio(b"fake audio content")
        
        # Verify temp file was deleted
        mock_unlink.assert_called_once()
    
    @patch('transcription_service.WhisperModel')
    @patch('transcription_service.os.unlink')
    @pytest.mark.asyncio
    async def test_temp_file_cleanup_on_error(self, mock_unlink, mock_whisper_model):
        """Test that temporary files are cleaned up even when transcription fails"""
        mock_model = MagicMock()
        mock_whisper_model.return_value = mock_model
        
        # Make transcription raise an exception
        mock_model.transcribe.side_effect = Exception("Transcription failed")
        
        service = TranscriptionService()
        
        with pytest.raises(Exception, match="Transcription failed"):
            await service.transcribe_audio(b"fake audio content")
        
        # Verify temp file was still deleted
        mock_unlink.assert_called_once()
    
    @patch('transcription_service.WhisperModel')
    @pytest.mark.asyncio
    async def test_multiple_segments(self, mock_whisper_model):
        """Test transcription with multiple segments"""
        mock_model = MagicMock()
        mock_whisper_model.return_value = mock_model
        
        # Mock multiple segments
        mock_segment1 = MagicMock()
        mock_segment1.start = 0.0
        mock_segment1.end = 2.0
        mock_segment1.text = "Hello"
        
        mock_segment2 = MagicMock()
        mock_segment2.start = 2.0
        mock_segment2.end = 4.0
        mock_segment2.text = "world"
        
        mock_info = MagicMock()
        mock_info.language = "en"
        
        mock_model.transcribe.return_value = ([mock_segment1, mock_segment2], mock_info)
        
        service = TranscriptionService()
        
        result = await service.transcribe_audio(b"fake audio content")
        
        assert result["text"] == "Hello world"
        assert len(result["segments"]) == 2
        assert result["segments"][0]["text"] == "Hello"
        assert result["segments"][1]["text"] == "world"
        assert result["segments"][0]["id"] == 0
        assert result["segments"][1]["id"] == 1
    
    @patch('transcription_service.WhisperModel')
    @pytest.mark.asyncio
    async def test_transcribe_audio_with_model_name(self, mock_whisper_model):
        """Test transcription with specific model name"""
        mock_model = MagicMock()
        mock_whisper_model.return_value = mock_model
        
        mock_segment = MagicMock()
        mock_segment.start = 0.0
        mock_segment.end = 1.0
        mock_segment.text = "Test with large model"
        
        mock_info = MagicMock()
        mock_info.language = "en"
        
        mock_model.transcribe.return_value = ([mock_segment], mock_info)
        
        service = TranscriptionService()
        
        # Test transcription with specific model name
        result = await service.transcribe_audio(b"fake audio content", "en", "large")
        
        # Verify the result
        assert result["text"] == "Test with large model"
        assert result["language"] == "en"
        
        # Verify that WhisperModel was called twice (once for init, once for model switch)
        assert mock_whisper_model.call_count == 2
        # Check the second call was with the new model
        mock_whisper_model.assert_called_with("large", device="cpu", compute_type="int8")
    
    @patch('transcription_service.WhisperModel')
    @pytest.mark.asyncio
    async def test_transcribe_audio_default_model_name(self, mock_whisper_model):
        """Test transcription with default model name (no switching)"""
        mock_model = MagicMock()
        mock_whisper_model.return_value = mock_model
        
        # Mock the model_name attribute to match config default
        mock_model.model_name = "base"
        
        mock_segment = MagicMock()
        mock_segment.start = 0.0
        mock_segment.end = 1.0
        mock_segment.text = "Test with default model"
        
        mock_info = MagicMock()
        mock_info.language = "en"
        
        mock_model.transcribe.return_value = ([mock_segment], mock_info)
        
        service = TranscriptionService()
        service.model = mock_model  # Set the model directly to avoid init call
        
        # Test transcription with default model name (should not switch models)
        result = await service.transcribe_audio(b"fake audio content", "en", "base")
        
        # Verify the result
        assert result["text"] == "Test with default model"
        assert result["language"] == "en"
        
        # Verify that WhisperModel was called only once during init (no model switching)
        assert mock_whisper_model.call_count == 1