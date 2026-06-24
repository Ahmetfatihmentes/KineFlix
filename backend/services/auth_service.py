import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import ValidationException
from backend.core.security import get_password_hash, verify_password
from backend.models.user import User
from backend.schemas.user import UserCreate, UserLogin


logger = logging.getLogger(__name__)


async def register_user(db: AsyncSession, user_in: UserCreate) -> User:
    existing_user = await db.scalar(select(User).where(User.email == user_in.email))
    if existing_user:
        logger.warning("Kayıt engellendi, e-posta zaten mevcut: %s", user_in.email)
        raise ValidationException("Bu e-posta adresi zaten kayıtlı.")

    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        role="standard",
        full_name=user_in.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info("Kullanıcı başarıyla kaydedildi: %s", user.email)
    return user


async def login_user(db: AsyncSession, credentials: UserLogin) -> User:
    user = await db.scalar(select(User).where(User.email == credentials.email))
    if not user or not verify_password(credentials.password, user.password_hash):
        raise ValidationException("E-posta veya şifre hatalı.")
    logger.info("Kullanıcı giriş yaptı: %s", user.email)
    return user
