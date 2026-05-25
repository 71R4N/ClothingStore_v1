from fastapi import APIRouter, Depends
from app.reviews.schemas import ReviewCreate, ReviewUpdate, ReviewRead
from app.reviews.dependencies import ReviewServiceDep
from app.reviews.services import ReviewService
from app.auth.dependencies import get_current_user, CurrentUserDep
from typing import Annotated
from uuid import UUID

from fastapi.openapi.models import Response

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/", response_model=ReviewRead, status_code=201)
async def create_review(
    data: ReviewCreate,
    review_svc: ReviewServiceDep,
    current_user: CurrentUserDep
):
    return await review_svc.create(str(current_user.id), data)

@router.get("/product/{product_id}", response_model=list[ReviewRead])
async def product_reviews(product_id: int, review_svc: ReviewServiceDep, skip: int = 0, limit: int = 20):
    return await review_svc.list_for_product(product_id, skip, limit)

@router.patch("/{review_id}", response_model=ReviewRead)
async def update_review(
    review_id: UUID,
    data: ReviewUpdate,
    review_svc: ReviewServiceDep,
    current_user: CurrentUserDep
):
    return await review_svc.update(str(review_id), str(current_user.id), data)

@router.delete("/{review_id}", status_code=204)
async def delete_review(
    review_id: UUID,
    review_svc: ReviewServiceDep,
    current_user: CurrentUserDep
):
    await review_svc.delete(str(review_id), str(current_user.id))
    return Response(status_code=204)
