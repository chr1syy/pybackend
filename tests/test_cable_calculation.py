import requests
import pytest
import datetime
from tests.conftest import BASE_URL

@pytest.fixture
def project_id(admin_headers):
    """Legt ein Dummy-Projekt über den API-Endpunkt an und gibt die ID zurück."""
    payload = {
        "project_number": f"{datetime.datetime.utcnow().year}-TEST",
        "name": "Dummy Projekt",
        "description": "Projekt für CableCalculation Tests"
    }
    resp = requests.post(BASE_URL + "/projects/", json=payload, headers=admin_headers)
    assert resp.status_code == 200, resp.text
    project = resp.json()
    return project["id"]



def test_create_read_update_delete_calc(admin_headers, project_id):
    # --- Create ---
    payload = {
        "origin": "Main Distribution",
        "destination": "Subpanel A",
        "cable_type": "NYM-J",
        "cable_length_m": 100.0,
        "number_of_cables": 1,
        "total_cores": 3,
        "loaded_cores": 2,
        "cross_section_l": 2.5,
        "cross_section_pe": 2.5,
        "laying_type": "B1",
        "fuse_rating_a": 16.0,
        "nominal_current_a": 15.0
    }
    resp = requests.post(
        f"{BASE_URL}/cable_calculation/?project_id={project_id}",
        json=payload,
        headers=admin_headers
    )
    assert resp.status_code == 200
    created = resp.json()
    calc_id = created["id"]
    version = created["version"]

    # --- Read ---
    resp = requests.get(
        f"{BASE_URL}/cable_calculation/{version}?project_id={project_id}",
        headers=admin_headers
    )
    assert resp.status_code == 200
    read = resp.json()
    assert read["id"] == calc_id
    assert read["cross_section_l"] == 2.5

    # --- List Versions ---
    resp = requests.get(
        f"{BASE_URL}/cable_calculation/versions/list?project_id={project_id}",
        headers=admin_headers
    )
    assert resp.status_code == 200, resp.text
    versions = resp.json()
    assert version in versions

    # --- Update ---
    update_payload = {
        "origin": "Main Distribution",
        "destination": "Subpanel A",
        "cable_type": "NYM-J",
        "cable_length_m": 100.0,
        "number_of_cables": 1,
        "total_cores": 3,
        "loaded_cores": 2,
        "cross_section_l": 4.0,
        "cross_section_pe": 2.5,
        "laying_type": "B1",
        "fuse_rating_a": 16.0,
        "nominal_current_a": 15.0
    }
    resp = requests.put(
        f"{BASE_URL}/cable_calculation/{calc_id}?project_id={project_id}",
        json=update_payload,
        headers=admin_headers
    )
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["cross_section_l"] == 4.0
    
    # --- Delete ---
    resp = requests.delete(
        f"{BASE_URL}/cable_calculation/{calc_id}?project_id={project_id}",
        headers=admin_headers
    )
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Calculation deleted"

    # --- Verify deletion ---
    resp = requests.get(
        f"{BASE_URL}/cable_calculation/{version}?project_id={project_id}",
        headers=admin_headers
    )
    assert resp.status_code == 404


def test_cable_calculation_ownership(admin_headers, project_id, db_session):
    """Test that cable calculations are assigned an owner and follow authorization rules."""
    from app.models import AccessCode

    # Create calculation as admin
    payload = {
        "origin": "Main Distribution",
        "destination": "Subpanel A",
        "cable_type": "NYM-J",
        "cable_length_m": 100.0,
        "number_of_cables": 1,
        "total_cores": 3,
        "loaded_cores": 2,
        "cross_section_l": 2.5,
        "cross_section_pe": 2.5,
        "laying_type": "B1",
        "fuse_rating_a": 16.0,
        "nominal_current_a": 15.0
    }
    resp = requests.post(
        f"{BASE_URL}/cable_calculation/?project_id={project_id}",
        json=payload,
        headers=admin_headers
    )
    assert resp.status_code == 200
    calc_id = resp.json()["id"]

    # Create a second user
    from tests.conftest import TEST_ADMIN_PASSWORD
    email = "cableuser@example.com"

    # Invite and register user
    resp = requests.post(f"{BASE_URL}/auth/invite", params={"email": email}, headers=admin_headers)
    code = db_session.query(AccessCode).filter_by(purpose="registration", used=False).first().code

    payload_reg = {"code": code, "email": email, "username": "cableuser", "password": "Cable123!Secure"}
    requests.post(f"{BASE_URL}/auth/complete-registration", json=payload_reg)

    # Login as second user
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": "Cable123!Secure"})
    user_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # User can VIEW calculations
    version = resp.json()["version"]
    view_resp = requests.get(
        f"{BASE_URL}/cable_calculation/{version}?project_id={project_id}",
        headers=user_headers
    )
    assert view_resp.status_code == 200

    # User can UPDATE calculations
    update_payload = payload.copy()
    update_payload["cross_section_l"] = 4.0
    update_resp = requests.put(
        f"{BASE_URL}/cable_calculation/{calc_id}?project_id={project_id}",
        json=update_payload,
        headers=user_headers
    )
    assert update_resp.status_code == 200

    # User CANNOT DELETE calculation they don't own
    delete_resp = requests.delete(
        f"{BASE_URL}/cable_calculation/{calc_id}?project_id={project_id}",
        headers=user_headers
    )
    assert delete_resp.status_code == 403
    assert "Not authorized" in delete_resp.json()["detail"]

    # Admin CAN DELETE (is owner)
    delete_resp = requests.delete(
        f"{BASE_URL}/cable_calculation/{calc_id}?project_id={project_id}",
        headers=admin_headers
    )
    assert delete_resp.status_code == 200
