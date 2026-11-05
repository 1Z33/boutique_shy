from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.api.deps import require_admin
from app.db.session import get_db
from app.models import Category, Product, ProductVariant
from app.schemas.catalog import CategoryCreate, CategoryRead, ProductCreate, ProductRead, ProductUpdate, VariantCreate

router = APIRouter(prefix="/catalog", tags=["catalog"])

@router.get("/categories", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return db.scalars(select(Category).where(Category.is_active.is_(True)).order_by(Category.name)).all()

@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    category = Category(**payload.model_dump())
    db.add(category)
    try:
        db.commit()
        db.refresh(category)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Une catégorie avec ce nom ou slug existe déjà.")
    return category

@router.get("/products", response_model=list[ProductRead])
def list_products(
    category: str | None = None,
    q: str | None = Query(default=None, max_length=100),
    featured: bool | None = None,
    limit: int = Query(default=24, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Product).options(selectinload(Product.variants)).join(Category).where(
        Product.is_active.is_(True), Category.is_active.is_(True)
    )
    if category:
        stmt = stmt.where(Category.slug == category)
    if q:
        stmt = stmt.where(Product.name.ilike(f"%{q}%"))
    if featured is not None:
        stmt = stmt.where(Product.is_featured.is_(featured))
    return db.scalars(stmt.order_by(Product.created_at.desc()).offset(offset).limit(limit)).all()

@router.get("/products/{slug}", response_model=ProductRead)
def get_product(slug: str, db: Session = Depends(get_db)):
    product = db.scalar(
        select(Product).options(selectinload(Product.variants)).where(Product.slug == slug, Product.is_active.is_(True))
    )
    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable.")
    return product

@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude={"variants"})
    category = db.get(Category, data["category_id"])
    if not category or not category.is_active:
        raise HTTPException(status_code=400, detail="Catégorie invalide.")
    product = Product(**data)
    product.variants = [ProductVariant(**variant.model_dump()) for variant in payload.variants]
    db.add(product)
    try:
        db.commit()
        db.refresh(product)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Le slug du produit ou un SKU existe déjà.")
    return db.scalar(select(Product).options(selectinload(Product.variants)).where(Product.id == product.id))

@router.patch("/products/{product_id}", response_model=ProductRead, dependencies=[Depends(require_admin)])
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = db.scalar(select(Product).options(selectinload(Product.variants)).where(Product.id == product_id))
    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

@router.post("/products/{product_id}/variants", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def add_variant(product_id: int, payload: VariantCreate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable.")
    variant = ProductVariant(product_id=product_id, **payload.model_dump())
    db.add(variant)
    try:
        db.commit()
        db.refresh(variant)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ce SKU existe déjà pour ce produit.")
    return {"id": variant.id, "sku": variant.sku, "size": variant.size, "color": variant.color, "stock_quantity": variant.stock_quantity}
