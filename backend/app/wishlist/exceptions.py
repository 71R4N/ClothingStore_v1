from app.core.exceptions import NotFoundException, ConflictException


class WishlistItemNotFoundError(NotFoundException):
    detail = "Wishlist item not found"


class WishlistItemAlreadyExistsError(ConflictException):
    detail = "Item already in wishlist"