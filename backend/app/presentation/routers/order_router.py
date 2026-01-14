"""Order router - order management endpoints"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel, Field
from typing import List, Optional
from app.domain.entities.order import OrderCreate, OrderItem
from app.application.services.order_service import OrderService
from app.application.services.drone_service import DroneService

router = APIRouter(tags=["orders"])


class AssignDroneToOrderRequest(BaseModel):
    drone_id: str = Field(..., min_length=1)


def _parse_object_id(value: str, *, field_name: str) -> ObjectId:
    """Parse a MongoDB ObjectId from a string"""
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")


@router.post("/orders", response_model=None)
async def create_order(payload: OrderCreate):
    """Create new order"""
    try:
        from app.infrastructure.persistence.database import get_db
        from app.infrastructure.persistence.repositories.mongo_repository import MongoOrderRepository, MongoDroneRepository
        from bson import ObjectId
        
        db = get_db()
        rid = _parse_object_id(payload.restaurant_id, field_name="restaurant_id")

        restaurant = await db.restaurants.find_one({"_id": rid})
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        order_repo = MongoOrderRepository()
        drone_repo = MongoDroneRepository()
        service = OrderService(order_repo, drone_repo)
        
        order = await service.create_order(
            payload.customer_id,
            payload.restaurant_id,
            payload.items,
            payload.total_price,
            payload.delivery_address,
        )
        response_payload = {"success": True, "order": order}
        return JSONResponse(
            content=jsonable_encoder(response_payload, custom_encoder={ObjectId: str})
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")


@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Get order details"""
    try:
        from app.infrastructure.persistence.repositories.mongo_repository import MongoOrderRepository, MongoDroneRepository
        from app.application.services.order_service import OrderService
        
        order_repo = MongoOrderRepository()
        drone_repo = MongoDroneRepository()
        service = OrderService(order_repo, drone_repo)
        
        order = await service.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/customer/{customer_id}/orders")
async def get_customer_orders(customer_id: str):
    """Get all orders for customer"""
    try:
        from app.infrastructure.persistence.repositories.mongo_repository import MongoOrderRepository, MongoDroneRepository
        from app.application.services.order_service import OrderService
        
        order_repo = MongoOrderRepository()
        drone_repo = MongoDroneRepository()
        service = OrderService(order_repo, drone_repo)
        
        orders = await service.get_customer_orders(customer_id)
        return orders
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/{order_id}/complete")
async def complete_order(order_id: str):
    """Mark an order as COMPLETED"""
    from app.infrastructure.persistence.database import get_db
    
    db = get_db()
    oid = _parse_object_id(order_id, field_name="order_id")

    order = await db.orders.find_one({"_id": oid})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.get("status") == "COMPLETED":
        return {"success": True, "message": "Order already completed"}

    from datetime import datetime
    await db.orders.update_one(
        {"_id": oid},
        {"$set": {"status": "COMPLETED", "updated_at": datetime.utcnow().isoformat()}},
    )

    # Free up drone if attached
    drone_id = order.get("drone_id")
    if isinstance(drone_id, str):
        try:
            did = _parse_object_id(drone_id, field_name="drone_id")
            await db.drones.update_one({"_id": did}, {"$set": {"status": "AVAILABLE"}})
        except HTTPException:
            pass

    updated = await db.orders.find_one({"_id": oid})
    
    def _serialize(doc):
        result = dict(doc)
        if "_id" in result:
            result["id"] = str(result.pop("_id"))
        return result
    
    return {"success": True, "message": "Order delivered successfully", "order": _serialize(updated)}


