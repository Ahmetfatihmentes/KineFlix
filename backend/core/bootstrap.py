import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from backend.core.database import AsyncSessionLocal, Base, engine
from backend.models.movie import Movie


logger = logging.getLogger(__name__)


async def initialize_database() -> None:
    """
    Create tables for local development and seed a minimal movie catalog.
    If the database itself does not exist yet, startup will fail before this step.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSessionLocal() as session:
            existing_movie = await session.scalar(select(Movie.id).limit(1))
            if existing_movie:
                return

            session.add_all(
                [
                    Movie(
                        id=1,
                        title="Interstellar",
                        overview="Space travel wormhole future science family survival",
                        genres="Sci-Fi Drama Adventure",
                        release_year=2014,
                    ),
                    Movie(
                        id=2,
                        title="The Martian",
                        overview="Astronaut survives alone on Mars with science and humor",
                        genres="Sci-Fi Adventure",
                        release_year=2015,
                    ),
                    Movie(
                        id=3,
                        title="Inception",
                        overview="Dream layers espionage mind-bending heist thriller",
                        genres="Sci-Fi Thriller",
                        release_year=2010,
                    ),
                    Movie(
                        id=4,
                        title="Gravity",
                        overview="Two astronauts struggle to survive in space after disaster",
                        genres="Sci-Fi Drama",
                        release_year=2013,
                    ),
                ]
            )
            await session.commit()
            logger.info("Seeded initial movie catalog.")
    except SQLAlchemyError:
        logger.warning(
            "Database bootstrap skipped because the configured database is unavailable."
        )
