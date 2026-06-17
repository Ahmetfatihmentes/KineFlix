import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import ValidationException
from backend.core.security import get_password_hash
from backend.models.user import User
from backend.schemas.user import UserCreate


logger = logging.getLogger(__name__)


async def register_user(db: AsyncSession, user_in: UserCreate) -> User:
    existing_user = await db.scalar(select(User).where(User.email == user_in.email))
    if existing_user:
        logger.warning("Registration blocked for duplicate email: %s", user_in.email)
        raise ValidationException("Bu e-posta adresi zaten kayıtlı.")

    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        role="standard",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info("User registered successfully: %s", user.email)
    return user
