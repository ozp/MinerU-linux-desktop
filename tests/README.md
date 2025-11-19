# Test Suite for MinerU Desktop Client

This directory contains the comprehensive test suite for the MinerU Desktop Client.

## Structure

```
tests/
├── unit/               # Unit tests
│   ├── test_validators.py    # Validation logic tests
│   ├── test_client.py         # MineruClient tests
│   └── test_config.py         # Configuration tests
├── integration/        # Integration tests
│   └── test_api_integration.py # API workflow tests
├── ui/                 # UI tests
│   └── test_main_window.py    # MainWindow UI tests
└── conftest.py         # Shared fixtures
```

## Running Tests

### Install Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/ -m unit

# Integration tests only
pytest tests/integration/ -m integration

# UI tests only
pytest tests/ui/ -m ui
```

### Run with Coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

View the coverage report by opening `htmlcov/index.html` in your browser.

## Test Coverage

Current coverage statistics:

- **mineru_client.py**: 89% ✅
- **validators.py**: 93% ✅
- **exceptions.py**: 100% ✅
- **Overall target**: >80% ✅

## Test Categories

### Unit Tests

**test_validators.py** (40 tests)
- API token validation
- File path validation
- Directory path validation
- File format validation
- Batch ID validation
- Language code validation
- Model version validation

**test_client.py** (23 tests)
- Client initialization
- Configuration loading
- Header generation
- Processing options
- Batch upload functionality
- Batch status checking
- Result downloading

**test_config.py** (7 tests)
- Settings dialog initialization
- Configuration persistence
- Settings loading and saving

### Integration Tests

**test_api_integration.py** (9 tests)
- Complete upload-to-download workflow
- Failed file handling
- Authentication errors
- API error handling
- Retry behavior
- Multiple file format support

### UI Tests

**test_main_window.py** (12 tests)
- Window initialization
- File selection
- Upload worker
- Processing workflow
- Status updates
- Menu actions

## Key Features

1. **Comprehensive Coverage**: >80% code coverage achieved
2. **Mocked External Dependencies**: All API calls and file operations are mocked
3. **Isolated Tests**: Each test is independent and deterministic
4. **Custom Exceptions**: Robust error handling with custom exception classes
5. **Input Validation**: Extensive validation for all user inputs
6. **Fixtures**: Reusable test fixtures for common test data

## Writing New Tests

When adding new tests:

1. Place tests in the appropriate directory (`unit/`, `integration/`, or `ui/`)
2. Use appropriate markers (`@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.ui`)
3. Follow the existing naming convention: `test_<feature>_<scenario>`
4. Use fixtures from `conftest.py` where applicable
5. Mock external dependencies (API calls, file I/O)
6. Ensure tests are isolated and don't depend on external state

## CI/CD Integration

This test suite is designed to run in CI/CD pipelines. Note:

- UI tests require a display server (use `xvfb-run` in headless environments)
- All dependencies are specified in `requirements-dev.txt`
- Tests complete in < 3 seconds
