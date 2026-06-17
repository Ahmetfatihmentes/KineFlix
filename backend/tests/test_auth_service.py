from sqlalchemy import select

from backend.core.exceptions import ValidationException
from backend.core.security import verify_password
from backend.schemas.user import UserCreate
from backend.models.user import User
from backend.services.auth_service import register_user


async def test_register_user_creates_user(db_session) -> None:
    user = await register_user(
        db_session,
        UserCreate(email="test@example.com", password="supersecret"),
    )

    persisted = await db_session.scalar(select(User).where(User.id == user.id))
    assert persisted is not None
    assert persisted.email == "test@example.com"
    assert persisted.password_hash != "supersecret"
    assert verify_password("supersecret", persisted.password_hash) is True


async def test_register_user_rejects_duplicate_email(db_session) -> None:
    await register_user(
        db_session,
        UserCreate(email="duplicate@example.com", password="supersecret"),
    )

    try:
        await register_user(
            db_session,
            UserCreate(email="duplicate@example.com", password="anotherpass"),
        )
    except ValidationException as exc:
        assert "zaten kayitli" in exc.message.lower() or "zaten kay\u0131tl\u0131" in exc.message.lower()
    else:
        raise AssertionError("ValidationException bekleniyordu.")
