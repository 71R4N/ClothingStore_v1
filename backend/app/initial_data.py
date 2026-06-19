# backend/app/initial_data.py
# !/usr/bin/env python3
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

# ---------- Тестовые данные: Расширенный каталог ----------
CATEGORIES = [
    # Корневые категории
    {"name": "Мужская одежда", "slug": "men", "parent_slug": None, "tryon_category": None},
    {"name": "Женская одежда", "slug": "women", "parent_slug": None, "tryon_category": None},
    {"name": "Обувь", "slug": "shoes", "parent_slug": None, "tryon_category": None},
    {"name": "Аксессуары", "slug": "accessories", "parent_slug": None, "tryon_category": None},

    # Мужская одежда (Верх и Низ)
    {"name": "Рубашки", "slug": "men-shirts", "parent_slug": "men", "tryon_category": "upper_body"},
    {"name": "Футболки", "slug": "men-tshirts", "parent_slug": "men", "tryon_category": "upper_body"},
    {"name": "Худи и свитшоты", "slug": "men-hoodies", "parent_slug": "men", "tryon_category": "upper_body"},
    {"name": "Куртки", "slug": "men-jackets", "parent_slug": "men", "tryon_category": "upper_body"},
    {"name": "Брюки", "slug": "men-pants", "parent_slug": "men", "tryon_category": "lower_body"},
    {"name": "Джинсы", "slug": "men-jeans", "parent_slug": "men", "tryon_category": "lower_body"},

    # Женская одежда (Платья, Верх и Низ)
    {"name": "Платья", "slug": "women-dresses", "parent_slug": "women", "tryon_category": "dress"},
    {"name": "Юбки", "slug": "women-skirts", "parent_slug": "women", "tryon_category": "lower_body"},
    {"name": "Брюки и джинсы", "slug": "women-pants", "parent_slug": "women", "tryon_category": "lower_body"},
    {"name": "Свитеры и джемперы", "slug": "women-sweaters", "parent_slug": "women", "tryon_category": "upper_body"},

    # Обувь и Аксессуары (Примерка не поддерживается)
    {"name": "Кроссовки", "slug": "sneakers", "parent_slug": "shoes", "tryon_category": None},
    {"name": "Ботинки", "slug": "boots", "parent_slug": "shoes", "tryon_category": None},
    {"name": "Сумки и рюкзаки", "slug": "bags", "parent_slug": "accessories", "tryon_category": None},
]

