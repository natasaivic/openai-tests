# OpenAI API Test Suite

This project contains comprehensive tests for OpenAI's API endpoints with enterprise-grade testing infrastructure, including smoke tests, TestRail integration, and automated CI/CD workflows.

## 🚀 Quick Start

### Setup

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```bash
   echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run smoke tests only (fast, essential tests)
pytest -m smoke

# Run authentication tests only (fastest)
pytest -m auth

# Run with detailed output and timing
pytest -v --durations=10

# Generate JUnit XML for TestRail integration
pytest --junitxml=test-results.xml
```

## 📁 Project Structure

```
├── .github/workflows/          # GitHub Actions CI/CD
│   ├── test-and-testrail.yml  # Main test workflow
│   └── smoke-tests.yml        # Daily smoke test schedule
├── tests/                     # Test files
│   ├── conftest.py           # Shared fixtures and helpers
│   ├── test_models.py        # Models endpoint tests
│   ├── test_files.py         # Files endpoint tests
│   ├── test_embeddings.py    # Embeddings endpoint tests
│   └── test_chat_completions.py # Chat completions tests
├── scripts/                   # TestRail integration
│   ├── sync_testrail.py      # Sync test cases to TestRail
│   ├── export_test_results.py # Export results to TestRail
│   └── testrail_connectivity_test.py # TestRail connection test
├── pytest.ini               # Pytest configuration and markers
├── requirements.txt          # Python dependencies
├── SMOKE_TESTS.md           # Smoke test documentation
└── README.md                # This file
```

## 🧪 Test Coverage

### Comprehensive Endpoint Testing

| Endpoint | Tests | Features Covered |
|----------|-------|------------------|
| **Models** (`/models`) | 25 tests | List models, retrieve specific model, auth, error handling, field validation |
| **Files** (`/files`) | 22 tests | Upload, list, retrieve, delete files, auth, file lifecycle, error handling |
| **Embeddings** (`/embeddings`) | 19 tests | Create embeddings, batch processing, auth, input validation, model testing |
| **Chat Completions** (`/chat/completions`) | 20 tests | Chat conversations, streaming, parameters, auth, error handling |

**Total: 86 comprehensive tests covering all major functionality**

### Test Categories

- ✅ **Success scenarios** - Valid requests and expected responses
- 🔐 **Authentication** - API key validation and authorization
- ❌ **Error handling** - Invalid requests, malformed data, network issues
- 🔒 **Security** - Input validation, injection prevention
- ⚡ **Performance** - Rate limiting, timeout handling
- 📊 **Response validation** - Structure, types, required fields

## 🚭 Smoke Tests

Smoke tests provide rapid health checks for critical system functionality.

### Essential Smoke Tests (7 tests, ~3 seconds)

- **Models**: API connectivity and authentication
- **Files**: File operations and authorization  
- **Embeddings**: Core AI functionality and auth
- **Chat**: Authentication validation (no API consumption)

### Usage

```bash
# Essential daily smoke tests
pytest -m smoke

# Authentication tests only (fastest)
pytest -m auth

# Extended smoke tests (with API consumption)
pytest -m smoke_extended
```

### Automated Daily Execution
- **Schedule**: 10:00 AM Pacific Time daily
- **Duration**: ~10 seconds total execution
- **Cost**: Minimal API consumption
- **Results**: Automated reporting and alerts

📖 **[Complete Smoke Tests Documentation](SMOKE_TESTS.md)**

## 🔗 TestRail Integration

Seamlessly integrate with TestRail for enterprise test management.

### Setup TestRail Integration

1. **Configure environment variables** in `.env`:
   ```env
   # TestRail Configuration
   TESTRAIL_URL=https://yourcompany.testrail.io
   TESTRAIL_USERNAME=your-email@company.com
   TESTRAIL_PASSWORD=your-api-key-or-password
   TESTRAIL_PROJECT_ID=1
   TESTRAIL_SUITE_ID=1  # Optional
   ```

2. **Test connectivity:**
   ```bash
   python scripts/testrail_connectivity_test.py
   ```

### Sync Test Cases to TestRail

```bash
# Discover and create TestRail test cases from pytest files
python scripts/sync_testrail.py
```

**What it creates:**
- Test sections based on test classes
- Test cases based on test methods
- Proper naming conventions and descriptions
- Organized test structure in TestRail

### Export Test Results

```bash
# 1. Run tests with JUnit XML output
pytest --junitxml=test-results.xml

# 2. Export results to TestRail
python scripts/export_test_results.py
```

