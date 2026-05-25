#!/usr/bin/env python3
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.users.models import User, UserSession
from app.catalog.models import Category, Product, ProductImage, ProductSize, ProductColor
from app.orders.models import Address, Order   # <--- добавить
from app.cart.models import CartItem
from app.wishlist.models import Wishlist
from app.reviews.models import Review
from app.notifications.models import Notification
from app.tryon.models import TryOnSession
# Добавьте другие модели, если нужны (Order, PaymentTransaction и т.п.)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------- Тестовые данные ----------
CATEGORIES = [
    {"name": "Мужская одежда", "slug": "men"},
    {"name": "Женская одежда", "slug": "women"},
    {"name": "Обувь", "slug": "shoes"},
    {"name": "Аксессуары", "slug": "accessories"},
]

PRODUCTS = [
    {
        "name": "Классическая рубашка",
        "slug": "classic-shirt",
        "description": "Хлопковая рубашка прямого кроя",
        "price": 2990,
        "category_slug": "men",
        "stock": 50,
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Белый", "Синий"],
        "image_urls": ["/images/shirt1.jpg", "/images/shirt2.jpg"],
    },
    {
        "name": "Платье летнее",
        "slug": "summer-dress",
        "description": "Легкое платье из вискозы",
        "price": 3990,
        "category_slug": "women",
        "stock": 30,
        "sizes": ["XS", "S", "M", "L"],
        "colors": ["Розовый", "Желтый"],
        "image_urls": ["/images/dress1.jpg", "/images/dress2.jpg"],
    },
    {
        "name": "Кроссовки",
        "slug": "sneakers",
        "description": "Удобные повседневные кроссовки",
        "price": 4990,
        "category_slug": "shoes",
        "stock": 40,
        "sizes": ["36", "37", "38", "39", "40", "41", "42"],
        "colors": ["Черный", "Белый", "Серый"],
        "image_urls": ["/images/sneakers1.jpg", "/images/sneakers2.jpg"],
    },
    {
        "name": "Сумка кожаная",
        "slug": "leather-bag",
        "description": "Натуральная кожа, вместительная",
        "price": 7990,
        "category_slug": "accessories",
        "stock": 15,
        "sizes": ["One size"],
        "colors": ["Коричневый", "Черный"],
        "image_urls": ["/images/bag1.jpg", "/images/bag2.jpg"],
    },
]

USERS = [
    {
        "email": "admin@example.com",
        "password": "admin123",
        "full_name": "Admin User",
        "is_superuser": True,
        "is_active": True,
    },
    {
        "email": "user@example.com",
        "password": "user123",
        "full_name": "Test User",
        "is_superuser": False,
        "is_active": True,
    },
]

REVIEWS = [
    {"product_slug": "classic-shirt", "user_email": "user@example.com", "rating": 5, "comment": "Отличная рубашка!"},
    {"product_slug": "summer-dress", "user_email": "user@example.com", "rating": 4, "comment": "Красивое платье, но маломерит"},
]

WISHLIST_ITEMS = [
    {"product_slug": "sneakers", "user_email": "user@example.com"},
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


# ---------- Основная функция заполнения ----------
async def init_db():
    logger.info("Начинаем заполнение базы тестовыми данными...")
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # --- Категории ---
            for cat_data in CATEGORIES:
                exists = await get_category_by_slug(session, cat_data["slug"])
                if not exists:
                    category = Category(name=cat_data["name"], slug=cat_data["slug"])
                    session.add(category)
                    logger.info(f"Добавлена категория: {cat_data['name']}")
                else:
                    logger.info(f"Категория {cat_data['name']} уже существует, пропускаем")

            await session.flush()

            # --- Товары ---
            for prod_data in PRODUCTS:
                category = await get_category_by_slug(session, prod_data["category_slug"])
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
                    description=prod_data["description"],
                    price=prod_data["price"],
                    category_id=category.id,
                    stock=prod_data["stock"],
                )
                session.add(product)
                await session.flush()

                # Размеры
                for size_name in prod_data["sizes"]:
                    size = ProductSize(product_id=product.id, size=size_name)
                    session.add(size)

                # Цвета
                for color_name in prod_data["colors"]:
                    color = ProductColor(product_id=product.id, color=color_name)
                    session.add(color)

                # Изображения
                for url in prod_data["image_urls"]:
                    img = ProductImage(product_id=product.id, image_url=url, is_primary=(url == prod_data["image_urls"][0]))
                    session.add(img)

                logger.info(f"Добавлен товар: {prod_data['name']}")

            # --- Пользователи ---
            for user_data in USERS:
                existing = await get_user_by_email(session, user_data["email"])
                if existing:
                    logger.info(f"Пользователь {user_data['email']} уже существует")
                    continue

                hashed_password = pwd_context.hash(user_data["password"])
                user = User(
                    email=user_data["email"],
                    hashed_password=hashed_password,
                    full_name=user_data.get("full_name"),
                    is_superuser=user_data["is_superuser"],
                    is_active=user_data["is_active"],
                )
                session.add(user)
                logger.info(f"Создан пользователь: {user_data['email']}")

            await session.flush()

            # --- Отзывы ---
            for rev_data in REVIEWS:
                product = await get_product_by_slug(session, rev_data["product_slug"])
                user = await get_user_by_email(session, rev_data["user_email"])
                if not product or not user:
                    logger.warning(f"Не удалось создать отзыв: товар {rev_data['product_slug']} или пользователь {rev_data['user_email']} не найдены")
                    continue

                # Проверим, нет ли уже отзыва от этого пользователя на этот товар
                stmt = select(Review).where(Review.product_id == product.id, Review.user_id == user.id)
                result = await session.execute(stmt)
                existing_review = result.scalar_one_or_none()
                if existing_review:
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
                user = await get_user_by_email(session, wish_data["user_email"])
                if not product or not user:
                    logger.warning(f"Не удалось добавить в вишлист: товар {wish_data['product_slug']} или пользователь {wish_data['user_email']} не найдены")
                    continue

                stmt = select(Wishlist).where(Wishlist.product_id == product.id, Wishlist.user_id == user.id)
                result = await session.execute(stmt)
                exists = result.scalar_one_or_none()
                if not exists:
                    wish = Wishlist(user_id=user.id, product_id=product.id)
                    session.add(wish)
                    logger.info(f"Товар {product.name} добавлен в вишлист пользователя {user.email}")

            # --- Корзина (несколько товаров) ---
            # Добавим для пользователя user@example.com пару товаров
            user = await get_user_by_email(session, "user@example.com")
            if user:
                # Найдём товары
                shirt = await get_product_by_slug(session, "classic-shirt")
                sneakers = await get_product_by_slug(session, "sneakers")
                if shirt:
                    # Проверим, есть ли уже этот товар в корзине
                    stmt = select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == shirt.id)
                    result = await session.execute(stmt)
                    if not result.scalar_one_or_none():
                        cart_item = CartItem(user_id=user.id, product_id=shirt.id, quantity=1)
                        session.add(cart_item)
                        logger.info(f"Рубашка добавлена в корзину пользователя {user.email}")
                if sneakers:
                    stmt = select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == sneakers.id)
                    result = await session.execute(stmt)
                    if not result.scalar_one_or_none():
                        cart_item = CartItem(user_id=user.id, product_id=sneakers.id, quantity=2)
                        session.add(cart_item)
                        logger.info(f"Кроссовки добавлены в корзину пользователя {user.email}")

            logger.info("Заполнение базы данных успешно завершено!")


def main():
    asyncio.run(init_db())


if __name__ == "__main__":
    main()