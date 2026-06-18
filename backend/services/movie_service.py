from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.movie import Movie
from backend.models.review import Review
from backend.schemas.movie import MovieDetailRead
from backend.services.recommender import movie_recommender


async def search_movies(
    db: AsyncSession, query: str, content_type: str | None = None
) -> list[Movie]:
    statement = select(Movie)
    if query.strip():
        statement = statement.where(
            or_(
                Movie.title.ilike(f"%{query}%"),
                Movie.overview.ilike(f"%{query}%"),
            )
        )
    if content_type:
        statement = statement.where(Movie.content_type == content_type)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def get_recommendations_for_movie(
    db: AsyncSession, movie_id: int, limit: int = 10
) -> list[Movie] | None:
    movie = await db.get(Movie, movie_id)
    if movie is None:
        return None

    if not movie_recommender.is_ready:
        return None

    source_content_type = movie.content_type or "Movie"
    fetch_limit = max(limit * 10, limit)
    recommendations = movie_recommender.recommend(movie_id=movie_id, top_k=fetch_limit)
    recommended_ids = [item.movie_id for item in recommendations]
    if not recommended_ids:
        return []

    statement = select(Movie).where(
        Movie.id.in_(recommended_ids),
        Movie.content_type == source_content_type,
    )
    result = await db.execute(statement)
    movies = list(result.scalars().all())
    movie_by_id = {movie_item.id: movie_item for movie_item in movies}
    return [
        movie_by_id[recommended_id]
        for recommended_id in recommended_ids
        if recommended_id in movie_by_id
    ][:limit]


async def get_reviews_for_movie(
    db: AsyncSession, movie_id: int, limit: int = 10
) -> list[Review] | None:
    movie = await db.get(Movie, movie_id)
    if movie is None:
        return None

    statement = select(Review).where(Review.movie_id == movie_id).limit(limit)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def get_movie_by_id(db: AsyncSession, movie_id: int) -> Movie | None:
    return await db.get(Movie, movie_id)


def to_movie_detail_read(movie: Movie) -> MovieDetailRead:
    return MovieDetailRead.model_validate(movie)
