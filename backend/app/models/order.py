"""Order model"""
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Optional

class OrderItem(BaseModel):
    """Item in an order"""
    menu_item_id: str
    name: str
    price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=1)


class OrderCreate(BaseModel):
    """Payload for creating an order (request body)."""

    customer_id: str
    restaurant_id: str
    items: List[OrderItem] = Field(..., min_length=1)
    total_price: float = Field(..., ge=0)

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "customer_id": "cust_123",
                "restaurant_id": "rest_123",
                "items": [
                    {"menu_item_id": "item_1", "name": "Pizza", "price": 12.99, "quantity": 1}
                ],
                "total_price": 12.99,
            }
        },
    )

    @model_validator(mode="before")
    @classmethod
    def _accept_legacy_total(cls, data):
        # Backward-compat: some clients still send {"total": ...}
        if isinstance(data, dict) and "total_price" not in data and "total" in data:
            data = dict(data)
            data["total_price"] = data["total"]
        return data

class Order(BaseModel):
    """Order placed by customer"""
    id: Optional[str] = None
    customer_id: str
    restaurant_id: str
    drone_id: Optional[str] = None
    items: List[OrderItem]
    total: float
    status: str = "PENDING"  # PENDING | PREPARING | READY_FOR_PICKUP | DELIVERING | COMPLETED
    delivery_lat: float = 10.762622
    delivery_lon: float = 106.660172
    drone_lat: float = 10.762622
    drone_lon: float = 106.660172
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "customer_id": "cust_123",
                "restaurant_id": "rest_123",
                "items": [
                    {"menu_item_id": "item_1", "name": "Pizza", "price": 12.99, "quantity": 1}
                ],
                "total": 12.99
            }
        }
