"""All API routes for FastFood delivery system"""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.models.user import User, LoginRequest
from app.models.restaurant import Restaurant
from app.models.menu_item import MenuItem
from app.models.order import Order, OrderItem
from app.models.drone import Drone
from app.services.auth_service import AuthService
from app.services.payment_service import PaymentService
from app.services.order_service import OrderService
from app.services.drone_service import DroneService
from app.core.database import get_db
from app.websocket.manager import manager
from bson import ObjectId
from bson.errors import InvalidId
from typing import Any, Dict, List
import asyncio

router = APIRouter()


def _parse_object_id(value: str, *, field_name: str) -> ObjectId:
    """Parse a MongoDB ObjectId from a string.

    Raises:
        HTTPException(400): if the value is not a valid ObjectId.
    """
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")


def _serialize_mongo_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB document to JSON-serializable dict.

    - Moves `_id` -> `id` (string)
    - Stringifies any nested ObjectIds we commonly store (e.g., restaurant_id)
    """
    out: Dict[str, Any] = dict(doc)

    if "_id" in out:
        out["id"] = str(out.pop("_id"))

    if isinstance(out.get("restaurant_id"), ObjectId):
        out["restaurant_id"] = str(out["restaurant_id"])

    return out

# Service instances
auth_service = AuthService()
payment_service = PaymentService()
order_service = OrderService()
drone_service = DroneService()


# ============= AUTH ROUTES =============
@router.post("/login")
async def login(request: LoginRequest):
    """Simple login - create or get user"""
    try:
        user = await auth_service.login(request)
        return JSONResponse({
            "success": True,
            "user": user
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============= CUSTOMER ROUTES =============
@router.get("/restaurants")
async def get_restaurants():
    """Get all restaurants"""
    db = get_db()
    restaurants = await db.restaurants.find().to_list(None)
    return [_serialize_mongo_doc(r) for r in restaurants]


@router.get("/restaurants/{restaurant_id}")
async def get_restaurant(restaurant_id: str):
    """Get restaurant details"""
    db = get_db()

    rid = _parse_object_id(restaurant_id, field_name="restaurant_id")
    restaurant = await db.restaurants.find_one({"_id": rid})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return _serialize_mongo_doc(restaurant)


@router.get("/restaurants/{restaurant_id}/menu")
async def get_restaurant_menu(restaurant_id: str):
    """Get menu items for restaurant"""
    db = get_db()

    rid = _parse_object_id(restaurant_id, field_name="restaurant_id")

    # Restaurant must exist
    restaurant = await db.restaurants.find_one({"_id": rid})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Support both legacy string storage and newer ObjectId storage for restaurant_id
    cursor = db.menu_items.find({"restaurant_id": {"$in": [rid, str(rid)]}})
    items = await cursor.to_list(None)
    return [_serialize_mongo_doc(item) for item in items]


@router.post("/orders")
async def create_order(customer_id: str, restaurant_id: str, items: List[OrderItem], total: float):
    """Create new order"""
    try:
        order = await order_service.create_order(customer_id, restaurant_id, items, total)
        return JSONResponse({
            "success": True,
            "order": order
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Get order details"""
    try:
        order = await order_service.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/customer/{customer_id}/orders")
