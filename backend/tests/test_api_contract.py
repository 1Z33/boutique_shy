from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "shy-boutique-api"}


def test_catalog_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}
    assert "/api/v1/catalog/categories" in paths
    assert "/api/v1/catalog/products" in paths
    assert "/api/v1/catalog/products/{slug}" in paths


def test_admin_routes_reject_missing_key_before_database_access() -> None:
    response = client.post(
        "/api/v1/catalog/categories",
        json={"name": "Robes", "slug": "robes"},
    )
    assert response.status_code in (401, 503)
