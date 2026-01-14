"""External service ports - abstract contracts for external services"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class ImageUploadService(ABC):
    """Image upload service port"""
    
    @abstractmethod
    async def upload_menu_item_image(self, file_obj: Any, filename: str) -> str:
        """Upload menu item image and return URL"""
        pass
    
    @abstractmethod
    async def upload_restaurant_image(self, file_obj: Any, filename: str) -> str:
        """Upload restaurant image and return URL"""
        pass


class PaymentPort(ABC):
    """Payment processing port"""
    
    @abstractmethod
    async def process_payment(self, order_id: str, amount: float) -> Dict[str, Any]:
        """Process payment"""
        pass


class CachePort(ABC):
    """Cache storage port"""
    
    @abstractmethod
    async def get(self, key: str) -> Any:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        pass
