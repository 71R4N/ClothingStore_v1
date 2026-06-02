#!/usr/bin/env python3
import asyncio
import logging
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.users.models import User
from app.catalog.models import Category, Product, ProductSize, ProductColor, ProductVariant
from app.cart.models import CartItem
from app.wishlist.models import Wishlist

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
        "category_slug": "shirts",
        "brand": "Classic Look",
        "is_active": True,
        "base_sku": "CST1001",
        "base_price": 2990,
        "sizes": ["S", "M", "L", "XL"],
        "size_stocks": {"S": 10, "M": 20, "L": 15, "XL": 5},
        "colors": [
            {"color_name": "Белый", "color_hex": "#FFFFFF"},
            {"color_name": "Синий", "color_hex": "#0000FF"},
        ],
    },
    {
        "name": "Платье летнее",
        "slug": "summer-dress",
        "description": "Легкое платье из вискозы",
        "category_slug": "dresses",
        "brand": "Summer Breeze",
        "is_active": True,
        "base_sku": "SDR1001",
        "base_price": 3990,
        "sizes": ["XS", "S", "M", "L"],
        "size_stocks": {"XS": 5, "S": 8, "M": 7, "L": 5},
        "colors": [
            {"color_name": "Розовый", "color_hex": "#FFC0CB"},
            {"color_name": "Желтый", "color_hex": "#FFFF00"},
        ],
    },
    {
        "name": "Кроссовки",
        "slug": "sport-sneakers",
        "description": "Удобные повседневные кроссовки",
        "category_slug": "sneakers",
        "brand": "Sportify",
        "is_active": True,
        "base_sku": "SNK1001",
        "base_price": 4990,
        "sizes": ["36", "37", "38", "39", "40", "41", "42"],
        "size_stocks": {"36": 5, "37": 8, "38": 10, "39": 7, "40": 5, "41": 3, "42": 2},
        "colors": [
            {"color_name": "Черный", "color_hex": "#000000"},
            {"color_name": "Белый", "color_hex": "#FFFFFF"},
        ],
    },
    {
        "name": "Сумка кожаная",
        "slug": "leather-bag",
        "description": "Натуральная кожа, вместительная",
        "category_slug": "bags",
        "brand": "Luxury Wear",
        "is_active": True,
        "base_sku": "BAG1001",
        "base_price": 7990,
        "sizes": ["One size"],
        "size_stocks": {"One size": 10},
        "colors": [
            {"color_name": "Коричневый", "color_hex": "#8B4513"},
            {"color_name": "Черный", "color_hex": "#000000"},
        ],
    },
]

USERS = [
    {
        "email": "admin@example.com",
        "password": "Admin123!",
        "first_name": "Admin",
        "last_name": "User",
        "phone": "+79001234567",
        "role": "admin",
        "is_active": True,
    },
    {
        "email": "user@example.com",
        "password": "User123!",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+79007654321",
        "role": "user",
        "is_active": True,
    },
]

WISHLIST_ITEMS = [
    {"product_slug": "sport-sneakers", "user_email": "user@example.com", "size": "38", "color": "Черный"},
]

