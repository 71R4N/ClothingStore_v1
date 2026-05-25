from typing import Annotated

from fastapi import Depends
from app.core.database import SessionDbDep
from app.tryon.repositories import TryOnRepo
from app.tryon.services import TryOnService

def get_tryon_service(session: SessionDbDep) -> TryOnService:
    return TryOnService(TryOnRepo(session))

TryOnServiceDep = Annotated[TryOnService, Depends(get_tryon_service)]
