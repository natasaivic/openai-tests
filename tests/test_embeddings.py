import pytest
import requests
from conftest import BASE_URL, check_rate_limit_and_skip

class TestEmbeddingsEndpoint:
    """Test cases for /embeddings endpoint operations"""
    
    @pytest.mark.smoke
    def test_create_embedding_success(self, headers):
        """Test POST /embeddings creates embedding successfully"""
        payload = {
            "input": "The quick brown fox jumps over the lazy dog",
            "model": "text-embedding-ada-002"
        }
        
        response = requests.post(f"{BASE_URL}/embeddings", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "object" in data
        assert "data" in data
        assert "model" in data
        assert "usage" in data
        
        assert data["object"] == "list"
        assert data["model"] == "text-embedding-ada-002"
        
        # Verify data array structure
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 1
        
        embedding = data["data"][0]
        assert "object" in embedding
        assert "embedding" in embedding
        assert "index" in embedding
        
        assert embedding["object"] == "embedding"
        assert embedding["index"] == 0
        assert isinstance(embedding["embedding"], list)
        assert len(embedding["embedding"]) > 0
        
        # Verify usage information
        usage = data["usage"]
        assert "prompt_tokens" in usage
        assert "total_tokens" in usage
        assert isinstance(usage["prompt_tokens"], int)
        assert isinstance(usage["total_tokens"], int)
        assert usage["prompt_tokens"] > 0
        assert usage["total_tokens"] > 0
    
    def test_create_embedding_multiple_inputs(self, headers):
        """Test POST /embeddings with multiple input strings"""
        payload = {
            "input": [
                "Hello world",
                "Goodbye world",
                "Testing embeddings"
            ],
            "model": "text-embedding-ada-002"
        }
        
        response = requests.post(f"{BASE_URL}/embeddings", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["object"] == "list"
        assert len(data["data"]) == 3
        
        for i, embedding in enumerate(data["data"]):
            assert embedding["object"] == "embedding"
            assert embedding["index"] == i
            assert isinstance(embedding["embedding"], list)
            assert len(embedding["embedding"]) > 0
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_create_embedding_unauthorized(self):
        """Test POST /embeddings with invalid API key returns 401"""
        invalid_headers = {
            "Authorization": "Bearer invalid_key",
            "Content-Type": "application/json"
        }
        payload = {
            "input": "Test input",
            "model": "text-embedding-ada-002"
        }
        
        response = requests.post(f"{BASE_URL}/embeddings", headers=invalid_headers, json=payload)
        
        assert response.status_code == 401
    
    def test_create_embedding_missing_auth(self):
        """Test POST /embeddings without authorization returns 401"""
        headers = {"Content-Type": "application/json"}
        payload = {
            "input": "Test input",
            "model": "text-embedding-ada-002"
        }
        
        response = requests.post(f"{BASE_URL}/embeddings", headers=headers, json=payload)
        
        assert response.status_code == 401
    
    def test_create_embedding_missing_input(self, headers):
        """Test POST /embeddings without input returns 400"""
        payload = {
            "model": "text-embedding-ada-002"
        }
        
        response = requests.post(f"{BASE_URL}/embeddings", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 400
    
    def test_create_embedding_missing_model(self, headers):
        """Test POST /embeddings without model returns 400"""
        payload = {
            "input": "Test input"
        }
        
        response = requests.post(f"{BASE_URL}/embeddings", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 400
    
    def test_create_embedding_empty_input(self, headers):
        """Test POST /embeddings with empty input returns 400"""
        payload = {
            "input": "",
            "model": "text-embedding-ada-002"
        }
        
        response = requests.post(f"{BASE_URL}/embeddings", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 400
    
    def test_create_embedding_invalid_model(self, headers):
        """Test POST /embeddings with invalid model returns 400 or 404"""
        payload = {
            "input": "Test input",
            "model": "nonexistent-model"
        }
        
        response = requests.post(f"{BASE_URL}/embeddings", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        
        assert response.status_code in [400, 404]
    
    def test_create_embedding_large_input(self, headers):
        """Test POST /embeddings with very large input"""
        # Create input that's likely to exceed token limits
        large_input = "This is a test sentence. " * 1000
        payload = {
            "input": large_input,
            "model": "text-embedding-ada-002"
        }
        
        response = requests.post(f"{BASE_URL}/embeddings", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        
        assert response.status_code in [400, 413]
    
    def test_create_embedding_empty_array_input(self, headers):
        """Test POST /embeddings with empty array input returns 400"""
        payload = {
            "input": [],
            "model": "text-embedding-ada-002"
        }
        
        response = requests.post(f"{BASE_URL}/embeddings", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 400
    
    def test_create_embedding_null_input(self, headers):
        """Test POST /embeddings with null input returns 400"""
        payload = {
            "input": None,
            "model": "text-embedding-ada-002"
        }
        
        response = requests.post(f"{BASE_URL}/embeddings", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 400
    
    def test_create_embedding_malformed_json(self, headers):
        """Test POST /embeddings with malformed JSON"""
        malformed_json = '{"input": "test", "model": "text-embedding-ada-002"'
        
        response = requests.post(
            f"{BASE_URL}/embeddings", 
            headers=headers, 
            data=malformed_json
        )
        
        assert response.status_code == 400
    
    def test_create_embedding_response_headers(self, headers):
        """Test response contains proper headers"""
        payload = {
            "input": "Test input",
            "model": "text-embedding-ada-002"
        }
        
        response = requests.post(f"{BASE_URL}/embeddings", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        assert "content-type" in response.headers
        content_type = response.headers["content-type"].lower()
        assert "application/json" in content_type
        
        try:
            response.json()
        except ValueError:
            pytest.fail("Response should contain valid JSON")
    
    def test_create_embedding_encoding_format_float(self, headers):
        """Test POST /embeddings with encoding_format set to float"""
        payload = {
            "input": "Test input",
            "model": "text-embedding-ada-002",
            "encoding_format": "float"
        }
        
        response = requests.post(f"{BASE_URL}/embeddings", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        data = response.json()
        
        embedding_values = data["data"][0]["embedding"]
        for value in embedding_values[:5]:  # Check first 5 values
            assert isinstance(value, float)
    
    def test_create_embedding_dimensions_parameter(self, headers):
        """Test POST /embeddings with dimensions parameter if supported"""
        payload = {
            "input": "Test input",
            "model": "text-embedding-ada-002",
            "dimensions": 512
        }
        
        response = requests.post(f"{BASE_URL}/embeddings", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        
        # This may not be supported by all models, so accept both success and error
        if response.status_code == 200:
            data = response.json()
            embedding_length = len(data["data"][0]["embedding"])
            assert embedding_length == 512
        else:
            assert response.status_code in [400, 422]
    
    def test_create_embedding_field_validation(self, headers):
        """Test that embedding response contains required fields with correct types"""
        payload = {
            "input": "Test validation",
            "model": "text-embedding-ada-002"
        }
        
        response = requests.post(f"{BASE_URL}/embeddings", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        assert response.status_code == 200
        
        data = response.json()
        
        # Validate top-level response structure
        assert isinstance(data["object"], str)
        assert isinstance(data["data"], list)
        assert isinstance(data["model"], str)
        assert isinstance(data["usage"], dict)
        
        # Validate embedding object structure
        embedding = data["data"][0]
        assert isinstance(embedding["object"], str)
        assert isinstance(embedding["embedding"], list)
        assert isinstance(embedding["index"], int)
        
        # Validate usage object structure
        usage = data["usage"]
        assert isinstance(usage["prompt_tokens"], int)
        assert isinstance(usage["total_tokens"], int)
        
        # Validate embedding values are numeric
        for value in embedding["embedding"][:10]:  # Check first 10 values
            assert isinstance(value, (int, float))