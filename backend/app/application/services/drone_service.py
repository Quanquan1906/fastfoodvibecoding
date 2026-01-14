"""Drone service - business logic for drones"""
from app.application.ports.repository_port import DroneRepository
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio


class DroneService:
    """Drone service - NO direct database access"""
    
    def __init__(self, drone_repo: DroneRepository):
        self.drone_repo = drone_repo
    
    async def create_drone(self, name: str, restaurant_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new drone"""
        drone_doc = {
            "name": name,
            "restaurant_id": restaurant_id,
            "status": "AVAILABLE",
            "latitude": 10.762622,
            "longitude": 106.660172,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return await self.drone_repo.save(drone_doc)
    
    async def get_drone(self, drone_id: str) -> Optional[Dict[str, Any]]:
        """Get drone by ID"""
        return await self.drone_repo.find_by_id(drone_id)
    
    async def get_restaurant_drones(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Get all drones for a restaurant"""
        return await self.drone_repo.find_by_restaurant(restaurant_id)
    
    async def get_all_drones(self) -> List[Dict[str, Any]]:
        """Get all drones (ADMIN)"""
        return await self.drone_repo.find_all()
    
    async def update_drone_status(self, drone_id: str, status: str) -> Dict[str, Any]:
        """Update drone status"""
        return await self.drone_repo.update_status(drone_id, status)
    
    async def update_drone_location(self, drone_id: str, latitude: float, longitude: float) -> Dict[str, Any]:
        """Update drone location"""
        return await self.drone_repo.update_location(drone_id, latitude, longitude)
    
    async def get_available_drone(self, restaurant_id: str) -> Optional[Dict[str, Any]]:
        """Get first available drone for restaurant"""
        drones = await self.drone_repo.find_by_restaurant(restaurant_id)
        for drone in drones:
            if drone.get("status") == "AVAILABLE":
                return drone
        return None
