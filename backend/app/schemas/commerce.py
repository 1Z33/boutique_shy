from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

PaymentMethod = Literal["AIRTEL_MONEY", "ORANGE_MONEY", "MPESA", "CASH_ON_DELIVERY"]

# --- Cart ---

class CartItemCreate(BaseModel):
    variant_id: int = Field(gt=0)
    quantity: int = Field(gt=0)

class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)

class CartItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    variant_id: int
    quantity: int

class CartRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
    items: list[CartItemRead] = []

# --- Order ---

class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_name_snapshot: str
    sku_snapshot: str
    variant_snapshot: str | None
    unit_price_cdf: int
    quantity: int
    line_total_cdf: int

class OrderCreate(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=100)
    customer_name: str = Field(min_length=2, max_length=160)
    customer_phone: str = Field(min_length=5, max_length=30)
    customer_email: str | None = None
    delivery_city: str = "Lubumbashi"
    delivery_district: str = Field(min_length=2, max_length=100)
    delivery_address: str = Field(min_length=2, max_length=255)
    delivery_landmark: str | None = None
    promotion_code: str | None = Field(default=None, max_length=60)

class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    public_number: str
    status: str
    currency: str
    subtotal_cdf: int
    discount_cdf: int
    delivery_fee_cdf: int
    total_cdf: int
    customer_name: str
    customer_phone: str
    customer_email: str | None
    items: list[OrderItemRead] = []

# --- Payment ---

class PaymentCreate(BaseModel):
    order_id: int = Field(gt=0)
    method: PaymentMethod
    amount_cdf: int = Field(gt=0)
    internal_reference: str = Field(min_length=4, max_length=100)

class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_id: int
    method: str
    status: str
    amount_cdf: int
    currency: str
    internal_reference: str
    provider_reference: str | None

class PaymentWebhookIn(BaseModel):
    provider_event_id: str = Field(min_length=1, max_length=180)
    status: str
    provider_reference: str | None = Field(default=None, max_length=150)
    internal_reference: str | None = Field(default=None, max_length=100)

# --- Stock ---

class StockReservationCreate(BaseModel):
    variant_id: int = Field(gt=0)
    quantity: int = Field(gt=0)

class StockMovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    movement_type: str
    quantity: int
    reason: str
    actor_user_id: int | None
    created_at: datetime

class LowStockItem(BaseModel):
    variant_id: int
    physical_quantity: int
    reserved_quantity: int
    available_quantity: int
    low_stock_threshold: int

class StockAdjustment(BaseModel):
    variant_id: int = Field(gt=0)
    quantity: int
    reason: str = Field(min_length=2, max_length=255)
    movement_type: Literal["RESTOCK", "ADJUSTMENT"] = "ADJUSTMENT"
