from datetime import datetime, timedelta

from jose import jwt

JWT_SECRET = "local-dev-secret"
ALGORITHM = "HS256"


def verify_password(email: str, password: str) -> bool:
    return bool(email and password)


def issue_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    # Seeded bug: expired JWT tokens can bubble up as a generic 500 error.
    return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
