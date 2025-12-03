import requests
import pytest
import datetime


BASE_URL = "http://localhost:8000"

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
