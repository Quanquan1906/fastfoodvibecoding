# 3-Tier Architecture - Refactored Code Examples

This document contains refactored code examples showing how to implement the 3-tier architecture.

---

## PART 1: DATA LAYER - REPOSITORIES

### 1.1 Base Repository Interface (Abstract)

**File:** `backend/app/data/repositories/base_repository.py`

```python
"""Base repository interface - all repositories inherit from this"""
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict


class BaseRepository(ABC):
    """Abstract base class for all repositories.
    
    Repositories handle all database operations.
    Services never access the database directly - they use repositories.
    """

    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record"""
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all records with pagination"""
        pass

    @abstractmethod
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record"""
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete a record"""
        pass
```

---

### 1.2 Order Repository Implementation

**File:** `backend/app/data/repositories/order_repository.py`

```python
"""Order repository - handles all order database operations.

This repository encapsulates all MongoDB queries for orders.
The application layer (services) use this instead of accessing DB directly.
"""

from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
from app.data.repositories.base_repository import BaseRepository
from app.core.database import get_db


class OrderRepository(BaseRepository):
    """MongoDB repository for Order persistence"""

    def __init__(self):
        self.collection_name = "orders"

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order in MongoDB
        
        Args:
            data: Order document with fields:
                - customer_id
                - restaurant_id
                - items
                - total
                - delivery_address
                - status (default: PENDING)
                - created_at
                - updated_at
        
        Returns:
            Created order with _id converted to id
        """
        db = get_db()
        
        # Ensure timestamps are set
        if "created_at" not in data:
            data["created_at"] = datetime.utcnow().isoformat()
        if "updated_at" not in data:
            data["updated_at"] = datetime.utcnow().isoformat()
        
        result = await db[self.collection_name].insert_one(data)
        
        # Fetch and return created document
        return await self.get_by_id(str(result.inserted_id))

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get order by ID"""
        db = get_db()
        
        try:
            order = await db[self.collection_name].find_one({"_id": ObjectId(id)})
            if order:
                return self._serialize(order)
            return None
        except Exception:
            return None

    async def get_all(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all orders with pagination"""
        db = get_db()
        
        orders = await db[self.collection_name].find() \
            .skip(skip) \
            .limit(limit) \
            .to_list(None)
        
        return [self._serialize(order) for order in orders]

    async def get_by_customer_id(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get all orders for a specific customer"""
        db = get_db()
        
        orders = await db[self.collection_name].find({"customer_id": customer_id}) \
            .to_list(None)
        
        return [self._serialize(order) for order in orders]

    async def get_by_restaurant_id(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Get all orders for a specific restaurant"""
        db = get_db()
        
        orders = await db[self.collection_name].find({"restaurant_id": restaurant_id}) \
            .to_list(None)
        
        return [self._serialize(order) for order in orders]

    async def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an order"""
        db = get_db()
        
        data["updated_at"] = datetime.utcnow().isoformat()
        
        await db[self.collection_name].update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )
        
        return await self.get_by_id(id)

    async def update_status(self, id: str, status: str) -> Optional[Dict[str, Any]]:
        """Update order status"""
        return await self.update(id, {"status": status})

    async def assign_drone(self, id: str, drone_id: str) -> Optional[Dict[str, Any]]:
        """Assign a drone to an order"""
        return await self.update(id, {"drone_id": drone_id})

    async def delete(self, id: str) -> bool:
        """Delete an order"""
        db = get_db()
        
        result = await db[self.collection_name].delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    def _serialize(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to dict with string IDs
        
        MongoDB uses ObjectId for _id field, but our API returns "id" as string.
        """
        out = dict(doc)
        if "_id" in out:
            out["id"] = str(out.pop("_id"))
        if isinstance(out.get("restaurant_id"), ObjectId):
            out["restaurant_id"] = str(out["restaurant_id"])
        if isinstance(out.get("drone_id"), ObjectId):
            out["drone_id"] = str(out["drone_id"])
        return out
```

---

## PART 2: DATA LAYER - ADAPTERS (External Services)

### 2.1 Storage Adapter Interface (Abstract)

