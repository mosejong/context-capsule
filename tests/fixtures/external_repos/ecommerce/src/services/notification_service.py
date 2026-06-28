def send_order_receipt(email: str, order_id: int) -> bool:
    return bool(email and order_id)


def send_payment_failed(email: str, reason: str) -> bool:
    return bool(email and reason)
