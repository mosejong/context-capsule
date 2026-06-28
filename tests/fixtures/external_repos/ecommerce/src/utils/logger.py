def log_request(method: str, path: str):
    print(f"{method} {path}")


def log_payment_event(user_id: int, amount: int, provider: str):
    print(f"payment user={user_id} amount={amount} provider={provider}")