PRODUCTS = [
    # --- МУЖСКАЯ ОДЕЖДА ---
    {
        "name": "Классическая хлопковая рубашка", "slug": "classic-shirt",
        "description": "Приталенная рубашка из 100% хлопка, идеальна для офиса и повседневной носки.",
        "category_slug": "men-shirts", "brand": "Classic Look", "is_active": True,
        "base_sku": "MSH1001", "base_price": 2990,
        "sizes": ["S", "M", "L", "XL"], "size_stocks": {"S": 10, "M": 20, "L": 15, "XL": 5},
        "colors": [{"color_name": "Черный", "color_hex": "#000000"}, {"color_name": "Голубой", "color_hex": "#ADD8E6"}],
    },
    {
        "name": "Базовая футболка оверсайз", "slug": "basic-tee",
        "description": "Мягкая футболка свободного кроя из плотного хлопка.",
        "category_slug": "men-tshirts", "brand": "Street Wear", "is_active": True,
        "base_sku": "MTS1002", "base_price": 1490,
        "sizes": ["S", "M", "L", "XL", "XXL"], "size_stocks": {"S": 15, "M": 30, "L": 25, "XL": 10, "XXL": 5},
        "colors": [{"color_name": "Черный", "color_hex": "#000000"}, {"color_name": "Серый", "color_hex": "#808080"}, {"color_name": "Бежевый", "color_hex": "#F5F5DC"}],
    },
    {
        "name": "Худи с круглым вырезом", "slug": "urban-hoodie",
        "description": "Теплое худи из футера с начесом, удобный карман-кенгуру.",
        "category_slug": "men-hoodies", "brand": "Urban Style", "is_active": True,
        "base_sku": "MHD1003", "base_price": 3490,
        "sizes": ["M", "L", "XL"], "size_stocks": {"M": 12, "L": 18, "XL": 8},
        "colors": [{"color_name": "Черный", "color_hex": "#000000"}, {"color_name": "Хаки", "color_hex": "#808000"}],
    },
    {
        "name": "Прямые джинсы", "slug": "straight-jeans",
        "description": "Классические джинсы прямого кроя из плотного денима.",
        "category_slug": "men-jeans", "brand": "Denim Co.", "is_active": True,
        "base_sku": "MJN1004", "base_price": 4590,
        "sizes": ["28", "30", "32", "34", "36"], "size_stocks": {"28": 5, "30": 10, "32": 15, "34": 10, "36": 5},
        "colors": [{"color_name": "Индиго", "color_hex": "#4B0082"}, {"color_name": "Светло-голубой", "color_hex": "#ADD8E6"}],
    },
    {
        "name": "Зимняя куртка-пуховик", "slug": "winter-parka",
        "description": "Теплая куртка с синтетическим утеплителем, водоотталкивающая ткань.",
        "category_slug": "men-jackets", "brand": "North Explorer", "is_active": True,
        "base_sku": "MJK1005", "base_price": 8990,
        "sizes": ["M", "L", "XL"], "size_stocks": {"M": 5, "L": 8, "XL": 4},
        "colors": [{"color_name": "Черный", "color_hex": "#000000"}, {"color_name": "Темно-зеленый", "color_hex": "#006400"}],
    },

    # --- ЖЕНСКАЯ ОДЕЖДА ---
    {
        "name": "Летнее платье с цветочным принтом", "slug": "floral-dress",
        "description": "Легкое платье из вискозы, длина миди.",
        "category_slug": "women-dresses", "brand": "Summer Breeze", "is_active": True,
        "base_sku": "WDR1006", "base_price": 3990,
        "sizes": ["XS", "S", "M", "L"], "size_stocks": {"XS": 4, "S": 8, "M": 10, "L": 6},
        "colors": [{"color_name": "Голубой", "color_hex": "#00B7EB"}, {"color_name": "Мятный фон", "color_hex": "#98FF98"}],
    },
    {
        "name": "Вечернее платье-миди", "slug": "evening-dress",
        "description": "Элегантное облегающее платье из бархата.",
        "category_slug": "women-dresses", "brand": "Elegance", "is_active": True,
        "base_sku": "WDR1007", "base_price": 6990,
        "sizes": ["XS", "S", "M"], "size_stocks": {"XS": 2, "S": 5, "M": 4},
        "colors": [{"color_name": "Черный", "color_hex": "#000000"}, {"color_name": "Изумрудный", "color_hex": "#50C878"}],
    },
    {
        "name": "Юбка-плиссе", "slug": "pleated-skirt",
        "description": "Воздушная юбка-плиссе с эластичным поясом.",
        "category_slug": "women-skirts", "brand": "Chic Style", "is_active": True,
        "base_sku": "WSK1008", "base_price": 2490,
        "sizes": ["XS", "S", "M", "L"], "size_stocks": {"XS": 6, "S": 12, "M": 10, "L": 5},
        "colors": [{"color_name": "Бежевый", "color_hex": "#F5F5DC"}, {"color_name": "Черный", "color_hex": "#000000"}],
    },
    {
        "name": "Кашемировый джемпер", "slug": "cashmere-sweater",
        "description": "Мягкий джемпер из смеси кашемира и шерсти, круглый вырез.",
        "category_slug": "women-sweaters", "brand": "Cozy Knit", "is_active": True,
        "base_sku": "WSW1009", "base_price": 5490,
        "sizes": ["S", "M", "L"], "size_stocks": {"S": 8, "M": 15, "L": 7},
        "colors": [{"color_name": "Молочный", "color_hex": "#FDFFF5"}, {"color_name": "Пудровый", "color_hex": "#E8C3C3"}],
    },
    {
        "name": "Брюки", "slug": "trousers-slim",
        "description": "Женские брюки зауженного кроя из хлопкового твила.",
        "category_slug": "women-pants", "brand": "Daily Fit", "is_active": True,
        "base_sku": "WPN1010", "base_price": 3290,
        "sizes": ["34", "36", "38", "40", "42"], "size_stocks": {"34": 5, "36": 10, "38": 12, "40": 8, "42": 4},
        "colors": [{"color_name": "Оливковый", "color_hex": "#808000"}, {"color_name": "Темно-синий", "color_hex": "#00008B"}],
    },

    # --- ОБУВЬ И АКСЕССУАРЫ (Примерка недоступна) ---
    {
        "name": "Спортивные кроссовки", "slug": "sport-sneakers",
        "description": "Легкие кроссовки с амортизирующей подошвой для бега и зала.",
        "category_slug": "sneakers", "brand": "Sportify", "is_active": True,
        "base_sku": "SH1011", "base_price": 5990,
        "sizes": ["36", "37", "38", "39", "40", "41", "42", "43"],
        "size_stocks": {"36": 4, "37": 6, "38": 8, "39": 10, "40": 10, "41": 6, "42": 4, "43": 2},
        "colors": [{"color_name": "Белый", "color_hex": "#FFFFFF"}, {"color_name": "Черный", "color_hex": "#000000"}],
    },
    {
        "name": "Кожаная сумка", "slug": "leather-bag",
        "description": "Вместительная сумка из натуральной кожи.",
        "category_slug": "bags", "brand": "Luxury Wear", "is_active": True,
        "base_sku": "AC1013", "base_price": 12990,
        "sizes": ["One size"], "size_stocks": {"One size": 15},
        "colors": [{"color_name": "Черный", "color_hex": "#000000"}],
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
                    tryon_category=cat_data.get("tryon_category")  # Сохранение типа для CatVTON
                )
                session.add(category)
                await session.flush()
                category_map[cat_data["slug"]] = category
                logger.info(f"Добавлена категория: {cat_data['name']} (tryon: {cat_data.get('tryon_category')})")

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
                    size = ProductSize(product_id=product.id, size_label=size_label)
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

                # Создание вариантов (каждая комбинация размер x цвет)
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

    logger.info("Заполнение базы данных успешно завершено!")


def main():
    asyncio.run(init_db())


if __name__ == "__main__":
    main()