import secrets
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.api.deps import get_current_user_optional
from app.db.session import get_db
from app.models import (
    Cart, CartItem, ProductVariant, Order, OrderItem, OrderStatusHistory,
    Payment, Delivery, DeliveryZone, Promotion,
)
from app.services import stock as stock_service
from app.schemas.commerce import (
    OrderCreate, OrderRead, OrderItemRead, PaymentMethod,
)
router = APIRouter(prefix="/orders", tags=["orders"])


def _generate_public_number(db: Session) -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    for _ in range(10):
        number = f"SHY-{today}-{secrets.token_hex(2).upper()}"
        if not db.scalar(select(Order).where(Order.public_number == number)):
            return number
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Impossible de générer un numéro de commande.")


def _resolve_cart_for_order(db: Session, user_id: int | None, guest_token: str | None) -> Cart:
    from app.api.cart import _resolve_cart
    return _resolve_cart(db, user_id, guest_token)


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    authorization: str | None = Header(default=None),
    x_guest_token: str | None = Header(default=None, alias="X-Guest-Token"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None

    # Idempotence : une clé déjà utilisée renvoie la commande existante.
    existing = db.scalar(select(Order).where(Order.idempotency_key == payload.idempotency_key))
    if existing:
        return _order_read(db, existing.id)

    cart = _resolve_cart_for_order(db, user_id, x_guest_token)
    items = db.scalars(
        select(CartItem).where(CartItem.cart_id == cart.id).order_by(CartItem.id)
    ).all()
    if not items:
        raise HTTPException(status_code=400, detail="Le panier est vide.")

    # Charger les variantes avec leur produit pour le prix et le snapshot.
    variant_ids = [i.variant_id for i in items]
    variants = {
        v.id: v for v in db.scalars(
            select(ProductVariant).options(selectinload(ProductVariant.product)).where(
                ProductVariant.id.in_(variant_ids)
            )
        ).all()
    }

    subtotal = 0
    order_items_data = []
    for item in items:
        variant = variants.get(item.variant_id)
        if not variant or not variant.is_active or not variant.product or not variant.product.is_active:
            raise HTTPException(status_code=400, detail=f"Variante {item.variant_id} indisponible.")
        if stock_service.available_quantity(db, item.variant_id) < item.quantity:
            raise HTTPException(status_code=409, detail=f"Stock insuffisant pour la variante {item.variant_id}.")
        unit_price = int(variant.product.price_cdf)
        line_total = unit_price * item.quantity
        subtotal += line_total
        order_items_data.append({
            "variant": variant,
            "quantity": item.quantity,
            "unit_price_cdf": unit_price,
            "line_total_cdf": line_total,
        })

    # Promotion.
    discount = 0
    promotion = None
    if payload.promotion_code:
        promotion = db.scalar(select(Promotion).where(Promotion.code == payload.promotion_code, Promotion.is_active.is_(True)))
        if not promotion:
            raise HTTPException(status_code=400, detail="Code promotionnel invalide.")
        if promotion.usage_limit is not None and promotion.used_count >= promotion.usage_limit:
            raise HTTPException(status_code=400, detail="Code promotionnel épuisé.")
        if subtotal < promotion.minimum_subtotal_cdf:
            raise HTTPException(status_code=400, detail="Montant minimum de commande non atteint pour ce code.")
        if promotion.discount_type == "PERCENT":
            discount = int(subtotal * promotion.discount_value / 100)
        else:
            discount = promotion.discount_value
        if promotion.max_discount_cdf is not None:
            discount = min(discount, promotion.max_discount_cdf)
        discount = max(0, discount)

    # Frais de livraison par ville.
    delivery_fee = 0
    zone = None
    zone = db.scalar(select(DeliveryZone).where(
        DeliveryZone.city == payload.delivery_city, DeliveryZone.is_active.is_(True)
    ).order_by(DeliveryZone.fee_cdf))
    if zone:
        delivery_fee = zone.fee_cdf

    total = max(0, subtotal - discount + delivery_fee)

    public_number = _generate_public_number(db)
    order = Order(
        public_number=public_number,
        user_id=user_id,
        status="PENDING_PAYMENT",
        currency="CDF",
        subtotal_cdf=subtotal,
        discount_cdf=discount,
        delivery_fee_cdf=delivery_fee,
        total_cdf=total,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        customer_email=payload.customer_email,
        delivery_city=payload.delivery_city,
        delivery_district=payload.delivery_district,
        delivery_address=payload.delivery_address,
        delivery_landmark=payload.delivery_landmark,
        idempotency_key=payload.idempotency_key,
    )
    db.add(order)
    db.flush()

    db.add(OrderStatusHistory(
        order_id=order.id, old_status=None, new_status="PENDING_PAYMENT",
        note="Commande créée", actor_user_id=user_id,
    ))

    # Réservation de stock et lignes de commande.
    for data in order_items_data:
        variant = data["variant"]
        db.add(OrderItem(
            order_id=order.id,
            variant_id=variant.id,
            product_name_snapshot=variant.product.name,
            sku_snapshot=variant.sku,
            variant_snapshot=(
                f"{variant.size or ''} / {variant.color or ''}".strip(" /") or None
            ),
            unit_price_cdf=data["unit_price_cdf"],
            quantity=data["quantity"],
            line_total_cdf=data["line_total_cdf"],
        ))
        stock_service.reserve_stock(
            db,
            variant_id=variant.id,
            quantity=data["quantity"],
            order_id=order.id,
            actor_user_id=user_id,
        )

    if promotion:
        promotion.used_count += 1
        db.add(promotion)

    # Paiement initié.
    payment_method: PaymentMethod = "CASH_ON_DELIVERY"
    db.add(Payment(
        order_id=order.id,
        method=payment_method,
        status="INITIATED",
        amount_cdf=total,
        currency="CDF",
        internal_reference=f"PAY-{public_number}-{secrets.token_hex(4)}",
    ))

    # Livraison.
    if zone:
        db.add(Delivery(
            order_id=order.id,
            zone_id=zone.id,
            status="PENDING",
        ))

    # Panier verrouillé.
    cart.is_active = False
    db.add(cart)

    db.commit()
    return _order_read(db, order.id)


@router.get("", response_model=list[OrderRead])
def list_orders(
    authorization: str | None = Header(default=None),
    x_guest_token: str | None = Header(default=None, alias="X-Guest-Token"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None
    stmt = select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc())
    if user_id:
        stmt = stmt.where(Order.user_id == user_id)
    elif x_guest_token:
        # Les commandes invité n'ont pas d'utilisateur ; on les expose via /orders/{id}.
        return []
    return db.scalars(stmt).all()


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    authorization: str | None = Header(default=None),
    x_guest_token: str | None = Header(default=None, alias="X-Guest-Token"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None
    order = db.scalar(select(Order).options(selectinload(Order.items)).where(Order.id == order_id))
    if not order:
        raise HTTPException(status_code=status.HTTP_404, detail="Commande introuvable.")
    if user_id and order.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403, detail="Non autorisé sur cette commande.")
    if not user_id and order.user_id is not None:
        raise HTTPException(status_code=status.HTTP_403, detail="Authentification requise pour cette commande.")
    return _order_read(db, order.id)


def _order_read(db: Session, order_id: int) -> OrderRead:
    order = db.scalar(select(Order).options(selectinload(Order.items)).where(Order.id == order_id))
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
        items=[
            OrderItemRead(
                id=i.id,
                product_name_snapshot=i.product_name_snapshot,
                sku_snapshot=i.sku_snapshot,
                variant_snapshot=i.variant_snapshot,
                unit_price_cdf=i.unit_price_cdf,
                quantity=i.quantity,
                line_total_cdf=i.line_total_cdf,
            ) for i in order.items
        ],
    )
