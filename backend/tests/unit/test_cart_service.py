# backend/tests/unit/test_cart_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from app.cart.services import CartService
from app.cart.schemas import CartItemCreate
from app.cart.exceptions import OutOfStockError, CartItemNotFoundError
from app.cart.models import CartItem


class TestCartService:
    """Модульные тесты сервиса корзины."""

    @pytest.mark.asyncio
    async def test_add_to_cart_new_item(self):
        """Добавление нового товара в пустую корзину."""
        cart_repo = MagicMock()
        variant_repo = MagicMock()

        # Явно указываем класс модели для корректной работы SQLAlchemy select()
        cart_repo.model = CartItem

        variant = MagicMock()
        variant.stock_quantity = 10
        variant_repo.read_by_id = AsyncMock(return_value=variant)
        cart_repo.find_item = AsyncMock(return_value=None)

        created_item = MagicMock(id=uuid4())
        cart_repo.create_item = AsyncMock(return_value=created_item)

        # Настраиваем мок сессии и результата execute
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = created_item
        cart_repo.session = MagicMock()
        cart_repo.session.execute = AsyncMock(return_value=mock_result)

        service = CartService(cart_repo, variant_repo)
        data = CartItemCreate(variant_id=1, quantity=2)
        result = await service.add_to_cart(uuid4(), None, data)

        assert result.id == created_item.id
        cart_repo.create_item.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_add_to_cart_out_of_stock(self):
        """Попытка добавить больше товара, чем есть на складе."""
        cart_repo = MagicMock()
        variant_repo = MagicMock()

        variant = MagicMock()
        variant.stock_quantity = 1
        variant_repo.read_by_id = AsyncMock(return_value=variant)
        cart_repo.find_item = AsyncMock(return_value=None)

        service = CartService(cart_repo, variant_repo)
        data = CartItemCreate(variant_id=1, quantity=5)

        with pytest.raises(OutOfStockError):
            await service.add_to_cart(uuid4(), None, data)

    @pytest.mark.asyncio
    async def test_add_to_cart_accumulate_quantity(self):
        """Повторное добавление того же товара увеличивает количество."""
        cart_repo = MagicMock()
        variant_repo = MagicMock()

        # Явно указываем класс модели
        cart_repo.model = CartItem

        variant = MagicMock()
        variant.stock_quantity = 20
        variant_repo.read_by_id = AsyncMock(return_value=variant)

        existing_item = MagicMock(id=uuid4(), quantity=3)
        cart_repo.find_item = AsyncMock(return_value=existing_item)

        updated_item = MagicMock(id=existing_item.id, quantity=5)
        cart_repo.update = AsyncMock(return_value=updated_item)

        # Настраиваем мок сессии и результата execute
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = updated_item
        cart_repo.session = MagicMock()
        cart_repo.session.execute = AsyncMock(return_value=mock_result)

        service = CartService(cart_repo, variant_repo)
        data = CartItemCreate(variant_id=1, quantity=2)
        result = await service.add_to_cart(uuid4(), None, data)

        assert result.quantity == 5
