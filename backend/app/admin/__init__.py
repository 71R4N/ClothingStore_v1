# backend/app/admin/__init__.py
from sqladmin import Admin
from app.core.database import engine
from app.admin.auth import AdminAuth
from app.admin.views import (
    UserAdmin, UserSessionAdmin,
    CategoryAdmin, ProductAdmin,
    ProductSizeAdmin, ProductColorAdmin, ProductVariantAdmin,
    OrderAdmin, OrderItemAdmin, CartItemAdmin,
    WishlistAdmin, TryOnSessionAdmin,
    PaymentAdmin, ReturnAdmin,
    ReturnItemAdmin,
)
from app.core.config import settings


def setup_admin(app) -> Admin:
    """
    Инициализирует и настраивает админ-панель SQLAdmin.

    Args:
        app: экземпляр FastAPI приложения

    Returns:
        Настроенный экземпляр Admin
    """
    admin = Admin(
        app=app,
        engine=engine,
        title="CatVTON Admin",
        base_url="/admin",
        authentication_backend=AdminAuth(
            secret_key=settings.ADMIN_SECRET_KEY
        ),
    )

    # Регистрация представлений моделей
    # Пользователи
    admin.add_view(UserAdmin)
    admin.add_view(UserSessionAdmin)

    # Каталог
    admin.add_view(CategoryAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(ProductSizeAdmin)
    admin.add_view(ProductColorAdmin)
    admin.add_view(ProductVariantAdmin)

    # Заказы и корзина
    admin.add_view(OrderAdmin)
    admin.add_view(OrderItemAdmin)
    admin.add_view(CartItemAdmin)

    admin.add_view(ReturnAdmin)
    admin.add_view(ReturnItemAdmin)

    # Прочее
    admin.add_view(WishlistAdmin)
    admin.add_view(TryOnSessionAdmin)
    admin.add_view(PaymentAdmin)

    return admin
