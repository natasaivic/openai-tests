import pytest
import requests
from conftest import BASE_URL, check_rate_limit_and_skip

class TestModelsEndpoint:
    """Test cases for /models endpoint operations"""
    
    @pytest.mark.smoke
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
    
    @pytest.mark.smoke
    @pytest.mark.auth
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
    
    def test_model_field_validation(self, headers):
        """Test that model objects contain required fields with correct types"""
        response = requests.get(f"{BASE_URL}/models", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        models = data["data"]
        
        for model in models:
            assert isinstance(model["id"], str), f"Model ID should be string, got {type(model['id'])}"
            assert isinstance(model["object"], str), f"Object field should be string, got {type(model['object'])}"
            assert isinstance(model["created"], int), f"Created field should be integer timestamp, got {type(model['created'])}"
            assert isinstance(model["owned_by"], str), f"Owned_by field should be string, got {type(model['owned_by'])}"
            
            assert model["object"] == "model", f"Object field should be 'model', got {model['object']}"
            assert len(model["id"]) > 0, "Model ID should not be empty"
            assert len(model["owned_by"]) > 0, "Owned_by should not be empty"
            assert model["created"] > 0, "Created timestamp should be positive"
    
    def test_model_ownership_patterns(self, headers):
        """Test model ownership validation for different owners"""
        response = requests.get(f"{BASE_URL}/models", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        models = data["data"]
        
        owners = set(model["owned_by"] for model in models)
        assert len(owners) > 0, "Should have at least one model owner"
        
        for model in models:
            owner = model["owned_by"]
            assert owner in ["openai", "system", "user", "openai-internal"] or owner.startswith("user-") or owner.startswith("org-"), \
                f"Unexpected owner format: {owner}"
    
    def test_model_id_format_validation(self, headers):
        """Test that model IDs follow expected patterns"""
        response = requests.get(f"{BASE_URL}/models", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        models = data["data"]
        
        for model in models:
            model_id = model["id"]
            assert isinstance(model_id, str), "Model ID must be string"
            assert len(model_id) > 0, "Model ID cannot be empty"
            assert not model_id.startswith(" "), "Model ID cannot start with space"
            assert not model_id.endswith(" "), "Model ID cannot end with space"
            assert "\n" not in model_id, "Model ID cannot contain newlines"
            assert "\t" not in model_id, "Model ID cannot contain tabs"
    
    def test_malformed_model_ids(self, headers):
        """Test GET /models/{model} with malformed model IDs"""
        malformed_ids = [
            "",
            " ",
            "model with spaces",
            "model/with/slashes",
            "model\nwith\nnewlines",
            "model\twith\ttabs",
            "model%20with%20encoding",
            "a" * 1000,
            "../../../etc/passwd"
        ]
        
        for model_id in malformed_ids:
            response = requests.get(f"{BASE_URL}/models/{model_id}", headers=headers)
            assert response.status_code in [400, 403, 404], \
                f"Malformed model ID '{model_id}' should return 400, 403 or 404, got {response.status_code}"
    
    def test_server_error_handling(self, headers):
        """Test handling of potential server errors"""
        response = requests.get(f"{BASE_URL}/models", headers=headers, timeout=30)
        
        assert response.status_code < 500, \
            f"Server should not return 5xx errors for valid requests, got {response.status_code}"
        
        if response.status_code != 200:
            assert response.status_code in [401, 403, 429], \
                f"Unexpected status code for models endpoint: {response.status_code}"
    
    def test_network_timeout_handling(self, headers):
        """Test request timeout handling"""
        try:
            response = requests.get(f"{BASE_URL}/models", headers=headers, timeout=0.001)
            if response.status_code == 200:
                pytest.skip("Request completed too quickly to test timeout")
        except requests.Timeout:
            pass
        except requests.ConnectionError:
            pytest.skip("Connection error - network may be unavailable")
    
    def test_api_key_format_validation(self):
        """Test various malformed API key formats"""
        malformed_keys = [
            "",
            "Bearer",
            "invalid_key_without_prefix",
            "sk-" + "x" * 200,
            "sk-",
            "bearer invalid_key",
            "Basic invalid_key",
            "sk-invalid key with spaces"
        ]
        
        for api_key in malformed_keys:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            response = requests.get(f"{BASE_URL}/models", headers=headers)
            assert response.status_code == 401, \
                f"Malformed API key '{api_key}' should return 401, got {response.status_code}"
    
    def test_missing_authorization_header(self):
        """Test missing Authorization header"""
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/models", headers=headers)
        assert response.status_code == 401
    
    def test_malformed_authorization_header(self):
        """Test malformed Authorization header formats"""
        malformed_headers = [
            {"Authorization": ""},
            {"Authorization": "Bearer"},
            {"Authorization": "Basic somekey"},
            {"Authorization": "Token somekey"},
            {"Authorization": "bearer lowercase"},
            {"Authorization": "Bearer "}
        ]
        
        for header in malformed_headers:
            header["Content-Type"] = "application/json"
            response = requests.get(f"{BASE_URL}/models", headers=header)
            assert response.status_code == 401, \
                f"Malformed header {header} should return 401, got {response.status_code}"
    
    def test_response_headers_validation(self, headers):
        """Test response contains proper headers"""
        response = requests.get(f"{BASE_URL}/models", headers=headers)
        assert response.status_code == 200
        
        assert "content-type" in response.headers, "Response should contain Content-Type header"
        content_type = response.headers["content-type"].lower()
        assert "application/json" in content_type, f"Content-Type should be JSON, got {content_type}"
        
        assert response.text, "Response body should not be empty"
        
        try:
            response.json()
        except ValueError:
            pytest.fail("Response should contain valid JSON")
    