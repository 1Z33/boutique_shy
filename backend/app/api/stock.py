from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import require_admin
from app.db.session import get_db
from app.models import ProductVariant, Inventory
from app.services import stock as stock_service
from app.schemas.commerce import StockAdjustment, LowStockItem

router = APIRouter(prefix="/stock", tags=["stock"])


@router.get("/low-stock", response_model=list[LowStockItem], dependencies=[Depends(require_admin)])
def list_low_stock(db: Session = Depends(get_db)):
    rows = stock_service.list_low_stock(db)
    result = []
    for inventory in rows:
        variant = db.get(ProductVariant, inventory.variant_id)
        result.append(LowStockItem(
            variant_id=inventory.variant_id,
            physical_quantity=inventory.physical_quantity,
            reserved_quantity=inventory.reserved_quantity,
            available_quantity=max(0, inventory.physical_quantity - inventory.reserved_quantity),
            low_stock_threshold=inventory.low_stock_threshold,
        ))
    return result


@router.post("/adjust", dependencies=[Depends(require_admin)])
def adjust_stock(payload: StockAdjustment, db: Session = Depends(get_db)):
    variant = db.get(ProductVariant, payload.variant_id)
    if not variant:
        raise HTTPException(status_code=status.HTTP_404, detail="Variante introuvable.")
    inventory = stock_service.adjust_stock(
        db,
        variant_id=payload.variant_id,
        quantity=payload.quantity,
        reason=payload.reason,
        movement_type=payload.movement_type,
    )
    return {
        "variant_id": inventory.variant_id,
        "physical_quantity": inventory.physical_quantity,
        "reserved_quantity": inventory.reserved_quantity,
    }
