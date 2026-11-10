from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app
from app.db.session import SessionLocal
from app.models import Category, Product, ProductVariant, Inventory, User

client = TestClient(app)
ADMIN_KEY = "CHANGE_ME_WITH_A_LONG_RANDOM_SECRET"
GUEST_TOKEN = "guest-test-token-12345"


def _headers(guest=True):
    h = {}
    if guest:
        h["X-Guest-Token"] = GUEST_TOKEN
    return h


def _admin_headers():
    return {"X-Admin-API-Key": ADMIN_KEY}


def _clean_db():
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM order_items"))
        db.execute(text("DELETE FROM order_status_history"))
        db.execute(text("DELETE FROM payments"))
        db.execute(text("DELETE FROM payment_webhook_events"))
        db.execute(text("DELETE FROM deliveries"))
        db.execute(text("DELETE FROM inventory_reservations"))
        db.execute(text("DELETE FROM stock_movements"))
        db.execute(text("DELETE FROM cart_items"))
        db.execute(text("DELETE FROM carts"))
        db.execute(text("DELETE FROM orders"))
        db.execute(text("DELETE FROM inventory"))
        db.execute(text("DELETE FROM product_variants"))
        db.execute(text("DELETE FROM products"))
        db.execute(text("DELETE FROM categories"))
        db.execute(text("DELETE FROM users"))
        db.commit()
    finally:
        db.close()


def _seed_catalog():
    db = SessionLocal()
    try:
        category = Category(name="Robes", slug="robes", is_active=True)
        db.add(category)
        db.flush()
        product = Product(
            category_id=category.id,
            name="Robe satin",
            slug="robe-satin-test",
            description="Une robe",
            price_cdf=85000,
            currency="CDF",
            images=[],
            is_active=True,
            is_featured=False,
        )
        db.add(product)
        db.flush()
        variant = ProductVariant(
            product_id=product.id,
            sku="ROBE-S-M-001",
            size="M",
            color="Rouge",
            stock_quantity=10,
            is_active=True,
        )
        db.add(variant)
        db.flush()
        db.add(Inventory(
            variant_id=variant.id,
            physical_quantity=10,
            reserved_quantity=0,
            low_stock_threshold=2,
        ))
        db.commit()
        return variant.id
    finally:
        db.close()




def test_guest_cart_add_and_duplicate_merge():
    _clean_db()
    variant_id = _seed_catalog()
    r = client.post("/api/v1/cart/items", json={"variant_id": variant_id, "quantity": 2}, headers=_headers())
    assert r.status_code == 201, r.text
    body = r.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 2

    # Même variante : les quantités fusionnent (pas de doublon).
    r = client.post("/api/v1/cart/items", json={"variant_id": variant_id, "quantity": 3}, headers=_headers())
    assert r.status_code == 201, r.text
    assert r.json()["items"][0]["quantity"] == 5

    # Mise à jour de quantité.
    item_id = r.json()["items"][0]["id"]
    r = client.patch(f"/api/v1/cart/items/{item_id}", json={"quantity": 1}, headers=_headers())
    assert r.status_code == 200, r.text
    assert r.json()["items"][0]["quantity"] == 1

    # Suppression.
    r = client.delete(f"/api/v1/cart/items/{item_id}", headers=_headers())
    assert r.status_code == 200, r.text
    assert r.json()["items"] == []


def test_insufficient_stock_rejected():
    _clean_db()
    variant_id = _seed_catalog()
    r = client.post("/api/v1/cart/items", json={"variant_id": variant_id, "quantity": 999}, headers=_headers())
    assert r.status_code == 409, r.text


def test_order_creation_reserves_stock_and_idempotency():
    _clean_db()
    variant_id = _seed_catalog()
    client.post("/api/v1/cart/items", json={"variant_id": variant_id, "quantity": 2}, headers=_headers())

    key = "idem-test-001"
    payload = {
        "idempotency_key": key,
        "customer_name": "Marie Client",
        "customer_phone": "+243900000002",
        "customer_email": "marie@example.com",
        "delivery_city": "Lubumbashi",
        "delivery_district": "Kampemba",
        "delivery_address": "Avenue du 30 Juin 123",
    }
    r = client.post("/api/v1/orders", json=payload, headers=_headers())
    assert r.status_code == 201, r.text
    order = r.json()
    assert order["public_number"].startswith("SHY-")
    assert order["total_cdf"] == 85000 * 2
    assert len(order["items"]) == 1
    assert order["items"][0]["quantity"] == 2

    # Idempotence : même clé renvoie la même commande sans en créer une nouvelle.
    r = client.post("/api/v1/orders", json=payload, headers=_headers())
    assert r.status_code == 201, r.text
    assert r.json()["public_number"] == order["public_number"]

    # Le stock a été réservé : disponible diminué.
    from app.services.stock import available_quantity
    assert available_quantity(SessionLocal(), variant_id) == 8


