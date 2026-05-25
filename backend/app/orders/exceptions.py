from app.core.exceptions import NotFoundException, ConflictException

class OrderNotFoundError(NotFoundException):
    detail = "Order not found"

class InvalidOrderStatusError(ConflictException):
    detail = "Invalid order status transition"

class PaymentFailedError(ConflictException):
    detail = "Payment failed"
    