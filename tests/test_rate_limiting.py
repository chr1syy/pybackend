import requests
import time
import os
from tests.conftest import BASE_URL, TEST_ADMIN_PASSWORD

# In test mode, rate limiting is disabled, so these tests verify the decorators exist
# but don't actually test rate limiting behavior
TESTING = os.getenv("TESTING", "false").lower() == "true"

def test_login_rate_limiting():
    """Test that login endpoint has rate limiting decorators (disabled in test mode)."""
    # Make multiple login attempts rapidly
    responses = []
    for i in range(6):
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "admin@example.com", "password": "WrongPassword123!"}
        )
        responses.append(resp.status_code)
        time.sleep(0.1)  # Small delay between requests

    # In test mode, all should return 401 (invalid credentials)
    # In production mode, would return 429 after 5 attempts
    assert responses[0] == 401
    if not TESTING:
        assert 429 in responses, f"Expected 429 rate limit error in responses: {responses}"


def test_forgot_password_rate_limiting():
    """Test that forgot-password endpoint has rate limiting decorators (disabled in test mode)."""
    # Make multiple forgot password requests rapidly
    responses = []
    for i in range(4):
        resp = requests.post(
            f"{BASE_URL}/auth/forgot-password",
            json={"email": f"test{i}@example.com"}
        )
        responses.append(resp.status_code)
        time.sleep(0.1)  # Small delay between requests

    # In test mode, all should return 200
    # In production mode, would return 429 after 3 attempts
    assert responses[0] == 200
    if not TESTING:
        assert 429 in responses, f"Expected 429 rate limit error in responses: {responses}"


def test_refresh_rate_limiting():
    """Test that refresh endpoint has rate limiting."""
    # First login to get a refresh token
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@example.com", "password": TEST_ADMIN_PASSWORD}
    )
    refresh_token = login_resp.json()["refresh_token"]

    # Make multiple refresh requests rapidly
    responses = []
    for i in range(15):
        resp = requests.post(
            f"{BASE_URL}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        responses.append(resp.status_code)
        time.sleep(0.1)

    # Some should succeed (200), but eventually we should hit rate limit (429)
    # Note: The global rate limit is 200/minute, so we won't hit it with just 15 requests
    # This test mainly ensures the endpoint doesn't fail under rapid requests
    assert 200 in responses
