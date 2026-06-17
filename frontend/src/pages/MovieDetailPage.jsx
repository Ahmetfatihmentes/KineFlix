import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import ReviewCard from '../components/ReviewCard'
import SentimentPanel from '../components/SentimentPanel'
import { getMovie, getRecommendations, getReviews } from '../services/api'
import { firstGenre, posterSrc } from '../utils/movie'

export default function MovieDetailPage() {
  const { id } = useParams()
  const [movie, setMovie] = useState(null)
  const [reviews, setReviews] = useState([])
  const [similar, setSimilar] = useState([])
  const [loading, setLoading] = useState(true)
  const [recLoading, setRecLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError('')
      try {
        const [movieRes, reviewsRes] = await Promise.all([
          getMovie(id),
          getReviews(id, 9),
        ])
        if (cancelled) return
        setMovie(movieRes.data)
        setReviews(reviewsRes.data)
        setRecLoading(true)
        const recRes = await getRecommendations(id, 8)
        if (cancelled) return
        const recData = recRes.data
        if (Array.isArray(recData)) setSimilar(recData)
        else if (recData?.status === 'loading') setSimilar([])
      } catch {
        if (!cancelled) setError('Film bulunamadı veya sunucu hatası.')
      } finally {
        if (!cancelled) {
          setLoading(false)
          setRecLoading(false)
        }
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [id])

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
              {movie.tagline && (
                <p className="font-body text-body-lg text-on-surface-variant italic mt-4">
                  &ldquo;{movie.tagline}&rdquo;
                </p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4 font-body text-body-md text-on-surface-variant">
                <p className="leading-relaxed opacity-90">{movie.overview || 'Özet mevcut değil.'}</p>
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
                  {movie.actors && (
                    <div>
                      <span className="block font-label text-label-md text-on-surface-variant uppercase mb-1">
                        Oyuncular
                      </span>
                      <span className="font-body text-title-md text-on-surface font-semibold line-clamp-2">
                        {movie.actors}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              <SentimentPanel
                positivePct={movie.positive_pct}
                rating={movie.letterboxd_rating}
              />
            </div>

            <div className="flex gap-4 flex-wrap">
              <button
                type="button"
                className="bg-primary-container text-on-primary-container px-8 py-3 rounded font-label text-label-md uppercase tracking-widest hover:bg-primary transition-colors flex items-center gap-2"
              >
                <span className="material-symbols-outlined material-symbols-filled">play_arrow</span>
                İzle
              </button>
              <button
                type="button"
                className="border border-secondary-container text-on-surface px-8 py-3 rounded font-label text-label-md uppercase tracking-widest hover:bg-secondary-container/50 transition-colors flex items-center gap-2"
              >
                <span className="material-symbols-outlined">add</span>
                Listeye Ekle
              </button>
            </div>
          </div>
        </div>

        <section className="mb-24">
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

        <section>
          <div className="flex items-center justify-between border-b border-outline-variant/30 pb-4 mb-8">
            <h2 className="font-headline text-headline-lg text-on-surface uppercase">Benzer Filmler</h2>
          </div>
          {recLoading ? (
            <p className="font-body text-on-surface-variant">Öneriler hazırlanıyor...</p>
          ) : similar.length === 0 ? (
            <p className="font-body text-on-surface-variant">Benzer film bulunamadı.</p>
          ) : (
            <div className="flex gap-6 overflow-x-auto pb-8 snap-x hide-scrollbar">
              {similar.map((m) => (
                <Link
                  key={m.id}
                  to={`/movies/${m.id}`}
                  className="min-w-[160px] md:min-w-[200px] flex-shrink-0 snap-start group"
                >
                  <div className="aspect-[2/3] rounded border border-outline-variant/20 overflow-hidden relative mb-3 group-hover:border-primary-container/50 transition-colors">
                    <img
                      alt={m.title}
                      src={posterSrc(m.poster_url)}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                    />
                  </div>
                  <h4 className="font-body text-[16px] font-semibold text-on-surface group-hover:text-primary-container transition-colors truncate">
                    {m.title}
                  </h4>
                  <p className="font-label text-[12px] text-on-surface-variant uppercase">
                    {m.release_year || '—'}
                  </p>
                </Link>
              ))}
            </div>
          )}
        </section>
      </main>

      <Footer />
    </div>
  )
}
