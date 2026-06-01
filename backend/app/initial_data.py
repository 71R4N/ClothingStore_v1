#!/usr/bin/env python3
import asyncio
import logging
import uuid
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.users.models import User, UserSession
from app.catalog.models import Category, Product, ProductImage, ProductSize, ProductColor, SizeChart
from app.cart.models import CartItem
from app.orders.models import Address, Order, OrderItem, PaymentTransaction, Return
from app.reviews.models import Review
from app.notifications.models import Notification
from app.wishlist.models import Wishlist
from app.tryon.models import TryOnSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------- Тестовые данные ----------
CATEGORIES = [
    {"name": "Мужская одежда", "slug": "men", "parent_slug": None},
    {"name": "Женская одежда", "slug": "women", "parent_slug": None},
    {"name": "Обувь", "slug": "shoes", "parent_slug": None},
    {"name": "Аксессуары", "slug": "accessories", "parent_slug": None},
    {"name": "Рубашки", "slug": "shirts", "parent_slug": "men"},
    {"name": "Платья", "slug": "dresses", "parent_slug": "women"},
    {"name": "Кроссовки", "slug": "sneakers", "parent_slug": "shoes"},
    {"name": "Сумки", "slug": "bags", "parent_slug": "accessories"},
]

PRODUCTS = [
    {
        "name": "Классическая рубашка",
        "slug": "classic-shirt",
        "description": "Хлопковая рубашка прямого кроя",
        "price": 2990,
        "old_price": None,
        "category_slug": "shirts",
        "brand": "Classic Look",
        "sku": "CST1001",
        "is_active": True,
        "sizes": [
            {"size_label": "S", "sku_variant": "CST1001-S", "stock_quantity": 10},
            {"size_label": "M", "sku_variant": "CST1001-M", "stock_quantity": 20},
            {"size_label": "L", "sku_variant": "CST1001-L", "stock_quantity": 15},
            {"size_label": "XL", "sku_variant": "CST1001-XL", "stock_quantity": 5},
        ],
        "colors": [
            {"color_name": "Белый", "color_hex": "#FFFFFF"},
            {"color_name": "Синий", "color_hex": "#0000FF"},
        ],
        "image_urls": [
            {"url": "/images/shirt1.jpg", "is_main": True, "sort_order": 0},
            {"url": "/images/shirt2.jpg", "is_main": False, "sort_order": 1},
        ],
    },
    {
        "name": "Платье летнее",
        "slug": "summer-dress",
        "description": "Легкое платье из вискозы",
        "price": 3990,
        "old_price": 4990,
        "category_slug": "dresses",
        "brand": "Summer Breeze",
        "sku": "SDR1001",
        "is_active": True,
        "sizes": [
            {"size_label": "XS", "sku_variant": "SDR1001-XS", "stock_quantity": 5},
            {"size_label": "S", "sku_variant": "SDR1001-S", "stock_quantity": 8},
            {"size_label": "M", "sku_variant": "SDR1001-M", "stock_quantity": 7},
            {"size_label": "L", "sku_variant": "SDR1001-L", "stock_quantity": 5},
        ],
        "colors": [
            {"color_name": "Розовый", "color_hex": "#FFC0CB"},
            {"color_name": "Желтый", "color_hex": "#FFFF00"},
        ],
        "image_urls": [
            {"url": "/images/dress1.jpg", "is_main": True, "sort_order": 0},
            {"url": "/images/dress2.jpg", "is_main": False, "sort_order": 1},
        ],
    },
    {
        "name": "Кроссовки",
        "slug": "sport-sneakers",
        "description": "Удобные повседневные кроссовки",
        "price": 4990,
        "old_price": None,
        "category_slug": "sneakers",
        "brand": "Sportify",
        "sku": "SNK1001",
        "is_active": True,
        "sizes": [
            {"size_label": "36", "sku_variant": "SNK1001-36", "stock_quantity": 5},
            {"size_label": "37", "sku_variant": "SNK1001-37", "stock_quantity": 8},
            {"size_label": "38", "sku_variant": "SNK1001-38", "stock_quantity": 10},
            {"size_label": "39", "sku_variant": "SNK1001-39", "stock_quantity": 7},
            {"size_label": "40", "sku_variant": "SNK1001-40", "stock_quantity": 5},
            {"size_label": "41", "sku_variant": "SNK1001-41", "stock_quantity": 3},
            {"size_label": "42", "sku_variant": "SNK1001-42", "stock_quantity": 2},
        ],
        "colors": [
            {"color_name": "Черный", "color_hex": "#000000"},
            {"color_name": "Белый", "color_hex": "#FFFFFF"},
        ],
        "image_urls": [
            {"url": "/images/sneakers1.jpg", "is_main": True, "sort_order": 0},
            {"url": "/images/sneakers2.jpg", "is_main": False, "sort_order": 1},
        ],
    },
    {
        "name": "Сумка кожаная",
        "slug": "leather-bag",
        "description": "Натуральная кожа, вместительная",
        "price": 7990,
        "old_price": 9990,
        "category_slug": "bags",
        "brand": "Luxury Wear",
        "sku": "BAG1001",
        "is_active": True,
        "sizes": [
            {"size_label": "One size", "sku_variant": "BAG1001-OS", "stock_quantity": 10},
        ],
        "colors": [
            {"color_name": "Коричневый", "color_hex": "#8B4513"},
            {"color_name": "Черный", "color_hex": "#000000"},
        ],
        "image_urls": [
            {"url": "/images/bag1.jpg", "is_main": True, "sort_order": 0},
            {"url": "/images/bag2.jpg", "is_main": False, "sort_order": 1},
        ],
    },
]