**File:** `backend/app/data/adapters/storage_adapter.py`

```python
"""Abstract storage adapter interface for image uploads.

Any storage provider (Cloudinary, AWS S3, Azure Blob, etc.) 
should implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Any


class IStorageAdapter(ABC):
    """Abstract interface for cloud storage providers"""

    @abstractmethod
    async def upload_image(self, file_obj: Any, filename: str, folder: str) -> str:
        """Upload image and return public URL
        
        Args:
            file_obj: File-like object (bytes or file stream)
            filename: Original filename
            folder: Folder/directory in storage (e.g., "menu_items", "restaurants")
        
        Returns:
            Public URL of uploaded image
        
        Raises:
            StorageException: If upload fails
        """
        pass

    @abstractmethod
    async def delete_image(self, url: str) -> bool:
        """Delete image by URL
        
        Returns:
            True if deleted, False otherwise
        """
        pass
```

---

### 2.2 Cloudinary Adapter Implementation

**File:** `backend/app/data/adapters/cloudinary_adapter.py`

```python
"""Cloudinary storage adapter - implements IStorageAdapter

This adapter encapsulates all Cloudinary-specific logic.
The application layer uses this instead of calling Cloudinary directly.

Benefits:
- Easy to swap for another storage provider (AWS S3, Azure)
- Single place to manage Cloudinary configuration
- Application logic is not tied to Cloudinary API
"""

from typing import Any
import os
import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError
from starlette.concurrency import run_in_threadpool
from app.data.adapters.storage_adapter import IStorageAdapter
from app.shared.exceptions import StorageException


class CloudinaryAdapter(IStorageAdapter):
    """Cloudinary implementation of storage adapter"""

    def __init__(self):
        """Initialize Cloudinary from environment variables"""
        self._configure_from_env()

    def _configure_from_env(self):
        """Configure Cloudinary from .env"""
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")

        if not cloud_name or not api_key or not api_secret:
            raise StorageException(
                "Missing Cloudinary credentials in environment variables"
            )

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )

    async def upload_image(self, file_obj: Any, filename: str, folder: str) -> str:
        """Upload image to Cloudinary
        
        Args:
            file_obj: Binary file object from FastAPI UploadFile
            filename: Original filename for reference
            folder: Cloudinary folder (e.g., "fastfood/menu_items")
        
        Returns:
            Secure HTTPS URL of uploaded image
        """
        try:
            # Run blocking Cloudinary operation in thread pool
            result = await run_in_threadpool(
                lambda: cloudinary.uploader.upload(
                    file_obj,
                    folder=f"fastfood/{folder}",
                    public_id=filename.split(".")[0],  # Remove extension
                    resource_type="auto",
                    secure=True
                )
            )
            
            return result["secure_url"]
        
        except CloudinaryError as e:
            raise StorageException(f"Cloudinary upload failed: {str(e)}")
        except Exception as e:
            raise StorageException(f"Image upload error: {str(e)}")

    async def delete_image(self, url: str) -> bool:
        """Delete image from Cloudinary by URL
        
        Args:
            url: The secure_url returned from upload
        
        Returns:
            True if successful
        """
        try:
            # Extract public_id from URL
            # URL format: https://res.cloudinary.com/cloud/image/upload/v123/fastfood/folder/public_id.ext
            public_id = url.split("/")[-1].split(".")[0]
            
            result = await run_in_threadpool(
                lambda: cloudinary.uploader.destroy(public_id)
            )
            
            return result.get("result") == "ok"
        
        except CloudinaryError as e:
            raise StorageException(f"Cloudinary delete failed: {str(e)}")
```

---

### 2.3 Payment Gateway Adapter Interface

**File:** `backend/app/data/adapters/payment_adapter.py`

```python
"""Abstract payment gateway adapter interface

Any payment provider (Stripe, PayPal, etc.) should implement this.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IPaymentGateway(ABC):
    """Abstract payment gateway interface"""

    @abstractmethod
    async def process_payment(
        self,
        amount: float,
        currency: str,
        customer_id: str,
        order_id: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a payment
        
        Returns:
            {
                "success": bool,
                "transaction_id": str,
                "status": str,  # "completed", "pending", "failed"
                "message": str,
                "error": str or None
            }
        """
        pass

    @abstractmethod
    async def refund_payment(self, transaction_id: str, amount: float) -> bool:
        """Refund a payment"""
        pass
```

