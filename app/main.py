from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, crud
from .db import Base, engine, get_db

# Create database tables on startup (simple approach for demo)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Retail Inventory Manager",
    description="Simple inventory management API for a retail store.",
    version="1.0.0",
)


@app.get("/", response_class=HTMLResponse)
def read_root():
    # Simple landing page pointing to docs
    return """
    <html>
        <head>
            <title>Retail Inventory Manager</title>
        </head>
        <body>
            <h1>Retail Inventory Manager API</h1>
            <p>Use the <a href="/docs">interactive API docs</a> to manage products.</p>
        </body>
    </html>
    """


@app.get("/products", response_model=List[schemas.Product])
def read_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products


@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


@app.post(
    "/products",
    response_model=schemas.Product,
    status_code=status.HTTP_201_CREATED,
)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    existing = crud.get_product_by_sku(db, product.sku)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists",
        )
    new_product = crud.create_product(db, product)
    return new_product


@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    updates: schemas.ProductUpdate,
    db: Session = Depends(get_db),
):
    updated = crud.update_product(db, product_id, updates)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return updated


@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    success = crud.delete_product(db, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return None