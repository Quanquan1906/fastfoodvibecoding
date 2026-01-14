"""Menu item router - menu management endpoints"""
from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from bson.errors import InvalidId
from typing import Optional
from app.domain.entities.menu_item import MenuItem
from app.infrastructure.external.cloudinary_client import CloudinaryNotConfiguredError, upload_menu_item_image

router = APIRouter(tags=["menu"])


def _parse_object_id(value: str, *, field_name: str) -> ObjectId:
    """Parse a MongoDB ObjectId from a string"""
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")


@router.post("/restaurant/menu")
async def create_menu_item(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    image: Optional[UploadFile] = File(None),
    restaurant_id: Optional[str] = Form(None),
):
    """Create menu item with image upload"""
    from app.infrastructure.persistence.database import get_db
    
    db = get_db()

    if image is None or not image.filename:
        raise HTTPException(status_code=400, detail="image file is required")

    if not restaurant_id:
        raise HTTPException(status_code=422, detail="restaurant_id is required")

    if image.content_type and not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="image must be an image/* content type")

    rid = _parse_object_id(restaurant_id, field_name="restaurant_id")

    restaurant = await db.restaurants.find_one({"_id": rid})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    try:
        try:
            image.file.seek(0)
        except:
            pass

        image_url = await upload_menu_item_image(image.file, filename=image.filename)
    except CloudinaryNotConfiguredError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Image upload failed: {e}")

    menu_item = {
        "restaurant_id": rid,
        "name": name,
        "description": description,
        "price": price,
        "image_url": image_url,
        "available": True,
        "created_at": None,
    }

    result = await db.menu_items.insert_one(menu_item)
    menu_item["_id"] = result.inserted_id

    def _serialize(doc):
        return {
            "id": str(doc["_id"]),
            "restaurant_id": str(doc.get("restaurant_id")),
            "name": doc.get("name"),
            "description": doc.get("description"),
            "price": doc.get("price"),
            "image_url": doc.get("image_url"),
            "available": doc.get("available"),
            "created_at": doc.get("created_at")
        }

    return {"success": True, "item": _serialize(menu_item)}


@router.put("/restaurant/menu/{item_id}")
async def update_menu_item(item_id: str, item: MenuItem):
    """Update menu item"""
    from app.infrastructure.persistence.database import get_db
    
    db = get_db()
    oid = _parse_object_id(item_id, field_name="item_id")

    update_doc = item.dict(exclude={"id"})
    if "restaurant_id" in update_doc and update_doc["restaurant_id"]:
        update_doc["restaurant_id"] = _parse_object_id(update_doc["restaurant_id"], field_name="restaurant_id")

    await db.menu_items.update_one({"_id": oid}, {"$set": update_doc})
    updated = await db.menu_items.find_one({"_id": oid})
    
    if not updated:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    def _serialize(doc):
        return {
            "id": str(doc["_id"]),
            "restaurant_id": str(doc.get("restaurant_id")),
            "name": doc.get("name"),
            "description": doc.get("description"),
            "price": doc.get("price"),
            "image_url": doc.get("image_url"),
            "available": doc.get("available"),
            "created_at": doc.get("created_at")
        }
    
    return _serialize(updated)


@router.delete("/restaurant/menu/{item_id}")
async def delete_menu_item(item_id: str):
    """Delete menu item"""
    from app.infrastructure.persistence.database import get_db
    
    db = get_db()
    oid = _parse_object_id(item_id, field_name="item_id")
    result = await db.menu_items.delete_one({"_id": oid})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    return {"success": True, "message": "Menu item deleted"}
