# How to Run Tests

The test suite requires the backend server to be running with rate limiting disabled.

## Option 1: Quick Test Run (Restart Server with TESTING=true)

1. Stop the currently running backend server (Ctrl+C in the terminal where it's running)

2. Start the backend with TESTING environment variable:
```bash
cd pybackend
TESTING=true .venv/bin/uvicorn app.main:app --reload
```

3. In another terminal, run the tests:
```bash
cd pybackend
.venv/bin/python3 -m pytest tests/ -v
```

## Option 2: Use the Test Runner Script

```bash
cd pybackend
./run_tests.sh tests/ -v
```

**Note:** The backend must be restarted with `TESTING=true` first!

## Option 3: Run Individual Test Files (if rate limiting is an issue)

```bash
# Security headers
.venv/bin/python3 -m pytest tests/test_security_headers.py -v

# Password validation
.venv/bin/python3 -m pytest tests/test_password.py -v

# Projects and ownership
.venv/bin/python3 -m pytest tests/test_projects.py -v

# Auth flow
.venv/bin/python3 -m pytest tests/test_auth_flow.py -v

# And so on...
```

## For CI/CD

In your CI/CD pipeline, make sure to:

1. Set `TESTING=true` environment variable before starting the server
2. Wait for the server to be ready
3. Run pytest

Example GitHub Actions:
```yaml
- name: Start FastAPI server
  env:
    TESTING: "true"
  run: |
    uvicorn app.main:app &
    sleep 5  # Wait for server to start

- name: Run tests
  run: |
    pytest tests/ -v
```

## Current Test Status

When running with TESTING=true (rate limiting disabled):
- **Total Tests**: 45
- **Expected**: All tests should pass
- **Security Features Tested**:
  - Authentication & Authorization
  - Password Validation
  - Rate Limiting (structure, not actual limits)
  - Ownership & Collaborative Access
  - Security Headers
  - SQL Injection Prevention
  - Audit Logging
