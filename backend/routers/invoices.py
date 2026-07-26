from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/invoices", tags=["invoices"])

class InvoiceItem(BaseModel):
    description: str
    amount: float

class InvoiceCreate(BaseModel):
    items: List[InvoiceItem] = Field(..., min_length=1)
    customer_id: str

class Invoice(BaseModel):
    id: str
    items: List[InvoiceItem]
    customer_id: str
    total_amount: float
    status: str
    created_at: datetime
    paid_at: Optional[datetime] = None

# In-memory store for invoices
MOCK_INVOICES = {}

@router.post("", response_model=Invoice)
async def create_invoice(invoice: InvoiceCreate):
    invoice_id = str(uuid.uuid4())
    now = datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None)
    total_amount = sum(item.amount for item in invoice.items)

    new_invoice = Invoice(
        id=invoice_id,
        items=invoice.items,
        customer_id=invoice.customer_id,
        total_amount=total_amount,
        status="unpaid",
        created_at=now
    )
    MOCK_INVOICES[invoice_id] = new_invoice
    return new_invoice

@router.get("", response_model=List[Invoice])
async def list_invoices():
    invoices = list(MOCK_INVOICES.values())
    # Sort by created_at descending
    invoices.sort(key=lambda x: x.created_at, reverse=True)
    return invoices

@router.get("/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: str):
    if invoice_id not in MOCK_INVOICES:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return MOCK_INVOICES[invoice_id]

@router.patch("/{invoice_id}/pay", response_model=Invoice)
async def pay_invoice(invoice_id: str):
    if invoice_id not in MOCK_INVOICES:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice = MOCK_INVOICES[invoice_id]
    if invoice.status == "paid":
        raise HTTPException(status_code=400, detail="Invoice already paid")

    invoice.status = "paid"
    invoice.paid_at = datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None)

    return invoice
