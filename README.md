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
pytest
```

## Project Structure

- `openapi.yaml` - OpenAI API specification
- `tests/` - Test files directory
  - `test_models.py` - Unit tests for /models endpoint
  - `test_embeddings.py` - Unit tests for /embeddings endpoint
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (API keys) - not tracked in git
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