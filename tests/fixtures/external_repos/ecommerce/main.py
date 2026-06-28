from fastapi import FastAPI

from src.api.routes import orders, products, users

app = FastAPI(title="ShopFlow Dummy Ecommerce API")

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
