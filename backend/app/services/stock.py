from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Inventory, InventoryReservation, StockMovement

RESERVATION_TTL_MINUTES = 30

MOVEMENT_RESERVATION = "RESERVATION"
MOVEMENT_RELEASE = "RELEASE"
MOVEMENT_SALE = "SALE"
MOVEMENT_RESTOCK = "RESTOCK"
MOVEMENT_ADJUSTMENT = "ADJUSTMENT"


def _get_inventory(db: Session, variant_id: int) -> Inventory | None:
    return db.scalar(select(Inventory).where(Inventory.variant_id == variant_id))


def record_movement(
    db: Session,
    inventory_id: int,
    movement_type: str,
    quantity: int,
    reason: str,
    actor_user_id: int | None = None,
) -> StockMovement:
    movement = StockMovement(
        inventory_id=inventory_id,
        movement_type=movement_type,
        quantity=quantity,
        reason=reason,
        actor_user_id=actor_user_id,
    )
    db.add(movement)
    db.flush()
    return movement


def available_quantity(db: Session, variant_id: int) -> int:
    inventory = _get_inventory(db, variant_id)
    if not inventory:
        return 0
    return max(0, inventory.physical_quantity - inventory.reserved_quantity)


def is_low_stock(db: Session, variant_id: int) -> bool:
    inventory = _get_inventory(db, variant_id)
    if not inventory:
        return False
    return (inventory.physical_quantity - inventory.reserved_quantity) <= inventory.low_stock_threshold


def reserve_stock(
    db: Session,
    variant_id: int,
    quantity: int,
    order_id: int | None,
    actor_user_id: int | None,
    ttl_minutes: int = RESERVATION_TTL_MINUTES,
) -> InventoryReservation:
    inventory = _get_inventory(db, variant_id)
    if not inventory:
        raise ValueError("Aucun stock configuré pour cette variante.")
    if available_quantity(db, variant_id) < quantity:
        raise ValueError("Stock insuffisant pour cette variante.")

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
    reservation = InventoryReservation(
        inventory_id=inventory.id,
        order_id=order_id,
        quantity=quantity,
        status="ACTIVE",
        expires_at=expires_at,
    )
    db.add(reservation)
    db.flush()

    inventory.reserved_quantity += quantity
    db.add(inventory)

    record_movement(
        db,
        inventory.id,
        MOVEMENT_RESERVATION,
        quantity,
        f"Réservation de stock pour la variante {variant_id}",
        actor_user_id,
    )
    db.flush()
    return reservation


def release_reservation(db: Session, reservation_id: int, actor_user_id: int | None = None) -> bool:
    reservation = db.get(InventoryReservation, reservation_id)
    if not reservation or reservation.status != "ACTIVE":
        return False
    inventory = db.get(Inventory, reservation.inventory_id)
    if inventory:
        inventory.reserved_quantity = max(0, inventory.reserved_quantity - reservation.quantity)
        db.add(inventory)
        record_movement(
            db,
            inventory.id,
            MOVEMENT_RELEASE,
            reservation.quantity,
            f"Libération de réservation {reservation.id}",
            actor_user_id,
        )
    reservation.status = "RELEASED"
    db.add(reservation)
    db.flush()
    return True


def commit_sale(db: Session, reservation_id: int, actor_user_id: int | None = None) -> bool:
    reservation = db.get(InventoryReservation, reservation_id)
    if not reservation or reservation.status != "ACTIVE":
        return False
    inventory = db.get(Inventory, reservation.inventory_id)
    if inventory:
        inventory.physical_quantity = max(0, inventory.physical_quantity - reservation.quantity)
        inventory.reserved_quantity = max(0, inventory.reserved_quantity - reservation.quantity)
        db.add(inventory)
        record_movement(
            db,
            inventory.id,
            MOVEMENT_SALE,
            reservation.quantity,
            f"Vente confirmée (réservation {reservation.id})",
            actor_user_id,
        )
    reservation.status = "SOLD"
    db.add(reservation)
    db.flush()
    return True


def adjust_stock(
    db: Session,
    variant_id: int,
    quantity: int,
    reason: str,
    movement_type: str,
    actor_user_id: int | None = None,
) -> Inventory:
    inventory = _get_inventory(db, variant_id)
    if not inventory:
        raise ValueError("Aucun stock configuré pour cette variante.")
    if movement_type == "RESTOCK":
        inventory.physical_quantity += quantity
    else:
        inventory.physical_quantity = max(0, inventory.physical_quantity + quantity)
    db.add(inventory)
    record_movement(
        db,
        inventory.id,
        movement_type,
        abs(quantity),
        reason,
        actor_user_id,
    )
    db.flush()
    return inventory


def list_low_stock(db: Session) -> list[Inventory]:
    stmt = select(Inventory)
    rows = db.scalars(stmt).all()
    result = []
    for inventory in rows:
        if (inventory.physical_quantity - inventory.reserved_quantity) <= inventory.low_stock_threshold:
            result.append(inventory)
    return result
