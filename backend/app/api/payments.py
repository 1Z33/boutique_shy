from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import (
    InventoryReservation, Order, OrderStatusHistory, Payment, PaymentWebhookEvent,
)
from app.services import stock as stock_service
from app.schemas.commerce import (
    PaymentCreate, PaymentRead, PaymentWebhookIn,
)

router = APIRouter(prefix="/payments", tags=["payments"])

ALLOWED_STATUSES = {"INITIATED", "AUTHORIZED", "PAID", "FAILED", "REFUNDED", "CANCELLED", "CANCELED"}


def _normalize_status(value: str) -> str:
    upper = value.strip().upper()
    return upper if upper in ALLOWED_STATUSES else "FAILED"


def _payment_read(db: Session, payment: Payment) -> PaymentRead:
    return PaymentRead(
        id=payment.id,
        order_id=payment.order_id,
        method=payment.method,
        status=payment.status,
        amount_cdf=payment.amount_cdf,
        currency=payment.currency,
        internal_reference=payment.internal_reference,
        provider_reference=payment.provider_reference,
    )


@router.post("", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
):
    order = db.get(Order, payload.order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404, detail="Commande introuvable.")
    existing = db.scalar(select(Payment).where(Payment.internal_reference == payload.internal_reference))
    if existing:
        return _payment_read(db, existing)
    payment = Payment(
        order_id=payload.order_id,
        method=payload.method,
        status="INITIATED",
        amount_cdf=payload.amount_cdf,
        currency="CDF",
        internal_reference=payload.internal_reference,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return _payment_read(db, payment)


@router.get("/order/{order_id}", response_model=PaymentRead)
def get_payment_by_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    payment = db.scalar(select(Payment).where(Payment.order_id == order_id).order_by(Payment.created_at.desc()))
    if not payment:
        raise HTTPException(status_code=status.HTTP_404, detail="Paiement introuvable.")
    return _payment_read(db, payment)


@router.post("/webhooks/{provider}", status_code=status.HTTP_200_OK)
def receive_webhook(
    provider: str = Path(min_length=1, max_length=30),
    payload: PaymentWebhookIn = ...,
    db: Session = Depends(get_db),
):
    provider = provider.strip().upper()
    event = db.scalar(
        select(PaymentWebhookEvent).where(
            PaymentWebhookEvent.provider == provider,
            PaymentWebhookEvent.provider_event_id == payload.provider_event_id,
        )
    )
    if event:
        # Événement déjà reçu : pas de retraitement (idempotence des webhooks).
        return {"status": "already_processed"}

    event = PaymentWebhookEvent(
        provider=provider,
        provider_event_id=payload.provider_event_id,
        processing_status="RECEIVED",
        payload_redacted=None,
    )
    db.add(event)
    db.flush()

    status_value = _normalize_status(payload.status)
    provider_reference = payload.provider_reference
    payment = None
    if payload.internal_reference:
        payment = db.scalar(select(Payment).where(Payment.internal_reference == payload.internal_reference))
    if not payment and provider_reference:
        payment = db.scalar(select(Payment).where(Payment.provider_reference == provider_reference))

    if payment:
        payment.provider_reference = provider_reference or payment.provider_reference
        payment.status = status_value
        payment.verified_at = datetime.now(timezone.utc) if status_value == "PAID" else payment.verified_at
        db.add(payment)

        if status_value == "PAID":
            order = db.get(Order, payment.order_id)
            if order and order.status != "PAID":
                order.status = "PAID"
                db.add(order)
                db.add(OrderStatusHistory(
                    order_id=order.id,
                    old_status=order.status if order.status != "PAID" else None,
                    new_status="PAID",
                    note="Paiement confirmé par webhook",
                ))
                # Confirmation définitive du stock : les réservations deviennent des ventes.
                reservations = db.scalars(
                    select(InventoryReservation).where(
                        InventoryReservation.order_id == order.id,
                        InventoryReservation.status == "ACTIVE",
                    )
                ).all()
                for reservation in reservations:
                    stock_service.commit_sale(db, reservation.id)

        elif status_value in {"FAILED", "CANCELLED", "CANCELED"}:
            order = db.get(Order, payment.order_id)
            if order and order.status == "PENDING_PAYMENT":
                order.status = "CANCELLED"
                db.add(order)
                db.add(OrderStatusHistory(
                    order_id=order.id,
                    old_status="PENDING_PAYMENT",
                    new_status="CANCELLED",
                    note="Paiement échoué ou annulé",
                ))
                reservations = db.scalars(
                    select(InventoryReservation).where(
                        InventoryReservation.order_id == order.id,
                        InventoryReservation.status == "ACTIVE",
                    )
                ).all()
                for reservation in reservations:
                    stock_service.release_reservation(db, reservation.id)

    event.processing_status = "PROCESSED"
    event.processed_at = datetime.now(timezone.utc)
    db.add(event)
    db.commit()
    return {"status": "processed"}
