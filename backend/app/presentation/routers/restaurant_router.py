"""Restaurant router - restaurant endpoints"""
from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from bson.errors import InvalidId
from typing import Optional
from app.application.services.restaurant_service import RestaurantService
from app.application.ports.external_service_port import ImageUploadService
from app.infrastructure.external.cloudinary_client import CloudinaryNotConfiguredError

router = APIRouter(tags=["restaurants"])


def _parse_object_id(value: str, *, field_name: str) -> ObjectId:
    """Parse a MongoDB ObjectId from a string"""
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")


@router.get("/restaurants")
async def get_restaurants(page: int = 1, limit: int = 6):
    """Get paginated restaurants"""
    from app.infrastructure.persistence.repositories.mongo_repository import MongoRestaurantRepository
    from app.infrastructure.persistence.database import get_db
    
    db = get_db()
    
    # Validate pagination params
    page = max(1, page)
    limit = max(1, min(limit, 100))
    
    # Calculate skip
    skip = (page - 1) * limit
    
    # Get total count
    total = await db.restaurants.count_documents({})
    
    # Get paginated restaurants
    cursor = db.restaurants.find().skip(skip).limit(limit)
    restaurants = await cursor.to_list(None)
    
    # Calculate total pages
    total_pages = (total + limit - 1) // limit
    
    def _serialize(r):
        return {
            "id": str(r["_id"]),
            "name": r.get("name"),
            "owner_id": r.get("owner_id"),
            "owner_username": r.get("owner_username"),
            "description": r.get("description"),
            "address": r.get("address"),
            "phone": r.get("phone"),
            "image_url": r.get("image_url"),
            "created_at": r.get("created_at")
        }
    
    return {
        "data": [_serialize(r) for r in restaurants],
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": total_pages
    }


@router.get("/restaurants/{restaurant_id}")
async def get_restaurant(restaurant_id: str, username: Optional[str] = None, role: Optional[str] = None):
    """Get restaurant details with ownership check for Restaurant users"""
    from app.infrastructure.persistence.database import get_db
    
    db = get_db()
    rid = _parse_object_id(restaurant_id, field_name="restaurant_id")
    restaurant = await db.restaurants.find_one({"_id": rid})
    
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Check access control
    if role == "RESTAURANT" and username:
        owner_username = restaurant.get("owner_username", "").strip().lower()
        username_normalized = username.strip().lower()
        
        print(f"[OWNERSHIP CHECK] Owner: '{owner_username}' | User: '{username_normalized}'")
        
        if owner_username and owner_username != username_normalized:
            print(f"[OWNERSHIP CHECK] DENIED")
            raise HTTPException(status_code=403, detail="You are not the owner of this restaurant.")
        
        print(f"[OWNERSHIP CHECK] ALLOWED")

    def _serialize(r):
        return {
            "id": str(r["_id"]),
            "name": r.get("name"),
            "owner_id": r.get("owner_id"),
            "owner_username": r.get("owner_username"),
            "description": r.get("description"),
            "address": r.get("address"),
            "phone": r.get("phone"),
            "image_url": r.get("image_url"),
            "created_at": r.get("created_at")
        }
    
    return _serialize(restaurant)


@router.get("/restaurants/{restaurant_id}/menu")
async def get_restaurant_menu(restaurant_id: str):
    """Get menu items for restaurant"""
    from app.infrastructure.persistence.database import get_db
    
    db = get_db()
    rid = _parse_object_id(restaurant_id, field_name="restaurant_id")

    # Restaurant must exist
    restaurant = await db.restaurants.find_one({"_id": rid})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Support both legacy string and ObjectId storage
    cursor = db.menu_items.find({"restaurant_id": {"$in": [rid, str(rid)]}})
    items = await cursor.to_list(None)
    
    def _serialize(item):
        return {
            "id": str(item["_id"]),
            "restaurant_id": str(item.get("restaurant_id")),
            "name": item.get("name"),
            "description": item.get("description"),
            "price": item.get("price"),
            "image_url": item.get("image_url"),
            "available": item.get("available"),
            "created_at": item.get("created_at")
        }
    
    return [_serialize(item) for item in items]


@router.post("/admin/restaurants")
async def create_restaurant(
    name: str = Form(...),
    owner_id: str = Form(...),
    owner_username: str = Form(...),
    description: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
):
    """Create restaurant with image upload"""
    from app.infrastructure.persistence.database import get_db
    from app.infrastructure.external.cloudinary_client import upload_restaurant_image
    
    db = get_db()

    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="name is required")
    if not owner_id or not owner_id.strip():
        raise HTTPException(status_code=400, detail="owner_id is required")
    if not owner_username or not owner_username.strip():
        raise HTTPException(status_code=400, detail="owner_username is required")
    if image is None or not image.filename:
        raise HTTPException(status_code=400, detail="image file is required")
    if image.content_type and not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="image must be an image/* content type")

    try:
        try:
            image.file.seek(0)
        except:
            pass
        image_url = await upload_restaurant_image(image.file, filename=image.filename)
    except CloudinaryNotConfiguredError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

    rest_doc = {
        "name": name,
        "owner_id": owner_id,
        "owner_username": owner_username,
        "description": description or "",
        "address": address or "",
        "phone": phone or "",
        "image_url": image_url,
        "created_at": "",
    }

    try:
        result = await db.restaurants.insert_one(rest_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create restaurant: {e}")

    # Update user's restaurant_id if owner exists
    try:
        await db.users.update_one(
            {"_id": ObjectId(owner_id)},
            {"$set": {"restaurant_id": str(result.inserted_id)}},
            upsert=False,
        )
    except Exception as user_error:
        print(f"Warning: Could not update user {owner_id}: {user_error}")

    response_payload = {"success": True, "restaurant": {"id": str(result.inserted_id), **rest_doc}}
    return JSONResponse(
        content=jsonable_encoder(response_payload, custom_encoder={ObjectId: str})
    )


@router.get("/admin/restaurants")
async def get_all_restaurants():
    """Get all restaurants"""
    try:
        from app.infrastructure.persistence.database import get_db
        db = get_db()
        restaurants = await db.restaurants.find().to_list(None)
        return [
            {
                "id": str(r["_id"]),
                "name": r.get("name", ""),
                "owner_id": r.get("owner_id", ""),
                "description": r.get("description", ""),
                "address": r.get("address", ""),
                "phone": r.get("phone", ""),
                "image_url": r.get("image_url", ""),
                "created_at": r.get("created_at", "")
            }
            for r in restaurants
        ]
    except Exception as e:
        print(f"Error fetching restaurants: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching restaurants: {str(e)}")
