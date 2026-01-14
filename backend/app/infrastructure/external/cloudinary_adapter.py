"""Cloudinary adapter - implements ImageUploadService port"""
from typing import Any
from app.application.ports.external_service_port import ImageUploadService
from app.infrastructure.external.cloudinary_client import (
    upload_menu_item_image as cloudinary_upload_menu_item,
    upload_restaurant_image as cloudinary_upload_restaurant,
    CloudinaryNotConfiguredError
)


class CloudinaryImageUploadAdapter(ImageUploadService):
    """Cloudinary implementation of ImageUploadService"""
    
    async def upload_menu_item_image(self, file_obj: Any, filename: str) -> str:
        """Upload menu item image"""
        try:
            return await cloudinary_upload_menu_item(file_obj, filename)
        except CloudinaryNotConfiguredError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to upload menu item image: {e}") from e
    
    async def upload_restaurant_image(self, file_obj: Any, filename: str) -> str:
        """Upload restaurant image"""
        try:
            return await cloudinary_upload_restaurant(file_obj, filename)
        except CloudinaryNotConfiguredError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to upload restaurant image: {e}") from e
