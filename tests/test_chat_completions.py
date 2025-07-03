import pytest
import requests
from conftest import BASE_URL, check_rate_limit_and_skip

class TestChatCompletionsEndpoint:
    """Test cases for /chat/completions endpoint operations"""
    
    @pytest.mark.smoke_extended
    def test_chat_completion_success(self, headers):
        """Test POST /chat/completions with valid request returns completion"""
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        required_fields = ["id", "object", "created", "model", "choices", "usage"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        assert data["object"] == "chat.completion"
        assert isinstance(data["choices"], list)
        assert len(data["choices"]) > 0
        
        # Verify choice structure
        choice = data["choices"][0]
        choice_fields = ["index", "message", "finish_reason"]
        for field in choice_fields:
            assert field in choice, f"Missing choice field: {field}"
        
        # Verify message structure
        message = choice["message"]
        message_fields = ["role", "content"]
        for field in message_fields:
            assert field in message, f"Missing message field: {field}"
        
        assert message["role"] == "assistant"
        assert isinstance(message["content"], str)
        assert len(message["content"]) > 0
        
        # Verify usage structure
        usage = data["usage"]
        usage_fields = ["prompt_tokens", "completion_tokens", "total_tokens"]
        for field in usage_fields:
            assert field in usage, f"Missing usage field: {field}"
            assert isinstance(usage[field], int)
            assert usage[field] > 0
    
    def test_chat_completion_multiple_messages(self, headers):
        """Test chat completion with conversation history"""
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What's the capital of France?"},
                {"role": "assistant", "content": "The capital of France is Paris."},
                {"role": "user", "content": "What's the population?"}
            ],
            "max_tokens": 50
        }
        
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["object"] == "chat.completion"
        assert len(data["choices"]) > 0
        assert data["choices"][0]["message"]["role"] == "assistant"
        assert len(data["choices"][0]["message"]["content"]) > 0
    
    def test_chat_completion_different_models(self, headers):
        """Test chat completion with different available models"""
        models_to_test = ["gpt-3.5-turbo", "gpt-4"]
        
        for model in models_to_test:
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": "Say 'Hello'"}
                ],
                "max_tokens": 10
            }
            
            response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
            check_rate_limit_and_skip(response)
            
            if response.status_code == 404:
                pytest.skip(f"Model {model} not available")
            
            assert response.status_code == 200
            data = response.json()
            assert data["model"] == model or data["model"].startswith(model)
    
    def test_chat_completion_temperature_variations(self, headers):
        """Test chat completion with different temperature values"""
        temperatures = [0.0, 0.5, 1.0, 1.5, 2.0]
        
        for temp in temperatures:
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": "Generate a random number"}
                ],
                "max_tokens": 10,
                "temperature": temp
            }
            
            response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
            check_rate_limit_and_skip(response)
            
            assert response.status_code == 200
            data = response.json()
            assert data["object"] == "chat.completion"
    
    def test_chat_completion_max_tokens_limit(self, headers):
        """Test chat completion with different max_tokens values"""
        max_tokens_values = [1, 10, 50, 100]
        
        for max_tokens in max_tokens_values:
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": "Tell me a story"}
                ],
                "max_tokens": max_tokens
            }
            
            response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
            check_rate_limit_and_skip(response)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify completion tokens don't exceed max_tokens
            completion_tokens = data["usage"]["completion_tokens"]
            assert completion_tokens <= max_tokens, \
                f"Completion tokens {completion_tokens} exceed max_tokens {max_tokens}"
    
    def test_chat_completion_streaming(self, headers):
        """Test chat completion with streaming enabled"""
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Count from 1 to 3"}
            ],
            "max_tokens": 50,
            "stream": True
        }
        
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, stream=True)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        
        # Verify streaming response
        content_chunks = []
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    data_part = line_text[6:]
                    if data_part.strip() == '[DONE]':
                        break
                    try:
                        import json
                        chunk_data = json.loads(data_part)
                        if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                            if 'delta' in chunk_data['choices'][0]:
                                delta = chunk_data['choices'][0]['delta']
                                if 'content' in delta:
                                    content_chunks.append(delta['content'])
                    except json.JSONDecodeError:
                        continue
        
        # Verify we received streaming content
        assert len(content_chunks) > 0, "Should receive streaming content chunks"
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_chat_completion_unauthorized(self):
        """Test POST /chat/completions with invalid API key returns 401"""
        invalid_headers = {
            "Authorization": "Bearer invalid_key",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        
        response = requests.post(f"{BASE_URL}/chat/completions", headers=invalid_headers, json=payload)
        assert response.status_code == 401
    
    def test_chat_completion_missing_auth(self):
        """Test POST /chat/completions without authorization returns 401"""
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        
        response = requests.post(f"{BASE_URL}/chat/completions", json=payload)
        assert response.status_code == 401
    
    def test_chat_completion_invalid_model(self, headers):
        """Test POST /chat/completions with invalid model returns 404"""
        payload = {
            "model": "nonexistent-model",
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        assert response.status_code == 404
    
    def test_chat_completion_missing_required_fields(self, headers):
        """Test POST /chat/completions with missing required fields returns 400"""
        # Missing model
        payload = {
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        assert response.status_code == 400
        
        # Missing messages
        payload = {
            "model": "gpt-3.5-turbo"
        }
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        assert response.status_code == 400
        
        # Empty messages
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": []
        }
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        assert response.status_code == 400
    
    def test_chat_completion_invalid_message_format(self, headers):
        """Test POST /chat/completions with invalid message format returns 400"""
        # Missing role
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"content": "Hello"}
            ]
        }
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        assert response.status_code == 400
        
        # Missing content
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user"}
            ]
        }
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        assert response.status_code == 400
        
        # Invalid role
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "invalid_role", "content": "Hello"}
            ]
        }
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        assert response.status_code == 400
    
    def test_chat_completion_invalid_parameters(self, headers):
        """Test POST /chat/completions with invalid parameter values returns 400"""
        # Invalid temperature
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": -1
        }
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        assert response.status_code == 400
        
        # Invalid max_tokens
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 0
        }
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        assert response.status_code == 400
        
        # Invalid top_p
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}],
            "top_p": 2.0
        }
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        assert response.status_code == 400
    
    def test_chat_completion_malformed_json(self, headers):
        """Test POST /chat/completions with malformed JSON returns 400"""
        malformed_data = '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello"'
        
        response = requests.post(
            f"{BASE_URL}/chat/completions", 
            headers=headers, 
            data=malformed_data
        )
        check_rate_limit_and_skip(response)
        assert response.status_code == 400
    
    def test_chat_completion_response_format(self, headers):
        """Test chat completion response format validation"""
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "What is 2+2?"}
            ],
            "max_tokens": 10
        }
        
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        
        # Verify response headers
        assert "content-type" in response.headers
        content_type = response.headers["content-type"].lower()
        assert "application/json" in content_type
        
        # Verify JSON is valid
        try:
            data = response.json()
        except ValueError:
            pytest.fail("Response should contain valid JSON")
        
        # Verify response structure types
        assert isinstance(data["id"], str)
        assert isinstance(data["object"], str)
        assert isinstance(data["created"], int)
        assert isinstance(data["model"], str)
        assert isinstance(data["choices"], list)
        assert isinstance(data["usage"], dict)
        
        # Verify choice structure types
        choice = data["choices"][0]
        assert isinstance(choice["index"], int)
        assert isinstance(choice["message"], dict)
        assert isinstance(choice["finish_reason"], str)
        
        # Verify message structure types
        message = choice["message"]
        assert isinstance(message["role"], str)
        assert isinstance(message["content"], str)
    
    def test_chat_completion_content_length_validation(self, headers):
        """Test chat completion with various content lengths"""
        # Very short content
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 5
        }
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        assert response.status_code == 200
        
        # Empty content (should fail)
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": ""}]
        }
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        assert response.status_code == 400
        
        # Very long content
        long_content = "Tell me about artificial intelligence. " * 100
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": long_content}],
            "max_tokens": 50
        }
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        check_rate_limit_and_skip(response)
        # Should either succeed or return 400 for too long input
        assert response.status_code in [200, 400]