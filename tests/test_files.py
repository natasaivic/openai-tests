import pytest
import requests
import io
import json
from conftest import BASE_URL, check_rate_limit_and_skip

class TestFilesEndpoint:
    """Test cases for /files endpoint operations"""
    
    @pytest.mark.smoke
    def test_list_files_success(self, headers):
        """Test GET /files returns list of files"""
        response = requests.get(f"{BASE_URL}/files", headers=headers)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "object" in data
        assert "data" in data
        assert data["object"] == "list"
        assert isinstance(data["data"], list)
        
        # If files exist, verify file object structure
        if data["data"]:
            file_obj = data["data"][0]
            assert "id" in file_obj
            assert "object" in file_obj
            assert "bytes" in file_obj
            assert "created_at" in file_obj
            assert "filename" in file_obj
            assert "purpose" in file_obj
            assert file_obj["object"] == "file"
    
    def test_list_files_with_purpose_filter(self, headers):
        """Test GET /files with purpose parameter"""
        response = requests.get(f"{BASE_URL}/files?purpose=fine-tune", headers=headers)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["object"] == "list"
        assert isinstance(data["data"], list)
        
        # Verify all returned files have the specified purpose
        for file_obj in data["data"]:
            assert file_obj["purpose"] == "fine-tune"
    
    def test_list_files_with_pagination(self, headers):
        """Test GET /files with limit parameter"""
        response = requests.get(f"{BASE_URL}/files?limit=5", headers=headers)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["object"] == "list"
        assert isinstance(data["data"], list)
        assert len(data["data"]) <= 5
    
    def test_list_files_with_order(self, headers):
        """Test GET /files with order parameter"""
        response = requests.get(f"{BASE_URL}/files?order=asc", headers=headers)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["object"] == "list"
        assert isinstance(data["data"], list)
        
        # Verify ascending order if multiple files exist
        if len(data["data"]) > 1:
            timestamps = [file_obj["created_at"] for file_obj in data["data"]]
            assert timestamps == sorted(timestamps)
    
    def test_upload_file_success(self, headers):
        """Test POST /files uploads file successfully"""
        # Create a test JSONL file
        test_data = {"text": "This is a test file for fine-tuning"}
        file_content = json.dumps(test_data) + "\n"
        
        files = {
            'file': ('test_data.jsonl', io.StringIO(file_content), 'application/jsonl'),
            'purpose': (None, 'fine-tune')
        }
        
        # Remove Content-Type header for multipart upload
        upload_headers = {k: v for k, v in headers.items() if k != 'Content-Type'}
        
        response = requests.post(f"{BASE_URL}/files", headers=upload_headers, files=files)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "object" in data
        assert "bytes" in data
        assert "created_at" in data
        assert "filename" in data
        assert "purpose" in data
        
        assert data["object"] == "file"
        assert data["filename"] == "test_data.jsonl"
        assert data["purpose"] == "fine-tune"
        assert data["bytes"] > 0
    
    def test_upload_file_missing_purpose(self, headers):
        """Test POST /files without purpose returns 400"""
        test_data = {"text": "Test data"}
        file_content = json.dumps(test_data) + "\n"
        
        files = {
            'file': ('test_data.jsonl', io.StringIO(file_content), 'application/jsonl')
        }
        
        upload_headers = {k: v for k, v in headers.items() if k != 'Content-Type'}
        
        response = requests.post(f"{BASE_URL}/files", headers=upload_headers, files=files)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 400
    
    def test_upload_file_missing_file(self, headers):
        """Test POST /files without file returns 400"""
        data = {'purpose': 'fine-tune'}
        
        upload_headers = {k: v for k, v in headers.items() if k != 'Content-Type'}
        
        response = requests.post(f"{BASE_URL}/files", headers=upload_headers, data=data)
        
        assert response.status_code == 400
    
    def test_upload_file_invalid_purpose(self, headers):
        """Test POST /files with invalid purpose"""
        test_data = {"text": "Test data"}
        file_content = json.dumps(test_data) + "\n"
        
        files = {
            'file': ('test_data.jsonl', io.StringIO(file_content), 'application/jsonl'),
            'purpose': (None, 'invalid-purpose')
        }
        
        upload_headers = {k: v for k, v in headers.items() if k != 'Content-Type'}
        
        response = requests.post(f"{BASE_URL}/files", headers=upload_headers, files=files)
        check_rate_limit_and_skip(response)
        
        assert response.status_code in [400, 422]
    
    def test_retrieve_file_success(self, headers):
        """Test GET /files/{file_id} retrieves file info"""
        # First upload a file to get a valid file_id
        test_data = {"text": "Test file for retrieval"}
        file_content = json.dumps(test_data) + "\n"
        
        files = {
            'file': ('retrieve_test.jsonl', io.StringIO(file_content), 'application/jsonl'),
            'purpose': (None, 'fine-tune')
        }
        
        upload_headers = {k: v for k, v in headers.items() if k != 'Content-Type'}
        upload_response = requests.post(f"{BASE_URL}/files", headers=upload_headers, files=files)
        check_rate_limit_and_skip(upload_response)
        
        if upload_response.status_code != 200:
            pytest.skip("Could not upload file for retrieval test")
        
        file_id = upload_response.json()["id"]
        
        # Now retrieve the file
        response = requests.get(f"{BASE_URL}/files/{file_id}", headers=headers)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == file_id
        assert data["object"] == "file"
        assert data["filename"] == "retrieve_test.jsonl"
        assert data["purpose"] == "fine-tune"
    
    def test_retrieve_file_not_found(self, headers):
        """Test GET /files/{file_id} with non-existent file returns 404"""
        response = requests.get(f"{BASE_URL}/files/file-nonexistent", headers=headers)
        
        assert response.status_code == 404
    
    def test_retrieve_file_content_success(self, headers):
        """Test GET /files/{file_id}/content retrieves file content"""
        # First upload a file
        test_data = {"text": "Content retrieval test"}
        file_content = json.dumps(test_data) + "\n"
        
        files = {
            'file': ('content_test.jsonl', io.StringIO(file_content), 'application/jsonl'),
            'purpose': (None, 'fine-tune')
        }
        
        upload_headers = {k: v for k, v in headers.items() if k != 'Content-Type'}
        upload_response = requests.post(f"{BASE_URL}/files", headers=upload_headers, files=files)
        check_rate_limit_and_skip(upload_response)
        
        if upload_response.status_code != 200:
            pytest.skip("Could not upload file for content retrieval test")
        
        file_id = upload_response.json()["id"]
        
        # Retrieve file content
        response = requests.get(f"{BASE_URL}/files/{file_id}/content", headers=headers)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        
        # Content should match what we uploaded
        content = response.text.strip()
        assert json.loads(content)["text"] == "Content retrieval test"
    
    def test_retrieve_file_content_not_found(self, headers):
        """Test GET /files/{file_id}/content with non-existent file returns 404"""
        response = requests.get(f"{BASE_URL}/files/file-nonexistent/content", headers=headers)
        
        assert response.status_code == 404
    
    def test_delete_file_success(self, headers):
        """Test DELETE /files/{file_id} deletes file successfully"""
        # First upload a file
        test_data = {"text": "File to be deleted"}
        file_content = json.dumps(test_data) + "\n"
        
        files = {
            'file': ('delete_test.jsonl', io.StringIO(file_content), 'application/jsonl'),
            'purpose': (None, 'fine-tune')
        }
        
        upload_headers = {k: v for k, v in headers.items() if k != 'Content-Type'}
        upload_response = requests.post(f"{BASE_URL}/files", headers=upload_headers, files=files)
        check_rate_limit_and_skip(upload_response)
        
        if upload_response.status_code != 200:
            pytest.skip("Could not upload file for deletion test")
        
        file_id = upload_response.json()["id"]
        
        # Delete the file
        response = requests.delete(f"{BASE_URL}/files/{file_id}", headers=headers)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == file_id
        assert data["object"] == "file"
        assert data["deleted"] is True
    
    def test_delete_file_not_found(self, headers):
        """Test DELETE /files/{file_id} with non-existent file returns 404"""
        response = requests.delete(f"{BASE_URL}/files/file-nonexistent", headers=headers)
        
        assert response.status_code == 404
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_files_unauthorized(self):
        """Test /files endpoints with invalid API key return 401"""
        invalid_headers = {
            "Authorization": "Bearer invalid_key",
            "Content-Type": "application/json"
        }
        
        # Test list files
        response = requests.get(f"{BASE_URL}/files", headers=invalid_headers)
        assert response.status_code == 401
        
        # Test retrieve file
        response = requests.get(f"{BASE_URL}/files/file-test", headers=invalid_headers)
        assert response.status_code == 401
        
        # Test delete file
        response = requests.delete(f"{BASE_URL}/files/file-test", headers=invalid_headers)
        assert response.status_code == 401
    
    def test_files_missing_auth(self):
        """Test /files endpoints without authorization return 401"""
        headers = {"Content-Type": "application/json"}
        
        # Test list files
        response = requests.get(f"{BASE_URL}/files", headers=headers)
        assert response.status_code == 401
        
        # Test retrieve file
        response = requests.get(f"{BASE_URL}/files/file-test", headers=headers)
        assert response.status_code == 401
        
        # Test delete file
        response = requests.delete(f"{BASE_URL}/files/file-test", headers=headers)
        assert response.status_code == 401
    
    def test_upload_large_file_limit(self, headers):
        """Test file upload size limits"""
        # Create a file that's larger than typical but still within reasonable test limits
        large_content = '{"text": "' + "x" * 10000 + '"}\n'
        
        files = {
            'file': ('large_test.jsonl', io.StringIO(large_content), 'application/jsonl'),
            'purpose': (None, 'fine-tune')
        }
        
        upload_headers = {k: v for k, v in headers.items() if k != 'Content-Type'}
        
        response = requests.post(f"{BASE_URL}/files", headers=upload_headers, files=files)
        check_rate_limit_and_skip(response)
        
        # Should either succeed or fail with appropriate error
        assert response.status_code in [200, 400, 413]
        
        if response.status_code == 200:
            # If successful, verify the file was uploaded with correct size
            data = response.json()
            assert data["bytes"] >= len(large_content.encode())
    
    def test_file_response_headers(self, headers):
        """Test that file responses contain proper headers"""
        response = requests.get(f"{BASE_URL}/files", headers=headers)
        check_rate_limit_and_skip(response)
        
        assert response.status_code == 200
        assert "content-type" in response.headers
        content_type = response.headers["content-type"].lower()
        assert "application/json" in content_type
        
        try:
            response.json()
        except ValueError:
            pytest.fail("Response should contain valid JSON")
    
    def test_file_field_validation(self, headers):
        """Test that file response contains required fields with correct types"""
        response = requests.get(f"{BASE_URL}/files", headers=headers)
        check_rate_limit_and_skip(response)
        assert response.status_code == 200
        
        data = response.json()
        
        # Validate top-level response structure
        assert isinstance(data["object"], str)
        assert isinstance(data["data"], list)
        
        # If files exist, validate file object structure
        if data["data"]:
            file_obj = data["data"][0]
            assert isinstance(file_obj["id"], str)
            assert isinstance(file_obj["object"], str)
            assert isinstance(file_obj["bytes"], int)
            assert isinstance(file_obj["created_at"], int)
            assert isinstance(file_obj["filename"], str)
            assert isinstance(file_obj["purpose"], str)
            
            # Validate field values
            assert file_obj["object"] == "file"
            assert file_obj["bytes"] >= 0
            assert file_obj["created_at"] > 0
            assert len(file_obj["filename"]) > 0
            assert len(file_obj["purpose"]) > 0