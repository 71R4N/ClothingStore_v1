import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import uuid

from app.core.database import Base, get_db_session
from app.main import app
from app.users.models import User
from app.catalog.models import Category, Product, ProductSize, ProductColor, ProductVariant


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine):
    async with async_engine.connect() as conn:
        trans = await conn.begin()

        session_factory = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint"
        )

        async with session_factory() as session:
            yield session

        await trans.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def mock_redis(monkeypatch):
    storage = {}

    class FakeRedis:
        async def connect(self): pass

        async def disconnect(self): pass

        async def get(self, key): return storage.get(key)

        async def setex(self, key, seconds, value): storage[key] = value

        async def delete(self, key): storage.pop(key, None)

    fake = FakeRedis()
    monkeypatch.setattr("app.core.redis_client.redis_client", fake)
    return fake


@pytest_asyncio.fixture
async def test_user(db_session) -> User:
    from passlib.context import CryptContext
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash=pwd_ctx.hash("TestPass123!"),
        first_name="Test",
        last_name="User",
        role="user",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_product(db_session) -> dict:
    category = Category(name="Test Cat", slug="test-cat")
    db_session.add(category)
    await db_session.flush()

    product = Product(
        name="Test Shirt",
        slug="test-shirt",
        category_id=category.id,
        is_active=True,
    )
    db_session.add(product)
    await db_session.flush()

    size = ProductSize(product_id=product.id, size_label="M")
    color = ProductColor(
        product_id=product.id, color_name="Black", color_hex="#000000"
    )
    db_session.add_all([size, color])
    await db_session.flush()

    variant = ProductVariant(
        product_id=product.id,
        size_id=size.id,
        color_id=color.id,
        sku="TEST-M-BLACK",
        stock_quantity=10,
        price=2990.00,
    )
    db_session.add(variant)
    await db_session.commit()
    await db_session.refresh(variant)

    return {
        "product": product,
        "variant": variant,
        "category": category,
    }


@pytest.fixture
def auth_headers(test_user) -> dict:
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
