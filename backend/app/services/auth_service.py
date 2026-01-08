"""Simple auth service - NO JWT, NO password hashing"""
from app.core.database import get_db
from app.models.user import User, LoginRequest
from bson import ObjectId
from datetime import datetime


class AuthService:
    """Simple login service"""

    async def login(self, request: LoginRequest) -> dict:
        """Login user - simple, no password validation"""
        db = get_db()
        
        # Check if user exists
        user = await db.users.find_one({
            "username": request.username,
            "role": request.role
        })
        
        if user:
            # Return existing user
            return {
                "id": str(user["_id"]),
                "username": user["username"],
                "role": user["role"],
                "restaurant_id": user.get("restaurant_id")
            }
        else:
            # Create new user
            new_user = {
                "username": request.username,
                "role": request.role,
                "created_at": datetime.utcnow().isoformat()
            }
            result = await db.users.insert_one(new_user)
            
            return {
                "id": str(result.inserted_id),
                "username": request.username,
                "role": request.role,
                "restaurant_id": None
            }

    async def get_user(self, user_id: str) -> dict:
        """Get user by ID"""
        db = get_db()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            return None
        
        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "role": user["role"],
            "restaurant_id": user.get("restaurant_id")
        }
