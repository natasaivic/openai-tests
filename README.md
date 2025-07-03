# OpenAI API Tests

This project contains comprehensive tests for OpenAI's API endpoints using the official OpenAPI specification. The tests are written in Python using pytest framework.

## Setup

1. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the project root:
   ```bash
   echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
   ```
   
   Alternatively, set environment variable directly:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

## Running Tests

```bash
# Run all tests
pytest

# Run tests with JUnit XML output (for TestRail integration)
pytest --junitxml=test-results.xml
```

## Project Structure

- `openapi.yaml` - OpenAI API specification
- `tests/` - Test files directory
  - `test_models.py` - Unit tests for /models endpoint
  - `test_embeddings.py` - Unit tests for /embeddings endpoint
  - `test_files.py` - Unit tests for /files endpoint
- `scripts/` - TestRail integration scripts
  - `sync_testrail.py` - Sync test cases to TestRail
  - `export_test_results.py` - Export test results to TestRail
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (API keys, TestRail config) - not tracked in git
- `.env.example` - Example environment configuration
- `.gitignore` - Git ignore file (includes .env protection)

## Test Coverage

### Models Endpoint (`/models`)
- List all models with validation
- Retrieve specific model details
- Authentication and authorization testing
- Error handling (404, 401, malformed requests)
- Field validation and type checking
- Model ID format validation
- Network timeout and server error handling

### Embeddings Endpoint (`/embeddings`)
- Create embeddings for single and multiple inputs
- Authentication and authorization testing
- Input validation (empty, null, oversized inputs)
- Model validation and error handling
- Response structure and field validation
- Encoding format testing
- Usage statistics validation

### Files Endpoint (`/files`)
- List files with filtering, pagination, and sorting
- Upload files with multipart form data handling
- Retrieve specific file information and metadata
- Download file content
- Delete files with proper cleanup
- Authentication and authorization testing
- File validation (purpose, format, size limits)
- Error handling (404, 400, 413 for file operations)
- Response structure and field validation
- Complete file lifecycle testing (upload → retrieve → delete)

## TestRail Integration

This project includes scripts for integrating with TestRail to sync test cases and export test results.

### Setup TestRail Integration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Configure your TestRail settings in `.env`:
   ```bash
   # TestRail Configuration
   TESTRAIL_URL=https://yourcompany.testrail.io
   TESTRAIL_USERNAME=your-email@company.com
   TESTRAIL_PASSWORD=your-api-key-or-password
   TESTRAIL_PROJECT_ID=1

   # Optional - if not provided, will use first available suite
   # TESTRAIL_SUITE_ID=1

   # Optional - directory containing test files (default: tests)
   # TESTRAIL_TEST_DIR=tests

   # Optional - JUnit XML file path (default: test-results.xml)
   # TESTRAIL_JUNIT_FILE=test-results.xml
   ```

### Sync Test Cases to TestRail

The sync script creates TestRail test sections and cases based on your pytest structure:

```bash
python scripts/sync_testrail.py
```

**Naming Convention:**
- Test classes become sections: `TestModelsEndpoint` → `Models Endpoint`
- Test methods become cases: `test_list_models_success` → `list_models_success`

**Example Output:**
- **Models Endpoint** section with 16 test cases
- **Embeddings Endpoint** section with 16 test cases  
- **Files Endpoint** section with 19 test cases

### Export Test Results to TestRail

After running tests with JUnit XML output, export the results to TestRail:

```bash
# 1. Run tests with JUnit XML output
pytest --junitxml=test-results.xml

# 2. Export results to TestRail
python scripts/export_test_results.py
```

**Features:**
- Automatically creates a timestamped test run
- Maps test results to existing TestRail test cases
- Includes execution time and error messages
- Handles passed, failed, and skipped test statuses
- Provides direct link to TestRail run

### Complete Workflow

```bash
# 1. Sync test cases to TestRail (one-time setup)
python scripts/sync_testrail.py

# 2. Run tests and export results
pytest --junitxml=test-results.xml
python scripts/export_test_results.py
```