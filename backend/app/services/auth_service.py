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
        
        if not user:
            # Create new user
            new_user = {
                "username": request.username,
                "role": request.role,
                "restaurant_id": None,
                "created_at": datetime.utcnow().isoformat(),
            }
            result = await db.users.insert_one(new_user)
            user = {"_id": result.inserted_id, **new_user}

        # For RESTAURANT users, ensure they have a restaurant_id.
        restaurant_id = user.get("restaurant_id")
        if user.get("role") == "RESTAURANT" and not restaurant_id:
            # Create a default restaurant owned by this user.
            rest_doc = {
                "name": f"{user['username']} Restaurant",
                "owner_id": str(user["_id"]),
                "description": "",
                "address": "",
                "phone": "",
                "created_at": datetime.utcnow().isoformat(),
            }
            rest_result = await db.restaurants.insert_one(rest_doc)
            restaurant_id = str(rest_result.inserted_id)
            await db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"restaurant_id": restaurant_id}},
            )

        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "role": user["role"],
            "restaurant_id": restaurant_id,
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
