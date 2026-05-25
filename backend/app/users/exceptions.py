from app.core.exceptions import NotFoundException

class UserNotFoundError(NotFoundException):
    detail = "User not found"