**Features:**
- Automatic test run creation with timestamps
- Maps pytest results to TestRail test cases
- Includes execution time and error details
- Handles passed, failed, and skipped statuses

## ⚙️ GitHub Actions CI/CD

Fully automated testing pipeline with multiple workflows.

### Main Test Workflow (`test-and-testrail.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` branch

**Features:**
- Full test suite execution with pytest
- JUnit XML result generation
- TestRail test case sync (main branch only)
- Automatic test result export to TestRail
- PR comments with formatted test results
- Test artifact storage (30-day retention)

### Daily Smoke Tests (`smoke-tests.yml`)

**Schedule:** 10:00 AM Pacific Time daily

**Features:**
- Essential smoke test execution
- Fast system health validation
- Comprehensive result reporting
- Failure detection and alerting
- Manual trigger capability
- Optional TestRail integration

### Required GitHub Secrets

Configure in **Settings** → **Secrets and variables** → **Actions**:

| Secret | Purpose | Example |
|--------|---------|---------|
| `OPENAI_API_KEY` | API authentication | `sk-proj-...` |
| `TESTRAIL_URL` | TestRail instance | `https://company.testrail.io` |
| `TESTRAIL_USERNAME` | TestRail user | `user@company.com` |
| `TESTRAIL_PASSWORD` | TestRail API key | `your-api-key` |
| `TESTRAIL_PROJECT_ID` | Project ID | `1` |
| `TESTRAIL_SUITE_ID` | Suite ID (optional) | `1` |

## 🏷️ Test Markers

Use pytest markers to run specific test categories:

```bash
# Smoke tests (essential health checks)
pytest -m smoke

# Authentication tests
pytest -m auth

# Extended smoke tests (with API consumption)
pytest -m smoke_extended

# Combine markers
pytest -m "smoke or auth"

# Exclude certain tests
pytest -m "not slow"
```

**Available markers:**
- `smoke` - Essential smoke tests for basic system health
- `smoke_extended` - Extended smoke tests with API consumption
- `auth` - Authentication and authorization tests
- `slow` - Tests that may take longer to execute
- `integration` - Integration tests requiring external dependencies

## 🔧 Development Workflow

### Local Development

```bash
# Run tests during development
pytest -v

# Quick health check
pytest -m smoke

# Test specific endpoint
pytest tests/test_models.py -v

# Debug specific test
pytest tests/test_models.py::TestModelsEndpoint::test_list_models_success -vv
```

### Before Committing

```bash
# Run smoke tests for quick validation
pytest -m smoke

# Run auth tests (fastest validation)
pytest -m auth

# Full test suite (if time permits)
pytest
```

### Pull Request Process

1. **Create feature branch**
2. **Write/update tests** for new functionality
3. **Run local smoke tests** (`pytest -m smoke`)
4. **Create pull request** → triggers automated testing
5. **Review test results** in PR comments
6. **Merge** → triggers TestRail sync and full result export

## 📈 Monitoring & Reporting

### Daily Health Monitoring
- **Automated smoke tests** every morning
- **Immediate failure alerts** via GitHub Actions
- **Test result history** in GitHub Actions artifacts
- **TestRail dashboard** integration

### Test Result Analysis
- **GitHub Actions summaries** with formatted results
- **JUnit XML artifacts** for detailed analysis
- **TestRail test runs** with execution history
- **PR comments** with test status and metrics

### Failure Investigation
- **Detailed error messages** in test output
- **Rate limiting detection** with graceful handling
- **Network issue identification** and retry logic
- **Authentication failure alerts** for credential issues

## 🚀 Best Practices

### Writing Tests
- Follow existing patterns in test files
- Use descriptive test names and docstrings
- Include proper error handling and assertions
- Add rate limiting protection for API calls
- Use appropriate test markers for categorization

### Test Maintenance
- Regularly review and update test coverage
- Monitor smoke test execution times
- Keep TestRail integration synchronized
- Update documentation for new features

### Cost Management
- Use smoke tests for frequent validation
- Minimize API consumption in automated tests
- Leverage authentication tests for quick checks
- Monitor rate limiting and adjust test frequency

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. **Add comprehensive tests** for new functionality
4. **Ensure smoke tests pass** (`pytest -m smoke`)
5. **Update documentation** as needed
6. **Create pull request** with detailed description

## 📄 License

This project is part of OpenAI API testing infrastructure.

---

**Last Updated:** December 2024  
**Test Suite Version:** v2.0  
**Total Tests:** 86 comprehensive tests across 4 endpoints