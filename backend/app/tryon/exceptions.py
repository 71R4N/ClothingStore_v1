from app.core.exceptions import NotFoundException, ConflictException

class TryOnSessionNotFoundError(NotFoundException):
    detail = "Try-on session not found"

class TryOnProcessingError(ConflictException):
    detail = "Error processing try-on request"
    