from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_admin
from app.core.config import settings
from app.core.security import hash_password
from app.db.session import get_db
from app.models import (
    Address,
    AuditLog,
    Cart,
    CartItem,
    Category,
    Delivery,
    DeliveryZone,
    Inventory,
    InventoryReservation,
    Notification,
    Order,
    OrderItem,
    OrderStatusHistory,
    Payment,
    PaymentWebhookEvent,
    Product,
    ProductVariant,
    Promotion,
    StockMovement,
    StorefrontPlacement3D,
    StorefrontZone3D,
    User,
)
from app.schemas.admin import (
    AddressAdminCreate,
    AddressAdminRead,
    AdminOk,
    AdminOverview,
    AuditLogCreate,
    AuditLogRead,
    CartAdminRead,
    CartItemAdminRead,
    DeliveryCreate,
    DeliveryRead,
    DeliveryUpdate,
    DeliveryZoneCreate,
    DeliveryZoneRead,
    DeliveryZoneUpdate,
    InventoryAdminRead,
    InventoryThresholdUpdate,
    NotificationCreate,
    NotificationRead,
    NotificationUpdate,
    OrderStatusAdminUpdate,
    OrderStatusHistoryRead,
    PaymentAdminRead,
    PaymentAdminUpdate,
    PromotionCreate,
    PromotionRead,
    PromotionUpdate,
    ReservationAdminRead,
    ReservationAdminUpdate,
    StockMovementAdminRead,
    StorefrontPlacement3DCreate,
    StorefrontPlacement3DRead,
    StorefrontPlacement3DUpdate,
    StorefrontZone3DCreate,
    StorefrontZone3DRead,
    StorefrontZone3DUpdate,
    UserAdminRead,
    UserAdminUpdate,
    WebhookEventAdminRead,
)
from app.schemas.catalog import CategoryCreate, CategoryRead, ProductCreate, ProductRead, ProductUpdate, VariantCreate
from app.schemas.commerce import LowStockItem, OrderItemRead, OrderRead, StockAdjustment
from app.services import stock as stock_service

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


def _commit(db: Session) -> None:
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def _audit(db: Session, action: str, entity_type: str, entity_id: str, details: str | None = None) -> None:
    db.add(AuditLog(action=action, entity_type=entity_type, entity_id=entity_id, details_redacted=details))
    db.flush()


ALLOWED_IMAGE_TYPES = {"image/png": "png", "image/jpeg": "jpg", "image/jpg": "jpg", "image/webp": "webp"}


