from fastapi import HTTPException, status
from app.core.exceptions import UnauthorizedException, ConflictException


class InvalidCredentialsError(UnauthorizedException):
    detail = "Invalid email or password"


class EmailAlreadyExistsError(ConflictException):
    detail = "User with this email already exists"


class CaptchaRequiredError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Captcha required. Please complete the verification."
        )


class InvalidCaptchaError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid captcha. Please try again."
        )