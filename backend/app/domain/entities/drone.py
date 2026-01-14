"""Drone domain entity"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class DroneStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"


class Drone(BaseModel):
    """Drone for delivery"""
    id: Optional[str] = None
    name: str
    restaurant_id: Optional[str] = None
    status: DroneStatus = Field(default=DroneStatus.AVAILABLE)
    latitude: float = 10.762622  # Hanoi default
    longitude: float = 106.660172  # Hanoi default
    created_at: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Drone-01",
                "restaurant_id": "<restaurant_object_id>",
                "status": "AVAILABLE",
            }
        }
    )

    @model_validator(mode="before")
    @classmethod
    def _normalize_legacy_status(cls, data):
        # Backward-compat: older code stored IDLE, treat as AVAILABLE.
        if isinstance(data, dict) and data.get("status") == "IDLE":
            data = dict(data)
            data["status"] = "AVAILABLE"
        return data
