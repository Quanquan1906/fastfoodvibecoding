"""Drone router - drone management endpoints"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel
from typing import Optional
from app.application.services.drone_service import DroneService

router = APIRouter(tags=["drones"])


class AdminCreateDroneRequest(BaseModel):
    name: Optional[str] = None
    restaurant_id: Optional[str] = None


class AdminAssignDroneRequest(BaseModel):
    drone_id: str
    restaurant_id: str


def _parse_object_id(value: str, *, field_name: str) -> ObjectId:
    """Parse a MongoDB ObjectId from a string"""
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")


@router.post("/admin/drones")
async def create_drone(payload: AdminCreateDroneRequest):
    """Create drone (ADMIN)"""
    try:
        from app.infrastructure.persistence.database import get_db
        from app.infrastructure.persistence.repositories.mongo_repository import MongoDroneRepository
        
        print("CREATE DRONE REQUEST:", payload.model_dump())

        db = get_db()
        name = (payload.name or "").strip()
        restaurant_id = (payload.restaurant_id or "").strip()

        if not name:
            raise HTTPException(status_code=400, detail="Missing drone name")
        if not restaurant_id:
            raise HTTPException(status_code=400, detail="Missing restaurant_id")

        rid = _parse_object_id(restaurant_id, field_name="restaurant_id")
        restaurant = await db.restaurants.find_one({"_id": rid})
        if not restaurant:
            raise HTTPException(status_code=400, detail="Invalid restaurant_id (restaurant not found)")

        drone_repo = MongoDroneRepository()
        service = DroneService(drone_repo)
        new_drone = await service.create_drone(name, str(rid))

        print("DRONE SAVED:", new_drone.get("id"))
        payload_out = {"message": "Drone created successfully", "drone": new_drone}
        return JSONResponse(
            status_code=201,
            content=jsonable_encoder(payload_out, custom_encoder={ObjectId: str}),
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print("CREATE DRONE ERROR:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/admin/assign-drone")
async def admin_assign_drone(payload: AdminAssignDroneRequest):
    """Admin assigns drone to restaurant"""
    from app.infrastructure.persistence.database import get_db
    
    db = get_db()
    did = _parse_object_id(payload.drone_id, field_name="drone_id")
    rid = _parse_object_id(payload.restaurant_id, field_name="restaurant_id")

    restaurant = await db.restaurants.find_one({"_id": rid})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    drone = await db.drones.find_one({"_id": did})
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")

    await db.drones.update_one(
        {"_id": did},
        {"$set": {"restaurant_id": str(rid), "status": "AVAILABLE"}},
    )
    updated_drone = await db.drones.find_one({"_id": did})
    
    def _serialize(doc):
        result = dict(doc)
        if "_id" in result:
            result["id"] = str(result.pop("_id"))
        if isinstance(result.get("restaurant_id"), ObjectId):
            result["restaurant_id"] = str(result["restaurant_id"])
        return result
    
    return {"success": True, "drone": _serialize(updated_drone)}


@router.get("/restaurant/{restaurant_id}/drones")
async def get_available_drones_for_restaurant(restaurant_id: str):
    """Get available drones for restaurant"""
    from app.infrastructure.persistence.database import get_db
    
    db = get_db()
    rid = _parse_object_id(restaurant_id, field_name="restaurant_id")

    drones = await db.drones.find(
        {
            "restaurant_id": str(rid),
            "status": {"$in": ["AVAILABLE", "IDLE"]},
        }
    ).to_list(None)

    def _serialize(doc):
        result = dict(doc)
        if "_id" in result:
            result["id"] = str(result.pop("_id"))
        if isinstance(result.get("restaurant_id"), ObjectId):
            result["restaurant_id"] = str(result["restaurant_id"])
        return result

    return [_serialize(d) for d in drones]


@router.get("/admin/drones")
async def get_all_drones():
    """Get all drones"""
    try:
        from app.infrastructure.persistence.repositories.mongo_repository import MongoDroneRepository
        
        drone_repo = MongoDroneRepository()
        service = DroneService(drone_repo)
        drones = await service.get_all_drones()
        return JSONResponse(
            content=jsonable_encoder(drones, custom_encoder={ObjectId: str})
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/admin/drones/restaurant/{restaurant_id}")
async def get_restaurant_drones(restaurant_id: str):
    """Get drones for restaurant"""
    try:
        from app.infrastructure.persistence.repositories.mongo_repository import MongoDroneRepository
        
        drone_repo = MongoDroneRepository()
        service = DroneService(drone_repo)
        drones = await service.get_restaurant_drones(restaurant_id)
        return JSONResponse(
            content=jsonable_encoder(drones, custom_encoder={ObjectId: str})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