---

## PART 3: APPLICATION LAYER - USE CASES / SERVICES

### 3.1 Order Use Case (Business Logic)

**File:** `backend/app/application/use_cases/order_use_case.py`

```python
"""Order use cases - business logic for order operations.

Use cases orchestrate repositories and adapters.
This is where all business rules live.

Key principle: Services are DECOUPLED from:
- Database (uses repository)
- External APIs (uses adapters)
- Framework specifics (FastAPI)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from app.data.repositories.order_repository import OrderRepository
from app.data.repositories.restaurant_repository import RestaurantRepository
from app.data.repositories.menu_item_repository import MenuItemRepository
from app.data.repositories.drone_repository import DroneRepository
from app.application.dto.order_dto import OrderCreateDTO, OrderResponseDTO
from app.shared.exceptions import (
    ValidationException,
    ResourceNotFoundException,
    BusinessRuleException
)


class OrderUseCase:
    """Order business logic - no framework dependencies"""

    def __init__(
        self,
        order_repo: OrderRepository,
        restaurant_repo: RestaurantRepository,
        menu_repo: MenuItemRepository,
        drone_repo: DroneRepository
    ):
        """Dependency injection - inject repositories"""
        self.order_repo = order_repo
        self.restaurant_repo = restaurant_repo
        self.menu_repo = menu_repo
        self.drone_repo = drone_repo

    async def create_order(
        self,
        customer_id: str,
        restaurant_id: str,
        items: List[Dict[str, Any]],
        total_price: float,
        delivery_address: str
    ) -> OrderResponseDTO:
        """Create a new order with business logic validation
        
        Business rules:
        1. Restaurant must exist and be active
        2. All menu items must belong to the restaurant
        3. Prices must match menu prices (prevent client-side tampering)
        4. Total price must match calculated sum
        5. Delivery address must be valid
        
        Args:
            customer_id: Customer placing order
            restaurant_id: Restaurant for order
            items: List of {menu_item_id, quantity}
            total_price: Total from client
            delivery_address: Delivery address
        
        Returns:
            OrderResponseDTO with created order
        
        Raises:
            ValidationException: If inputs invalid
            BusinessRuleException: If business rules violated
            ResourceNotFoundException: If restaurant/items not found
        """
        
        # RULE 1: Validate restaurant exists and is active
        restaurant = await self.restaurant_repo.get_by_id(restaurant_id)
        if not restaurant:
            raise ResourceNotFoundException(f"Restaurant {restaurant_id} not found")
        
        if not restaurant.get("is_active"):
            raise BusinessRuleException("Restaurant is not accepting orders")

        # RULE 2 & 3: Validate all items exist and calculate correct total
        calculated_total = 0.0
        validated_items = []
        
        for item in items:
            menu_item_id = item.get("menu_item_id")
            quantity = item.get("quantity", 1)
            
            if not menu_item_id or quantity < 1:
                raise ValidationException(f"Invalid item: {item}")
            
            # Get menu item from DB
            menu_item = await self.menu_repo.get_by_id(menu_item_id)
            if not menu_item:
                raise ResourceNotFoundException(f"Menu item {menu_item_id} not found")
            
            # Verify item belongs to this restaurant
            if str(menu_item.get("restaurant_id")) != restaurant_id:
                raise BusinessRuleException(
                    f"Item {menu_item_id} does not belong to restaurant {restaurant_id}"
                )
            
            # Calculate price with DB values (never trust client)
            item_total = menu_item["price"] * quantity
            calculated_total += item_total
            
            validated_items.append({
                "menu_item_id": menu_item_id,
                "name": menu_item["name"],
                "price": menu_item["price"],
                "quantity": quantity,
                "subtotal": item_total
            })
        
        # RULE 4: Validate total price
        # Allow small floating point differences
        if abs(calculated_total - total_price) > 0.01:
            raise BusinessRuleException(
                f"Price mismatch. Expected {calculated_total}, got {total_price}"
            )
        
        # RULE 5: Validate delivery address
        if not delivery_address or len(delivery_address.strip()) < 5:
            raise ValidationException("Delivery address is too short")

        # All validations passed - create order
        order_data = {
            "customer_id": customer_id,
            "restaurant_id": restaurant_id,
            "items": validated_items,
            "total": calculated_total,
            "delivery_address": delivery_address,
            "status": "PENDING",
            "delivery_lat": 10.762622,  # Default location
            "delivery_lon": 106.660172,
            "drone_lat": 10.762622,
            "drone_lon": 106.660172,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        created_order = await self.order_repo.create(order_data)
        return OrderResponseDTO(**created_order)

    async def get_order(self, order_id: str) -> OrderResponseDTO:
        """Get order by ID"""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ResourceNotFoundException(f"Order {order_id} not found")
        return OrderResponseDTO(**order)

    async def get_customer_orders(
        self,
        customer_id: str
    ) -> List[OrderResponseDTO]:
        """Get all orders for a customer"""
        orders = await self.order_repo.get_by_customer_id(customer_id)
        return [OrderResponseDTO(**order) for order in orders]

    async def update_order_status(
        self,
        order_id: str,
        new_status: str
    ) -> OrderResponseDTO:
        """Update order status with validation
        
        Business rule: Only allow valid status transitions
        - PENDING → CONFIRMED, CANCELLED
        - CONFIRMED → IN_DELIVERY, CANCELLED
        - IN_DELIVERY → DELIVERED
        - Others → no change
        """
        valid_statuses = ["PENDING", "CONFIRMED", "IN_DELIVERY", "DELIVERED", "CANCELLED"]
        
        if new_status not in valid_statuses:
            raise ValidationException(f"Invalid status: {new_status}")
        
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ResourceNotFoundException(f"Order {order_id} not found")
        
        # Business rule: validate status transition
        current_status = order.get("status")
        valid_transitions = {
            "PENDING": ["CONFIRMED", "CANCELLED"],
            "CONFIRMED": ["IN_DELIVERY", "CANCELLED"],
            "IN_DELIVERY": ["DELIVERED"],
            "DELIVERED": [],
            "CANCELLED": []
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise BusinessRuleException(
                f"Cannot transition from {current_status} to {new_status}"
            )
        
        # Update status
        updated_order = await self.order_repo.update_status(order_id, new_status)
        return OrderResponseDTO(**updated_order)

    async def assign_drone_to_order(
        self,
        order_id: str,
        drone_id: str
    ) -> OrderResponseDTO:
        """Assign drone to order (business logic)
        
        Business rules:
        1. Drone must exist
        2. Drone must be available (not already assigned)
        3. Order must be in CONFIRMED status
        """
        
        # Validate order
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ResourceNotFoundException(f"Order {order_id} not found")
        
        if order.get("status") != "CONFIRMED":
            raise BusinessRuleException(
                f"Order must be CONFIRMED to assign drone. Current status: {order.get('status')}"
            )
        
        # Validate drone
        drone = await self.drone_repo.get_by_id(drone_id)
        if not drone:
            raise ResourceNotFoundException(f"Drone {drone_id} not found")
        
        if drone.get("assigned_order_id"):
            raise BusinessRuleException(f"Drone {drone_id} is already assigned to an order")
        
        # Assign drone
        updated_order = await self.order_repo.assign_drone(order_id, drone_id)
        
        # Update drone as assigned
        await self.drone_repo.assign_order(drone_id, order_id)
        
        return OrderResponseDTO(**updated_order)
```

