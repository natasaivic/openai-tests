# Smoke Tests Documentation

## Overview

Smoke tests are a subset of essential tests that validate core system functionality quickly and reliably. They serve as a daily health check for the OpenAI API integration.

## Test Categories

### Essential Smoke Tests (`@pytest.mark.smoke`)
These tests run daily at 10 AM UTC and complete in under 5 seconds:

| Endpoint | Test | Purpose | Execution Time |
|----------|------|---------|----------------|
| **Models** | `test_list_models_success` | Core API connectivity | ~0.7s |
| **Models** | `test_list_models_unauthorized` | Authentication validation | ~0.3s |
| **Files** | `test_list_files_success` | Files endpoint health | ~0.5s |
| **Files** | `test_files_unauthorized` | Comprehensive auth test | ~0.7s |
| **Embeddings** | `test_create_embedding_success` | Core AI functionality | ~0.6s |
| **Embeddings** | `test_create_embedding_unauthorized` | Auth validation | ~0.1s |
| **Chat** | `test_chat_completion_unauthorized` | Auth only (no consumption) | ~0.2s |

**Total: 7 tests, ~3.1 seconds execution time**

### Extended Smoke Tests (`@pytest.mark.smoke_extended`)
These tests include API consumption and are available for manual execution:

| Endpoint | Test | Purpose | Notes |
|----------|------|---------|-------|
| **Chat** | `test_chat_completion_success` | Full chat functionality | Consumes API tokens |

### Authentication Tests (`@pytest.mark.auth`)
Fast tests that validate authentication across all endpoints (~1.2 seconds):

- All unauthorized tests from each endpoint
- No API consumption
- Critical for detecting auth system issues

## Usage Commands

### Run Essential Smoke Tests
```bash
# Daily automated tests (fast, minimal consumption)
pytest -m smoke

# With verbose output and timing
pytest -m smoke -v --durations=0
```

### Run Authentication Tests Only
```bash
# Fastest health check (no API consumption)
pytest -m auth

# Perfect for pre-deployment validation
pytest -m auth --tb=short
```

### Run Extended Smoke Tests
```bash
# Include API consumption tests
pytest -m smoke_extended

# Run both essential and extended
pytest -m "smoke or smoke_extended"
```

### Combine Markers
```bash
# Run all smoke tests except chat completions
pytest -m "smoke and not chat"

# Run only models and files smoke tests
pytest -m "smoke" tests/test_models.py tests/test_files.py
```

## Automated Execution

### Daily Schedule
- **Time**: 10:00 AM Pacific Time daily (PDT/PST)
- **Trigger**: GitHub Actions cron job
- **Tests**: Essential smoke tests only (`@pytest.mark.smoke`)
- **Duration**: ~10 seconds total (including setup)
- **Note**: During PST (Nov-Mar), tests run at 9:00 AM due to UTC scheduling

### Manual Trigger
You can manually trigger smoke tests via GitHub Actions:
1. Go to Actions tab in GitHub
2. Select "Daily Smoke Tests" workflow
3. Click "Run workflow"
4. Choose test type: `smoke`, `smoke_extended`, or `auth`

## Test Results & Reporting

### Success Criteria
- ✅ **All Passed**: System is healthy
- ⚠️ **Some Skipped**: Rate limiting (acceptable)
- ❌ **Any Failed**: System health issue detected

### Failure Indicators
| Failure Pattern | Likely Cause | Action Required |
|----------------|--------------|-----------------|
| All auth tests fail | API key issue | Check credentials |
| Models tests fail | API connectivity | Check network/DNS |
| Embeddings fail | AI service issue | Check OpenAI status |
| Files tests fail | Storage service issue | Check file operations |

### Artifacts
- **Test Results**: JUnit XML format stored for 7 days
- **TestRail Integration**: Automatic export (if configured)
- **GitHub Summary**: Formatted results in workflow summary

## Configuration

### Pytest Configuration
Custom markers are defined in `pytest.ini`:
```ini
markers =
    smoke: Essential smoke tests for basic system health (fast execution)
    smoke_extended: Extended smoke tests with API consumption (slower execution)
    auth: Authentication and authorization tests
```

### Environment Variables
Required for smoke test execution:
- `OPENAI_API_KEY`: Valid OpenAI API key with appropriate permissions

### GitHub Secrets
For automated execution:
- `OPENAI_API_KEY`: API key for testing
- `TESTRAIL_*`: TestRail integration (optional)

## Best Practices

### When to Use Smoke Tests
- **Daily monitoring**: Automated daily health checks
- **Pre-deployment**: Quick validation before releases
- **Incident response**: Fast system health assessment
- **Development**: Quick feedback during development

### When NOT to Use Smoke Tests
- **Comprehensive testing**: Use full test suite instead
- **Performance testing**: Use dedicated performance tests
- **Load testing**: Smoke tests are not designed for load

### Troubleshooting

#### Common Issues
1. **Rate Limiting (429 errors)**
   - Normal behavior, tests will skip gracefully
   - No action required

2. **Authentication Failures**
   - Check API key validity
   - Verify environment variable setup

3. **Network Issues**
   - Check connectivity to api.openai.com
   - Verify DNS resolution

#### Debug Commands
```bash
# Run with maximum verbosity
pytest -m smoke -vv --tb=long

# Run single test for debugging
pytest tests/test_models.py::TestModelsEndpoint::test_list_models_success -v

# Collect tests without running
pytest --collect-only -m smoke
```

## Integration with CI/CD

The smoke tests integrate seamlessly with your development workflow:

1. **Daily Health Checks**: Automated morning validation
2. **Quick Feedback**: Results available within minutes
3. **Failure Alerts**: Immediate notification of system issues
4. **Minimal Cost**: Designed to minimize API consumption
5. **TestRail Sync**: Automatic test management integration

## Maintenance

### Adding New Smoke Tests
1. Identify critical functionality for new endpoints
2. Add `@pytest.mark.smoke` to essential tests
3. Ensure tests complete quickly (<2 seconds each)
4. Minimize API consumption where possible
5. Update this documentation

### Removing Smoke Tests
1. Remove marker from test
2. Update this documentation
3. Consider impact on daily monitoring coverage

---

*Last Updated: $(date)*
*Test Suite Version: v1.0*