@router.post("/uploads/images", status_code=status.HTTP_201_CREATED)
async def upload_product_images(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(400, "Aucun fichier reçu.")
    if len(files) > 12:
        raise HTTPException(400, "Maximum 12 images par envoi.")
    dest_dir = settings.uploads_dir / "products"
    dest_dir.mkdir(parents=True, exist_ok=True)
    urls: list[str] = []
    for file in files:
        ctype = (file.content_type or "").lower().split(";")[0].strip()
        ext = ALLOWED_IMAGE_TYPES.get(ctype)
        if not ext:
            name = (file.filename or "").lower()
            if name.endswith(".png"):
                ext = "png"
            elif name.endswith(".jpg") or name.endswith(".jpeg"):
                ext = "jpg"
            elif name.endswith(".webp"):
                ext = "webp"
        if not ext:
            raise HTTPException(400, f"Type non supporté pour {file.filename or 'fichier'} (PNG/JPG/WEBP uniquement).")
        data = await file.read()
        if not data:
            raise HTTPException(400, f"Fichier vide: {file.filename or 'image'}.")
        if len(data) > 8 * 1024 * 1024:
            raise HTTPException(400, f"Image trop volumineuse (>8 Mo): {file.filename or 'image'}.")
        name = f"{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex}.{ext}"
        path = dest_dir / name
        path.write_bytes(data)
        urls.append(f"/uploads/products/{name}")
    return {"urls": urls}


@router.get("/overview", response_model=AdminOverview)
def overview(db: Session = Depends(get_db)):
    low = len(stock_service.list_low_stock(db))
    return AdminOverview(
        users=db.scalar(select(func.count()).select_from(User)) or 0,
        products=db.scalar(select(func.count()).select_from(Product)) or 0,
        active_carts=db.scalar(select(func.count()).select_from(Cart).where(Cart.is_active.is_(True))) or 0,
        orders=db.scalar(select(func.count()).select_from(Order)) or 0,
        payments=db.scalar(select(func.count()).select_from(Payment)) or 0,
        deliveries=db.scalar(select(func.count()).select_from(Delivery)) or 0,
        promotions=db.scalar(select(func.count()).select_from(Promotion)) or 0,
        low_stock=low,
        notifications=db.scalar(select(func.count()).select_from(Notification)) or 0,
        audit_logs=db.scalar(select(func.count()).select_from(AuditLog)) or 0,
    )


# --- Users ---
@router.get("/users", response_model=list[UserAdminRead])
def list_users(
    q: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(User).order_by(User.id.desc())
    if q:
        like = f"%{q}%"
        stmt = stmt.where((User.full_name.ilike(like)) | (User.phone.ilike(like)) | (User.email.ilike(like)))
    return db.scalars(stmt.offset(offset).limit(limit)).all()


@router.get("/users/{user_id}", response_model=UserAdminRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Utilisateur introuvable.")
    return user


@router.patch("/users/{user_id}", response_model=UserAdminRead)
def update_user(user_id: int, payload: UserAdminUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Utilisateur introuvable.")
    data = payload.model_dump(exclude_unset=True)
    password = data.pop("password", None)
    for k, v in data.items():
        setattr(user, k, v)
    if password:
        user.password_hash = hash_password(password)
    db.add(user)
    _audit(db, "USER_UPDATE", "User", str(user_id))
    _commit(db)
    db.refresh(user)
    return user


# --- Addresses ---
@router.get("/addresses", response_model=list[AddressAdminRead])
def list_addresses(user_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(Address).order_by(Address.id.desc())
    if user_id is not None:
        stmt = stmt.where(Address.user_id == user_id)
    return db.scalars(stmt).all()


@router.post("/addresses", response_model=AddressAdminRead, status_code=status.HTTP_201_CREATED)
def create_address(payload: AddressAdminCreate, db: Session = Depends(get_db)):
    if not db.get(User, payload.user_id):
        raise HTTPException(400, "Utilisateur introuvable.")
    row = Address(**payload.model_dump())
    db.add(row)
    _audit(db, "ADDRESS_CREATE", "Address", "pending")
    _commit(db)
    db.refresh(row)
    return row


@router.delete("/addresses/{address_id}", response_model=AdminOk)
def delete_address(address_id: int, db: Session = Depends(get_db)):
    row = db.get(Address, address_id)
    if not row:
        raise HTTPException(404, "Adresse introuvable.")
    db.delete(row)
    _audit(db, "ADDRESS_DELETE", "Address", str(address_id))
    _commit(db)
    return AdminOk()


# --- Catalog (admin sees all) ---
@router.get("/categories", response_model=list[CategoryRead])
def admin_categories(db: Session = Depends(get_db)):
    return db.scalars(select(Category).order_by(Category.id.desc())).all()


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def admin_create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    category = Category(**payload.model_dump())
    db.add(category)
    _audit(db, "CATEGORY_CREATE", "Category", payload.slug)
    try:
        _commit(db)
        db.refresh(category)
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        msg = str(exc)
        if "unique" in msg.lower() or "duplicate" in msg.lower():
            raise HTTPException(409, "Catégorie ou slug déjà existant.")
        raise HTTPException(400, f"Création catégorie impossible: {msg[:300]}")
    return category


@router.patch("/categories/{category_id}", response_model=CategoryRead)
def admin_update_category(category_id: int, payload: CategoryCreate, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(404, "Catégorie introuvable.")
    for k, v in payload.model_dump().items():
        setattr(category, k, v)
    db.add(category)
    _audit(db, "CATEGORY_UPDATE", "Category", str(category_id))
    try:
        _commit(db)
        db.refresh(category)
    except Exception:
        raise HTTPException(409, "Conflit de nom/slug.")
    return category


@router.get("/products", response_model=list[ProductRead])
def admin_products(
    include_inactive: bool = True,
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Product).options(selectinload(Product.variants)).order_by(Product.id.desc())
    if not include_inactive:
        stmt = stmt.where(Product.is_active.is_(True))
    return db.scalars(stmt.offset(offset).limit(limit)).all()


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def admin_create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude={"variants"})
    data["price_cdf"] = Decimal(str(data["price_cdf"]))
    data["currency"] = "CDF"
    if not db.get(Category, data["category_id"]):
        raise HTTPException(400, "Catégorie invalide.")
    product = Product(**data)
    product.variants = [ProductVariant(**v.model_dump()) for v in payload.variants]
    db.add(product)
    try:
        db.flush()
        for variant in product.variants:
            db.add(Inventory(variant_id=variant.id, physical_quantity=variant.stock_quantity, reserved_quantity=0))
        _audit(db, "PRODUCT_CREATE", "Product", product.slug)
        _commit(db)
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        msg = str(exc)
        lower = msg.lower()
        if "unique" in lower or "duplicate" in lower or "slug" in lower or "sku" in lower:
            raise HTTPException(409, "Slug produit ou SKU déjà existant.")
        raise HTTPException(400, f"Création produit impossible: {msg[:300]}")
    created = db.scalar(select(Product).options(selectinload(Product.variants)).where(Product.id == product.id))
    if not created:
        raise HTTPException(500, "Produit créé mais introuvable.")
    return created


@router.patch("/products/{product_id}", response_model=ProductRead)
def admin_update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = db.scalar(select(Product).options(selectinload(Product.variants)).where(Product.id == product_id))
    if not product:
        raise HTTPException(404, "Produit introuvable.")
    values = payload.model_dump(exclude_unset=True)
    if "price_cdf" in values and values["price_cdf"] is not None:
        values["price_cdf"] = Decimal(values["price_cdf"])
    if "category_id" in values and values["category_id"] is not None and not db.get(Category, values["category_id"]):
        raise HTTPException(400, "Catégorie invalide.")
    for k, v in values.items():
        setattr(product, k, v)
    db.add(product)
    _audit(db, "PRODUCT_UPDATE", "Product", str(product_id))
    _commit(db)
    db.refresh(product)
    return product


@router.post("/products/{product_id}/variants", status_code=status.HTTP_201_CREATED)
def admin_add_variant(product_id: int, payload: VariantCreate, db: Session = Depends(get_db)):
    if not db.get(Product, product_id):
        raise HTTPException(404, "Produit introuvable.")
    variant = ProductVariant(product_id=product_id, **payload.model_dump())
    db.add(variant)
    try:
        db.flush()
        db.add(Inventory(variant_id=variant.id, physical_quantity=variant.stock_quantity, reserved_quantity=0))
        _audit(db, "VARIANT_CREATE", "ProductVariant", variant.sku)
        _commit(db)
        db.refresh(variant)
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        msg = str(exc)
        if "unique" in msg.lower() or "duplicate" in msg.lower() or "sku" in msg.lower():
            raise HTTPException(409, "SKU déjà existant pour ce produit.")
        raise HTTPException(400, f"Création variante impossible: {msg[:300]}")
    return {"id": variant.id, "sku": variant.sku, "size": variant.size, "color": variant.color, "stock_quantity": variant.stock_quantity, "is_active": variant.is_active}


@router.patch("/variants/{variant_id}")
def admin_update_variant(
    variant_id: int,
    sku: str | None = None,
    size: str | None = None,
    color: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
):
    variant = db.get(ProductVariant, variant_id)
    if not variant:
        raise HTTPException(404, "Variante introuvable.")
    if sku is not None:
        variant.sku = sku
    if size is not None:
        variant.size = size
    if color is not None:
        variant.color = color
    if is_active is not None:
        variant.is_active = is_active
    db.add(variant)
    _audit(db, "VARIANT_UPDATE", "ProductVariant", str(variant_id))
    try:
        _commit(db)
    except Exception:
        raise HTTPException(409, "Conflit SKU.")
    return {"id": variant.id, "sku": variant.sku, "size": variant.size, "color": variant.color, "is_active": variant.is_active}


# --- Inventory / stock ---
@router.get("/inventory", response_model=list[InventoryAdminRead])
def list_inventory(db: Session = Depends(get_db)):
    return db.scalars(select(Inventory).order_by(Inventory.id.desc())).all()


@router.patch("/inventory/{inventory_id}/threshold", response_model=InventoryAdminRead)
def update_threshold(inventory_id: int, payload: InventoryThresholdUpdate, db: Session = Depends(get_db)):
    inv = db.get(Inventory, inventory_id)
    if not inv:
        raise HTTPException(404, "Inventaire introuvable.")
    inv.low_stock_threshold = payload.low_stock_threshold
    db.add(inv)
    _audit(db, "INVENTORY_THRESHOLD", "Inventory", str(inventory_id))
    _commit(db)
    db.refresh(inv)
    return inv


@router.post("/stock/adjust")
def admin_adjust_stock(payload: StockAdjustment, db: Session = Depends(get_db)):
    if not db.get(ProductVariant, payload.variant_id):
        raise HTTPException(404, "Variante introuvable.")
    inv = stock_service.adjust_stock(db, variant_id=payload.variant_id, quantity=payload.quantity, reason=payload.reason, movement_type=payload.movement_type)
    _audit(db, "STOCK_ADJUST", "Inventory", str(inv.id), payload.reason)
    _commit(db)
    return {"variant_id": inv.variant_id, "physical_quantity": inv.physical_quantity, "reserved_quantity": inv.reserved_quantity}


@router.get("/stock/low", response_model=list[LowStockItem])
def admin_low_stock(db: Session = Depends(get_db)):
    rows = stock_service.list_low_stock(db)
    return [
        LowStockItem(
            variant_id=i.variant_id,
            physical_quantity=i.physical_quantity,
            reserved_quantity=i.reserved_quantity,
            available_quantity=max(0, i.physical_quantity - i.reserved_quantity),
            low_stock_threshold=i.low_stock_threshold,
        )
        for i in rows
    ]


@router.get("/stock/movements", response_model=list[StockMovementAdminRead])
def list_movements(
    inventory_id: int | None = None,
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(StockMovement).order_by(StockMovement.id.desc())
    if inventory_id is not None:
        stmt = stmt.where(StockMovement.inventory_id == inventory_id)
    return db.scalars(stmt.limit(limit)).all()


@router.get("/stock/reservations", response_model=list[ReservationAdminRead])
def list_reservations(
    status_filter: str | None = Query(default=None, alias="status"),
    order_id: int | None = None,
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(InventoryReservation).order_by(InventoryReservation.id.desc())
    if status_filter:
        stmt = stmt.where(InventoryReservation.status == status_filter)
    if order_id is not None:
        stmt = stmt.where(InventoryReservation.order_id == order_id)
    return db.scalars(stmt.limit(limit)).all()


@router.patch("/stock/reservations/{reservation_id}", response_model=ReservationAdminRead)
def update_reservation(reservation_id: int, payload: ReservationAdminUpdate, db: Session = Depends(get_db)):
    r = db.get(InventoryReservation, reservation_id)
    if not r:
        raise HTTPException(404, "Réservation introuvable.")
    old = r.status
    if payload.status == "RELEASED" and old == "ACTIVE":
        stock_service.release_reservation(db, reservation_id)
    elif payload.status == "SOLD" and old == "ACTIVE":
        stock_service.commit_sale(db, reservation_id)
    else:
        r.status = payload.status
        db.add(r)
    _audit(db, "RESERVATION_UPDATE", "InventoryReservation", str(reservation_id), f"{old}->{payload.status}")
    _commit(db)
    db.refresh(r)
    return r


# --- Carts ---
@router.get("/carts", response_model=list[CartAdminRead])
def list_carts(active: bool | None = None, limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)):
    stmt = select(Cart).order_by(Cart.id.desc())
    if active is not None:
        stmt = stmt.where(Cart.is_active.is_(active))
    return db.scalars(stmt.limit(limit)).all()


@router.get("/carts/{cart_id}/items", response_model=list[CartItemAdminRead])
def list_cart_items(cart_id: int, db: Session = Depends(get_db)):
    if not db.get(Cart, cart_id):
        raise HTTPException(404, "Panier introuvable.")
    return db.scalars(select(CartItem).where(CartItem.cart_id == cart_id).order_by(CartItem.id)).all()


@router.delete("/carts/{cart_id}", response_model=AdminOk)
def delete_cart(cart_id: int, db: Session = Depends(get_db)):
    cart = db.get(Cart, cart_id)
    if not cart:
        raise HTTPException(404, "Panier introuvable.")
    db.delete(cart)
    _audit(db, "CART_DELETE", "Cart", str(cart_id))
    _commit(db)
    return AdminOk()


# --- Orders ---
def _order_read(db: Session, order_id: int) -> OrderRead:
    order = db.scalar(select(Order).options(selectinload(Order.items)).where(Order.id == order_id))
    if not order:
        raise HTTPException(404, "Commande introuvable.")
    return OrderRead(
        id=order.id,
        public_number=order.public_number,
        status=order.status,
        currency=order.currency,
        subtotal_cdf=order.subtotal_cdf,
        discount_cdf=order.discount_cdf,
        delivery_fee_cdf=order.delivery_fee_cdf,
        total_cdf=order.total_cdf,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_email=order.customer_email,
        items=[OrderItemRead.model_validate(i) for i in order.items],
    )


@router.get("/orders", response_model=list[OrderRead])
def admin_orders(
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc())
    if status_filter:
        stmt = stmt.where(Order.status == status_filter)
    rows = db.scalars(stmt.offset(offset).limit(limit)).all()
    return [
        OrderRead(
            id=o.id,
            public_number=o.public_number,
            status=o.status,
            currency=o.currency,
            subtotal_cdf=o.subtotal_cdf,
            discount_cdf=o.discount_cdf,
            delivery_fee_cdf=o.delivery_fee_cdf,
            total_cdf=o.total_cdf,
            customer_name=o.customer_name,
            customer_phone=o.customer_phone,
            customer_email=o.customer_email,
            items=[OrderItemRead.model_validate(i) for i in o.items],
        )
        for o in rows
    ]


@router.get("/orders/{order_id}", response_model=OrderRead)
def admin_get_order(order_id: int, db: Session = Depends(get_db)):
    return _order_read(db, order_id)


@router.patch("/orders/{order_id}/status", response_model=OrderRead)
def admin_update_order_status(order_id: int, payload: OrderStatusAdminUpdate, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(404, "Commande introuvable.")
    old = order.status
    order.status = payload.status
    db.add(order)
    db.add(OrderStatusHistory(order_id=order.id, old_status=old, new_status=payload.status, note=payload.note))
    reservations = db.scalars(
        select(InventoryReservation).where(InventoryReservation.order_id == order.id, InventoryReservation.status == "ACTIVE")
    ).all()
    if payload.commit_active_reservations or payload.status.upper() == "PAID":
        for r in reservations:
            stock_service.commit_sale(db, r.id)
    elif payload.release_active_reservations or payload.status.upper() in {"CANCELLED", "CANCELED", "FAILED"}:
        for r in reservations:
            stock_service.release_reservation(db, r.id)
    _audit(db, "ORDER_STATUS", "Order", str(order_id), f"{old}->{payload.status}")
    _commit(db)
    return _order_read(db, order_id)


@router.get("/orders/{order_id}/history", response_model=list[OrderStatusHistoryRead])
def admin_order_history(order_id: int, db: Session = Depends(get_db)):
    if not db.get(Order, order_id):
        raise HTTPException(404, "Commande introuvable.")
    return db.scalars(select(OrderStatusHistory).where(OrderStatusHistory.order_id == order_id).order_by(OrderStatusHistory.id.desc())).all()


# --- Payments ---
@router.get("/payments", response_model=list[PaymentAdminRead])
def admin_payments(
    order_id: int | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(Payment).order_by(Payment.id.desc())
    if order_id is not None:
        stmt = stmt.where(Payment.order_id == order_id)
    if status_filter:
        stmt = stmt.where(Payment.status == status_filter)
    return db.scalars(stmt.limit(limit)).all()


@router.patch("/payments/{payment_id}", response_model=PaymentAdminRead)
def admin_update_payment(payment_id: int, payload: PaymentAdminUpdate, db: Session = Depends(get_db)):
    p = db.get(Payment, payment_id)
    if not p:
        raise HTTPException(404, "Paiement introuvable.")
    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"]:
        data["status"] = data["status"].strip().upper()
        if data["status"] == "PAID" and not p.verified_at:
            p.verified_at = datetime.now(timezone.utc)
    for k, v in data.items():
        if v is not None:
            setattr(p, k, v)
    db.add(p)
    _audit(db, "PAYMENT_UPDATE", "Payment", str(payment_id))
    _commit(db)
    db.refresh(p)
    return p


@router.get("/webhook-events", response_model=list[WebhookEventAdminRead])
def admin_webhook_events(limit: int = Query(default=200, ge=1, le=500), db: Session = Depends(get_db)):
    return db.scalars(select(PaymentWebhookEvent).order_by(PaymentWebhookEvent.id.desc()).limit(limit)).all()


# --- Delivery ---
@router.get("/delivery-zones", response_model=list[DeliveryZoneRead])
def admin_delivery_zones(db: Session = Depends(get_db)):
    return db.scalars(select(DeliveryZone).order_by(DeliveryZone.city, DeliveryZone.name)).all()


@router.post("/delivery-zones", response_model=DeliveryZoneRead, status_code=status.HTTP_201_CREATED)
def admin_create_delivery_zone(payload: DeliveryZoneCreate, db: Session = Depends(get_db)):
    row = DeliveryZone(**payload.model_dump())
    db.add(row)
    try:
        _audit(db, "DELIVERY_ZONE_CREATE", "DeliveryZone", payload.name)
        _commit(db)
        db.refresh(row)
    except Exception:
        raise HTTPException(409, "Zone de livraison déjà existante.")
    return row


@router.patch("/delivery-zones/{zone_id}", response_model=DeliveryZoneRead)
def admin_update_delivery_zone(zone_id: int, payload: DeliveryZoneUpdate, db: Session = Depends(get_db)):
    row = db.get(DeliveryZone, zone_id)
    if not row:
        raise HTTPException(404, "Zone introuvable.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.add(row)
    _audit(db, "DELIVERY_ZONE_UPDATE", "DeliveryZone", str(zone_id))
    try:
        _commit(db)
        db.refresh(row)
    except Exception:
        raise HTTPException(409, "Conflit de zone.")
    return row


@router.delete("/delivery-zones/{zone_id}", response_model=AdminOk)
def admin_delete_delivery_zone(zone_id: int, db: Session = Depends(get_db)):
    row = db.get(DeliveryZone, zone_id)
    if not row:
        raise HTTPException(404, "Zone introuvable.")
    db.delete(row)
    _audit(db, "DELIVERY_ZONE_DELETE", "DeliveryZone", str(zone_id))
    try:
        _commit(db)
    except Exception:
        raise HTTPException(409, "Zone utilisée par une livraison.")
    return AdminOk()


@router.get("/deliveries", response_model=list[DeliveryRead])
def admin_deliveries(
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(Delivery).order_by(Delivery.id.desc())
    if status_filter:
        stmt = stmt.where(Delivery.status == status_filter)
    return db.scalars(stmt.limit(limit)).all()


@router.post("/deliveries", response_model=DeliveryRead, status_code=status.HTTP_201_CREATED)
def admin_create_delivery(payload: DeliveryCreate, db: Session = Depends(get_db)):
    if not db.get(Order, payload.order_id):
        raise HTTPException(400, "Commande introuvable.")
    if not db.get(DeliveryZone, payload.zone_id):
        raise HTTPException(400, "Zone introuvable.")
    row = Delivery(**payload.model_dump())
    db.add(row)
    try:
        _audit(db, "DELIVERY_CREATE", "Delivery", str(payload.order_id))
        _commit(db)
        db.refresh(row)
    except Exception:
        raise HTTPException(409, "Livraison déjà existante pour cette commande.")
    return row


@router.patch("/deliveries/{delivery_id}", response_model=DeliveryRead)
def admin_update_delivery(delivery_id: int, payload: DeliveryUpdate, db: Session = Depends(get_db)):
    row = db.get(Delivery, delivery_id)
    if not row:
        raise HTTPException(404, "Livraison introuvable.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.add(row)
    _audit(db, "DELIVERY_UPDATE", "Delivery", str(delivery_id))
    _commit(db)
    db.refresh(row)
    return row


# --- Promotions ---
@router.get("/promotions", response_model=list[PromotionRead])
def admin_promotions(db: Session = Depends(get_db)):
    return db.scalars(select(Promotion).order_by(Promotion.id.desc())).all()


@router.post("/promotions", response_model=PromotionRead, status_code=status.HTTP_201_CREATED)
def admin_create_promotion(payload: PromotionCreate, db: Session = Depends(get_db)):
    row = Promotion(**payload.model_dump(), used_count=0)
    db.add(row)
    try:
        _audit(db, "PROMOTION_CREATE", "Promotion", payload.code)
        _commit(db)
        db.refresh(row)
    except Exception:
        raise HTTPException(409, "Code promotionnel déjà existant.")
    return row


@router.patch("/promotions/{promotion_id}", response_model=PromotionRead)
def admin_update_promotion(promotion_id: int, payload: PromotionUpdate, db: Session = Depends(get_db)):
    row = db.get(Promotion, promotion_id)
    if not row:
        raise HTTPException(404, "Promotion introuvable.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.add(row)
    _audit(db, "PROMOTION_UPDATE", "Promotion", str(promotion_id))
    try:
        _commit(db)
        db.refresh(row)
    except Exception:
        raise HTTPException(409, "Conflit de code.")
    return row


@router.delete("/promotions/{promotion_id}", response_model=AdminOk)
def admin_delete_promotion(promotion_id: int, db: Session = Depends(get_db)):
    row = db.get(Promotion, promotion_id)
    if not row:
        raise HTTPException(404, "Promotion introuvable.")
    db.delete(row)
    _audit(db, "PROMOTION_DELETE", "Promotion", str(promotion_id))
    _commit(db)
    return AdminOk()


# --- Storefront 3D ---
@router.get("/storefront-zones", response_model=list[StorefrontZone3DRead])
def admin_storefront_zones(db: Session = Depends(get_db)):
    return db.scalars(select(StorefrontZone3D).order_by(StorefrontZone3D.sort_order, StorefrontZone3D.id)).all()


@router.post("/storefront-zones", response_model=StorefrontZone3DRead, status_code=status.HTTP_201_CREATED)
def admin_create_storefront_zone(payload: StorefrontZone3DCreate, db: Session = Depends(get_db)):
    row = StorefrontZone3D(**payload.model_dump())
    db.add(row)
    try:
        _audit(db, "STOREFRONT_ZONE_CREATE", "StorefrontZone3D", payload.slug)
        _commit(db)
        db.refresh(row)
    except Exception:
        raise HTTPException(409, "Slug de zone déjà existant.")
    return row


@router.patch("/storefront-zones/{zone_id}", response_model=StorefrontZone3DRead)
def admin_update_storefront_zone(zone_id: int, payload: StorefrontZone3DUpdate, db: Session = Depends(get_db)):
    row = db.get(StorefrontZone3D, zone_id)
    if not row:
        raise HTTPException(404, "Zone 3D introuvable.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.add(row)
    _audit(db, "STOREFRONT_ZONE_UPDATE", "StorefrontZone3D", str(zone_id))
    _commit(db)
    db.refresh(row)
    return row


@router.delete("/storefront-zones/{zone_id}", response_model=AdminOk)
def admin_delete_storefront_zone(zone_id: int, db: Session = Depends(get_db)):
    row = db.get(StorefrontZone3D, zone_id)
    if not row:
        raise HTTPException(404, "Zone 3D introuvable.")
    db.delete(row)
    _audit(db, "STOREFRONT_ZONE_DELETE", "StorefrontZone3D", str(zone_id))
    _commit(db)
    return AdminOk()


@router.get("/storefront-placements", response_model=list[StorefrontPlacement3DRead])
def admin_storefront_placements(zone_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(StorefrontPlacement3D).order_by(StorefrontPlacement3D.id.desc())
    if zone_id is not None:
        stmt = stmt.where(StorefrontPlacement3D.zone_id == zone_id)
    return db.scalars(stmt).all()


@router.post("/storefront-placements", response_model=StorefrontPlacement3DRead, status_code=status.HTTP_201_CREATED)
def admin_create_storefront_placement(payload: StorefrontPlacement3DCreate, db: Session = Depends(get_db)):
    if not db.get(StorefrontZone3D, payload.zone_id):
        raise HTTPException(400, "Zone 3D introuvable.")
    row = StorefrontPlacement3D(**payload.model_dump())
    db.add(row)
    _audit(db, "STOREFRONT_PLACEMENT_CREATE", "StorefrontPlacement3D", str(payload.zone_id))
    _commit(db)
    db.refresh(row)
    return row


@router.patch("/storefront-placements/{placement_id}", response_model=StorefrontPlacement3DRead)
def admin_update_storefront_placement(placement_id: int, payload: StorefrontPlacement3DUpdate, db: Session = Depends(get_db)):
    row = db.get(StorefrontPlacement3D, placement_id)
    if not row:
        raise HTTPException(404, "Placement introuvable.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.add(row)
    _audit(db, "STOREFRONT_PLACEMENT_UPDATE", "StorefrontPlacement3D", str(placement_id))
    _commit(db)
    db.refresh(row)
    return row


@router.delete("/storefront-placements/{placement_id}", response_model=AdminOk)
def admin_delete_storefront_placement(placement_id: int, db: Session = Depends(get_db)):
    row = db.get(StorefrontPlacement3D, placement_id)
    if not row:
        raise HTTPException(404, "Placement introuvable.")
    db.delete(row)
    _audit(db, "STOREFRONT_PLACEMENT_DELETE", "StorefrontPlacement3D", str(placement_id))
    _commit(db)
    return AdminOk()


# --- Notifications ---
@router.get("/notifications", response_model=list[NotificationRead])
def admin_notifications(limit: int = Query(default=200, ge=1, le=500), db: Session = Depends(get_db)):
    return db.scalars(select(Notification).order_by(Notification.id.desc()).limit(limit)).all()


@router.post("/notifications", response_model=NotificationRead, status_code=status.HTTP_201_CREATED)
def admin_create_notification(payload: NotificationCreate, db: Session = Depends(get_db)):
    row = Notification(**payload.model_dump())
    db.add(row)
    _audit(db, "NOTIFICATION_CREATE", "Notification", payload.template_key)
    _commit(db)
    db.refresh(row)
    return row


@router.patch("/notifications/{notification_id}", response_model=NotificationRead)
def admin_update_notification(notification_id: int, payload: NotificationUpdate, db: Session = Depends(get_db)):
    row = db.get(Notification, notification_id)
    if not row:
        raise HTTPException(404, "Notification introuvable.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.add(row)
    _audit(db, "NOTIFICATION_UPDATE", "Notification", str(notification_id))
    _commit(db)
    db.refresh(row)
    return row


# --- Audit logs ---
@router.get("/audit-logs", response_model=list[AuditLogRead])
def admin_audit_logs(limit: int = Query(default=300, ge=1, le=1000), db: Session = Depends(get_db)):
    return db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)).all()


@router.post("/audit-logs", response_model=AuditLogRead, status_code=status.HTTP_201_CREATED)
def admin_create_audit_log(payload: AuditLogCreate, db: Session = Depends(get_db)):
    row = AuditLog(**payload.model_dump())
    db.add(row)
    _commit(db)
    db.refresh(row)
    return row