---

### 3.2 Data Transfer Objects (DTOs)

**File:** `backend/app/application/dto/order_dto.py`

```python
"""Data Transfer Objects for Order operations.

DTOs decouple the API layer from the database layer.
They define what data is sent to/from the API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class OrderItemDTO(BaseModel):
    """Item in an order"""
    menu_item_id: str
    name: str
    price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=1)
    subtotal: float = Field(..., ge=0)


class OrderCreateDTO(BaseModel):
    """DTO for creating an order (request body)"""
    customer_id: str
    restaurant_id: str
    items: List[OrderItemDTO] = Field(..., min_length=1)
    total_price: float = Field(..., ge=0)
    delivery_address: str = Field(..., min_length=5)


class OrderResponseDTO(BaseModel):
    """DTO for order response (API return value)"""
    id: str
    customer_id: str
    restaurant_id: str
    items: List[OrderItemDTO]
    total: float
    delivery_address: str
    status: str
    drone_id: Optional[str] = None
    delivery_lat: float
    delivery_lon: float
    drone_lat: float
    drone_lon: float
    created_at: str
    updated_at: str
```

---

## PART 4: PRESENTATION LAYER - ROUTERS (FastAPI)

### 4.1 Order Router (API Endpoints)

**File:** `backend/app/presentation/routers/order_router.py`