USERS = [
    {
        "email": "admin@example.com",
        "password": "admin123",
        "first_name": "Admin",
        "last_name": "User",
        "phone": "+79001234567",
        "role": "admin",
        "is_active": True,
    },
    {
        "email": "user@example.com",
        "password": "user123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+79007654321",
        "role": "user",
        "is_active": True,
    },
]

REVIEWS = [
    {"product_slug": "classic-shirt", "user_email": "user@example.com", "rating": 5, "comment": "Отличная рубашка!"},
    {"product_slug": "summer-dress", "user_email": "user@example.com", "rating": 4, "comment": "Красивое платье, но маломерит"},
]

WISHLIST_ITEMS = [
    {"product_slug": "sport-sneakers", "user_email": "user@example.com"},
]

CART_ITEMS = [
    {"product_slug": "classic-shirt", "user_email": "user@example.com", "quantity": 1, "size_label": "M", "color_name": "Белый"},
]

# ---------- Вспомогательные функции ----------
async def get_category_by_slug(session: AsyncSession, slug: str) -> Optional[Category]:
    result = await session.execute(select(Category).where(Category.slug == slug))
    return result.scalar_one_or_none()

async def get_product_by_slug(session: AsyncSession, slug: str) -> Optional[Product]:
    result = await session.execute(select(Product).where(Product.slug == slug))
    return result.scalar_one_or_none()

async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_size_by_label(session: AsyncSession, product_id: int, size_label: str) -> Optional[ProductSize]:
    result = await session.execute(
        select(ProductSize).where(ProductSize.product_id == product_id, ProductSize.size_label == size_label)
    )
    return result.scalar_one_or_none()

async def get_color_by_name(session: AsyncSession, product_id: int, color_name: str) -> Optional[ProductColor]:
    result = await session.execute(
        select(ProductColor).where(ProductColor.product_id == product_id, ProductColor.color_name == color_name)
    )
    return result.scalar_one_or_none()