@router.get("/restaurant/{restaurant_id}/orders")
async def get_restaurant_orders(restaurant_id: str):
    """Get all orders for restaurant"""
    try:
        from app.infrastructure.persistence.repositories.mongo_repository import MongoOrderRepository, MongoDroneRepository
        from app.application.services.order_service import OrderService
        
        order_repo = MongoOrderRepository()
        drone_repo = MongoDroneRepository()
        service = OrderService(order_repo, drone_repo)
        
        orders = await service.get_restaurant_orders(restaurant_id)
        return orders
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/restaurant/orders/{order_id}/accept")
async def accept_order(order_id: str):
    """Accept order (PENDING -> PREPARING)"""
    try:
        from app.infrastructure.persistence.repositories.mongo_repository import MongoOrderRepository, MongoDroneRepository
        from app.application.services.order_service import OrderService
        
        order_repo = MongoOrderRepository()
        drone_repo = MongoDroneRepository()
        service = OrderService(order_repo, drone_repo)
        
        order = await service.update_order_status(order_id, "PREPARING")
        return JSONResponse({
            "success": True,
            "order": order
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
class UpdateOrderStatusRequest(BaseModel):
    status: str = Field(..., min_length=1)


@router.post("/restaurant/orders/{order_id}/status")
async def update_order_status_route(order_id: str, payload: UpdateOrderStatusRequest):
    """Update order status"""
    try:
        from app.infrastructure.persistence.repositories.mongo_repository import MongoOrderRepository, MongoDroneRepository
        from app.application.services.order_service import OrderService
        
        order_repo = MongoOrderRepository()
        drone_repo = MongoDroneRepository()
        service = OrderService(order_repo, drone_repo)
        
        order = await service.update_order_status(order_id, payload.status)
        return JSONResponse({
            "success": True,
            "order": order
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/restaurant/orders/{order_id}/assign-drone")
async def assign_drone_to_order_legacy(order_id: str, drone_id: str):
    """Legacy endpoint (backward compatibility)"""
    return await assign_drone_to_order(order_id, AssignDroneToOrderRequest(drone_id=drone_id))


@router.post("/orders/{order_id}/assign-drone")
async def assign_drone_to_order(order_id: str, payload: AssignDroneToOrderRequest):
    """Assign drone to order (READY_FOR_PICKUP -> DELIVERING)"""
    from app.infrastructure.persistence.database import get_db
    
    db = get_db()

    oid = _parse_object_id(order_id, field_name="order_id")
    did = _parse_object_id(payload.drone_id, field_name="drone_id")

    order = await db.orders.find_one({"_id": oid})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.get("status") != "READY_FOR_PICKUP":
        raise HTTPException(
            status_code=409,
            detail=f"Order must be READY_FOR_PICKUP to assign a drone (current: {order.get('status')})",
        )

    drone = await db.drones.find_one({"_id": did})
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")

    drone_status = drone.get("status")
    if drone_status == "IDLE":
        drone_status = "AVAILABLE"
    if drone_status != "AVAILABLE":
        raise HTTPException(status_code=409, detail=f"Drone is not available (current: {drone.get('status')})")

    if str(drone.get("restaurant_id") or "") != str(order.get("restaurant_id") or ""):
        raise HTTPException(status_code=409, detail="Drone does not belong to this restaurant")

    # Update order and drone
    await db.orders.update_one(
        {"_id": oid},
        {
            "$set": {
                "drone_id": str(did),
                "drone_name": drone.get("name", ""),
                "status": "DELIVERING",
            }
        },
    )
    await db.drones.update_one({"_id": did}, {"$set": {"status": "BUSY"}})

    updated_order = await db.orders.find_one({"_id": oid})
    updated_drone = await db.drones.find_one({"_id": did})

    def _serialize_order(doc):
        result = dict(doc)
        if "_id" in result:
            result["id"] = str(result.pop("_id"))
        return result
    
    def _serialize_drone(doc):
        result = dict(doc)
        if "_id" in result:
            result["id"] = str(result.pop("_id"))
        if isinstance(result.get("restaurant_id"), ObjectId):
            result["restaurant_id"] = str(result["restaurant_id"])
        return result

    return {
        "success": True,
        "order": _serialize_order(updated_order),
        "drone": _serialize_drone(updated_drone),
        "message": "🚁 Drone assigned - Delivery started",
    }


@router.get("/admin/orders")
async def get_all_orders():
    """Get all orders (admin)"""
    try:
        from app.infrastructure.persistence.repositories.mongo_repository import MongoOrderRepository, MongoDroneRepository
        from app.application.services.order_service import OrderService
        
        order_repo = MongoOrderRepository()
        drone_repo = MongoDroneRepository()
        service = OrderService(order_repo, drone_repo)
        
        orders = await service.get_all_orders()
        return orders
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/payments/mock/{order_id}")
async def mock_payment(order_id: str, background_tasks: BackgroundTasks):
    """Mock payment - always succeeds"""
    try:
        from app.infrastructure.persistence.repositories.mongo_repository import MongoOrderRepository, MongoDroneRepository
        from app.application.services.order_service import OrderService
        from app.application.services.payment_service import PaymentService
        
        order_repo = MongoOrderRepository()
        drone_repo = MongoDroneRepository()
        payment_service = PaymentService(order_repo)
        order_service = OrderService(order_repo, drone_repo)
        
        result = await payment_service.mock_pay(order_id)
        
        # Start drone simulation
        order = await order_service.get_order(order_id)
        if order and order.get("drone_id"):
            background_tasks.add_task(
                order_service.simulate_drone_movement,
                order_id,
                order["drone_id"]
            )
        
        return JSONResponse({
            "success": True,
            "payment": result
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
