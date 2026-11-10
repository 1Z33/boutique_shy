from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

class AdminOk(BaseModel):
    ok: bool = True

# Users / Addresses
class UserAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    phone: str
    email: str | None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserAdminUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=160)
    email: str | None = Field(default=None, max_length=254)
    role: str | None = Field(default=None, max_length=30)
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=4, max_length=128)

class AddressAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    city: str
    district: str
    street_address: str
    landmark: str | None
    recipient_name: str
    recipient_phone: str

class AddressAdminCreate(BaseModel):
    user_id: int = Field(gt=0)
    city: str = "Lubumbashi"
    district: str = Field(min_length=1, max_length=100)
    street_address: str = Field(min_length=1, max_length=255)
    landmark: str | None = Field(default=None, max_length=255)
    recipient_name: str = Field(min_length=1, max_length=160)
    recipient_phone: str = Field(min_length=1, max_length=30)

# Inventory / movements / reservations
class InventoryAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    variant_id: int
    physical_quantity: int
    reserved_quantity: int
    low_stock_threshold: int
    created_at: datetime
    updated_at: datetime

class InventoryThresholdUpdate(BaseModel):
    low_stock_threshold: int = Field(ge=0)

class StockMovementAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    inventory_id: int
    movement_type: str
    quantity: int
    reason: str
    actor_user_id: int | None
    created_at: datetime

class ReservationAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    inventory_id: int
    order_id: int | None
    quantity: int
    status: str
    expires_at: datetime
    created_at: datetime

class ReservationAdminUpdate(BaseModel):
    status: Literal["ACTIVE", "RELEASED", "SOLD", "EXPIRED"]

# Carts
class CartItemAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cart_id: int
    variant_id: int
    quantity: int

class CartAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int | None
    guest_token_hash: str | None
    is_active: bool
    created_at: datetime

# Orders
class OrderStatusAdminUpdate(BaseModel):
    status: str = Field(min_length=2, max_length=40)
    note: str | None = Field(default=None, max_length=500)
    release_active_reservations: bool = False
    commit_active_reservations: bool = False

class OrderStatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_id: int
    old_status: str | None
    new_status: str
    note: str | None
    actor_user_id: int | None
    created_at: datetime

# Payments / webhooks
class PaymentAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_id: int
    method: str
    status: str
    amount_cdf: int
    currency: str
    internal_reference: str
    provider_reference: str | None
    verified_at: datetime | None
    created_at: datetime

class PaymentAdminUpdate(BaseModel):
    status: str | None = Field(default=None, max_length=24)
    provider_reference: str | None = Field(default=None, max_length=150)

class WebhookEventAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    provider: str
    provider_event_id: str
    payment_id: int | None
    processing_status: str
    received_at: datetime
    processed_at: datetime | None

# Delivery
class DeliveryZoneCreate(BaseModel):
    city: str = "Lubumbashi"
    name: str = Field(min_length=1, max_length=120)
    fee_cdf: int = Field(ge=0)
    estimated_minutes: int | None = Field(default=None, ge=0)
    is_active: bool = True

class DeliveryZoneUpdate(BaseModel):
    city: str | None = Field(default=None, max_length=80)
    name: str | None = Field(default=None, max_length=120)
    fee_cdf: int | None = Field(default=None, ge=0)
    estimated_minutes: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

class DeliveryZoneRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    city: str
    name: str
    fee_cdf: int
    estimated_minutes: int | None
    is_active: bool

class DeliveryCreate(BaseModel):
    order_id: int = Field(gt=0)
    zone_id: int = Field(gt=0)
    courier_user_id: int | None = None
    status: str = "PENDING"
    proof_note: str | None = None

class DeliveryUpdate(BaseModel):
    zone_id: int | None = Field(default=None, gt=0)
    courier_user_id: int | None = None
    status: str | None = Field(default=None, max_length=40)
    proof_note: str | None = None
    failure_reason: str | None = Field(default=None, max_length=255)

class DeliveryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_id: int
    zone_id: int
    courier_user_id: int | None
    status: str
    proof_note: str | None
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime

# Promotions
class PromotionCreate(BaseModel):
    code: str = Field(min_length=1, max_length=60)
    discount_type: str = Field(min_length=1, max_length=20)
    discount_value: int = Field(ge=0)
    max_discount_cdf: int | None = Field(default=None, ge=0)
    minimum_subtotal_cdf: int = Field(default=0, ge=0)
    usage_limit: int | None = Field(default=None, ge=0)
    is_active: bool = True

class PromotionUpdate(BaseModel):
    code: str | None = Field(default=None, max_length=60)
    discount_type: str | None = Field(default=None, max_length=20)
    discount_value: int | None = Field(default=None, ge=0)
    max_discount_cdf: int | None = Field(default=None, ge=0)
    minimum_subtotal_cdf: int | None = Field(default=None, ge=0)
    usage_limit: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    used_count: int | None = Field(default=None, ge=0)

class PromotionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    discount_type: str
    discount_value: int
    max_discount_cdf: int | None
    minimum_subtotal_cdf: int
    usage_limit: int | None
    used_count: int
    is_active: bool

# Storefront 3D
class StorefrontZone3DCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=140)
    description: str | None = None
    sort_order: int = 0
    is_published: bool = False

class StorefrontZone3DUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    slug: str | None = Field(default=None, max_length=140)
    description: str | None = None
    sort_order: int | None = None
    is_published: bool | None = None

class StorefrontZone3DRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    description: str | None
    sort_order: int
    is_published: bool

class StorefrontPlacement3DCreate(BaseModel):
    zone_id: int = Field(gt=0)
    product_id: int | None = None
    asset_url: str | None = Field(default=None, max_length=1000)
    position_x: int = 0
    position_y: int = 0
    position_z: int = 0
    rotation_y: int = 0
    scale_percent: int = 100
    is_visible: bool = True

class StorefrontPlacement3DUpdate(BaseModel):
    zone_id: int | None = Field(default=None, gt=0)
    product_id: int | None = None
    asset_url: str | None = Field(default=None, max_length=1000)
    position_x: int | None = None
    position_y: int | None = None
    position_z: int | None = None
    rotation_y: int | None = None
    scale_percent: int | None = None
    is_visible: bool | None = None

class StorefrontPlacement3DRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    zone_id: int
    product_id: int | None
    asset_url: str | None
    position_x: int
    position_y: int
    position_z: int
    rotation_y: int
    scale_percent: int
    is_visible: bool

# Notifications / Audit
class NotificationCreate(BaseModel):
    user_id: int | None = None
    order_id: int | None = None
    channel: str = Field(min_length=1, max_length=30)
    recipient: str = Field(min_length=1, max_length=255)
    template_key: str = Field(min_length=1, max_length=100)
    status: str = "QUEUED"
    error_message: str | None = None

class NotificationUpdate(BaseModel):
    status: str | None = Field(default=None, max_length=30)
    error_message: str | None = None

class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int | None
    order_id: int | None
    channel: str
    recipient: str
    template_key: str
    status: str
    error_message: str | None

class AuditLogCreate(BaseModel):
    actor_user_id: int | None = None
    action: str = Field(min_length=1, max_length=100)
    entity_type: str = Field(min_length=1, max_length=80)
    entity_id: str = Field(min_length=1, max_length=80)
    details_redacted: str | None = None

class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    actor_user_id: int | None
    action: str
    entity_type: str
    entity_id: str
    details_redacted: str | None
    created_at: datetime

class AdminOverview(BaseModel):
    users: int
    products: int
    active_carts: int
    orders: int
    payments: int
    deliveries: int
    promotions: int
    low_stock: int
    notifications: int
    audit_logs: int
