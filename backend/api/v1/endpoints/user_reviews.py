from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.deps import get_current_user_id
from backend.models.user_review import UserReview
from backend.schemas.user_review import UserReviewCreate, UserReviewRead
from backend.services.ollama_service import analyze_sentiment

router = APIRouter()


@router.post("/", response_model=UserReviewRead, status_code=201)
async def add_review(
    body: UserReviewCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    sentiment = await analyze_sentiment(body.review_text)
    review = UserReview(
        user_id=user_id,
        movie_id=body.movie_id,
        review_text=body.review_text,
        sentiment=sentiment,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


@router.get("/{movie_id}", response_model=list[UserReviewRead])
async def get_movie_user_reviews(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserReview)
        .where(UserReview.movie_id == movie_id)
        .order_by(UserReview.created_at.desc())
    )
    return result.scalars().all()


@router.delete("/{review_id}", status_code=204)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    review = await db.get(UserReview, review_id)
    if not review or review.user_id != user_id:
        raise HTTPException(status_code=404, detail="Yorum bulunamadı")
    await db.delete(review)
    await db.commit()
