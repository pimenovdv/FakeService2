from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import uuid
import time

router = APIRouter(prefix="/api/payments", tags=["payments"])

# In-memory store for mock payments
mock_payments: Dict[str, dict] = {}

class PaymentRequest(BaseModel):
    amount: float
    currency: str
    payment_method: str
    description: Optional[str] = None

class PaymentResponse(BaseModel):
    payment_id: str
    status: str
    amount: float
    currency: str
    timestamp: float

@router.post("", response_model=PaymentResponse)
async def process_payment(request: PaymentRequest):
    payment_id = str(uuid.uuid4())

    # Simulate basic validation
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    payment_data = {
        "payment_id": payment_id,
        "status": "success", # Mocking successful payment
        "amount": request.amount,
        "currency": request.currency,
        "timestamp": time.time()
    }

    # Store payment
    mock_payments[payment_id] = payment_data

    return PaymentResponse(**payment_data)

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment_status(payment_id: str):
    payment = mock_payments.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return PaymentResponse(**payment)
