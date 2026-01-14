"""Restaurant domain entity"""
from pydantic import BaseModel
from typing import Optional

class Restaurant(BaseModel):
    """Restaurant (Multi-tenant)"""
    id: Optional[str] = None
    name: str
    owner_id: str
    owner_username: str  # Username of the restaurant owner
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    image_url: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Pizza Palace",
                "owner_id": "owner_123",
                "owner_username": "john_pizza",
                "description": "Best pizza in town"
            }
        }
