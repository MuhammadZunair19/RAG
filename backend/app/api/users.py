"""User management: list users (admin only)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models import User
from app.schemas.user import User as UserSchema
from app.core.dependencies import get_current_user, require_role

router = APIRouter()


@router.get("/", response_model=list[UserSchema])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    """List all users. Admin only."""
    result = await db.execute(select(User))
    return [UserSchema.model_validate(u) for u in result.scalars().all()]
