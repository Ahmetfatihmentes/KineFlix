import pytest

from backend.services.recommender import movie_recommender


@pytest.mark.asyncio
async def test_recommender_returns_related_movies_for_known_id(db_session) -> None:
    await movie_recommender.initialize(db_session)

    recommendations = movie_recommender.recommend(movie_id=1, top_k=2)

    assert len(recommendations) == 2
    assert all(item.movie_id != 1 for item in recommendations)
    assert recommendations[0].score >= recommendations[1].score


@pytest.mark.asyncio
async def test_recommender_returns_empty_list_for_unknown_id(db_session) -> None:
    await movie_recommender.initialize(db_session)

    recommendations = movie_recommender.recommend(movie_id=999)

    assert recommendations == []
