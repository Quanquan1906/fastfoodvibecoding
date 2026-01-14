"""User domain entity"""
from typing import Optional
from pydantic import BaseModel


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
