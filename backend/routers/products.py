from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

router = APIRouter(prefix="/api/products", tags=["products"])

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None

class Product(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    stock: int

# In-memory store for products
MOCK_PRODUCTS = {}

@router.post("", response_model=Product)
async def create_product(product: ProductCreate):
    product_id = str(uuid.uuid4())

    new_product = Product(
        id=product_id,
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock
    )
    MOCK_PRODUCTS[product_id] = new_product
    return new_product

@router.get("", response_model=List[Product])
async def list_products():
    return list(MOCK_PRODUCTS.values())

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    if product_id not in MOCK_PRODUCTS:
        raise HTTPException(status_code=404, detail="Product not found")
    return MOCK_PRODUCTS[product_id]

@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: str, product_update: ProductUpdate):
    if product_id not in MOCK_PRODUCTS:
        raise HTTPException(status_code=404, detail="Product not found")

    product = MOCK_PRODUCTS[product_id]

    if product_update.name is not None:
        product.name = product_update.name
    if product_update.description is not None:
        product.description = product_update.description
    if product_update.price is not None:
        product.price = product_update.price
    if product_update.stock is not None:
        product.stock = product_update.stock

    return product

@router.delete("/{product_id}")
async def delete_product(product_id: str):
    if product_id not in MOCK_PRODUCTS:
        raise HTTPException(status_code=404, detail="Product not found")

    del MOCK_PRODUCTS[product_id]
    return {"detail": "Product deleted successfully"}
