# conftest.py
import pytest
import subprocess
import requests
import os

BASE_URL = "http://localhost:8000"

@pytest.fixture(autouse=True)
def reset_and_seed_admin():
    """Vor jedem Test: DB zurücksetzen und Admin neu anlegen."""
    subprocess.run(["python3", "-m", "scripts.reset_db"], check=True)
    subprocess.run(["python3", "-m", "scripts.seed_test_admin"], check=True)
    yield

@pytest.fixture
def admin_headers(reset_and_seed_admin):
    """Loggt den Admin ein und gibt fertige Headers mit Access-Token zurück."""
    url = f"{BASE_URL}/auth/login"
    data = {"username": "admin", "password": "admin"}
    response = requests.post(url, data=data)
    assert response.status_code == 200
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}
