from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from backend.core.config import get_settings


class Base(DeclarativeBase):
    """
    SQLAlchemy modelleri için temel sınıf.
    """


settings = get_settings()

engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async veritabanı oturumu döndüren FastAPI bağımlılığı.
    """
    async with AsyncSessionLocal() as session:
        yield session
