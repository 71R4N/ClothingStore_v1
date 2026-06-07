from sqladmin import ModelView, action
from sqladmin.helpers import get_object_identifier
from starlette.requests import Request
from starlette.responses import RedirectResponse
from typing import Any, List
from uuid import UUID

from app.users.models import User, UserSession
from app.catalog.models import (
    Category, Product, ProductSize, ProductColor, ProductVariant
)
from app.cart.models import CartItem
from app.orders.models import Order, OrderItem
from app.wishlist.models import Wishlist
from app.tryon.models import TryOnSession
from app.payments.models import Payment
from app.returns.models import Return, ReturnItem
from app.core.database import AsyncSessionLocal
from app.returns.repositories import ReturnRepo, ReturnItemRepo
from app.orders.repositories import OrderRepo, OrderItemRepo
from app.catalog.repositories import ProductVariantRepo
from app.returns.services import ReturnService


class ReturnAdmin(ModelView, model=Return):
    """Админ-представление для заявок на возврат."""
    name = "Возврат"
    name_plural = "Возвраты товаров"
    icon = "fa-solid fa-rotate-left"
    column_list = [
        Return.id, Return.order_id, Return.user_id,
        Return.status, Return.reason_type, Return.total_amount,
        Return.created_at, Return.resolved_at
    ]
    column_details_list = [
        Return.id, Return.order_id, Return.user_id, Return.guest_email,
        Return.status, Return.reason_type, Return.description,
        Return.total_amount, Return.refund_payment_id,
        Return.rejection_reason, Return.created_at,
        Return.updated_at, Return.resolved_at, Return.resolved_by
    ]
    column_searchable_list = [
        Return.id, Return.guest_email, Return.status
    ]
    column_sortable_list = [
        Return.created_at, Return.status, Return.total_amount
    ]
    column_default_sort = ("created_at", True)
    column_formatters = {
        Return.status: lambda m, v: m.status.value if m.status else "",
        Return.reason_type: lambda m, v: (
            m.reason_type.value if m.reason_type else ""
        ),
    }
    form_choices = {
        "status": [
            ("pending", "Ожидает"),
            ("approved", "Одобрено"),
            ("rejected", "Отклонено"),
            ("refunded", "Возвращено"),
            ("cancelled", "Отменено"),
            ("failed", "Ошибка"),
        ],
    }
    can_create = False
    can_edit = False
    can_delete = True
    can_view_details = True

    @action(
        name="approve",
        label="Одобрить",
        confirmation_message="Одобрить выбранные заявки на возврат? Товары будут возвращены на склад, а средства — отправлены на возврат.",
    )
    async def approve_action(self, request: Request) -> RedirectResponse:
        """
        Массовое одобрение заявок на возврат.
        Возвращает RedirectResponse для корректной работы маршрутов Starlette.
        """
        pks = request.query_params.getlist("pks")
        # Формируем URL для редиректа: возвращаемся на предыдущую страницу
        redirect_url = request.headers.get("referer", "/admin/return/list")

        if not pks:
            return RedirectResponse(url=redirect_url, status_code=303)

        async with AsyncSessionLocal() as session:
            return_repo = ReturnRepo(session)
            return_item_repo = ReturnItemRepo(session)
            order_repo = OrderRepo(session)
            order_item_repo = OrderItemRepo(session)
            variant_repo = ProductVariantRepo(session)
            service = ReturnService(
                return_repo=return_repo,
                return_item_repo=return_item_repo,
                order_repo=order_repo,
                order_item_repo=order_item_repo,
                variant_repo=variant_repo,
            )
            admin_id_str = request.session.get("admin_user_id")
            admin_id = UUID(admin_id_str) if admin_id_str else None

            for pk in pks:
                try:
                    return_id = UUID(str(pk))
                    await service.approve_return(return_id, admin_id)
                except Exception:
                    # Ошибки бизнес-логики логируются внутри сервисного слоя
                    pass

        return RedirectResponse(url=redirect_url, status_code=303)

    @action(
        name="reject",
        label="Отклонить",
        confirmation_message="Отклонить выбранные заявки? Будет указана стандартная причина отклонения.",
    )
    async def reject_action(self, request: Request) -> RedirectResponse:
        """
        Массовое отклонение заявок со стандартной причиной.
        """
        pks = request.query_params.getlist("pks")
        redirect_url = request.headers.get("referer", "/admin/return/list")

        if not pks:
            return RedirectResponse(url=redirect_url, status_code=303)

        rejection_reason = "Заявка отклонена администратором. Для уточнения причины свяжитесь с поддержкой."

        async with AsyncSessionLocal() as session:
            return_repo = ReturnRepo(session)
            return_item_repo = ReturnItemRepo(session)
            order_repo = OrderRepo(session)
            order_item_repo = OrderItemRepo(session)
            variant_repo = ProductVariantRepo(session)
            service = ReturnService(
                return_repo=return_repo,
                return_item_repo=return_item_repo,
                order_repo=order_repo,
                order_item_repo=order_item_repo,
                variant_repo=variant_repo,
            )
            admin_id_str = request.session.get("admin_user_id")
            admin_id = UUID(admin_id_str) if admin_id_str else None

            for pk in pks:
                try:
                    return_id = UUID(str(pk))
                    await service.reject_return(return_id, admin_id, rejection_reason)
                except Exception:
                    pass

        return RedirectResponse(url=redirect_url, status_code=303)


