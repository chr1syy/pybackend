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

    # 3. Complete registration
    payload = {"code": code, "email": email, "username": "newuser", "password": "secret"}
    resp = requests.post(f"{BASE_URL}/complete-registration", json=payload)
    assert resp.status_code == 200

    # 4. User existiert
    user = db_session.query(User).filter_by(email=email).first()
    assert user is not None


def test_forgot_and_reset_password(db_session):
    email = "admin@example.com"
    # 1. Forgot password
    resp = requests.post(f"{BASE_URL}/forgot-password", json={"email": email})
    assert resp.status_code == 200

    # 2. Reset-Code aus DB holen
    code = db_session.query(AccessCode).filter_by(purpose="password_reset", used=False).first().code

    # 3. Reset password
    payload = {"code": code, "email": email, "new_password": "newpass123"}
    resp = requests.post(f"{BASE_URL}/reset-password", json=payload)
    assert resp.status_code == 200

    # 4. Login mit neuem Passwort
    resp = requests.post(f"{BASE_URL}/login", json={"email": email, "password": "newpass123"})
    assert resp.status_code == 200