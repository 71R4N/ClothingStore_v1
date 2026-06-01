from app.core.exceptions import UnauthorizedException, ConflictException

class InvalidCredentialsError(UnauthorizedException):
    detail = "Invalid email or password"

class EmailAlreadyExistsError(ConflictException):
    detail = "User with this email already exists"

class CaptchaRequiredError(Exception):
    pass

class InvalidCaptchaError(Exception):
    pass
