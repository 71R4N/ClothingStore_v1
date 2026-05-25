from app.core.exceptions import NotFoundException

class CategoryNotFoundError(NotFoundException):
    detail = "Category not found"

class ProductNotFoundError(NotFoundException):
    detail = "Product not found"
