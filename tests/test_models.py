import os
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.openai.com/v1"
API_KEY = os.getenv("OPENAI_API_KEY")

@pytest.fixture
def headers():
    """Common headers for API requests"""
    if not API_KEY:
        pytest.skip("OPENAI_API_KEY environment variable not set")
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

class TestModelsEndpoint:
    """Test cases for /models endpoint operations"""
    
    def test_list_models_success(self, headers):
        """Test GET /models returns list of available models"""
        response = requests.get(f"{BASE_URL}/models", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "object" in data
        assert "data" in data
        assert data["object"] == "list"
        assert isinstance(data["data"], list)
        
        # Verify at least one model exists
        assert len(data["data"]) > 0
        
        # Verify model object structure
        model = data["data"][0]
        required_fields = ["id", "object", "created", "owned_by"]
        for field in required_fields:
            assert field in model
        assert model["object"] == "model"
    
    def test_list_models_unauthorized(self):
        """Test GET /models with invalid API key returns 401"""
        invalid_headers = {
            "Authorization": "Bearer invalid_key",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{BASE_URL}/models", headers=invalid_headers)
        
        assert response.status_code == 401
    
    def test_list_models_missing_auth(self):
        """Test GET /models without authorization returns 401"""
        response = requests.get(f"{BASE_URL}/models")
        
        assert response.status_code == 401
    
    def test_retrieve_specific_model_success(self, headers):
        """Test GET /models/{model} returns specific model details"""
        # First get list of models to pick a valid one
        models_response = requests.get(f"{BASE_URL}/models", headers=headers)
        assert models_response.status_code == 200
        
        models_data = models_response.json()
        model_id = models_data["data"][0]["id"]
        
        # Test retrieving specific model
        response = requests.get(f"{BASE_URL}/models/{model_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        required_fields = ["id", "object", "created", "owned_by"]
        for field in required_fields:
            assert field in data
        assert data["object"] == "model"
        assert data["id"] == model_id
    
    def test_retrieve_nonexistent_model(self, headers):
        """Test GET /models/{model} with non-existent model returns 404"""
        response = requests.get(f"{BASE_URL}/models/nonexistent-model", headers=headers)
        
        assert response.status_code == 404
    
    def test_retrieve_model_unauthorized(self):
        """Test GET /models/{model} with invalid API key returns 401"""
        invalid_headers = {
            "Authorization": "Bearer invalid_key",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{BASE_URL}/models/gpt-3.5-turbo", headers=invalid_headers)
        
        assert response.status_code == 401
    