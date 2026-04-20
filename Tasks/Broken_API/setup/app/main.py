"""
Broken API — a small e-commerce FastAPI service with 5 bugs to find and fix.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import init_db
from routes.products import router as products_router
from routes.orders import router as orders_router
from routes.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="ShopAPI", version="1.0.0", lifespan=lifespan)

app.include_router(products_router)
app.include_router(orders_router)
app.include_router(users_router)


@app.get("/health")
def health():
    return {"status": "ok"}
