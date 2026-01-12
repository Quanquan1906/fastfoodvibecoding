"""Simple auth service - NO JWT, NO password hashing"""
from app.core.database import get_db
from app.models.user import User, LoginRequest
from bson import ObjectId
from datetime import datetime
import re


class AuthService:
    """Simple login service"""

    async def login(self, request: LoginRequest) -> dict:
        """Login user - simple, no password validation"""
        db = get_db()

        username = (request.username or "").strip()
        role = (request.role or "").strip().upper()

        print("LOGIN:", username, "ROLE:", role)
        
        # Check if user exists
        user = await db.users.find_one({
            "username": {"$regex": f"^{re.escape(username)}$", "$options": "i"},
            "role": {"$regex": f"^{re.escape(role)}$", "$options": "i"},
        })
        
        if not user:
            # Create new user
            new_user = {
                "username": username,
                "role": role,
                "restaurant_id": None,
                "created_at": datetime.utcnow().isoformat(),
            }
            result = await db.users.insert_one(new_user)
            user = {"_id": result.inserted_id, **new_user}
        else:
            # Normalize stored values (helps prevent role-casing bugs)
            updates = {}
            if user.get("username") != username:
                updates["username"] = username
            if (user.get("role") or "").upper() != role:
                updates["role"] = role
            if updates:
                await db.users.update_one({"_id": user["_id"]}, {"$set": updates})
                user.update(updates)

        # For RESTAURANT users, find the restaurant where they are the owner
        restaurant_id = None
        if (user.get("role") or "").upper() == "RESTAURANT":
            # Query for existing restaurant with matching owner_username
            restaurant = await db.restaurants.find_one({
                "owner_username": {"$regex": f"^{re.escape(username)}$", "$options": "i"}
            })
            
            print("LOGIN RESTAURANT:", username, "FOUND:", restaurant)
            
            if not restaurant:
                # User is not the owner of any restaurant
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=403,
                    detail="You are not the owner of any restaurant"
                )
            
            restaurant_id = str(restaurant["_id"])
            
            # Update user's restaurant_id if it's not already set
            if not user.get("restaurant_id"):
                await db.users.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"restaurant_id": restaurant_id}},
                )

        return {
            "id": str(user["_id"]),
            "username": username,
            "role": role,
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
