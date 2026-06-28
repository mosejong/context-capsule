from fastapi import APIRouter, HTTPException

from src.db.models import Order
from src.services.payment_service import authorize_payment

router = APIRouter()


@router.post("/")
def create_order(user_id: int, product_id: int, amount: int):
    payment = authorize_payment(user_id=user_id, amount=amount)
    if not payment["approved"]:
        raise HTTPException(status_code=402, detail="payment declined")
    order = Order(id=1, user_id=user_id, product_id=product_id, amount=amount)
    return {"order_id": order.id, "status": "paid"}