def test_order_requires_non_empty_cart():
    _clean_db()
    _seed_catalog()
    r = client.post("/api/v1/orders", json={
        "idempotency_key": "idem-empty",
        "customer_name": "Client Test",
        "customer_phone": "+243900000003",
        "delivery_city": "Lubumbashi",
        "delivery_district": "Kampemba",
        "delivery_address": "Ave 1",
    }, headers=_headers())
    assert r.status_code == 400, r.text


def test_payment_and_webhook_paid_commits_stock():
    _clean_db()
    variant_id = _seed_catalog()
    client.post("/api/v1/cart/items", json={"variant_id": variant_id, "quantity": 1}, headers=_headers())
    r = client.post("/api/v1/orders", json={
        "idempotency_key": "idem-pay",
        "customer_name": "Jean Client",
        "customer_phone": "+243900000004",
        "delivery_city": "Lubumbashi",
        "delivery_district": "Kampemba",
        "delivery_address": "Ave 2",
    }, headers=_headers())
    assert r.status_code == 201, r.text
    order = r.json()

    # Paiement initié.
    r = client.post("/api/v1/payments", json={
        "order_id": order["id"],
        "method": "AIRTEL_MONEY",
        "amount_cdf": order["total_cdf"],
        "internal_reference": "PAY-REF-001",
    })
    assert r.status_code == 201, r.text

    # Webhook paiement réussi.
    r = client.post("/api/v1/payments/webhooks/AIRTEL_MONEY", json={
        "provider_event_id": "evt-airtel-001",
        "status": "PAID",
        "provider_reference": "prov-ref-001",
        "internal_reference": "PAY-REF-001",
    })
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "processed"

    # Commande passée en PAID.
    r = client.get(f"/api/v1/orders/{order['id']}", headers=_headers())
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "PAID"

    # Stock confirmé (vente) : disponible diminué définitivement.
    from app.services.stock import available_quantity
    assert available_quantity(SessionLocal(), variant_id) == 9

    # Re-envoi du même webhook : déjà traité, pas de retraitement.
    r = client.post("/api/v1/payments/webhooks/AIRTEL_MONEY", json={
        "provider_event_id": "evt-airtel-001",
        "status": "PAID",
        "provider_reference": "prov-ref-001",
        "internal_reference": "PAY-REF-001",
    })
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "already_processed"


def test_webhook_failed_releases_stock():
    _clean_db()
    variant_id = _seed_catalog()
    client.post("/api/v1/cart/items", json={"variant_id": variant_id, "quantity": 1}, headers=_headers())
    r = client.post("/api/v1/orders", json={
        "idempotency_key": "idem-fail",
        "customer_name": "Jane Client",
        "customer_phone": "+243900000005",
        "delivery_city": "Lubumbashi",
        "delivery_district": "Kampemba",
        "delivery_address": "Ave 3",
    }, headers=_headers())
    order = r.json()
    r = client.post("/api/v1/payments", json={
        "order_id": order["id"],
        "method": "MPESA",
        "amount_cdf": order["total_cdf"],
        "internal_reference": "PAY-REF-FAIL",
    })
    assert r.status_code == 201, r.text
    r = client.post("/api/v1/payments/webhooks/MPESA", json={
        "provider_event_id": "evt-mpesa-fail",
        "status": "FAILED",
        "internal_reference": "PAY-REF-FAIL",
    })
    assert r.status_code == 200, r.text
    r = client.get(f"/api/v1/orders/{order['id']}", headers=_headers())
    assert r.json()["status"] == "CANCELLED"
    from app.services.stock import available_quantity
    assert available_quantity(SessionLocal(), variant_id) == 10


def test_low_stock_endpoint_admin():
    _clean_db()
    variant_id = _seed_catalog()
    r = client.get("/api/v1/stock/low-stock", headers=_admin_headers())
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


def test_authenticated_user_cart_isolated():
    _clean_db()
    variant_id = _seed_catalog()
    db = SessionLocal()
    try:
        db.add(User(id=1, full_name="Acheteur", phone="+243900000010", password_hash="x", is_active=True))
        db.commit()
    finally:
        db.close()
    from app.core.security import create_access_token
    headers = {"Authorization": f"Bearer {create_access_token('1')}"}
    r = client.post("/api/v1/cart/items", json={"variant_id": variant_id, "quantity": 1}, headers=headers)
    assert r.status_code == 201, r.text
    r = client.get("/api/v1/cart", headers=headers)
    assert r.status_code == 200
    assert len(r.json()["items"]) == 1