async def get_customer_orders(customer_id: str):
    """Get all orders for customer"""
    try:
        orders = await order_service.get_customer_orders(customer_id)
        return orders
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/payments/mock/{order_id}")
async def mock_payment(order_id: str, background_tasks: BackgroundTasks):
    """Mock payment - always succeeds"""
    try:
        result = await payment_service.mock_pay(order_id)
        
        # Start drone simulation in background
        order = await order_service.get_order(order_id)
        if order and order.get("drone_id"):
            background_tasks.add_task(
                drone_service.simulate_drone_movement,
                order_id,
                order["drone_id"]
            )
        
        return JSONResponse({
            "success": True,
            "payment": result
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.websocket("/ws/orders/{order_id}")
async def websocket_order_tracking(order_id: str, websocket: WebSocket):
    """WebSocket for order tracking"""
    await manager.connect(order_id, websocket)
    
    try:
        while True:
            # Get latest order info
            order = await order_service.get_order(order_id)
            
            if order:
                # Send order update
                await manager.broadcast_order_update(order_id, order)
            
            # Send update every 2 seconds
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        manager.disconnect(order_id, websocket)
    except Exception as e:
        manager.disconnect(order_id, websocket)
        print(f"WebSocket error: {e}")


# ============= RESTAURANT ROUTES =============
@router.post("/restaurant/menu")
async def create_menu_item(item: MenuItem, restaurant_id: str | None = None):
    """Create menu item"""
    db = get_db()

    effective_restaurant_id = restaurant_id or item.restaurant_id
    if not effective_restaurant_id:
        raise HTTPException(status_code=422, detail="restaurant_id is required")

    rid = _parse_object_id(effective_restaurant_id, field_name="restaurant_id")

    restaurant = await db.restaurants.find_one({"_id": rid})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    menu_item = {
        "restaurant_id": rid,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "image_url": item.image_url,
        "available": item.available,
        "created_at": item.created_at,
    }

    result = await db.menu_items.insert_one(menu_item)
    menu_item["_id"] = result.inserted_id

    return {"success": True, "item": _serialize_mongo_doc(menu_item)}


@router.put("/restaurant/menu/{item_id}")
async def update_menu_item(item_id: str, item: MenuItem):
    """Update menu item"""
    db = get_db()
    oid = _parse_object_id(item_id, field_name="item_id")

    update_doc = item.dict(exclude={"id"})
    # Keep restaurant_id type consistent if client sends it
    if "restaurant_id" in update_doc and update_doc["restaurant_id"]:
        update_doc["restaurant_id"] = _parse_object_id(update_doc["restaurant_id"], field_name="restaurant_id")

    await db.menu_items.update_one({"_id": oid}, {"$set": update_doc})
    updated = await db.menu_items.find_one({"_id": oid})
    if not updated:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return _serialize_mongo_doc(updated)


@router.delete("/restaurant/menu/{item_id}")
async def delete_menu_item(item_id: str):
    """Delete menu item"""
    db = get_db()
    oid = _parse_object_id(item_id, field_name="item_id")
    result = await db.menu_items.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"success": True, "message": "Menu item deleted"}


@router.get("/restaurant/{restaurant_id}/orders")
async def get_restaurant_orders(restaurant_id: str):
    """Get all orders for restaurant"""
    try:
        orders = await order_service.get_restaurant_orders(restaurant_id)
        return orders
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/restaurant/orders/{order_id}/accept")
async def accept_order(order_id: str):
    """Accept order (PENDING -> PREPARING)"""
    try:
        order = await order_service.update_order_status(order_id, "PREPARING")
        return JSONResponse({
            "success": True,
            "order": order
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/restaurant/orders/{order_id}/status")
async def update_order_status_route(order_id: str, status: str):
    """Update order status"""
    try:
        order = await order_service.update_order_status(order_id, status)
        return JSONResponse({
            "success": True,
            "order": order
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/restaurant/orders/{order_id}/assign-drone")
async def assign_drone_to_order(order_id: str, drone_id: str):
    """Assign drone to order and start delivery"""
    try:
        # Assign drone
        order = await order_service.assign_drone(order_id, drone_id)
        
        # Update drone status
        await drone_service.update_drone_status(drone_id, "BUSY")
        
        # Update order to DELIVERING
        order = await order_service.update_order_status(order_id, "DELIVERING")
        
        return JSONResponse({
            "success": True,
            "order": order,
            "message": "🚁 Drone assigned - Delivery started"
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============= ADMIN ROUTES =============
@router.post("/admin/restaurants")
async def create_restaurant(restaurant: Restaurant):
    """Create restaurant"""
    try:
        db = get_db()
        rest_doc = {
            "name": restaurant.name,
            "owner_id": restaurant.owner_id,
            "description": restaurant.description if restaurant.description else "",
            "address": restaurant.address if restaurant.address else "",
            "phone": restaurant.phone if restaurant.phone else "",
            "created_at": restaurant.created_at if restaurant.created_at else ""
        }
        result = await db.restaurants.insert_one(rest_doc)
        
        # Update user's restaurant_id if owner exists
        try:
            await db.users.update_one(
                {"_id": ObjectId(restaurant.owner_id)},
                {"$set": {"restaurant_id": str(result.inserted_id)}},
                upsert=False
            )
        except Exception as user_error:
            # Owner might not exist yet, continue anyway
            print(f"Warning: Could not update user {restaurant.owner_id}: {user_error}")
        
        return JSONResponse({
            "success": True,
            "restaurant": {"id": str(result.inserted_id), **rest_doc}
        })
    except Exception as e:
        print(f"Error creating restaurant: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to create restaurant: {str(e)}")


@router.get("/admin/restaurants")
async def get_all_restaurants():
    """Get all restaurants"""
    try:
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
                "created_at": r.get("created_at", "")
            }
            for r in restaurants
        ]
    except Exception as e:
        print(f"❌ Error fetching restaurants: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching restaurants: {str(e)}")



@router.post("/admin/drones")
async def create_drone(drone: Drone):
    """Create drone"""
    try:
        new_drone = await drone_service.create_drone(drone.name, drone.restaurant_id)
        return JSONResponse({
            "success": True,
            "drone": new_drone
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/admin/drones")
async def get_all_drones():
    """Get all drones"""
    try:
        drones = await drone_service.get_all_drones()
        return drones
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/admin/drones/restaurant/{restaurant_id}")
async def get_restaurant_drones(restaurant_id: str):
    """Get drones for restaurant"""
    try:
        drones = await drone_service.get_restaurant_drones(restaurant_id)
        return drones
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/admin/users")
async def get_all_users():
    """Get all users"""
    try:
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


@router.get("/admin/orders")
async def get_all_orders():
    """Get all orders (system overview)"""
    try:
        orders = await order_service.get_all_orders()
        return orders
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Health check
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "✅ FastFood API is running"}
