"""Add commerce tables and seed canonical inventory.

Revision ID: 0002_commerce_foundation
Revises: 0001_create_catalog
"""
from alembic import op
from app.db.base import Base
from app import models  # noqa: F401

revision = "0002_commerce_foundation"
down_revision = "0001_create_catalog"
branch_labels = None
depends_on = None

NEW_TABLES = [
    "audit_logs", "notifications", "storefront_placements_3d", "storefront_zones_3d",
    "promotions", "deliveries", "payment_webhook_events", "order_status_history",
    "order_items", "inventory_reservations", "payments", "cart_items", "carts",
    "stock_movements", "inventory", "delivery_zones", "orders", "addresses", "users",
]

def upgrade() -> None:
    # Additive migration: existing catalogue tables and records remain untouched.
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)
    op.alter_column("products", "currency", server_default="CDF")
    # Copy each existing variant stock into the new canonical inventory ledger.
    op.execute("""
        INSERT INTO inventory (variant_id, physical_quantity, reserved_quantity, low_stock_threshold)
        SELECT id, GREATEST(stock_quantity, 0), 0, 2
        FROM product_variants
        ON CONFLICT (variant_id) DO NOTHING
    """)

def downgrade() -> None:
    # Only new tables are removed. Existing catalogue tables/data are preserved.
    for table_name in NEW_TABLES:
        op.drop_table(table_name)
    op.alter_column("products", "currency", server_default="USD")