class ReturnItemAdmin(ModelView, model=ReturnItem):
    """Админ-представление для позиций возврата."""
    name = "Позиция возврата"
    name_plural = "Позиции возвратов"
    icon = "fa-solid fa-list-check"

    column_list = [
        ReturnItem.id, ReturnItem.return_id,
        ReturnItem.order_item_id, ReturnItem.variant_id,
        ReturnItem.quantity, ReturnItem.refund_amount,
        ReturnItem.created_at
    ]

    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True


# ============================================================
# ПОЛЬЗОВАТЕЛИ
# ============================================================
class UserAdmin(ModelView, model=User):
    """Админ-представление для модели User."""

    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"

    column_list = [
        User.id, User.email, User.first_name, User.last_name,
        User.phone, User.role, User.is_active, User.created_at
    ]
    column_details_list = [
        User.id, User.email, User.first_name, User.last_name,
        User.phone, User.role, User.is_active, User.created_at
    ]
    form_columns = [
        "email", "first_name", "last_name", "phone",
        "role", "is_active"
    ]
    column_searchable_list = [User.email, User.first_name, User.last_name]
    column_sortable_list = [User.email, User.created_at, User.role]
    column_default_sort = ("created_at", True)

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    form_choices = {
        "role": [("user", "Пользователь"), ("admin", "Администратор")],
    }


class UserSessionAdmin(ModelView, model=UserSession):
    """Админ-представление для сессий пользователей."""

    name = "Сессия"
    name_plural = "Сессии пользователей"
    icon = "fa-solid fa-key"

    column_list = [
        UserSession.id, UserSession.user_id,
        UserSession.expires_at, UserSession.created_at
    ]

    can_create = False
    can_edit = False
    can_delete = True


# ============================================================
# КАТАЛОГ
# ============================================================
class CategoryAdmin(ModelView, model=Category):
    """Админ-представление для категорий."""

    name = "Категория"
    name_plural = "Категории"
    icon = "fa-solid fa-folder"

    column_list = [
        Category.id, Category.name, Category.slug,
        Category.parent_id, Category.description
    ]
    form_columns = [
        "name", "slug", "parent_id", "description", "image_url"
    ]
    column_searchable_list = [Category.name, Category.slug]
    column_sortable_list = [Category.name, Category.id]

    can_create = True
    can_edit = True
    can_delete = True


class ProductAdmin(ModelView, model=Product):
    """Админ-представление для товаров."""

    name = "Товар"
    name_plural = "Товары"
    icon = "fa-solid fa-shirt"

    column_list = [
        Product.id, Product.name, Product.slug,
        Product.category_id, Product.brand,
        Product.is_active, Product.created_at
    ]
    form_columns = [
        "name", "slug", "description", "category_id",
        "brand", "brand_logo", "is_active"
    ]
    column_searchable_list = [Product.name, Product.slug, Product.brand]
    column_sortable_list = [Product.name, Product.created_at, Product.is_active]
    column_default_sort = ("created_at", True)

    can_create = True
    can_edit = True
    can_delete = True


class ProductSizeAdmin(ModelView, model=ProductSize):
    """Админ-представление для размеров."""

    name = "Размер"
    name_plural = "Размеры товаров"
    icon = "fa-solid fa-ruler"

    column_list = [
        ProductSize.id, ProductSize.product_id,
        ProductSize.size_label
    ]
    form_columns = [
        "product_id", "size_label", "chest_cm",
        "waist_cm", "hips_cm", "height_cm"
    ]


class ProductColorAdmin(ModelView, model=ProductColor):
    """Админ-представление для цветов."""

    name = "Цвет"
    name_plural = "Цвета товаров"
    icon = "fa-solid fa-palette"

    column_list = [
        ProductColor.id, ProductColor.product_id,
        ProductColor.color_name, ProductColor.color_hex
    ]
    form_columns = ["product_id", "color_name", "color_hex"]


