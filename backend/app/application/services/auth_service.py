"""Auth service - business logic for authentication"""
from app.application.ports.repository_port import UserRepository, RestaurantRepository
from app.domain.entities.user import LoginRequest
from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException


class AuthService:
    """Authentication service - NO direct database access"""
    
    def __init__(self, user_repo: UserRepository, restaurant_repo: RestaurantRepository):
        self.user_repo = user_repo
        self.restaurant_repo = restaurant_repo
    
    async def login(self, request: LoginRequest) -> Dict[str, Any]:
        """Login user - simple, no password validation"""
        username = (request.username or "").strip()
        role = (request.role or "").strip().upper()
        
        print("LOGIN:", username, "ROLE:", role)
        
        # Check if user exists
        user = await self.user_repo.find_by_username(username, role)
        
        if not user:
            # Create new user
            new_user = {
                "username": username,
                "role": role,
                "restaurant_id": None,
                "created_at": datetime.utcnow().isoformat(),
            }
            user = await self.user_repo.save(new_user)
        else:
            # Normalize stored values
            updates = {}
            if user.get("username") != username:
                updates["username"] = username
            if (user.get("role") or "").upper() != role:
                updates["role"] = role
            if updates:
                user = await self.user_repo.update(user["id"], updates)
        
        # For RESTAURANT users, find the restaurant where they are the owner
        restaurant_id = None
        if (user.get("role") or "").upper() == "RESTAURANT":
            restaurant = await self.restaurant_repo.find_by_owner(username)
            
            print("LOGIN RESTAURANT:", username, "FOUND:", restaurant)
            
            if not restaurant:
                raise HTTPException(
                    status_code=403,
                    detail="You are not the owner of any restaurant"
                )
            
            restaurant_id = restaurant["id"]
            
            # Update user's restaurant_id if it's not already set
            if not user.get("restaurant_id"):
                user = await self.user_repo.update(user["id"], {"restaurant_id": restaurant_id})
        
        return {
            "id": user["id"],
            "username": username,
            "role": role,
            "restaurant_id": restaurant_id,
        }
    
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user by ID"""
        user = await self.user_repo.find_by_id(user_id)
        
        if not user:
            return None
        
        return {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "restaurant_id": user.get("restaurant_id")
        }
