from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import auth, products, listings, stores, orders, settings as settings_router

app = FastAPI(title="DiscoveryFX API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,            prefix="/api/auth",     tags=["auth"])
app.include_router(products.router,        prefix="/api/products", tags=["products"])
app.include_router(listings.router,        prefix="/api/listings", tags=["listings"])
app.include_router(stores.router,          prefix="/api/stores",   tags=["stores"])
app.include_router(orders.router,          prefix="/api/orders",   tags=["orders"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
