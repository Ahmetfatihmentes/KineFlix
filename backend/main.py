from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.error_handlers import register_exception_handlers
from backend.api.v1.api import api_router
from backend.core.bootstrap import initialize_database
from backend.core import logging_config
from backend.core.rate_limiter import RateLimitMiddleware
from backend.core.redis_client import close_redis, init_redis
from backend.services.recommender import movie_recommender


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_database()
    await init_redis()
    await movie_recommender.start_background_initialization()
    yield
    movie_recommender.reset()
    await close_redis()


def create_app() -> FastAPI:
    """
    Application factory to create FastAPI app with routes and middleware.
    """
    logging_config.configure_logging()

    app = FastAPI(title="KineFlix Backend", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "https://kineflix-frontend.onrender.com",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RateLimitMiddleware)
    register_exception_handlers(app)
    app.include_router(api_router)

    static_dir = Path("backend/static")
    static_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    return app


app = create_app()