# ---------- Основная функция ----------
async def init_db():
    logger.info("Начинаем заполнение базы тестовыми данными...")
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # --- Категории (с parent_id) ---
            category_map = {}
            for cat_data in CATEGORIES:
                exists = await get_category_by_slug(session, cat_data["slug"])
                if exists:
                    logger.info(f"Категория {cat_data['name']} уже существует, пропускаем")
                    category_map[cat_data["slug"]] = exists
                    continue

                parent = None
                if cat_data["parent_slug"]:
                    parent = category_map.get(cat_data["parent_slug"]) or await get_category_by_slug(session, cat_data["parent_slug"])
                category = Category(
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                    parent_id=parent.id if parent else None,
                )
                session.add(category)
                await session.flush()
                category_map[cat_data["slug"]] = category
                logger.info(f"Добавлена категория: {cat_data['name']}")

            # --- Товары ---
            for prod_data in PRODUCTS:
                category = category_map.get(prod_data["category_slug"]) or await get_category_by_slug(session, prod_data["category_slug"])
                if not category:
                    logger.warning(f"Категория {prod_data['category_slug']} не найдена, пропускаем товар {prod_data['name']}")
                    continue

                product = await get_product_by_slug(session, prod_data["slug"])
                if product:
                    logger.info(f"Товар {prod_data['name']} уже существует, пропускаем")
                    continue

                product = Product(
                    name=prod_data["name"],
                    slug=prod_data["slug"],
                    description=prod_data.get("description"),
                    price=prod_data["price"],
                    old_price=prod_data.get("old_price"),
                    category_id=category.id,
                    brand=prod_data.get("brand"),
                    sku=prod_data["sku"],
                    is_active=prod_data.get("is_active", True),
                )
                session.add(product)
                await session.flush()

                # Размеры
                for size_data in prod_data.get("sizes", []):
                    size = ProductSize(
                        product_id=product.id,
                        size_label=size_data["size_label"],
                        sku_variant=size_data["sku_variant"],
                        stock_quantity=size_data["stock_quantity"],
                    )
                    session.add(size)

                # Цвета
                for color_data in prod_data.get("colors", []):
                    color = ProductColor(
                        product_id=product.id,
                        color_name=color_data["color_name"],
                        color_hex=color_data["color_hex"],
                    )
                    session.add(color)

                # Изображения
                for img_data in prod_data.get("image_urls", []):
                    img = ProductImage(
                        product_id=product.id,
                        url=img_data["url"],
                        is_main=img_data.get("is_main", False),
                        sort_order=img_data.get("sort_order", 0),
                    )
                    session.add(img)

                logger.info(f"Добавлен товар: {prod_data['name']}")

            # --- Пользователи ---
            user_objects = {}
            for user_data in USERS:
                existing = await get_user_by_email(session, user_data["email"])
                if existing:
                    logger.info(f"Пользователь {user_data['email']} уже существует")
                    user_objects[user_data["email"]] = existing
                    continue

                hashed_password = pwd_context.hash(user_data["password"])
                user = User(
                    email=user_data["email"],
                    password_hash=hashed_password,
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    phone=user_data.get("phone"),
                    role=user_data["role"],
                    is_active=user_data["is_active"],
                )
                session.add(user)
                await session.flush()
                user_objects[user_data["email"]] = user
                logger.info(f"Создан пользователь: {user_data['email']}")

            # --- Отзывы ---
            for rev_data in REVIEWS:
                product = await get_product_by_slug(session, rev_data["product_slug"])
                user = user_objects.get(rev_data["user_email"])
                if not product or not user:
                    logger.warning(f"Не удалось создать отзыв: товар {rev_data['product_slug']} или пользователь {rev_data['user_email']} не найдены")
                    continue

                # Проверяем, нет ли уже отзыва от этого пользователя на этот товар
                stmt = select(Review).where(Review.product_id == product.id, Review.user_id == user.id)
                result = await session.execute(stmt)
                if result.scalar_one_or_none():
                    logger.info(f"Отзыв от {user.email} на {product.name} уже есть")
                    continue

                review = Review(
                    product_id=product.id,
                    user_id=user.id,
                    rating=rev_data["rating"],
                    comment=rev_data.get("comment"),
                )
                session.add(review)
                logger.info(f"Добавлен отзыв от {user.email} на {product.name}")

            # --- Список желаний ---
            for wish_data in WISHLIST_ITEMS:
                product = await get_product_by_slug(session, wish_data["product_slug"])
                user = user_objects.get(wish_data["user_email"])
                if not product or not user:
                    logger.warning(f"Не удалось добавить в вишлист: товар {wish_data['product_slug']} или пользователь {wish_data['user_email']} не найдены")
                    continue

                stmt = select(Wishlist).where(Wishlist.product_id == product.id, Wishlist.user_id == user.id)
                result = await session.execute(stmt)
                if not result.scalar_one_or_none():
                    wish = Wishlist(user_id=user.id, product_id=product.id)
                    session.add(wish)
                    logger.info(f"Товар {product.name} добавлен в вишлист пользователя {user.email}")

            # --- Корзина ---
            for cart_data in CART_ITEMS:
                product = await get_product_by_slug(session, cart_data["product_slug"])
                user = user_objects.get(cart_data["user_email"])
                if not product or not user:
                    logger.warning(f"Не удалось добавить в корзину: товар {cart_data['product_slug']} или пользователь {cart_data['user_email']} не найдены")
                    continue

                size = None
                if cart_data.get("size_label"):
                    size = await get_size_by_label(session, product.id, cart_data["size_label"])
                color = None
                if cart_data.get("color_name"):
                    color = await get_color_by_name(session, product.id, cart_data["color_name"])

                # Проверяем, есть ли уже такой товар в корзине
                stmt = select(CartItem).where(
                    CartItem.user_id == user.id,
                    CartItem.product_id == product.id,
                    CartItem.size_id == (size.id if size else None),
                    CartItem.color_id == (color.id if color else None)
                )
                result = await session.execute(stmt)
                existing_item = result.scalar_one_or_none()
                if existing_item:
                    logger.info(f"Товар {product.name} уже в корзине пользователя {user.email}, увеличиваем количество")
                    existing_item.quantity += cart_data["quantity"]
                else:
                    cart_item = CartItem(
                        user_id=user.id,
                        product_id=product.id,
                        size_id=size.id if size else None,
                        color_id=color.id if color else None,
                        quantity=cart_data["quantity"],
                    )
                    session.add(cart_item)
                    logger.info(f"Товар {product.name} добавлен в корзину пользователя {user.email}")

            logger.info("Заполнение базы данных успешно завершено!")

def main():
    asyncio.run(init_db())

if __name__ == "__main__":
    main()