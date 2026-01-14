"""User router - user endpoints"""
from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["users"])


@router.get("/admin/users")
async def get_all_users():
    """Get all users"""
    try:
        from app.infrastructure.persistence.database import get_db
        
        db = get_db()
        users = await db.users.find().to_list(None)
        return [
            {
                "id": str(u["_id"]),
                "username": u.get("username"),
                "role": u.get("role"),
                "restaurant_id": u.get("restaurant_id")
            }
            for u in users
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
