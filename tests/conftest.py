import pytest
import subprocess
import requests

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session", autouse=True)
def seed_admin():
    """Führt das Seed-Skript aus, bevor Tests starten."""
    subprocess.run(["python3", "seed_admin.py"], check=True)
    yield
    # Nach Tests: Admin bleibt bestehen, keine Löschung nötig

@pytest.fixture
def admin_tokens(seed_admin):
    """Loggt den Admin ein und gibt Access/Refresh zurück."""
    url = f"{BASE_URL}/auth/login"
    data = {"username": "admin", "password": "admin"}
    response = requests.post(url, data=data)
    assert response.status_code == 200
    return response.json()
