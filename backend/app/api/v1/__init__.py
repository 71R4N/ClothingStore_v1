from fastapi import APIRouter
from app.auth.routes import router as auth_router
from app.users.routes import router as users_router
from app.catalog.routes import router as catalog_router
from app.cart.routes import router as cart_router
from app.orders.routes import router as orders_router
from app.tryon.routes import router as tryon_router
from app.wishlist.routes import router as wishlist_router
from app.upload.routes import router as upload_router


v1_router = APIRouter()
v1_router.include_router(auth_router)
v1_router.include_router(users_router)
v1_router.include_router(catalog_router)
v1_router.include_router(cart_router)
v1_router.include_router(orders_router)
v1_router.include_router(tryon_router)
v1_router.include_router(wishlist_router)
v1_router.include_router(upload_router)
