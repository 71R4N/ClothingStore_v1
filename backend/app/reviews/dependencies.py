from typing import Annotated

from fastapi import Depends
from app.core.database import SessionDbDep
from app.reviews.repositories import ReviewRepo
from app.reviews.services import ReviewService

def get_review_service(session: SessionDbDep) -> ReviewService:
    return ReviewService(ReviewRepo(session))

ReviewServiceDep = Annotated[ReviewService, Depends(get_review_service)]
