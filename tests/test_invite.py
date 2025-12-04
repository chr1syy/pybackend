import requests
import pytest

from app.models import AccessCode, User
from app.utils.db import SessionLocal, Base, engine

@pytest.fixture(scope="function")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

BASE_URL = "http://localhost:8000/auth"

@pytest.fixture(autouse=True)
def mock_send_email(monkeypatch):
    def fake_send_email(to, subject, body):
        print(f"[MOCK] Mail an {to}: {subject} – {body}")
    monkeypatch.setattr("app.auth.routes.send_email", fake_send_email)

def test_invite_and_registration(admin_headers, db_session):
    # 1. Invite
    email = "newuser@example.com"
    resp = requests.post(f"{BASE_URL}/invite", params={"email": email}, headers=admin_headers)
    assert resp.status_code == 200

    # 2. Code aus DB holen
    code = db_session.query(AccessCode).filter_by(purpose="registration", used=False).first().code

    # 3. Complete registration with secure password
    payload = {"code": code, "email": email, "username": "newuser", "password": "SecurePass123!"}
    resp = requests.post(f"{BASE_URL}/complete-registration", json=payload)
    assert resp.status_code == 200

    # 4. User existiert
    user = db_session.query(User).filter_by(email=email).first()
    assert user is not None

    # 5. Login with new user works
    login_resp = requests.post(f"{BASE_URL}/login", json={"email": email, "password": "SecurePass123!"})
    assert login_resp.status_code == 200


def test_registration_weak_password(admin_headers, db_session):
    """Test that registration rejects weak passwords."""
    # 1. Invite
    email = "weakpass@example.com"
    resp = requests.post(f"{BASE_URL}/invite", params={"email": email}, headers=admin_headers)
    assert resp.status_code == 200

    # 2. Code aus DB holen
    code = db_session.query(AccessCode).filter_by(purpose="registration", used=False).first().code

    # 3. Try to register with weak password
    payload = {"code": code, "email": email, "username": "weakuser", "password": "weak"}
    resp = requests.post(f"{BASE_URL}/complete-registration", json=payload)
    assert resp.status_code == 422
    assert "password" in resp.json()["detail"][0]["loc"]


def test_forgot_and_reset_password(db_session):
    email = "admin@example.com"
    # 1. Forgot password - should return generic message
    resp = requests.post(f"{BASE_URL}/forgot-password", json={"email": email})
    assert resp.status_code == 200
    assert "If the email exists" in resp.json()["detail"]

    # 2. Reset-Code aus DB holen
    code = db_session.query(AccessCode).filter_by(purpose="password_reset", used=False).first().code

    # 3. Reset password with secure password
    payload = {"code": code, "email": email, "new_password": "NewSecure123!Pass"}
    resp = requests.post(f"{BASE_URL}/reset-password", json=payload)
    assert resp.status_code == 200

    # 4. Login mit neuem Passwort
    resp = requests.post(f"{BASE_URL}/login", json={"email": email, "password": "NewSecure123!Pass"})
    assert resp.status_code == 200


def test_forgot_password_nonexistent_email(db_session):
    """Test that forgot password doesn't leak information about email existence."""
    email = "nonexistent@example.com"
    resp = requests.post(f"{BASE_URL}/forgot-password", json={"email": email})
    # Should return 200 and generic message even for non-existent emails
    assert resp.status_code == 200
    assert "If the email exists" in resp.json()["detail"]