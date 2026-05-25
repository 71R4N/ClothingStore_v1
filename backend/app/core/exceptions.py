from fastapi import HTTPException, status

class BaseAppException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Internal server error"

    def __init__(self, detail: str | None = None, status_code: int | None = None):
        if detail:
            self.detail = detail
        if status_code:
            self.status_code = status_code
        super().__init__(status_code=self.status_code, detail=self.detail)

class NotFoundException(BaseAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found"

class ConflictException(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Conflict"

class ForbiddenException(BaseAppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Forbidden"

class UnauthorizedException(BaseAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Not authenticated"
