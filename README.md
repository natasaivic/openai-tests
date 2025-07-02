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
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (API keys) - not tracked in git
- `.gitignore` - Git ignore file (includes .env protection) 