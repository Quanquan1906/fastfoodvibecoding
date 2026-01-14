"""Order service - business logic for orders"""
from app.application.ports.repository_port import OrderRepository, DroneRepository
from app.domain.entities.order import OrderItem
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio


class OrderService:
    """Order service - NO direct database access"""
    
    def __init__(self, order_repo: OrderRepository, drone_repo: DroneRepository):
        self.order_repo = order_repo
        self.drone_repo = drone_repo
    
    async def create_order(
        self, 
        customer_id: str, 
        restaurant_id: str, 
        items: List[OrderItem], 
        total: float, 
        delivery_address: str
    ) -> Dict[str, Any]:
        """Create a new order"""
        serialized_items = []
        for item in items:
            if isinstance(item, dict):
                serialized_items.append(item)
            elif hasattr(item, "model_dump"):
                serialized_items.append(item.model_dump())
            else:
                serialized_items.append(item.dict())
        
        order_doc = {
            "customer_id": customer_id,
            "restaurant_id": restaurant_id,
            "items": serialized_items,
            "total": total,
            "delivery_address": delivery_address,
            "status": "PENDING",
            "delivery_lat": 10.762622,
            "delivery_lon": 106.660172,
            "drone_lat": 10.762622,
            "drone_lon": 106.660172,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return await self.order_repo.save(order_doc)
    
    async def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order by ID"""
        return await self.order_repo.find_by_id(order_id)
    
    async def get_customer_orders(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get all orders for a customer"""
        return await self.order_repo.find_by_customer(customer_id)
    
    async def get_restaurant_orders(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Get all orders for a restaurant"""
        return await self.order_repo.find_by_restaurant(restaurant_id)
    
    async def update_order_status(self, order_id: str, status: str) -> Dict[str, Any]:
        """Update order status"""
        return await self.order_repo.update_status(order_id, status)
    
    async def assign_drone(self, order_id: str, drone_id: str) -> Dict[str, Any]:
        """Assign drone to order"""
        return await self.order_repo.assign_drone(order_id, drone_id)
    
    async def get_all_orders(self) -> List[Dict[str, Any]]:
        """Get all orders (for admin)"""
        # This would need a find_all method in the repository
        # For now, return empty list (can be extended)
        return []
    
    async def simulate_drone_movement(self, order_id: str, drone_id: str):
        """Simulate fake drone movement for delivery"""
        # Get current order
        order = await self.order_repo.find_by_id(order_id)
        if not order or order.get("status") != "DELIVERING":
            return
        
        # Simulate 20 steps of movement (simplified)
        for step in range(20):
            # Would need additional repository methods for full implementation
            await asyncio.sleep(0.5)  # Simulate delay
