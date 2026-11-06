from app.models import Inventory, Order, Payment, User
from app.schemas.catalog import ProductCreate

def test_product_contract_uses_cdf_integer_amount():
    payload = ProductCreate(category_id=1, name="Robe satin", slug="robe-satin", price_cdf=85000)
    assert payload.price_cdf == 85000

def test_usd_catalog_contract_is_rejected():
    try:
        ProductCreate(category_id=1, name="Robe satin", slug="robe-satin", price=50, currency="USD")
    except Exception:
        return
    raise AssertionError("Le contrat catalogue doit utiliser price_cdf et non USD.")

def test_commerce_models_are_registered():
    assert Inventory.__tablename__ == "inventory"
    assert Order.__tablename__ == "orders"
    assert Payment.__tablename__ == "payments"
    assert User.__tablename__ == "users"
