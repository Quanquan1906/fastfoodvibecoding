"""Order management service"""
from app.core.database import get_db
from app.models.order import Order, OrderItem
from bson import ObjectId
from datetime import datetime
from typing import List, Optional


class OrderService:
    """Service for order operations"""

    async def create_order(self, customer_id: str, restaurant_id: str, items: List[OrderItem], total: float) -> dict:
        """Create a new order"""
        db = get_db()
        
        order_doc = {
            "customer_id": customer_id,
            "restaurant_id": restaurant_id,
            "items": [item.dict() for item in items],
            "total": total,
            "status": "PENDING",
            "delivery_lat": 10.762622,
            "delivery_lon": 106.660172,
            "drone_lat": 10.762622,
            "drone_lon": 106.660172,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = await db.orders.insert_one(order_doc)
        return {
            "id": str(result.inserted_id),
            **order_doc
        }

    async def get_order(self, order_id: str) -> Optional[dict]:
        """Get order by ID"""
        db = get_db()
        order = await db.orders.find_one({"_id": ObjectId(order_id)})
        
        if not order:
            return None
        
        return {
            "id": str(order["_id"]),
            **order
        }

    async def get_customer_orders(self, customer_id: str) -> List[dict]:
        """Get all orders for a customer"""
        db = get_db()
        orders = await db.orders.find({"customer_id": customer_id}).to_list(None)
        
        return [
            {"id": str(order["_id"]), **order}
            for order in orders
        ]

    async def get_restaurant_orders(self, restaurant_id: str) -> List[dict]:
        """Get all orders for a restaurant"""
        db = get_db()
        orders = await db.orders.find({"restaurant_id": restaurant_id}).to_list(None)
        
        return [
            {"id": str(order["_id"]), **order}
            for order in orders
        ]

    async def update_order_status(self, order_id: str, status: str) -> dict:
        """Update order status"""
        db = get_db()
        
        await db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        return await self.get_order(order_id)

    async def assign_drone(self, order_id: str, drone_id: str) -> dict:
        """Assign drone to order"""
        db = get_db()
        
        await db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {
                "$set": {
                    "drone_id": drone_id,
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        return await self.get_order(order_id)

    async def get_all_orders(self) -> List[dict]:
        """Get all orders (ADMIN)"""
        db = get_db()
        orders = await db.orders.find().to_list(None)
        
        return [
            {"id": str(order["_id"]), **order}
            for order in orders
        ]
