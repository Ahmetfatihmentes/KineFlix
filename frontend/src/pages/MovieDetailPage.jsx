import { useEffect, useReducer, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import ReviewCard from '../components/ReviewCard'
import SentimentPanel from '../components/SentimentPanel'
import {
  getMovie,
  getRecommendations,
  getRecommendationReason,
  getReviews,
  getAiReview,
  getTrailer,
  getWatchHistory,
  addToWatchHistory,
  removeFromWatchHistory,
  getWatchStatus,
  addToWatchlist,
  removeFromWatchlist,
  getWatchlistStatus,
  toggleLike,
  getLikeStatus,
  addUserReview,
  getUserReviews,
  deleteUserReview,
} from '../services/api'
import { firstGenre, displayOverview, displayTagline, posterSrc } from '../utils/movie'

const initialLoadingState = {
  loading: true,
  error: '',
  recLoading: false,
  recError: false,
  trailerLoading: false,
  watchLoading: false,
  watchlistLoading: false,
  whyLoading: false,
  aiReviewLoading: false,
}

function loadingReducer(state, action) {
  switch (action.type) {
    case 'PAGE_LOAD_START':
      return { ...state, loading: true, error: '' }
    case 'PAGE_LOAD_DONE':
      return { ...state, loading: false }
    case 'PAGE_LOAD_ERROR':
      return { ...state, loading: false, error: action.payload }
    case 'REC_START':
      return { ...state, recLoading: true, recError: false }
    case 'REC_DONE':
      return { ...state, recLoading: false }
    case 'REC_ERROR':
      return { ...state, recLoading: false, recError: true }
    case 'TRAILER_LOADING':
      return { ...state, trailerLoading: action.payload }
    case 'WATCH_LOADING':
      return { ...state, watchLoading: action.payload }
    case 'WATCHLIST_LOADING':
      return { ...state, watchlistLoading: action.payload }
    case 'WHY_LOADING':
      return { ...state, whyLoading: action.payload }
    case 'AI_REVIEW_START':
      return { ...state, aiReviewLoading: true }
    case 'AI_REVIEW_DONE':
      return { ...state, aiReviewLoading: false }
    default:
      return state
  }
}

export default function MovieDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [state, dispatch] = useReducer(loadingReducer, initialLoadingState)
  const { loading, error, recLoading, recError, trailerLoading, watchLoading, watchlistLoading, whyLoading, aiReviewLoading } = state
  const [movie, setMovie] = useState(null)
  const [reviews, setReviews] = useState([])
  const [similar, setSimilar] = useState([])
  const [trailerKey, setTrailerKey] = useState(null)
  const [showTrailer, setShowTrailer] = useState(false)
  const [watched, setWatched] = useState(false)
  const [inWatchlist, setInWatchlist] = useState(false)
  const [whyRecommended, setWhyRecommended] = useState(null)
  const [reasonCache, setReasonCache] = useState({})
  const [loadingReasons, setLoadingReasons] = useState({})
  const [hoveredMovieId, setHoveredMovieId] = useState(null)
  const [aiReview, setAiReview] = useState(null)
  const [showAllActors, setShowAllActors] = useState(false)
  const [userReviews, setUserReviews] = useState([])
  const [reviewText, setReviewText] = useState('')
  const [reviewSubmitting, setReviewSubmitting] = useState(false)
  const [liked, setLiked] = useState(false)
  const [likeCount, setLikeCount] = useState(0)
  const [likeLoading, setLikeLoading] = useState(false)
  const currentUserId = parseInt(localStorage.getItem('kineflix_user_id') || '0', 10)

  useEffect(() => {
    let cancelled = false
    async function load() {
      dispatch({ type: 'PAGE_LOAD_START' })
      try {
        const [movieRes, reviewsRes] = await Promise.all([
          getMovie(id),
          getReviews(id, 9),
        ])
        if (cancelled) return
        setMovie(movieRes.data)
        setReviews(reviewsRes.data)
        dispatch({ type: 'REC_START' })
        const loadRecommendations = async (attempt = 0) => {
          try {
            const recRes = await getRecommendations(id, 8)
            if (cancelled) return
            const recData = recRes.data
            if (Array.isArray(recData)) {
              setSimilar(recData)
              dispatch({ type: 'REC_DONE' })
              return
            }
            if (recData?.status === 'loading' && attempt < 10) {
              await new Promise((resolve) => setTimeout(resolve, 5000))
              if (!cancelled) loadRecommendations(attempt + 1)
              return
            }
            setSimilar([])
            dispatch({ type: 'REC_ERROR' })
          } catch {
            if (!cancelled) {
              setSimilar([])
              dispatch({ type: 'REC_ERROR' })
            }
          }
        }
        await loadRecommendations()
      } catch {
        if (!cancelled) dispatch({ type: 'PAGE_LOAD_ERROR', payload: 'Film bulunamadı veya sunucu hatası.' })
      } finally {
        if (!cancelled) dispatch({ type: 'PAGE_LOAD_DONE' })
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [id])

  useEffect(() => {
    if (!id || !movie) return

    setWhyRecommended(null)

    const fetchWhyRecommended = async (sourceId, recommendedId) => {
      dispatch({ type: 'WHY_LOADING', payload: true })
      try {
        const { data } = await getRecommendationReason(sourceId, recommendedId)
        setWhyRecommended(data)
      } catch (e) {
        console.error(e)
      } finally {
        dispatch({ type: 'WHY_LOADING', payload: false })
      }
    }

    const urlParams = new URLSearchParams(window.location.search)
    const sourceMovieId = urlParams.get('from')

    if (sourceMovieId) {
      fetchWhyRecommended(sourceMovieId, id)
      return
    }

    const user = localStorage.getItem('kineflix_user')
    if (!user) return

    getWatchHistory()
      .then((res) => {
        const history = Array.isArray(res.data) ? res.data : []
        const lastWatched = history.find((h) => h.id !== parseInt(id, 10))
        if (lastWatched) {
          fetchWhyRecommended(lastWatched.id, id)
        }
      })
      .catch(console.error)
  }, [id, movie])

  useEffect(() => {
    if (!id || !movie) return

    let cancelled = false

    const fetchAiReview = async () => {
      dispatch({ type: 'AI_REVIEW_START' })
      setAiReview(null)
      try {
        const { data } = await getAiReview(id)
        if (cancelled) return
        if (data.ai_review) {
          setAiReview(data)
        }
      } catch (e) {
        console.error(e)
      } finally {
        if (!cancelled) dispatch({ type: 'AI_REVIEW_DONE' })
      }
    }

    fetchAiReview()

    return () => {
      cancelled = true
    }
  }, [id, movie])

  useEffect(() => {
    if (!id) return
    getUserReviews(id)
      .then(({ data }) => setUserReviews(data))
      .catch(() => {})
  }, [id])

  useEffect(() => {
    if (!id || !currentUserId) return
    getLikeStatus(id)
      .then(({ data }) => {
        setLiked(data.liked)
        setLikeCount(data.like_count)
      })
      .catch(() => {})
  }, [id, currentUserId])

  const handleLike = async () => {
    if (!currentUserId || likeLoading) return
    setLikeLoading(true)
    try {
      const { data } = await toggleLike(id)
      setLiked(data.liked)
      setLikeCount((prev) => prev + (data.liked ? 1 : -1))
    } catch (e) {
      console.error(e)
    } finally {
      setLikeLoading(false)
    }
  }

  const handleReviewSubmit = async () => {
    if (!reviewText.trim()) return
    setReviewSubmitting(true)
    try {
      const { data } = await addUserReview(parseInt(id, 10), reviewText.trim())
      setUserReviews((prev) => [data, ...prev])
      setReviewText('')
    } catch (e) {
      console.error(e)
    } finally {
      setReviewSubmitting(false)
    }
  }

  const handleReviewDelete = async (reviewId) => {
    try {
      await deleteUserReview(reviewId)
      setUserReviews((prev) => prev.filter((r) => r.id !== reviewId))
    } catch (e) {
      console.error(e)
    }
  }

  const fetchShortReason = async (recommendedId) => {
    if (reasonCache[recommendedId] || loadingReasons[recommendedId]) return

    setLoadingReasons((prev) => ({ ...prev, [recommendedId]: true }))

    try {
      const { data } = await getRecommendationReason(id, recommendedId, true)
      setReasonCache((prev) => ({ ...prev, [recommendedId]: data.reason }))
    } catch (e) {
      console.error(e)
      setReasonCache((prev) => ({ ...prev, [recommendedId]: 'Benzer türde bir yapım.' }))
    } finally {
      setLoadingReasons((prev) => ({ ...prev, [recommendedId]: false }))
    }
  }

  useEffect(() => {
    if (!id) return
    getWatchStatus(id)
      .then((res) => setWatched(res.data.watched))
      .catch(() => {})
    getWatchlistStatus(id)
      .then((res) => setInWatchlist(res.data.in_watchlist))
      .catch(() => {})
  }, [id])

  const handlePlayTrailer = async () => {
    if (trailerKey) {
      setShowTrailer(true)
      return
    }
    dispatch({ type: 'TRAILER_LOADING', payload: true })
    try {
      const res = await getTrailer(id)
      setTrailerKey(res.data.youtube_key)
      setShowTrailer(true)
    } catch {
      alert('Bu film için fragman bulunamadı.')
    } finally {
      dispatch({ type: 'TRAILER_LOADING', payload: false })
    }
  }

  const handleWatch = async () => {
    dispatch({ type: 'WATCH_LOADING', payload: true })
    try {
      if (watched) {
        await removeFromWatchHistory(Number(id))
        setWatched(false)
      } else {
        await addToWatchHistory(Number(id))
        setWatched(true)
      }
    } catch (e) {
      console.error(e)
    } finally {
      dispatch({ type: 'WATCH_LOADING', payload: false })
    }
  }

  const handleWatchlist = async () => {
    dispatch({ type: 'WATCHLIST_LOADING', payload: true })
    try {
      if (inWatchlist) {
        await removeFromWatchlist(Number(id))
        setInWatchlist(false)
      } else {
        await addToWatchlist(Number(id))
        setInWatchlist(true)
      }
    } catch (e) {
      console.error(e)
    } finally {
      dispatch({ type: 'WATCHLIST_LOADING', payload: false })
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-surface flex items-center justify-center">
        <p className="font-body text-on-surface-variant">Yükleniyor...</p>
      </div>
    )
  }

  if (error || !movie) {
    return (
      <div className="min-h-screen bg-surface flex flex-col items-center justify-center gap-4">
        <p className="text-error font-body">{error || 'Film bulunamadı.'}</p>
        <Link to="/home" className="text-primary font-label uppercase">
          Ana Sayfaya Dön
        </Link>
      </div>
    )
  }

  const genre = firstGenre(movie.genres)
  const tagline = displayTagline(movie)
  const overview = displayOverview(movie)

  return (
    <div className="min-h-screen relative">
      <div className="film-grain" />
      <Navbar />

      <main className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-8 md:py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 mb-16">
          <div className="lg:col-span-4">
            <div className="aspect-[2/3] rounded border border-outline-variant/30 overflow-hidden sticky top-24">
              <img
                alt={movie.title}
                src={posterSrc(movie.poster_url)}
                className="w-full h-full object-cover"
              />
            </div>
            <button
              type="button"
              onClick={handlePlayTrailer}
              disabled={trailerLoading}
              className="w-full mt-4 bg-primary-container text-on-primary-container px-6 py-3 rounded font-label text-label-md uppercase tracking-widest hover:bg-primary transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <span className="material-symbols-outlined material-symbols-filled">
                {trailerLoading ? 'hourglass_empty' : 'play_arrow'}
              </span>
              {trailerLoading ? 'Yükleniyor...' : 'Fragmanı İzle'}
            </button>
          </div>

          <div className="lg:col-span-8 flex flex-col gap-8">
            <div>
              <span className="font-label text-label-md text-primary uppercase tracking-widest">
                {genre}
                {movie.release_year ? ` • ${movie.release_year}` : ''}
              </span>
              <h1 className="font-display text-display-lg text-on-surface uppercase mt-2 leading-none">
                {movie.title}
              </h1>
              {tagline && (
                <p className="font-body text-body-lg text-on-surface-variant italic mt-4">
                  &ldquo;{tagline}&rdquo;
                </p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
              <div className="space-y-4 font-body text-body-md text-on-surface-variant">
                <p className="leading-relaxed opacity-90">{overview || 'Özet mevcut değil.'}</p>
                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-outline-variant/30">
                  {movie.director && (
                    <div>
                      <span className="block font-label text-label-md text-on-surface-variant uppercase mb-1">
                        Yönetmen
                      </span>
                      <span className="font-body text-title-md text-on-surface font-semibold">
                        {movie.director}
                      </span>
                    </div>
                  )}
                  {movie.actors && (() => {
                    const all = movie.actors.split(',').map((a) => a.trim()).filter(Boolean)
                    const visible = showAllActors ? all : all.slice(0, 3)
                    return (
                      <div>
                        <span className="block font-label text-label-md text-on-surface-variant uppercase mb-1">
                          Oyuncular
                        </span>
                        <span className="font-body text-title-md text-on-surface font-semibold">
                          {visible.join(', ')}
                        </span>
                        {all.length > 3 && (
                          <button
                            type="button"
                            onClick={() => setShowAllActors((v) => !v)}
                            className="block mt-1 font-label text-xs text-primary hover:underline"
                          >
                            {showAllActors ? 'Daha Az' : 'Tümünü Gör'}
                          </button>
                        )}
                      </div>
                    )
                  })()}
                </div>
              </div>

              <SentimentPanel
                positivePct={movie.positive_pct}
                rating={movie.letterboxd_rating}
              />
            </div>

            {(whyLoading || whyRecommended) && (
              <div className="border-l-2 border-primary pl-4 my-4">
                <p className="text-primary text-xs font-label-md uppercase mb-2">
                  ✨ Neden Önerildi?
                </p>
                {whyLoading ? (
                  <p className="text-on-surface-variant text-sm animate-pulse">
                    AI analizi yapılıyor...
                  </p>
                ) : (
                  <>
                    {whyRecommended?.source_movie && (
                      <p className="text-primary-container text-xs mb-1">
                        {whyRecommended.source_movie} izlediğin için
                      </p>
                    )}
                    <p className="text-on-surface-variant text-sm leading-relaxed">
                      {whyRecommended?.reason}
                    </p>
                  </>
                )}
              </div>
            )}

            <div className="flex gap-4 flex-wrap">
              <button
                type="button"
                onClick={handleWatch}
                disabled={watchLoading}
                className="border border-secondary-container text-on-surface px-8 py-3 rounded font-label text-label-md uppercase tracking-widest hover:bg-secondary-container/50 transition-colors flex items-center gap-2 disabled:opacity-50"
              >
                <span className="material-symbols-outlined">
                  {watchLoading ? 'hourglass_empty' : watched ? 'check' : 'add'}
                </span>
                {watchLoading ? 'Yükleniyor...' : watched ? 'İzlendi' : 'İzle'}
              </button>
              <button
                type="button"
                onClick={handleWatchlist}
                disabled={watchlistLoading}
                className="border border-secondary-container text-on-surface px-8 py-3 rounded font-label text-label-md uppercase tracking-widest hover:bg-secondary-container/50 transition-colors flex items-center gap-2 disabled:opacity-50"
              >
                <span className="material-symbols-outlined">
                  {watchlistLoading ? 'hourglass_empty' : inWatchlist ? 'check' : 'add'}
                </span>
                {watchlistLoading
                  ? 'Yükleniyor...'
                  : inWatchlist
                    ? 'Listemde'
                    : 'Listeye Ekle'}
              </button>
              {currentUserId ? (
                <button
                  type="button"
                  onClick={handleLike}
                  disabled={likeLoading}
                  className="border border-error/50 px-6 py-3 rounded font-label text-label-md uppercase tracking-widest hover:bg-error/10 transition-colors flex items-center gap-2 disabled:opacity-50"
                >
                  <span className={`text-xl leading-none ${liked ? 'text-red-500' : 'text-on-surface-variant'}`}>
                    {liked ? '♥' : '♡'}
                  </span>
                </button>
              ) : null}
            </div>
          </div>
        </div>

        <section className="mb-24">
          {(aiReviewLoading || aiReview) && (
            <div className="mb-8 border border-primary/30 rounded-lg p-5 bg-surface-container">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-primary text-lg">🤖</span>
                <h3 className="text-primary font-label-md uppercase text-sm tracking-wider">
                  AI Eleştirmen Değerlendirmesi
                </h3>
              </div>

              {aiReviewLoading ? (
                <div className="space-y-2">
                  <div className="h-3 bg-surface-container-high rounded animate-pulse w-full" />
                  <div className="h-3 bg-surface-container-high rounded animate-pulse w-4/5" />
                  <div className="h-3 bg-surface-container-high rounded animate-pulse w-3/5" />
                  <p className="text-on-surface-variant text-xs mt-2 animate-pulse">
                    AI analizi yapılıyor...
                  </p>
                </div>
              ) : aiReview?.ai_review ? (
                <>
                  <p className="text-on-surface text-sm leading-relaxed">
                    {aiReview.ai_review}
                  </p>
                  {aiReview.review_count ? (
                    <p className="text-on-surface-variant text-xs mt-3">
                      📊 {aiReview.review_count} eleştirmen yorumu analiz edildi
                    </p>
                  ) : null}
                </>
              ) : null}
            </div>
          )}

          <div className="flex items-center justify-between border-b border-outline-variant/30 pb-4 mb-8">
            <h2 className="font-headline text-headline-lg text-on-surface uppercase">
              Eleştirmen Yorumları
            </h2>
          </div>
          {reviews.length === 0 ? (
            <p className="font-body text-on-surface-variant">Henüz yorum yok.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {reviews.map((review) => (
                <ReviewCard key={review.id} review={review} />
              ))}
            </div>
          )}
        </section>

        <section className="mb-16">
          <div className="flex items-center justify-between border-b border-outline-variant/30 pb-4 mb-8">
            <h2 className="font-headline text-headline-lg text-on-surface uppercase">Kullanıcı Yorumları</h2>
          </div>

          {currentUserId ? (
            <div className="mb-8">
              <textarea
                className="w-full bg-surface-container border border-outline-variant rounded-lg p-4 text-on-surface text-sm resize-none focus:outline-none focus:border-primary"
                rows={3}
                placeholder="Bu film hakkında ne düşünüyorsunuz?"
                value={reviewText}
                onChange={(e) => setReviewText(e.target.value)}
              />
              <div className="flex justify-end mt-2">
                <button
                  onClick={handleReviewSubmit}
                  disabled={reviewSubmitting || !reviewText.trim()}
                  className="px-5 py-2 bg-primary text-on-primary rounded font-label text-sm uppercase tracking-wider disabled:opacity-50"
                >
                  {reviewSubmitting ? 'Gönderiliyor...' : 'Gönder'}
                </button>
              </div>
            </div>
          ) : (
            <p className="text-on-surface-variant text-sm mb-6">Yorum yazmak için <Link to="/login" className="text-primary underline">giriş yapın</Link>.</p>
          )}

          {userReviews.length === 0 ? (
            <p className="font-body text-on-surface-variant">Henüz kullanıcı yorumu yok.</p>
          ) : (
            <div className="flex flex-col gap-4">
              {userReviews.map((review) => (
                <div key={review.id} className="bg-surface-container border border-outline-variant/30 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-xs font-label uppercase tracking-wider px-2 py-0.5 rounded ${review.sentiment === 'POSITIVE' ? 'bg-tertiary-container/30 text-tertiary-container' : 'bg-error-container/30 text-error'}`}>
                      {review.sentiment === 'POSITIVE' ? '✓ Pozitif' : '✗ Negatif'}
                    </span>
                    <div className="flex items-center gap-3">
                      <span className="text-on-surface-variant text-xs">
                        {new Date(review.created_at).toLocaleDateString('tr-TR')}
                      </span>
                      {review.user_id === currentUserId && (
                        <button
                          onClick={() => handleReviewDelete(review.id)}
                          className="text-error text-xs hover:underline"
                        >
                          Sil
                        </button>
                      )}
                    </div>
                  </div>
                  <p className="text-on-surface text-sm leading-relaxed">{review.review_text}</p>
                </div>
              ))}
            </div>
          )}
        </section>

        <section>
          <div className="flex items-center justify-between border-b border-outline-variant/30 pb-4 mb-8">
            <h2 className="font-headline text-headline-lg text-on-surface uppercase">Benzer Filmler</h2>
          </div>
          {recLoading ? (
            <div className="flex gap-6 overflow-x-auto pb-8 hide-scrollbar">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="min-w-[160px] md:min-w-[200px] flex-shrink-0 animate-pulse">
                  <div className="w-full aspect-[2/3] rounded bg-surface-container-highest mb-2" />
                  <div className="h-3 rounded bg-surface-container-highest w-3/4 mb-1" />
                  <div className="h-3 rounded bg-surface-container-highest w-1/2" />
                </div>
              ))}
            </div>
          ) : recError ? (
            <p className="font-body text-on-surface-variant">Öneriler şu an yüklenemiyor.</p>
          ) : similar.length === 0 ? (
            <p className="font-body text-on-surface-variant">Benzer film bulunamadı.</p>
          ) : (
            <div className="flex gap-6 overflow-x-auto pb-8 snap-x hide-scrollbar">
              {similar.map((m) => (
                <div
                  key={m.id}
                  className="min-w-[160px] md:min-w-[200px] flex-shrink-0 snap-start relative cursor-pointer group"
                  onMouseEnter={() => {
                    setHoveredMovieId(m.id)
                    fetchShortReason(m.id)
                  }}
                  onMouseLeave={() => setHoveredMovieId(null)}
                  onClick={() => navigate(`/movies/${m.id}?from=${id}`)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault()
                      navigate(`/movies/${m.id}?from=${id}`)
                    }
                  }}
                  role="button"
                  tabIndex={0}
                >
                  <div className="aspect-[2/3] rounded border border-outline-variant/20 overflow-hidden relative mb-3 group-hover:border-primary-container/50 transition-colors">
                    <img
                      alt={m.title}
                      src={posterSrc(m.poster_url)}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                    />
                    {hoveredMovieId === m.id && (
                      <div className="absolute inset-0 bg-black/85 rounded flex flex-col justify-end p-3 z-10">
                        <p className="text-primary text-xs font-label-md uppercase mb-1">
                          Neden Önerildi?
                        </p>
                        {loadingReasons[m.id] ? (
                          <p className="text-on-surface-variant text-xs animate-pulse">
                            Yükleniyor...
                          </p>
                        ) : (
                          <p className="text-on-surface text-xs leading-relaxed line-clamp-4">
                            {reasonCache[m.id] || 'Benzer türde bir yapım.'}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                  <h4 className="font-body text-[16px] font-semibold text-on-surface group-hover:text-primary-container transition-colors truncate">
                    {m.title}
                  </h4>
                  <p className="font-label text-[12px] text-on-surface-variant uppercase">
                    {m.release_year || '—'}
                  </p>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      <Footer />

      {showTrailer && trailerKey && (
        <div
          className="fixed inset-0 bg-black/85 z-50 flex items-center justify-center p-4"
          onClick={() => setShowTrailer(false)}
          role="presentation"
        >
          <div
            className="relative w-full max-w-4xl"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-label="Film fragmanı"
          >
            <button
              type="button"
              onClick={() => setShowTrailer(false)}
              className="absolute -top-12 right-0 text-on-surface text-3xl leading-none hover:text-primary-container transition-colors"
            >
              ✕
            </button>
            <div className="aspect-video w-full">
              <iframe
                className="w-full h-full rounded border border-outline-variant/30"
                src={`https://www.youtube.com/embed/${trailerKey}?autoplay=1&rel=0`}
                title="Film Fragmanı"
                allow="autoplay; encrypted-media; fullscreen"
                allowFullScreen
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