```python
"""Order API routes (FastAPI router)

Router responsibilities:
1. Parse HTTP requests
2. Validate input with Pydantic models
3. Call use cases via dependency injection
4. Return HTTP responses

Router does NOT contain business logic.
Router does NOT access database directly.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List
from app.application.use_cases.order_use_case import OrderUseCase
from app.application.dto.order_dto import OrderCreateDTO, OrderResponseDTO, OrderItemDTO
from app.presentation.dependencies import get_order_use_case
from app.shared.exceptions import (
    ValidationException,
    BusinessRuleException,
    ResourceNotFoundException,
    StorageException
)


router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderResponseDTO, status_code=201)
async def create_order(
    request: OrderCreateDTO,
    use_case: OrderUseCase = Depends(get_order_use_case)
) -> OrderResponseDTO:
    """Create a new order
    
    Request body:
        {
            "customer_id": "cust_123",
            "restaurant_id": "rest_123",
            "items": [
                {
                    "menu_item_id": "item_1",
                    "quantity": 2
                }
            ],
            "total_price": 25.99,
            "delivery_address": "123 Main St, City"
        }
    
    Response: Created order with all details
    """
    try:
        # Call use case (business logic is here, not in router)
        order = await use_case.create_order(
            customer_id=request.customer_id,
            restaurant_id=request.restaurant_id,
            items=[item.model_dump() for item in request.items],
            total_price=request.total_price,
            delivery_address=request.delivery_address
        )
        return order
    
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{order_id}", response_model=OrderResponseDTO)
async def get_order(
    order_id: str,
    use_case: OrderUseCase = Depends(get_order_use_case)
) -> OrderResponseDTO:
    """Get order by ID"""
    try:
        return await use_case.get_order(order_id)
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/customer/{customer_id}", response_model=List[OrderResponseDTO])
async def get_customer_orders(
    customer_id: str,
    use_case: OrderUseCase = Depends(get_order_use_case)
) -> List[OrderResponseDTO]:
    """Get all orders for a customer"""
    try:
        return await use_case.get_customer_orders(customer_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: str,
    use_case: OrderUseCase = Depends(get_order_use_case)
) -> OrderResponseDTO:
    """Update order status (PENDING → CONFIRMED → IN_DELIVERY → DELIVERED)"""
    try:
        return await use_case.update_order_status(order_id, status)
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BusinessRuleException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{order_id}/assign-drone")
async def assign_drone(
    order_id: str,
    drone_id: str,
    use_case: OrderUseCase = Depends(get_order_use_case)
) -> OrderResponseDTO:
    """Assign a drone to an order"""
    try:
        return await use_case.assign_drone_to_order(order_id, drone_id)
    except BusinessRuleException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

### 4.2 Dependency Injection

**File:** `backend/app/presentation/dependencies.py`

```python
"""FastAPI dependency injection using Depends()

This file creates and provides instances of use cases to routers.
FastAPI automatically manages lifecycle and caching.
"""

from fastapi import Depends
from app.application.use_cases.order_use_case import OrderUseCase
from app.application.use_cases.restaurant_use_case import RestaurantUseCase
from app.data.repositories.order_repository import OrderRepository
from app.data.repositories.restaurant_repository import RestaurantRepository
from app.data.repositories.menu_item_repository import MenuItemRepository
from app.data.repositories.drone_repository import DroneRepository
from app.data.adapters.cloudinary_adapter import CloudinaryAdapter


