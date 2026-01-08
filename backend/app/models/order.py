"""Order model"""
from pydantic import BaseModel
from typing import Optional, List

class OrderItem(BaseModel):
    """Item in an order"""
    menu_item_id: str
    name: str
    price: float
    quantity: int

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
