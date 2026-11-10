import hashlib

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_optional
from app.db.session import get_db
from app.models import Cart, CartItem, ProductVariant
from app.services.stock import available_quantity
from app.schemas.commerce import CartRead, CartItemCreate, CartItemUpdate, CartItemRead

router = APIRouter(prefix="/cart", tags=["cart"])


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _resolve_cart(db: Session, user_id: int | None, guest_token: str | None) -> Cart:
    if user_id:
        cart = db.scalar(select(Cart).where(Cart.user_id == user_id, Cart.is_active.is_(True)).order_by(Cart.id.desc()))
        if cart:
            return cart
        cart = Cart(user_id=user_id, is_active=True)
        db.add(cart)
        try:
            db.commit()
            db.refresh(cart)
            return cart
        except IntegrityError:
            db.rollback()
            cart = db.scalar(select(Cart).where(Cart.user_id == user_id, Cart.is_active.is_(True)).order_by(Cart.id.desc()))
            if cart:
                return cart
            raise

    if guest_token:
        token_hash = _token_hash(guest_token)
        cart = db.scalar(
            select(Cart).where(Cart.guest_token_hash == token_hash, Cart.is_active.is_(True)).order_by(Cart.id.desc())
        )
        if cart:
            return cart
        existing = db.scalar(select(Cart).where(Cart.guest_token_hash == token_hash).order_by(Cart.id.desc()))
        if existing:
            existing.is_active = True
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing
        cart = Cart(guest_token_hash=token_hash, is_active=True)
        db.add(cart)
        try:
            db.commit()
            db.refresh(cart)
            return cart
        except IntegrityError:
            db.rollback()
            cart = db.scalar(select(Cart).where(Cart.guest_token_hash == token_hash).order_by(Cart.id.desc()))
            if cart:
                if not cart.is_active:
                    cart.is_active = True
                    db.add(cart)
                    db.commit()
                    db.refresh(cart)
                return cart
            raise

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Utilisateur ou panier invité requis.")


def _cart_read(db: Session, cart: Cart) -> CartRead:
    items = db.scalars(
        select(CartItem).where(CartItem.cart_id == cart.id).order_by(CartItem.id)
    ).all()
    return CartRead(
        id=cart.id,
        is_active=cart.is_active,
        items=[CartItemRead(id=i.id, variant_id=i.variant_id, quantity=i.quantity) for i in items],
    )


@router.get("", response_model=CartRead)
def get_cart(
    authorization: str | None = Header(default=None),
    x_guest_token: str | None = Header(default=None, alias="X-Guest-Token"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None
    cart = _resolve_cart(db, user_id, x_guest_token)
    return _cart_read(db, cart)


@router.post("/items", response_model=CartRead, status_code=status.HTTP_201_CREATED)
def add_cart_item(
    payload: CartItemCreate,
    authorization: str | None = Header(default=None),
    x_guest_token: str | None = Header(default=None, alias="X-Guest-Token"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None
    cart = _resolve_cart(db, user_id, x_guest_token)

    variant = db.get(ProductVariant, payload.variant_id)
    if not variant or not variant.is_active:
        raise HTTPException(status_code=status.HTTP_404, detail="Variante introuvable.")

    if available_quantity(db, payload.variant_id) < payload.quantity:
        raise HTTPException(status_code=409, detail="Stock insuffisant pour cette variante.")

    existing = db.scalar(
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.variant_id == payload.variant_id)
    )
    if existing:
        new_quantity = existing.quantity + payload.quantity
        if available_quantity(db, payload.variant_id) < new_quantity:
            raise HTTPException(status_code=409, detail="Stock insuffisant pour cette variante.")
        existing.quantity = new_quantity
        db.add(existing)
    else:
        db.add(CartItem(cart_id=cart.id, variant_id=payload.variant_id, quantity=payload.quantity))
    db.commit()
    return _cart_read(db, cart)


@router.patch("/items/{item_id}", response_model=CartRead)
def update_cart_item(
    item_id: int,
    payload: CartItemUpdate,
    authorization: str | None = Header(default=None),
    x_guest_token: str | None = Header(default=None, alias="X-Guest-Token"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None
    cart = _resolve_cart(db, user_id, x_guest_token)
    item = db.scalar(select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id))
    if not item:
        raise HTTPException(status_code=status.HTTP_404, detail="Article de panier introuvable.")

    if available_quantity(db, item.variant_id) < payload.quantity:
        raise HTTPException(status_code=409, detail="Stock insuffisant pour cette variante.")
    item.quantity = payload.quantity
    db.add(item)
    db.commit()
    return _cart_read(db, cart)


@router.delete("/items/{item_id}", response_model=CartRead)
def remove_cart_item(
    item_id: int,
    authorization: str | None = Header(default=None),
    x_guest_token: str | None = Header(default=None, alias="X-Guest-Token"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None
    cart = _resolve_cart(db, user_id, x_guest_token)
    item = db.scalar(select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id))
    if not item:
        raise HTTPException(status_code=status.HTTP_404, detail="Article de panier introuvable.")
    db.delete(item)
    db.commit()
    return _cart_read(db, cart)


@router.delete("", response_model=CartRead)
def clear_cart(
    authorization: str | None = Header(default=None),
    x_guest_token: str | None = Header(default=None, alias="X-Guest-Token"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None
    cart = _resolve_cart(db, user_id, x_guest_token)
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    return _cart_read(db, cart)
