from fastapi import APIRouter

from backend.api.v1.endpoints import auth, movies, personalized, recommendations, users, watch_history, watchlist


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(movies.router, prefix="/movies", tags=["movies"])
api_router.include_router(
    recommendations.router, prefix="/movies", tags=["recommendations"]
)
api_router.include_router(
    personalized.router, prefix="/recommendations", tags=["recommendations"]
)
api_router.include_router(
    watch_history.router, prefix="/watch-history", tags=["watch-history"]
)
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])
