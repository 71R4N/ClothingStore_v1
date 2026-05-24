from fastapi import APIRouter
from backend.app.auth.routes import router as auth_router
from backend.app.users.routes import router as users_router
from backend.app.catalog.routes import router as catalog_router
from backend.app.cart.routes import router as cart_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth_router)
v1_router.include_router(users_router)
v1_router.include_router(catalog_router)
v1_router.include_router(cart_router)

# позже добавим catalog, cart, orders, tryon и т.д.
