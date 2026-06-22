import pathlib
import sys
from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.core.database import Base, get_db
from backend.main import create_app
from backend.models.movie import Movie
from backend.models.review import Review
from backend.services.recommender import movie_recommender


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        session.add_all(
            [
                Movie(
                    id=1,
                    title="Interstellar",
                    overview="Space travel wormhole future science family survival",
                    genres="Sci-Fi Drama Adventure",
                    release_year=2014,
                    letterboxd_rating=4.5,
                    content_type="Movie",
                    trailer_key="abc123",
                ),
                Movie(
                    id=2,
                    title="The Martian",
                    overview="Astronaut survives alone on Mars with science and humor",
                    genres="Sci-Fi Adventure",
                    release_year=2015,
                    letterboxd_rating=4.2,
                    content_type="Movie",
                ),
                Movie(
                    id=3,
                    title="Inception",
                    overview="Dream layers espionage mind-bending heist thriller",
                    genres="Sci-Fi Thriller",
                    release_year=2010,
                    letterboxd_rating=4.4,
                    content_type="Movie",
                ),
                Movie(
                    id=4,
                    title="Gravity",
                    overview="Two astronauts struggle to survive in space after disaster",
                    genres="Sci-Fi Drama",
                    release_year=2013,
                    letterboxd_rating=4.1,
                    content_type="Movie",
                ),
            ]
        )
        session.add_all(
            [
                Review(
                    id=1,
                    movie_id=1,
                    review_text="A stunning visual masterpiece with emotional depth.",
                    sentiment="positive",
                    critic_name="Critic A",
                ),
                Review(
                    id=2,
                    movie_id=1,
                    review_text="Nolan delivers an ambitious sci-fi epic.",
                    sentiment="positive",
                    critic_name="Critic B",
                ),
            ]
        )
        await session.commit()

        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(autouse=True)
def reset_movie_recommender(tmp_path: pathlib.Path) -> Generator[None, None, None]:
    import backend.services.recommender as recommender_module

    test_cache_path = tmp_path / "tfidf_matrix.pkl"
    original_cache_path = recommender_module.TFIDF_CACHE_PATH
    recommender_module.TFIDF_CACHE_PATH = test_cache_path
    movie_recommender.reset()
    yield
    movie_recommender.reset()
    recommender_module.TFIDF_CACHE_PATH = original_cache_path


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[TestClient, None]:
    await movie_recommender.initialize(db_session)

    app = create_app()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with patch("backend.main.initialize_database", new_callable=AsyncMock):
        with patch(
            "backend.main.movie_recommender.start_background_initialization",
            new_callable=AsyncMock,
        ):
            with patch("backend.main.init_redis", new_callable=AsyncMock):
                with patch("backend.main.close_redis", new_callable=AsyncMock):
                    with TestClient(app) as test_client:
                        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client) -> dict[str, str]:
    client.post(
        "/auth/register",
        json={"email": "testuser@example.com", "password": "supersecret"},
    )
    login = client.post(
        "/auth/login",
        json={"email": "testuser@example.com", "password": "supersecret"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
