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

def check_rate_limit_and_skip(response):
    """Helper function to check for rate limit errors and skip test if encountered"""
    if response.status_code == 429:
        pytest.skip("Rate limit exceeded (HTTP 429) - skipping test")