from fastapi import APIRouter, HTTPException

from src.services.auth_service import issue_token, verify_password

router = APIRouter()


@router.post("/login")
def login_user(email: str, password: str):
    if not verify_password(email, password):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = issue_token(email)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def current_user():
    return {"email": "demo@example.com", "role": "buyer"}
