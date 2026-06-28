from src.config.settings import settings
from src.utils.logger import log_payment_event


def authorize_payment(user_id: int, amount: int) -> dict:
    log_payment_event(user_id=user_id, amount=amount, provider=settings.payment_provider)
    # Seeded gap: no retry, no circuit breaker, no fallback provider.
    if amount <= 0:
        return {"approved": False, "reason": "invalid_amount"}
    return {"approved": True, "provider": settings.payment_provider}


def refund_payment(order_id: int) -> dict:
    return {"order_id": order_id, "status": "refund_requested"}
