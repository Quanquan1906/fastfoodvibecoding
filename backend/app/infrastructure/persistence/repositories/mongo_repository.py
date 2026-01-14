"""MongoDB repository implementations"""
from typing import List, Optional, Dict, Any
from bson import ObjectId
from bson.errors import InvalidId
from app.infrastructure.persistence.database import get_db
from app.application.ports.repository_port import (
    UserRepository, OrderRepository, RestaurantRepository,
    MenuItemRepository, DroneRepository
)
from datetime import datetime


class MongoUserRepository(UserRepository):
    """MongoDB implementation of UserRepository"""
    
    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Find user by ID"""
        try:
            db = get_db()
            user = await db.users.find_one({"_id": ObjectId(id)})
            return self._serialize(user) if user else None
        except InvalidId:
            return None
    
    async def find_by_username(self, username: str, role: str) -> Optional[Dict[str, Any]]:
        """Find user by username and role"""
        import re
        db = get_db()
        user = await db.users.find_one({
            "username": {"$regex": f"^{re.escape(username)}$", "$options": "i"},
            "role": {"$regex": f"^{re.escape(role)}$", "$options": "i"},
        })
        return self._serialize(user) if user else None
    
    async def save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save user"""
        db = get_db()
        result = await db.users.insert_one(data)
        return {**data, "_id": result.inserted_id}
    
    async def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user"""
        db = get_db()
        await db.users.update_one({"_id": ObjectId(id)}, {"$set": data})
        return await self.find_by_id(id)
    
    async def delete(self, id: str) -> bool:
        """Delete user"""
        db = get_db()
        result = await db.users.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    
    @staticmethod
    def _serialize(doc: Optional[Dict]) -> Optional[Dict[str, Any]]:
        """Serialize MongoDB document"""
        if not doc:
            return None
        result = dict(doc)
        if "_id" in result:
            result["id"] = str(result.pop("_id"))
        return result


class MongoOrderRepository(OrderRepository):
    """MongoDB implementation of OrderRepository"""
    
    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Find order by ID"""
        try:
            db = get_db()
            order = await db.orders.find_one({"_id": ObjectId(id)})
            return self._serialize(order) if order else None
        except InvalidId:
            return None
    
    async def find_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Find all orders by customer"""
        db = get_db()
        orders = await db.orders.find({"customer_id": customer_id}).to_list(None)
        return [self._serialize(o) for o in orders]
    
    async def find_by_restaurant(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Find all orders by restaurant"""
        db = get_db()
        orders = await db.orders.find({"restaurant_id": restaurant_id}).to_list(None)
        return [self._serialize(o) for o in orders]
    
    async def save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save order"""
        db = get_db()
        result = await db.orders.insert_one(data)
        inserted_id_str = str(result.inserted_id)
        return {**data, "_id": result.inserted_id, "id": inserted_id_str}
    
    async def update_status(self, order_id: str, status: str) -> Dict[str, Any]:
        """Update order status"""
        db = get_db()
        await db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": status, "updated_at": datetime.utcnow().isoformat()}}
        )
        return await self.find_by_id(order_id)
    
    async def assign_drone(self, order_id: str, drone_id: str) -> Dict[str, Any]:
        """Assign drone to order"""
        db = get_db()
        await db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"drone_id": drone_id, "status": "DELIVERING"}}
        )
        return await self.find_by_id(order_id)
    
    async def delete(self, id: str) -> bool:
        """Delete order"""
        db = get_db()
        result = await db.orders.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    
    @staticmethod
    def _serialize(doc: Optional[Dict]) -> Optional[Dict[str, Any]]:
        """Serialize MongoDB document"""
        if not doc:
            return None
        result = dict(doc)
        if "_id" in result:
            result["id"] = str(result.pop("_id"))
        if isinstance(result.get("restaurant_id"), ObjectId):
            result["restaurant_id"] = str(result["restaurant_id"])
        if isinstance(result.get("drone_id"), ObjectId):
            result["drone_id"] = str(result["drone_id"])
        return result


class MongoRestaurantRepository(RestaurantRepository):
    """MongoDB implementation of RestaurantRepository"""
    
    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Find restaurant by ID"""
        try:
            db = get_db()
            restaurant = await db.restaurants.find_one({"_id": ObjectId(id)})
            return self._serialize(restaurant) if restaurant else None
        except InvalidId:
            return None
    
    async def find_all(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Find all restaurants"""
        db = get_db()
        restaurants = await db.restaurants.find().skip(skip).limit(limit).to_list(None)
        return [self._serialize(r) for r in restaurants]
    
    async def find_by_owner(self, owner_username: str) -> Optional[Dict[str, Any]]:
        """Find restaurant by owner"""
        import re
        db = get_db()
        restaurant = await db.restaurants.find_one({
            "owner_username": {"$regex": f"^{re.escape(owner_username)}$", "$options": "i"}
        })
        return self._serialize(restaurant) if restaurant else None
    
    async def save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save restaurant"""
        db = get_db()
        result = await db.restaurants.insert_one(data)
        return {**data, "_id": result.inserted_id}
    
    async def delete(self, id: str) -> bool:
        """Delete restaurant"""
        db = get_db()
        result = await db.restaurants.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    
    @staticmethod
    def _serialize(doc: Optional[Dict]) -> Optional[Dict[str, Any]]:
        """Serialize MongoDB document"""
        if not doc:
            return None
        result = dict(doc)
        if "_id" in result:
            result["id"] = str(result.pop("_id"))
        return result


class MongoMenuItemRepository(MenuItemRepository):
    """MongoDB implementation of MenuItemRepository"""
    
    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Find menu item by ID"""
        try:
            db = get_db()
            item = await db.menu_items.find_one({"_id": ObjectId(id)})
            return self._serialize(item) if item else None
        except InvalidId:
            return None
    
    async def find_by_restaurant(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Find all menu items for a restaurant"""
        db = get_db()
        items = await db.menu_items.find({"restaurant_id": restaurant_id}).to_list(None)
        return [self._serialize(i) for i in items]
    
    async def save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save menu item"""
        db = get_db()
        result = await db.menu_items.insert_one(data)
        return {**data, "_id": result.inserted_id}
    
    async def delete(self, id: str) -> bool:
        """Delete menu item"""
        db = get_db()
        result = await db.menu_items.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    
    async def delete_by_restaurant(self, restaurant_id: str) -> int:
        """Delete all menu items for a restaurant"""
        db = get_db()
        result = await db.menu_items.delete_many({"restaurant_id": restaurant_id})
        return result.deleted_count
    
    @staticmethod
    def _serialize(doc: Optional[Dict]) -> Optional[Dict[str, Any]]:
        """Serialize MongoDB document"""
        if not doc:
            return None
        result = dict(doc)
        if "_id" in result:
            result["id"] = str(result.pop("_id"))
        return result


class MongoDroneRepository(DroneRepository):
    """MongoDB implementation of DroneRepository"""
    
    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Find drone by ID"""
        try:
            db = get_db()
            drone = await db.drones.find_one({"_id": ObjectId(id)})
            return self._serialize(drone) if drone else None
        except InvalidId:
            return None
    
    async def find_by_restaurant(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Find all drones for a restaurant"""
        db = get_db()
        drones = await db.drones.find({"restaurant_id": restaurant_id}).to_list(None)
        return [self._serialize(d) for d in drones]
    
    async def find_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Find drones by status"""
        db = get_db()
        drones = await db.drones.find({"status": status}).to_list(None)
        return [self._serialize(d) for d in drones]
    
    async def find_all(self, skip: int = 0, limit: int = None) -> List[Dict[str, Any]]:
        """Find all drones"""
        db = get_db()
        drones = await db.drones.find({}).skip(skip).to_list(limit)
        return [self._serialize(d) for d in drones]

    async def save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save drone"""
        db = get_db()
        result = await db.drones.insert_one(data)
        inserted_id_str = str(result.inserted_id)
        return {**data, "_id": result.inserted_id, "id": inserted_id_str}
    
    async def update_status(self, drone_id: str, status: str) -> Dict[str, Any]:
        """Update drone status"""
        db = get_db()
        await db.drones.update_one(
            {"_id": ObjectId(drone_id)},
            {"$set": {"status": status}}
        )
        return await self.find_by_id(drone_id)
    
    async def update_location(self, drone_id: str, latitude: float, longitude: float) -> Dict[str, Any]:
        """Update drone location"""
        db = get_db()
        await db.drones.update_one(
            {"_id": ObjectId(drone_id)},
            {"$set": {"latitude": latitude, "longitude": longitude}}
        )
        return await self.find_by_id(drone_id)
    
    async def delete(self, id: str) -> bool:
        """Delete drone"""
        db = get_db()
        result = await db.drones.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    
    @staticmethod
    def _serialize(doc: Optional[Dict]) -> Optional[Dict[str, Any]]:
        """Serialize MongoDB document"""
        if not doc:
            return None
        result = dict(doc)
        if "_id" in result:
            result["id"] = str(result.pop("_id"))
        if isinstance(result.get("restaurant_id"), ObjectId):
            result["restaurant_id"] = str(result["restaurant_id"])
        return result
