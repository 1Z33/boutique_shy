from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str | None = None

class CategoryRead(CategoryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool

class VariantCreate(BaseModel):
    sku: str = Field(min_length=2, max_length=80)
    size: str | None = Field(default=None, max_length=30)
    color: str | None = Field(default=None, max_length=60)
    stock_quantity: int = Field(default=0, ge=0)

class VariantRead(VariantCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool

class ProductCreate(BaseModel):
    category_id: int = Field(gt=0)
    name: str = Field(min_length=2, max_length=180)
    slug: str = Field(min_length=2, max_length=200, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str | None = None
    price_cdf: int = Field(gt=0)
    images: list[str] = Field(default_factory=list, max_length=12)
    is_featured: bool = False
    variants: list[VariantCreate] = Field(default_factory=list)

    @field_validator("images")
    @classmethod
    def validate_images(cls, values: list[str]) -> list[str]:
        for value in values:
            if not value.startswith(("https://", "http://")):
                raise ValueError("Chaque image doit être une URL HTTP(S).")
        return values

class ProductUpdate(BaseModel):
    category_id: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=2, max_length=180)
    slug: str | None = Field(default=None, min_length=2, max_length=200, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str | None = None
    price_cdf: int | None = Field(default=None, gt=0)
    images: list[str] | None = Field(default=None, max_length=12)
    is_active: bool | None = None
    is_featured: bool | None = None

class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: int
    name: str
    slug: str
    description: str | None
    price_cdf: int
    currency: Literal["CDF"]
    images: list[str]
    is_active: bool
    is_featured: bool
    variants: list[VariantRead]
