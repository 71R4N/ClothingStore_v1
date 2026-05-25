from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.database import Base
# Импортируем все модели, чтобы Alembic их видел
from app.users.models import User, UserSession
from app.catalog.models import Category, Product, ProductImage, ProductSize, ProductColor, SizeChart
from app.cart.models import CartItem
from app.orders.models import Address, Order, OrderItem, PaymentTransaction, Return
from app.tryon.models import TryOnSession
from app.reviews.models import Review
from app.notifications.models import Notification
from app.wishlist.models import Wishlist

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = settings.SYNC_POSTGRES_DB_URL
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    from sqlalchemy import create_engine
    connectable = create_engine(settings.SYNC_POSTGRES_DB_URL)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()