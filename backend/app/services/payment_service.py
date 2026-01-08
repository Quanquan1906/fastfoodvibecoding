"""Mock payment service - 100% simulated"""
from app.core.database import get_db
from bson import ObjectId
from datetime import datetime


class PaymentService:
    """Mock payment - always succeeds"""

    async def mock_pay(self, order_id: str) -> dict:
        """Mock payment - instant success"""
        db = get_db()
        
        # Update order status to PREPARING
        await db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {
                "$set": {
                    "status": "PREPARING",
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        return {
            "order_id": order_id,
            "status": "PAID",
            "message": "✅ Mock payment successful - Order is now PREPARING",
            "transaction_id": f"MOCK-{order_id[:8]}"
        }