# Repository instances
def get_order_repo() -> OrderRepository:
    return OrderRepository()


def get_restaurant_repo() -> RestaurantRepository:
    return RestaurantRepository()


def get_menu_repo() -> MenuItemRepository:
    return MenuItemRepository()


def get_drone_repo() -> DroneRepository:
    return DroneRepository()


# Adapter instances
def get_storage_adapter():
    return CloudinaryAdapter()


# Use Case instances (orchestrate repositories)
def get_order_use_case(
    order_repo: OrderRepository = Depends(get_order_repo),
    restaurant_repo: RestaurantRepository = Depends(get_restaurant_repo),
    menu_repo: MenuItemRepository = Depends(get_menu_repo),
    drone_repo: DroneRepository = Depends(get_drone_repo)
) -> OrderUseCase:
    """Create and inject OrderUseCase with all dependencies"""
    return OrderUseCase(
        order_repo=order_repo,
        restaurant_repo=restaurant_repo,
        menu_repo=menu_repo,
        drone_repo=drone_repo
    )


def get_restaurant_use_case(
    restaurant_repo: RestaurantRepository = Depends(get_restaurant_repo),
    storage: CloudinaryAdapter = Depends(get_storage_adapter)
) -> RestaurantUseCase:
    """Create and inject RestaurantUseCase"""
    return RestaurantUseCase(restaurant_repo, storage)
