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


@pytest.mark.asyncio
async def test_recommender_is_ready_after_initialize(db_session) -> None:
    await movie_recommender.initialize(db_session)

    assert movie_recommender.is_ready is True


@pytest.mark.asyncio
async def test_recommender_start_background_initialization_skips_when_ready(db_session) -> None:
    await movie_recommender.initialize(db_session)
    assert movie_recommender.is_ready is True

    await movie_recommender.start_background_initialization()

    assert movie_recommender.is_ready is True


@pytest.mark.asyncio
async def test_recommender_loads_from_cache(tmp_path, db_session) -> None:
    import backend.services.recommender as recommender_module

    await movie_recommender.initialize(db_session)
    cache_path = tmp_path / "cached.pkl"
    recommender_module.TFIDF_CACHE_PATH = cache_path
    movie_recommender.reset()

    await movie_recommender.initialize(db_session)
    assert movie_recommender.is_ready is True

    movie_recommender.reset()
    await movie_recommender.initialize(db_session)
    assert movie_recommender.is_ready is True

