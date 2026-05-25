from app.core.exceptions import NotFoundException

class ReviewNotFoundError(NotFoundException):
    detail = "Review not found"
    