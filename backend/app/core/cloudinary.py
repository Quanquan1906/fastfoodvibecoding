"""Cloudinary integration helpers.

Reads credentials from environment variables:
- CLOUDINARY_CLOUD_NAME
- CLOUDINARY_API_KEY
- CLOUDINARY_API_SECRET

Keeps upload logic in one place so routes stay simple.
"""

from __future__ import annotations

import os
from typing import Any, Dict

import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError
from starlette.concurrency import run_in_threadpool


class CloudinaryNotConfiguredError(RuntimeError):
    pass


def _configure_cloudinary_from_env() -> None:
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if not cloud_name or not api_key or not api_secret:
        raise CloudinaryNotConfiguredError(
            "Missing Cloudinary credentials. Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET"
        )

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,
    )


async def upload_menu_item_image(file_obj, filename: str) -> str:
    """Upload a menu item image to Cloudinary and return the secure URL.

    file_obj should be a binary file-like object (e.g., UploadFile.file).
    """

    _configure_cloudinary_from_env()

    def _upload_sync() -> Dict[str, Any]:
        # Note: Cloudinary SDK upload is synchronous.
        return cloudinary.uploader.upload(
            file_obj,
            folder="fastfood/menu_items",
            resource_type="image",
            use_filename=True,
            unique_filename=True,
            overwrite=False,
        )

    try:
        result = await run_in_threadpool(_upload_sync)
    except CloudinaryNotConfiguredError:
        raise
    except CloudinaryError as e:
        raise RuntimeError(f"Cloudinary upload failed: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Cloudinary upload failed: {e}") from e

    url = result.get("secure_url") or result.get("url")
    if not url:
        raise RuntimeError("Cloudinary upload did not return a URL")

    return str(url)


async def upload_restaurant_image(file_obj, filename: str) -> str:
    """Upload a restaurant image to Cloudinary and return the secure URL."""

    _configure_cloudinary_from_env()

    def _upload_sync() -> Dict[str, Any]:
        return cloudinary.uploader.upload(
            file_obj,
            folder="fastfood/restaurants",
            resource_type="image",
            use_filename=True,
            unique_filename=True,
            overwrite=False,
        )

    try:
        result = await run_in_threadpool(_upload_sync)
    except CloudinaryNotConfiguredError:
        raise
    except CloudinaryError as e:
        raise RuntimeError(f"Cloudinary upload failed: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Cloudinary upload failed: {e}") from e

    url = result.get("secure_url") or result.get("url")
    if not url:
        raise RuntimeError("Cloudinary upload did not return a URL")

    return str(url)
