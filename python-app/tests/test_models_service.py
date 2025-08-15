import pytest
from models_service import ModelsService

class TestModelsService:
    """Test cases for the ModelsService"""
    
    def test_init(self):
        """Test service initialization"""
        service = ModelsService("base")
        assert service.current_model == "base"
    
    def test_get_available_models(self):
        """Test getting available models"""
        service = ModelsService()
        models = service.get_available_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        
        # Check that all expected models are present
        model_names = [model["name"] for model in models]
        expected_models = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
        
        for expected in expected_models:
            assert expected in model_names
        
        # Check model structure
        for model in models:
            assert "name" in model
            assert "size" in model
            assert "description" in model
            assert "parameters" in model
            assert "relative_speed" in model
            assert "vram_required" in model
        
    def test_is_model_available(self):
        """Test checking if model is available"""
        service = ModelsService()
        
        assert service.is_model_available("base") == True
        assert service.is_model_available("tiny") == True
        assert service.is_model_available("nonexistent") == False
    
    def test_get_model_info(self):
        """Test getting specific model information"""
        service = ModelsService()
        
        info = service.get_model_info("base")
        assert info is not None
        assert info["name"] == "base"
        
        info = service.get_model_info("nonexistent")
        assert info is None
    
    def test_get_recommended_model(self):
        """Test getting recommended models"""
        service = ModelsService()
        
        assert service.get_recommended_model("speed") == "tiny"
        assert service.get_recommended_model("balanced") == "base"
        assert service.get_recommended_model("accuracy") == "large-v3"
        assert service.get_recommended_model("unknown") == "base"  # default
    
    def test_get_models_with_status(self):
        """Test getting models with download status"""
        service = ModelsService()
        models = service.get_models_with_status()
        
        assert isinstance(models, list)
        assert len(models) > 0
        
        # Check that all models have download status
        for model in models:
            assert "downloaded" in model
            assert isinstance(model["downloaded"], bool)
    
    def test_get_downloaded_models(self):
        """Test getting list of downloaded models"""
        service = ModelsService()
        downloaded = service.get_downloaded_models()
        
        assert isinstance(downloaded, list)
        # All items should be valid model names
        available_names = [model["name"] for model in service.get_available_models()]
        for model_name in downloaded:
            assert model_name in available_names