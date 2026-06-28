from fastapi import APIRouter

router = APIRouter()

PRODUCTS = [
    {"id": 1, "name": "Keyboard", "price": 120000},
    {"id": 2, "name": "Mouse", "price": 59000},
    {"id": 3, "name": "Monitor", "price": 320000},
]


@router.get("/")
def list_products():
    # TODO: add limit/offset pagination before this grows.
    return {"items": PRODUCTS, "count": len(PRODUCTS)}


@router.get("/{product_id}")
def get_product(product_id: int):
    return next((item for item in PRODUCTS if item["id"] == product_id), None)
