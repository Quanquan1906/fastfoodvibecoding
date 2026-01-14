"""Restaurant service - business logic for restaurants"""
from app.application.ports.repository_port import RestaurantRepository, MenuItemRepository
from app.application.ports.external_service_port import ImageUploadService
from typing import Dict, Any, List, Optional


class RestaurantService:
    """Restaurant service - NO direct database access"""
    
    def __init__(
        self, 
        restaurant_repo: RestaurantRepository, 
        menu_repo: MenuItemRepository,
        image_upload: ImageUploadService = None
    ):
        self.restaurant_repo = restaurant_repo
        self.menu_repo = menu_repo
        self.image_upload = image_upload
    
    async def get_restaurants(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all restaurants with pagination"""
        return await self.restaurant_repo.find_all(skip, limit)
    
    async def get_restaurant(self, restaurant_id: str) -> Optional[Dict[str, Any]]:
        """Get restaurant by ID"""
        return await self.restaurant_repo.find_by_id(restaurant_id)
    
    async def get_restaurant_menu(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Get menu items for a restaurant"""
        return await self.menu_repo.find_by_restaurant(restaurant_id)
    
    async def get_menu_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get menu item by ID"""
        return await self.menu_repo.find_by_id(item_id)
    
    async def create_restaurant(self, name: str, owner_id: str, owner_username: str) -> Dict[str, Any]:
        """Create a new restaurant"""
        restaurant_doc = {
            "name": name,
            "owner_id": owner_id,
            "owner_username": owner_username,
            "description": None,
            "address": None,
            "phone": None,
            "image_url": None,
        }
        return await self.restaurant_repo.save(restaurant_doc)
    
    async def create_menu_item(self, restaurant_id: str, name: str, price: float) -> Dict[str, Any]:
        """Create a menu item"""
        item_doc = {
            "restaurant_id": restaurant_id,
            "name": name,
            "description": None,
            "price": price,
            "image_url": None,
            "available": True,
        }
        return await self.menu_repo.save(item_doc)