class ProductVariantAdmin(ModelView, model=ProductVariant):
    """Админ-представление для вариантов товаров (SKU)."""

    name = "Вариант"
    name_plural = "Варианты товаров"
    icon = "fa-solid fa-tags"

    column_list = [
        ProductVariant.id, ProductVariant.sku,
        ProductVariant.product_id, ProductVariant.color_id,
        ProductVariant.size_id, ProductVariant.price,
        ProductVariant.stock_quantity
    ]
    form_columns = [
        "product_id", "color_id", "size_id", "sku",
        "price", "stock_quantity", "image_url", "attributes"
    ]
    column_searchable_list = [ProductVariant.sku]
    column_sortable_list = [ProductVariant.price, ProductVariant.stock_quantity]


# ============================================================
# ЗАКАЗЫ И КОРЗИНА
# ============================================================
class OrderAdmin(ModelView, model=Order):
    """Админ-представление для заказов."""

    name = "Заказ"
    name_plural = "Заказы"
    icon = "fa-solid fa-shopping-bag"

    column_list = [
        Order.id, Order.user_id, Order.guest_email,
        Order.status, Order.total, Order.city,
        Order.created_at
    ]
    form_columns = [
        "user_id", "guest_email", "status",
        "street", "city", "total"
    ]
    column_searchable_list = [Order.guest_email, Order.id]
    column_sortable_list = [Order.created_at, Order.total, Order.status]
    column_default_sort = ("created_at", True)

    column_formatters = {
        Order.status: lambda m, v: m.status.value if m.status else "",
    }

    form_choices = {
        "status": [
            ("pending", "Ожидает обработки"),
            ("processing", "В обработке"),
            ("shipped", "Отправлен"),
            ("delivered", "Доставлен"),
            ("cancelled", "Отменён"),
        ],
    }

    can_create = False
    can_edit = True
    can_delete = True


class OrderItemAdmin(ModelView, model=OrderItem):
    """Админ-представление для позиций заказа."""

    name = "Позиция заказа"
    name_plural = "Позиции заказов"
    icon = "fa-solid fa-list"

    column_list = [
        OrderItem.id, OrderItem.order_id,
        OrderItem.variant_id, OrderItem.quantity,
        OrderItem.price_at_purchase
    ]

    can_create = False
    can_edit = False
    can_delete = False


class CartItemAdmin(ModelView, model=CartItem):
    """Админ-представление для корзины."""

    name = "Позиция корзины"
    name_plural = "Корзины"
    icon = "fa-solid fa-cart-shopping"

    column_list = [
        CartItem.id, CartItem.user_id,
        CartItem.variant_id, CartItem.quantity,
        CartItem.added_at
    ]

    can_create = False
    can_edit = False
    can_delete = True


# ============================================================
# WISHLIST И ПРИМЕРКА
# ============================================================
class WishlistAdmin(ModelView, model=Wishlist):
    """Админ-представление для списка желаний."""

    name = "Желание"
    name_plural = "Избранное"
    icon = "fa-solid fa-heart"

    column_list = [
        Wishlist.id, Wishlist.user_id,
        Wishlist.variant_id, Wishlist.created_at
    ]

    can_create = False
    can_edit = False
    can_delete = True


class TryOnSessionAdmin(ModelView, model=TryOnSession):
    """Админ-представление для сессий виртуальной примерки."""

    name = "Примерка"
    name_plural = "Сессии примерки"
    icon = "fa-solid fa-camera"

    column_list = [
        TryOnSession.id, TryOnSession.user_id,
        TryOnSession.variant_id, TryOnSession.status,
        TryOnSession.duration_ms, TryOnSession.created_at
    ]
    column_searchable_list = [TryOnSession.status]
    column_sortable_list = [TryOnSession.created_at, TryOnSession.status]
    column_default_sort = ("created_at", True)

    can_create = False
    can_edit = False
    can_delete = True


# ============================================================
# ПЛАТЕЖИ
# ============================================================
class PaymentAdmin(ModelView, model=Payment):
    """Админ-представление для платежей."""

    name = "Платёж"
    name_plural = "Платежи"
    icon = "fa-solid fa-credit-card"

    column_list = [
        Payment.id, Payment.order_id,
        Payment.yookassa_payment_id, Payment.amount,
        Payment.status, Payment.payment_method,
        Payment.is_test, Payment.created_at
    ]
    column_searchable_list = [Payment.yookassa_payment_id, Payment.order_id]
    column_sortable_list = [Payment.created_at, Payment.amount, Payment.status]
    column_default_sort = ("created_at", True)

    can_create = False
    can_edit = False
    can_delete = False
