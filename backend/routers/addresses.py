from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
import datetime

router = APIRouter(prefix="/api/addresses", tags=["addresses"])

class Address(BaseModel):
    id: Optional[str] = None
    user_id: str
    name: str
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

addresses_db: List[dict] = []

@router.get("", response_model=List[dict])
def get_addresses():
    return addresses_db

@router.post("", response_model=dict)
def create_address(address: Address):
    address_dict = address.model_dump()
    address_dict["id"] = str(uuid.uuid4())
    address_dict["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    address_dict["updated_at"] = address_dict["created_at"]

    # If is_default is true, set others to false for this user
    if address_dict.get("is_default"):
        for addr in addresses_db:
            if addr.get("user_id") == address_dict["user_id"]:
                addr["is_default"] = False

    addresses_db.append(address_dict)
    return address_dict

@router.put("/{address_id}", response_model=dict)
def update_address(address_id: str, address_update: Address):
    for i, addr in enumerate(addresses_db):
        if addr["id"] == address_id:
            update_dict = address_update.model_dump(exclude_unset=True)

            # If is_default is true, set others to false for this user
            if update_dict.get("is_default"):
                for other_addr in addresses_db:
                    if other_addr.get("user_id") == addr.get("user_id") and other_addr["id"] != address_id:
                        other_addr["is_default"] = False

            addr.update(update_dict)
            addr["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            # Ensure ID stays the same
            addr["id"] = address_id
            return addr

    raise HTTPException(status_code=404, detail="Address not found")

@router.delete("/{address_id}")
def delete_address(address_id: str):
    for i, addr in enumerate(addresses_db):
        if addr["id"] == address_id:
            del addresses_db[i]
            return {"detail": "Address deleted"}

    raise HTTPException(status_code=404, detail="Address not found")
