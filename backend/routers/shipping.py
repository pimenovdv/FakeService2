from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
from typing import List, Optional
import uuid

router = APIRouter(prefix="/api/shipping", tags=["shipping"])

# Models for calculating shipping rates
class ShippingItem(BaseModel):
    product_id: str
    weight_kg: float
    dimensions_cm: Optional[List[float]] = None # [length, width, height]

class ShippingCalculateRequest(BaseModel):
    destination_country: str
    destination_zip: str
    items: List[ShippingItem]

class ShippingOption(BaseModel):
    service_id: str
    service_name: str
    cost: float
    estimated_days: int

class ShippingCalculateResponse(BaseModel):
    options: List[ShippingOption]

# Models for tracking shipments
class ShipmentTrackingEvent(BaseModel):
    timestamp: str
    location: str
    status: str

class ShipmentTrackingInfo(BaseModel):
    tracking_number: str
    carrier: str
    status: str
    events: List[ShipmentTrackingEvent]

@router.post("/calculate", response_model=ShippingCalculateResponse)
async def calculate_shipping(request: ShippingCalculateRequest):
    """Calculate mock shipping rates based on items and destination."""
    # Basic mock logic for calculating shipping
    total_weight = sum(item.weight_kg for item in request.items)

    # Mock different shipping options
    standard_cost = max(5.0, total_weight * 2.5)
    express_cost = max(15.0, total_weight * 5.0)

    options = [
        ShippingOption(
            service_id="standard_1",
            service_name="Standard Shipping",
            cost=round(standard_cost, 2),
            estimated_days=5
        ),
        ShippingOption(
            service_id="express_1",
            service_name="Express Shipping",
            cost=round(express_cost, 2),
            estimated_days=2
        )
    ]

    return ShippingCalculateResponse(options=options)

@router.get("/track/{tracking_number}", response_model=ShipmentTrackingInfo)
async def track_shipment(tracking_number: str = Path(...)):
    """Track a shipment by its tracking number."""
    if tracking_number.startswith("ERR"):
        raise HTTPException(status_code=404, detail="Tracking number not found")

    # Mock successful tracking response
    return ShipmentTrackingInfo(
        tracking_number=tracking_number,
        carrier="MockCarrier Express",
        status="In Transit",
        events=[
            ShipmentTrackingEvent(
                timestamp="2023-10-26T10:00:00Z",
                location="Origin Facility, NY",
                status="Package received by carrier"
            ),
            ShipmentTrackingEvent(
                timestamp="2023-10-27T14:30:00Z",
                location="Transit Center, PA",
                status="In Transit"
            )
        ]
    )
