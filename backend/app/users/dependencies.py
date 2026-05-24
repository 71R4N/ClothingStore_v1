from backend.app.core.database import SessionDbDep
from backend.app.users.repositories import UserRepo
from backend.app.users.services import UserService

def get_user_service(session: SessionDbDep) -> UserService:
    return UserService(UserRepo(session))
