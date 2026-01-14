"""User domain entity"""
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    """User entity for CUSTOMER, RESTAURANT, ADMIN"""
    id: Optional[str] = None
    username: str
    role: str  # "CUSTOMER" | "RESTAURANT" | "ADMIN"
    restaurant_id: Optional[str] = None  # For RESTAURANT role
    created_at: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "username": "john_customer",
                "role": "CUSTOMER"
            }
        }


class LoginRequest(BaseModel):
    """Login request"""
    username: str
    role: str