CART_ITEMS = [
    {"product_slug": "classic-shirt", "user_email": "user@example.com", "quantity": 1, "size": "M", "color": "Белый"},
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


# ---------- Основная функция ----------
async def init_db():
    logger.info("Начинаем заполнение базы тестовыми данными...")
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # --- Категории ---
            category_map = {}
            for cat_data in CATEGORIES:
                exists = await get_category_by_slug(session, cat_data["slug"])
                if exists:
                    logger.info(f"Категория {cat_data['name']} уже существует")
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

            # --- Товары и Варианты ---
            for prod_data in PRODUCTS:
                category = category_map.get(prod_data["category_slug"]) or await get_category_by_slug(session, prod_data["category_slug"])
                if not category:
                    logger.warning(f"Категория {prod_data['category_slug']} не найдена")
                    continue

                product = await get_product_by_slug(session, prod_data["slug"])
                if product:
                    logger.info(f"Товар {prod_data['name']} уже существует")
                    continue

                product = Product(
                    name=prod_data["name"],
                    slug=prod_data["slug"],
                    description=prod_data.get("description"),
                    category_id=category.id,
                    brand=prod_data.get("brand"),
                    is_active=prod_data.get("is_active", True),
                )
                session.add(product)
                await session.flush()

                # Размеры
                size_objects = {}
                for size_label in prod_data.get("sizes", []):
                    size = ProductSize(
                        product_id=product.id,
                        size_label=size_label,
                    )
                    session.add(size)
                    await session.flush()
                    size_objects[size_label] = size

                # Цвета
                color_objects = {}
                for color_data in prod_data.get("colors", []):
                    color = ProductColor(
                        product_id=product.id,
                        color_name=color_data["color_name"],
                        color_hex=color_data["color_hex"],
                    )
                    session.add(color)
                    await session.flush()
                    color_objects[color_data["color_name"]] = color

                # Создаём варианты (каждая комбинация размер x цвет)
                for size_label, size_obj in size_objects.items():
                    for color_name, color_obj in color_objects.items():
                        sku = f"{prod_data['base_sku']}-{size_label}-{color_name.replace(' ', '')}"
                        variant = ProductVariant(
                            product_id=product.id,
                            size_id=size_obj.id,
                            color_id=color_obj.id,
                            sku=sku,
                            stock_quantity=prod_data.get("size_stocks", {}).get(size_label, 0),
                            price=prod_data["base_price"],
                            image_url=f"/images/products/{prod_data['slug']}-main.jpg",
                        )
                        session.add(variant)

                await session.flush()
                logger.info(f"Добавлен товар: {prod_data['name']} с {len(size_objects) * len(color_objects)} вариантами")

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

            # --- Wishlist ---
            for wish_data in WISHLIST_ITEMS:
                product = await get_product_by_slug(session, wish_data["product_slug"])
                user = user_objects.get(wish_data["user_email"])
                if not product or not user:
                    logger.warning(f"Не удалось добавить в вишлист: товар или пользователь не найдены")
                    continue

                size = wish_data.get("size", "")
                color = wish_data.get("color", "")

                # Ищем конкретный вариант через JOIN с размерами и цветами
                stmt = (
                    select(ProductVariant)
                    .join(ProductSize)
                    .join(ProductColor)
                    .where(
                        ProductVariant.product_id == product.id,
                        ProductSize.size_label == size,
                        ProductColor.color_name == color
                    )
                )
                result = await session.execute(stmt)
                variant = result.scalar_one_or_none()

                if not variant:
                    logger.warning(f"Не найден вариант ({size}, {color}) для wishlist: {product.name}")
                    continue

                # Проверяем, нет ли уже такой записи
                stmt = select(Wishlist).where(Wishlist.variant_id == variant.id, Wishlist.user_id == user.id)
                result = await session.execute(stmt)
                if not result.scalar_one_or_none():
                    wish = Wishlist(user_id=user.id, variant_id=variant.id)
                    session.add(wish)
                    logger.info(f"Вариант {variant.sku} добавлен в вишлист пользователя {user.email}")

            # --- Корзина ---
            for cart_data in CART_ITEMS:
                product = await get_product_by_slug(session, cart_data["product_slug"])
                user = user_objects.get(cart_data["user_email"])
                if not product or not user:
                    logger.warning(f"Не удалось добавить в корзину: товар или пользователь не найдены")
                    continue

                size = cart_data.get("size", "")
                color = cart_data.get("color", "")

                # Ищем вариант по размеру и цвету
                stmt = (
                    select(ProductVariant)
                    .join(ProductSize)
                    .join(ProductColor)
                    .where(
                        ProductVariant.product_id == product.id,
                        ProductSize.size_label == size,
                        ProductColor.color_name == color
                    )
                )
                result = await session.execute(stmt)
                variant = result.scalar_one_or_none()

                if not variant:
                    logger.warning(f"Не найден вариант ({size}, {color}) для корзины: {product.name}")
                    continue

                # Проверяем существующую запись
                stmt = select(CartItem).where(CartItem.user_id == user.id, CartItem.variant_id == variant.id)
                result = await session.execute(stmt)
                existing_item = result.scalar_one_or_none()

                if existing_item:
                    existing_item.quantity += cart_data["quantity"]
                    logger.info(f"Увеличено количество {variant.sku} в корзине")
                else:
                    cart_item = CartItem(
                        user_id=user.id,
                        variant_id=variant.id,
                        quantity=cart_data["quantity"],
                    )
                    session.add(cart_item)
                    logger.info(f"Вариант {variant.sku} добавлен в корзину пользователя {user.email}")

            logger.info("Заполнение базы данных успешно завершено!")


def main():
    asyncio.run(init_db())


if __name__ == "__main__":
    main()