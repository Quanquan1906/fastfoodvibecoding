"""Drone model"""
from pydantic import BaseModel
from typing import Optional

class Drone(BaseModel):
    """Drone for delivery"""
    id: Optional[str] = None
    name: str
    restaurant_id: str
    status: str = "IDLE"  # IDLE | BUSY
    latitude: float = 10.762622  # Hanoi default
    longitude: float = 106.660172  # Hanoi default
    created_at: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Drone-01",
                "restaurant_id": "rest_123",
                "status": "IDLE"
            }
        }
