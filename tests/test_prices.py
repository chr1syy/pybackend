import requests
import pytest

BASE_URL = "http://localhost:8000/prices"

def test_category_article_price_flow(admin_headers):
    # --- Category: Create ---
    cat_payload = {"name": "Elektro"}
    resp = requests.post(f"{BASE_URL}/categories", json=cat_payload, headers=admin_headers)
    assert resp.status_code == 200
    category = resp.json()
    cat_id = category["id"]

    # --- Category: List ---
    resp = requests.get(f"{BASE_URL}/categories", headers=admin_headers)
    assert resp.status_code == 200
    categories = resp.json()
    assert any(c["id"] == cat_id for c in categories)

    # --- Category: Update ---
    update_payload = {"name": "Elektrotechnik"}
    resp = requests.put(f"{BASE_URL}/categories/{cat_id}", json=update_payload, headers=admin_headers)
    assert resp.status_code == 200
    updated_cat = resp.json()
    assert updated_cat["name"] == "Elektrotechnik"

    # --- Article: Create ---
    art_payload = {"name": "NYM-J 3x1.5", "category_id": cat_id}
    resp = requests.post(f"{BASE_URL}/articles", json=art_payload, headers=admin_headers)
    assert resp.status_code == 200
    article = resp.json()
    art_id = article["id"]

    # --- Article: List by Category ---
    resp = requests.get(f"{BASE_URL}/categories/{cat_id}/articles", headers=admin_headers)
    assert resp.status_code == 200
    articles = resp.json()
    assert any(a["id"] == art_id for a in articles)

    # --- Article: Update ---
    art_update = {"name": "NYM-J 3x2.5", "category_id": cat_id}
    resp = requests.put(f"{BASE_URL}/articles/{art_id}", json=art_update, headers=admin_headers)
    assert resp.status_code == 200
    updated_art = resp.json()
    assert updated_art["name"] == "NYM-J 3x2.5"

    # --- Price: Create ---
    price_payload = {"price": 0.45, "date": "2025-12-03", "article_id": art_id}
    resp = requests.post(f"{BASE_URL}/prices", json=price_payload, headers=admin_headers)
    assert resp.status_code == 200
    price = resp.json()
    price_id = price["id"]

    # --- Price: List by Article ---
    resp = requests.get(f"{BASE_URL}/articles/{art_id}/prices", headers=admin_headers)
    assert resp.status_code == 200
    prices = resp.json()
    assert any(p["id"] == price_id for p in prices)

    # --- Price: Delete ---
    resp = requests.delete(f"{BASE_URL}/prices/{price_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Price deleted"

    # --- Article: Delete ---
    resp = requests.delete(f"{BASE_URL}/articles/{art_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Article deleted"

    # --- Category: Delete ---
    resp = requests.delete(f"{BASE_URL}/categories/{cat_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Category deleted"
