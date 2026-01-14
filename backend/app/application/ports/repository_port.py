"""Port interfaces - abstract contracts for data access"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.domain.entities.user import User, LoginRequest
from app.domain.entities.order import Order, OrderCreate
from app.domain.entities.restaurant import Restaurant
from app.domain.entities.menu_item import MenuItem
from app.domain.entities.drone import Drone


class BaseRepository(ABC):
    """Abstract base repository"""
    
    @abstractmethod
    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Find entity by ID"""
        pass
    
    @abstractmethod
    async def save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save entity"""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete entity"""
        pass


class UserRepository(BaseRepository):
    """User data access port"""
    
    @abstractmethod
    async def find_by_username(self, username: str, role: str) -> Optional[Dict[str, Any]]:
        """Find user by username and role"""
        pass
    
    @abstractmethod
    async def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user"""
        pass


class OrderRepository(BaseRepository):
    """Order data access port"""
    
    @abstractmethod
    async def find_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Find all orders by customer"""
        pass
    
    @abstractmethod
    async def find_by_restaurant(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Find all orders by restaurant"""
        pass
    
    @abstractmethod
    async def update_status(self, order_id: str, status: str) -> Dict[str, Any]:
        """Update order status"""
        pass
    
    @abstractmethod
    async def assign_drone(self, order_id: str, drone_id: str) -> Dict[str, Any]:
        """Assign drone to order"""
        pass


class RestaurantRepository(BaseRepository):
    """Restaurant data access port"""
    
    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Find all restaurants"""
        pass
    
    @abstractmethod
    async def find_by_owner(self, owner_username: str) -> Optional[Dict[str, Any]]:
        """Find restaurant by owner"""
        pass


class MenuItemRepository(BaseRepository):
    """Menu item data access port"""
    
    @abstractmethod
    async def find_by_restaurant(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Find all menu items for a restaurant"""
        pass
    
    @abstractmethod
    async def delete_by_restaurant(self, restaurant_id: str) -> int:
        """Delete all menu items for a restaurant"""
        pass


class DroneRepository(BaseRepository):
    """Drone data access port"""
    
    @abstractmethod
    async def find_by_restaurant(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Find all drones for a restaurant"""
        pass
    
    @abstractmethod
    async def find_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Find drones by status"""
        pass
    
    @abstractmethod
    async def update_status(self, drone_id: str, status: str) -> Dict[str, Any]:
        """Update drone status"""
        pass
    
    @abstractmethod
    async def update_location(self, drone_id: str, latitude: float, longitude: float) -> Dict[str, Any]:
        """Update drone location"""
        pass
