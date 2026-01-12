"""Drone management and fake movement service"""
from app.core.database import get_db
from bson import ObjectId
from datetime import datetime
from typing import Optional, List
import asyncio


class DroneService:
    """Service for drone operations and fake movement"""

    def _serialize_drone(self, drone: dict) -> dict:
        if not drone:
            return drone

        drone_id = drone.get("_id")
        serialized = {k: v for k, v in drone.items() if k != "_id"}
        if drone_id is not None:
            serialized["id"] = str(drone_id)

        # Ensure MongoDB ObjectId fields are JSON-serializable
        restaurant_id = serialized.get("restaurant_id")
        if isinstance(restaurant_id, ObjectId):
            serialized["restaurant_id"] = str(restaurant_id)

        # Backward-compat: older records may have status=IDLE
        if serialized.get("status") == "IDLE":
            serialized["status"] = "AVAILABLE"
        return serialized

    async def create_drone(self, name: str, restaurant_id: str | None = None) -> dict:
        """Create a new drone"""
        db = get_db()
        
        drone_doc = {
            "name": name,
            "restaurant_id": restaurant_id,
            "status": "AVAILABLE",
            "latitude": 10.762622,
            "longitude": 106.660172,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = await db.drones.insert_one(drone_doc)
        return {
            "id": str(result.inserted_id),
            **drone_doc
        }

    async def get_drone(self, drone_id: str) -> Optional[dict]:
        """Get drone by ID"""
        db = get_db()
        drone = await db.drones.find_one({"_id": ObjectId(drone_id)})
        
        if not drone:
            return None
        
        return self._serialize_drone(drone)

    async def get_restaurant_drones(self, restaurant_id: str) -> List[dict]:
        """Get all drones for a restaurant"""
        db = get_db()
        drones = await db.drones.find({"restaurant_id": restaurant_id}).to_list(None)
        
        return [self._serialize_drone(drone) for drone in drones]

    async def get_all_drones(self) -> List[dict]:
        """Get all drones (ADMIN)"""
        db = get_db()
        drones = await db.drones.find().to_list(None)
        
        return [self._serialize_drone(drone) for drone in drones]

    async def update_drone_status(self, drone_id: str, status: str) -> dict:
        """Update drone status"""
        db = get_db()
        
        await db.drones.update_one(
            {"_id": ObjectId(drone_id)},
            {"$set": {"status": status}}
        )
        
        return await self.get_drone(drone_id)

    async def simulate_drone_movement(self, order_id: str, drone_id: str):
        """Simulate fake drone movement for delivery"""
        db = get_db()
        
        # Simulate 20 steps of movement
        for step in range(20):
            # Get current order
            order = await db.orders.find_one({"_id": ObjectId(order_id)})
            if not order or order.get("status") != "DELIVERING":
                break
            
            # Update drone position
            new_lat = order["drone_lat"] + 0.0005
            new_lon = order["drone_lon"] + 0.0005
            
            await db.orders.update_one(
                {"_id": ObjectId(order_id)},
                {
                    "$set": {
                        "drone_lat": new_lat,
                        "drone_lon": new_lon,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            )
            
            await asyncio.sleep(2)  # Move every 2 seconds
        
        # Mark order as completed
        await db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {
                "$set": {
                    "status": "COMPLETED",
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        # Mark drone as idle
        await db.drones.update_one(
            {"_id": ObjectId(drone_id)},
            {"$set": {"status": "AVAILABLE"}}
        )
