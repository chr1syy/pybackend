# conftest.py
import pytest
import subprocess
import requests
import os
import sys

# Set TESTING environment variable before any imports
os.environ["TESTING"] = "true"

BASE_URL = "http://localhost:8000"
# Test admin password that meets security requirements
TEST_ADMIN_PASSWORD = "TestAdmin123!Secure"

# Get the Python executable from the virtual environment
VENV_PYTHON = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".venv", "bin", "python3")
# Fallback to system python if venv doesn't exist
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

@pytest.fixture(autouse=True)
def reset_and_seed_admin():
    """Vor jedem Test: DB zurücksetzen und Admin neu anlegen."""
    subprocess.run([VENV_PYTHON, "-m", "scripts.reset_db"], check=True)
    subprocess.run([VENV_PYTHON, "-m", "scripts.seed_admin_test"], check=True)
    yield

@pytest.fixture
def admin_headers(reset_and_seed_admin):
    """Loggt den Admin ein und gibt fertige Headers mit Access-Token zurück."""
    url = f"{BASE_URL}/auth/login"
    data = {"email": "admin@example.com", "password": TEST_ADMIN_PASSWORD}
    response = requests.post(url, json=data)
    assert response.status_code == 200
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}
