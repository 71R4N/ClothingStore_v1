from app.core.exceptions import NotFoundException, ConflictException

class CartItemNotFoundError(NotFoundException):
    detail = "Cart item not found"

class OutOfStockError(ConflictException):
    detail = "Requested quantity exceeds available stock"
    