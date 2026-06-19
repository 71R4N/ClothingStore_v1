from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.tryon.schemas import TryOnRequest, TryOnSessionRead
from app.tryon.dependencies import TryOnServiceDep
from app.auth.dependencies import OptionalUserDep
from app.catalog.repositories import ProductVariantRepo
from app.catalog.models import Product
from app.core.database import SessionDbDep
from uuid import UUID
from app.core.exceptions import ForbiddenException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/try-on", tags=["tryon"])


@router.post("/sessions", response_model=TryOnSessionRead, status_code=201)
async def create_tryon(
        data: TryOnRequest,
        tryon_svc: TryOnServiceDep,
        current_user: OptionalUserDep,
        session: SessionDbDep,
):
    variant_repo = ProductVariantRepo(session)
    variant = await variant_repo.read_by_id(data.variant_id)
    if not variant:
        from app.catalog.exceptions import ProductNotFoundError
        raise ProductNotFoundError(detail="Product variant not found")

    garment_image_url = variant.image_url or data.garment_image_url

    stmt = select(Product).where(Product.id == variant.product_id).options(
        selectinload(Product.category)
    )
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    category = data.category
    if not category and product and product.category:
        category = product.category.tryon_category or "upper_body"
    elif not category:
        category = "upper_body"

    user_id = current_user.id if current_user else None

    request_data = TryOnRequest(
        variant_id=data.variant_id,
        person_image_url=data.person_image_url,
        garment_image_url=garment_image_url,
        mask_image_url=data.mask_image_url,
        category=category
    )

    session_obj = await tryon_svc.create_session(user_id, request_data)

    try:
        from worker.tasks.tryon import process_tryon_session
        process_tryon_session.delay(str(session_obj.id))
        logger.info(f"Celery task queued for session {session_obj.id}")
    except Exception as e:
        logger.warning(f"Celery not available, processing synchronously: {e}")
        await tryon_svc.process_session(session_obj.id)

    session_obj = await tryon_svc.get_session(session_obj.id)
    return session_obj


@router.get("/sessions/{session_id}", response_model=TryOnSessionRead)
async def get_session(
        session_id: UUID,
        tryon_svc: TryOnServiceDep,
        current_user: OptionalUserDep
):
    session_obj = await tryon_svc.get_session(session_id)
    if current_user:
        if session_obj.user_id and session_obj.user_id != current_user.id:
            raise ForbiddenException()
    elif session_obj.user_id:
        raise ForbiddenException()
    return session_obj


@router.get("/sessions", response_model=list[TryOnSessionRead])
async def list_sessions(
        tryon_svc: TryOnServiceDep,
        current_user: OptionalUserDep,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100)
):
    if current_user:
        return await tryon_svc.get_user_sessions(current_user.id, skip, limit)
    return []