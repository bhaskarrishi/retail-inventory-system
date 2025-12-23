from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    sku: str
    price: float
    quantity: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    sku: str | None = None
    price: float | None = None
    quantity: int | None = None


class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True  # allows returning SQLAlchemy models directly