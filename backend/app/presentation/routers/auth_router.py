"""Auth router - authentication endpoints"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.domain.entities.user import LoginRequest
from app.application.services.auth_service import AuthService

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=None)
async def login(request: LoginRequest):
    """Simple login - create or get user"""
    try:
        from app.infrastructure.persistence.repositories.mongo_repository import MongoUserRepository, MongoRestaurantRepository
        
        user_repo = MongoUserRepository()
        restaurant_repo = MongoRestaurantRepository()
        service = AuthService(user_repo, restaurant_repo)
        
        user = await service.login(request)
        return JSONResponse({
            "success": True,
            "user": user
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
