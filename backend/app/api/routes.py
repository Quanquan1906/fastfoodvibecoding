"""All API routes for FastFood delivery system"""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
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
from typing import List
import asyncio

router = APIRouter()

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
    try:
        db = get_db()
        restaurants = await db.restaurants.find().to_list(None)
        return [
            {"id": str(r["_id"]), **r}
            for r in restaurants
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/restaurants/{restaurant_id}")
async def get_restaurant(restaurant_id: str):
    """Get restaurant details"""
    try:
        db = get_db()
        restaurant = await db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return {"id": str(restaurant["_id"]), **restaurant}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/restaurants/{restaurant_id}/menu")
async def get_restaurant_menu(restaurant_id: str):
    """Get menu items for restaurant"""
    try:
        db = get_db()
        items = await db.menu_items.find({"restaurant_id": restaurant_id}).to_list(None)
        return [
            {"id": str(item["_id"]), **item}
            for item in items
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
async def create_menu_item(restaurant_id: str, item: MenuItem):
    """Create menu item"""
    try:
        db = get_db()
        menu_item = {
            "restaurant_id": restaurant_id,
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "image_url": item.image_url,
            "available": item.available,
            "created_at": item.created_at
        }
        result = await db.menu_items.insert_one(menu_item)
        return JSONResponse({
            "success": True,
            "item": {"id": str(result.inserted_id), **menu_item}
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/restaurant/menu/{item_id}")
async def update_menu_item(item_id: str, item: MenuItem):
    """Update menu item"""
    try:
        db = get_db()
        await db.menu_items.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": item.dict(exclude={"id"})}
        )
        updated = await db.menu_items.find_one({"_id": ObjectId(item_id)})
        return {"id": str(updated["_id"]), **updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/restaurant/menu/{item_id}")
async def delete_menu_item(item_id: str):
    """Delete menu item"""
    try:
        db = get_db()
        await db.menu_items.delete_one({"_id": ObjectId(item_id)})
        return JSONResponse({"success": True, "message": "Menu item deleted"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
            "description": restaurant.description,
            "address": restaurant.address,
            "phone": restaurant.phone,
            "created_at": restaurant.created_at
        }
        result = await db.restaurants.insert_one(rest_doc)
        
        # Create restaurant owner user if not exists
        await db.users.update_one(
            {"_id": ObjectId(restaurant.owner_id)},
            {"$set": {"restaurant_id": str(result.inserted_id)}},
            upsert=False
        )
        
        return JSONResponse({
            "success": True,
            "restaurant": {"id": str(result.inserted_id), **rest_doc}
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/admin/restaurants")
async def get_all_restaurants():
    """Get all restaurants"""
    try:
        db = get_db()
        restaurants = await db.restaurants.find().to_list(None)
        return [
            {"id": str(r["_id"]), **r}
            for r in restaurants
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
