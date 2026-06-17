from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.schemas.user import UserCreate, UserLogin, UserRead
from backend.services import auth_service


router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    """
    User registration endpoint.
    """
    return await auth_service.register_user(db=db, user_in=user_in)


@router.post("/login", response_model=UserRead)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)) -> UserRead:
    """
    User login endpoint.
    """
    return await auth_service.login_user(db=db, credentials=user_in)
