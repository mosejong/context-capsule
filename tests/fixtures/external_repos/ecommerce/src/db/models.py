from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int
    email: str
    hashed_password: str
    created_at: datetime
    # Seeded gap: last_login is missing for issue #47.


@dataclass
class Product:
    id: int
    name: str
    price: int


@dataclass
class Order:
    id: int
    user_id: int
    product_id: int
    amount: int
