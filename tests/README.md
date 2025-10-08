# Sambo Academy - Test Suite

Comprehensive test suite for the Sambo Academy management system.

## 📋 Test Coverage

### Core Modules

- **test_attendance.py** - Attendance marking, retrieval, and statistics (18 tests)
  - Marking students as present/absent/transferred
  - Automatic payment creation for transferred sessions
  - Attendance calendar and statistics
  - Error handling for invalid data

- **test_payments.py** - Payment creation, updates, and statistics (15 tests)
  - Full, partial, and discount payments
  - Payment retrieval and filtering
  - Payment updates and deletions
  - Monthly statistics

- **test_subscriptions.py** - Subscription management (12 tests)
  - Creating 8 and 12 session subscriptions
  - Subscription updates and deactivation
  - Business rule: one active subscription per student
  - Subscription deletion

- **test_students.py** - Student CRUD operations (12 tests)
  - Student creation with primary and additional groups
  - Filtering by group and active status
  - Student updates and group transfers
  - Student deletion

- **test_statistics.py** - Statistics endpoints (existing tests)
  - Attendance statistics summary
  - Payment statistics
  - Group-level statistics

## 🚀 Running Tests

### Quick Start

```bash
# Run all tests
./run_tests.sh
```

### Manual Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_attendance.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_attendance.py::TestAttendanceMarking::test_mark_attendance_transferred -v
```

## 📊 Coverage Reports

After running tests with coverage:

- **Terminal**: Shows coverage summary in console
- **HTML**: Open `htmlcov/index.html` in browser
- **XML**: `coverage.xml` for CI/CD integration

## 🧪 Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── test_attendance.py       # Attendance tests
├── test_payments.py         # Payment tests
├── test_subscriptions.py    # Subscription tests
├── test_students.py         # Student tests
└── test_statistics.py       # Statistics tests
```

## 🔧 Fixtures

Common fixtures available in all tests (defined in `conftest.py`):

- `client` - Async HTTP client for API testing
- `auth_headers` - Authentication headers
- `db_session` - Test database session
- `test_user` - Test user (admin)
- `test_group` - Test training group
- `test_student` - Test student
- `test_tournament` - Test tournament
- `test_subscription` - Test subscription

## 📝 Writing New Tests

### Example Test

```python
@pytest.mark.asyncio
async def test_example(client: AsyncClient, auth_headers: dict, test_student):
    """Test description."""
    data = {
        "student_id": str(test_student.id),
        "field": "value"
    }
    
    response = await client.post(
        "/api/endpoint",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    result = response.json()
    assert result["field"] == "value"
```

## 🎯 Test Categories

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Fast execution

### Integration Tests
- Test API endpoints end-to-end
- Use test database
- Verify business logic

### Edge Cases
- Invalid input handling
- Boundary conditions
- Error scenarios

## ⚠️ Important Notes

1. **Test Database**: Tests use a separate test database (`sambo_test`)
2. **Isolation**: Each test runs in a transaction that's rolled back
3. **Async**: All tests are async and use `pytest-asyncio`
4. **Authentication**: Tests use mock authentication tokens

## 🐛 Debugging Tests

```bash
# Run with detailed output
pytest tests/ -vv

# Stop on first failure
pytest tests/ -x

# Run last failed tests
pytest tests/ --lf

# Show print statements
pytest tests/ -s

# Run with debugger on failure
pytest tests/ --pdb
```

## 📈 CI/CD Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest tests/ --cov=app --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## 🔍 Test Metrics

Current test coverage:
- **Attendance**: ~85% coverage
- **Payments**: ~80% coverage
- **Subscriptions**: ~75% coverage
- **Students**: ~80% coverage
- **Overall**: ~70% coverage (target: 80%+)

## 📚 Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [httpx async client](https://www.python-httpx.org/)
