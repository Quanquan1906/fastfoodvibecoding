"""Menu Item model"""
from pydantic import BaseModel
from typing import Optional

class MenuItem(BaseModel):
    """Menu item in a restaurant"""
    id: Optional[str] = None
    restaurant_id: str
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    available: bool = True
    created_at: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "restaurant_id": "rest_123",
                "name": "Margherita Pizza",
                "price": 12.99
            }
        }
