from __future__ import annotations

import asyncio
import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai_engine.nlp_preprocessor import clean_text
from backend.core.database import AsyncSessionLocal
from backend.models.movie import Movie


logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TFIDF_CACHE_PATH = PROJECT_ROOT / "models" / "tfidf_matrix.pkl"
TFIDF_MAX_FEATURES = 10_000


@dataclass
class RecommendationCandidate:
    movie_id: int
    score: float


@dataclass
class _IndexedMovie:
    movie_id: int
    text: str


@dataclass
class _TfidfCachePayload:
    movie_count: int
    movies: list[_IndexedMovie]
    index_by_id: dict[int, int]
    vectorizer: TfidfVectorizer
    matrix: Any


class MovieRecommender:
    """
    TF-IDF + cosine similarity recommender backed by PostgreSQL movie catalog.
    Matrix build runs in the background; cached matrix is persisted to disk.
    """

    def __init__(self) -> None:
        self._movies: list[_IndexedMovie] = []
        self._index_by_id: dict[int, int] = {}
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self._is_ready = False
        self._is_loading = False
        self._load_task: asyncio.Task[None] | None = None

    @property
    def is_ready(self) -> bool:
        return self._is_ready

    @property
    def is_loading(self) -> bool:
        return self._is_loading and not self._is_ready

    def reset(self) -> None:
        if self._load_task and not self._load_task.done():
            self._load_task.cancel()
        self._load_task = None
        self._movies = []
        self._index_by_id = {}
        self._vectorizer = None
        self._matrix = None
        self._is_ready = False
        self._is_loading = False

    def _build_corpus_text(self, movie: Movie) -> str:
        parts = [
            movie.title,
            movie.overview or "",
            movie.genres or "",
            movie.themes or "",
        ]
        return clean_text(" ".join(part for part in parts if part))

    async def _get_movie_count(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count()).select_from(Movie))
        return int(result.scalar_one())

    async def _fetch_movies_data(self, db: AsyncSession) -> list[tuple[int, str]]:
        result = await db.execute(select(Movie))
        movies = list(result.scalars().all())
        return [(movie.id, self._build_corpus_text(movie)) for movie in movies]

    def _apply_cache_payload(self, payload: _TfidfCachePayload) -> None:
        self._movies = payload.movies
        self._index_by_id = payload.index_by_id
        self._vectorizer = payload.vectorizer
        self._matrix = payload.matrix

    def _build_and_cache(self, movies_data: list[tuple[int, str]], movie_count: int) -> None:
        self._movies = []
        self._index_by_id = {}
        corpus: list[str] = []

        for movie_id, text in movies_data:
            self._index_by_id[movie_id] = len(self._movies)
            self._movies.append(_IndexedMovie(movie_id=movie_id, text=text))
            corpus.append(text)

        self._vectorizer = TfidfVectorizer(max_features=TFIDF_MAX_FEATURES)
        self._matrix = self._vectorizer.fit_transform(corpus) if corpus else None
        self._save_to_pickle(movie_count)

    def _save_to_pickle(self, movie_count: int) -> None:
        TFIDF_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = _TfidfCachePayload(
            movie_count=movie_count,
            movies=self._movies,
            index_by_id=self._index_by_id,
            vectorizer=self._vectorizer,
            matrix=self._matrix,
        )
        with TFIDF_CACHE_PATH.open("wb") as cache_file:
            pickle.dump(payload, cache_file)
        logger.info("TF-IDF matrix cached to %s", TFIDF_CACHE_PATH)

    def _try_load_from_pickle(self, movie_count: int) -> bool:
        if not TFIDF_CACHE_PATH.exists():
            return False

        try:
            with TFIDF_CACHE_PATH.open("rb") as cache_file:
                payload = pickle.load(cache_file)
        except (OSError, pickle.UnpicklingError):
            logger.warning("Failed to read TF-IDF cache; rebuilding matrix.")
            return False

        if not isinstance(payload, _TfidfCachePayload):
            logger.warning("Invalid TF-IDF cache format; rebuilding matrix.")
            return False

        if payload.movie_count != movie_count:
            logger.info(
                "TF-IDF cache stale (movies=%s, cached=%s); rebuilding matrix.",
                movie_count,
                payload.movie_count,
            )
            return False

        self._apply_cache_payload(payload)
        logger.info("TF-IDF matrix loaded from cache (%s movies).", movie_count)
        return True

    async def initialize(self, db: AsyncSession) -> None:
        """Blocking initialization for tests and manual rebuilds."""
        if self._is_ready:
            return

        movie_count = await self._get_movie_count(db)
        if self._try_load_from_pickle(movie_count):
            self._is_ready = True
            return

        movies_data = await self._fetch_movies_data(db)
        await asyncio.to_thread(self._build_and_cache, movies_data, movie_count)
        self._is_ready = True

    async def start_background_initialization(self) -> None:
        if self._is_ready or self._is_loading:
            return

        if self._load_task and not self._load_task.done():
            return

        self._is_loading = True
        self._load_task = asyncio.create_task(self._load_in_background())

    async def _load_in_background(self) -> None:
        try:
            async with AsyncSessionLocal() as db:
                movie_count = await self._get_movie_count(db)
                if self._try_load_from_pickle(movie_count):
                    self._is_ready = True
                    return

                movies_data = await self._fetch_movies_data(db)

            await asyncio.to_thread(self._build_and_cache, movies_data, movie_count)
            self._is_ready = True
            logger.info("TF-IDF matrix built in background.")
        except asyncio.CancelledError:
            logger.info("TF-IDF background build cancelled.")
            raise
        except Exception:
            logger.exception("TF-IDF background build failed.")
        finally:
            self._is_loading = False

    def recommend(
        self,
        movie_id: int,
        top_k: int = 10,
    ) -> list[RecommendationCandidate]:
        if not self._is_ready:
            return []

        if self._matrix is None or movie_id not in self._index_by_id:
            return []

        movie_index = self._index_by_id[movie_id]
        scores = cosine_similarity(self._matrix[movie_index], self._matrix).flatten()
        ranked = sorted(
            [
                RecommendationCandidate(
                    movie_id=self._movies[index].movie_id,
                    score=float(score),
                )
                for index, score in enumerate(scores)
                if self._movies[index].movie_id != movie_id
            ],
            key=lambda item: item.score,
            reverse=True,
        )
        return ranked[:top_k]


movie_recommender = MovieRecommender()