```

---

## PART 5: PRESENTATION LAYER - WEBSOCKET

### 5.1 WebSocket Endpoint

**File:** `backend/app/presentation/websocket/order_tracking.py`

```python
"""WebSocket endpoint for order tracking (real-time updates)

WebSocket endpoints follow the same 3-tier architecture:
- Presentation: Handle WebSocket connections
- Application: Orchestrate data
- Data: Fetch from repositories
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.websocket.manager import ConnectionManager
from app.application.use_cases.order_use_case import OrderUseCase
from app.presentation.dependencies import get_order_use_case


router = APIRouter(prefix="/ws", tags=["websocket"])
manager = ConnectionManager()


@router.websocket("/track-order/{order_id}")
async def websocket_track_order(
    websocket: WebSocket,
    order_id: str,
    use_case: OrderUseCase = Depends(get_order_use_case)
):
    """WebSocket endpoint for real-time order tracking
    
    Client connects: ws://localhost:8000/ws/track-order/{order_id}
    Server sends order updates whenever status changes.
    """
    await manager.connect(order_id, websocket)
    
    try:
        while True:
            # Wait for messages from client (optional: client can send ping)
            data = await websocket.receive_text()
            
            # Client requested current order status
            if data == "ping":
                try:
                    order = await use_case.get_order(order_id)
                    await websocket.send_json({
                        "type": "order_update",
                        "order": order.model_dump()
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
    
    except WebSocketDisconnect:
        manager.disconnect(order_id, websocket)
    except Exception as e:
        manager.disconnect(order_id, websocket)


async def broadcast_order_status_change(order_id: str, order_data: dict):
    """Called from use case when order status changes
    
    This broadcasts the update to all connected WebSocket clients.
    """
    await manager.broadcast_order_update(order_id, {
        "type": "order_update",
        "order": order_data
    })
```

---

## PART 6: FRONTEND - SERVICE LAYER

### 6.1 API Client

**File:** `frontend/src/infrastructure/api/client.js`

```javascript
/**
 * API client - handles HTTP communication with backend
 * Part of Infrastructure Layer (no business logic)
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

// Create axios instance with default config
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth and redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

---

### 6.2 Order API Service

**File:** `frontend/src/infrastructure/api/order_client.js`

```javascript
/**
 * Order API service - encapsulates all order API calls
 * Infrastructure Layer: only HTTP communication, no business logic
 */

import apiClient from './client';

export const orderClient = {
  /**
   * Create a new order
   */
  async createOrder(orderData) {
    const response = await apiClient.post('/orders', orderData);
    return response.data;
  },

  /**
   * Get order by ID
   */
  async getOrder(orderId) {
    const response = await apiClient.get(`/orders/${orderId}`);
    return response.data;
  },

  /**
   * Get all orders for customer
   */
  async getCustomerOrders(customerId) {
    const response = await apiClient.get(`/orders/customer/${customerId}`);
    return response.data;
  },

  /**
   * Update order status
   */
  async updateOrderStatus(orderId, status) {
    const response = await apiClient.patch(`/orders/${orderId}/status`, {
      status,
    });
    return response.data;
  },

  /**
   * Assign drone to order
   */
  async assignDrone(orderId, droneId) {
    const response = await apiClient.post(`/orders/${orderId}/assign-drone`, {
      drone_id: droneId,
    });
    return response.data;
  },
};
```

---

### 6.3 Frontend Custom Hook (Business Logic Container)

**File:** `frontend/src/presentation/hooks/useOrder.js`

```javascript
/**
 * Custom Hook: useOrder
 * 
 * This hook contains order-related business logic:
 * - Fetching orders
 * - Managing order state
 * - Handling order validation
 * 
 * Presentation Layer: Uses infrastructure services
 */

import { useState, useEffect } from 'react';
import { orderClient } from '../../infrastructure/api/order_client';

export const useOrder = (orderId) => {
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch order on mount
  useEffect(() => {
    const fetchOrder = async () => {
      if (!orderId) return;

      setLoading(true);
      setError(null);

      try {
        const data = await orderClient.getOrder(orderId);
        setOrder(data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load order');
      } finally {
        setLoading(false);
      }
    };

    fetchOrder();
  }, [orderId]);

  // Update order status
  const updateStatus = async (newStatus) => {
    try {
      const updated = await orderClient.updateOrderStatus(orderId, newStatus);
      setOrder(updated);
      return updated;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update status');
      throw err;
    }
  };

  // Assign drone
  const assignDrone = async (droneId) => {
    try {
      const updated = await orderClient.assignDrone(orderId, droneId);
      setOrder(updated);
      return updated;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to assign drone');
      throw err;
    }
  };

  return { order, loading, error, updateStatus, assignDrone };
};
```

---

### 6.4 Frontend Page Component (Presentation)

**File:** `frontend/src/presentation/pages/customer/Orders.jsx`

```javascript
/**
 * Customer Orders Page - Presentation Layer
 * 
 * Responsibilities:
 * - Render UI only
 * - Use hooks for data
 * - Call handlers for user actions
 * 
 * Does NOT:
 * - Call API directly
 * - Contain business logic
 * - Store complex state
 */

import React, { useState, useEffect } from 'react';
import { useOrder } from '../../hooks/useOrder';
import { orderClient } from '../../../infrastructure/api/order_client';
import OrderCard from '../../components/OrderCard';
import Loading from '../../components/common/Loading';
import './Orders.css';

export default function CustomerOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch customer orders on mount
  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const customerId = localStorage.getItem('customer_id');
        if (!customerId) {
          setError('Not logged in');
          return;
        }

        const data = await orderClient.getCustomerOrders(customerId);
        setOrders(data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load orders');
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  // Handle order click
  const handleOrderClick = (orderId) => {
    window.location.href = `/customer/track/${orderId}`;
  };

  if (loading) return <Loading />;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="orders-container">
      <h1>My Orders</h1>
      
      {orders.length === 0 ? (
        <p>You haven't placed any orders yet.</p>
      ) : (
        <div className="orders-grid">
          {orders.map((order) => (
            <OrderCard
              key={order.id}
              order={order}
              onClick={() => handleOrderClick(order.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## SUMMARY TABLE

| Layer | Backend | Frontend | Responsibility |
|-------|---------|----------|-----------------|
| **Presentation** | `routers/` + `websocket/` | `pages/` + `components/` | Handle HTTP/WS, UI rendering |
| **Application** | `use_cases/` + `services/` | `hooks/` | Business logic, validation |
| **Data** | `repositories/` + `adapters/` | `api/` clients | External integration |

