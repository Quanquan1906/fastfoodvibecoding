"""Payment service - business logic for payments"""
from app.application.ports.repository_port import OrderRepository
from app.application.ports.external_service_port import PaymentPort
from typing import Dict, Any
from datetime import datetime


class PaymentService:
    """Payment service - uses injected payment port"""
    
    def __init__(self, order_repo: OrderRepository, payment_port: PaymentPort = None):
        self.order_repo = order_repo
        self.payment_port = payment_port
    
    async def mock_pay(self, order_id: str) -> Dict[str, Any]:
        """Mock payment - instant success"""
        # Update order status to PREPARING
        await self.order_repo.update_status(order_id, "PREPARING")
        
        return {
            "order_id": order_id,
            "status": "PAID",
            "message": "✅ Mock payment successful - Order is now PREPARING",
            "transaction_id": f"MOCK-{order_id[:8]}"
        }
    
    async def process_payment(self, order_id: str, amount: float) -> Dict[str, Any]:
        """Process payment using payment port"""
        if self.payment_port:
            return await self.payment_port.process_payment(order_id, amount)
        else:
            return await self.mock_pay(order_id)
