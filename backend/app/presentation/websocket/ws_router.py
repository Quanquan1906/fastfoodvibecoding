"""WebSocket endpoint router"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.presentation.websocket.handlers import manager
from app.infrastructure.persistence.repositories.mongo_repository import MongoOrderRepository, MongoDroneRepository
from app.application.services.order_service import OrderService
import asyncio

router = APIRouter()


@router.websocket("/ws/orders/{order_id}")
async def websocket_order_tracking(order_id: str, websocket: WebSocket):
    """WebSocket for order tracking"""
    await manager.connect(order_id, websocket)
    
    try:
        order_repo = MongoOrderRepository()
        drone_repo = MongoDroneRepository()
        service = OrderService(order_repo, drone_repo)
        
        while True:
            # Get latest order info
            order = await service.get_order(order_id)
            
            if order:
                # Send order update
                await manager.broadcast_order_update(order_id, order)
            
            # Send update every 2 seconds
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        manager.disconnect(order_id, websocket)
    except Exception as e:
        manager.disconnect(order_id, websocket)
        print(f"WebSocket error: {e}")
