import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import { getWatchlist, removeFromWatchlist } from '../services/api'
import { firstGenre, posterSrc } from '../utils/movie'

const CONTENT_FILTERS = [
  { key: 'all', label: 'Tümü' },
  { key: 'Movie', label: 'Filmler' },
  { key: 'TV Show', label: 'Diziler' },
]

export default function WatchlistPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [contentFilter, setContentFilter] = useState('all')
  const [removingId, setRemovingId] = useState(null)

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError('')
      try {
        const { data } = await getWatchlist()
        if (!cancelled) setItems(Array.isArray(data) ? data : [])
      } catch {
        if (!cancelled) setError('Liste yüklenemedi.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [])

  const filtered = useMemo(() => {
    if (contentFilter === 'all') return items
    return items.filter((item) => item.content_type === contentFilter)
  }, [items, contentFilter])

  const movieCount = items.filter((item) => item.content_type !== 'TV Show').length
  const showCount = items.filter((item) => item.content_type === 'TV Show').length

  const handleWatch = (title, event) => {
    event.preventDefault()
    event.stopPropagation()
    const query = encodeURIComponent(title || '')
    window.open(`https://www.justwatch.com/tr/search?q=${query}`, '_blank')
  }

  const handleRemove = async (movieId, event) => {
    event.preventDefault()
    event.stopPropagation()
    setRemovingId(movieId)
    try {
      await removeFromWatchlist(movieId)
      setItems((prev) => prev.filter((item) => item.id !== movieId))
    } catch {
      setError('Listeden çıkarılamadı.')
    } finally {
      setRemovingId(null)
    }
  }

  return (
    <div className="min-h-screen relative flex flex-col">
      <div className="film-grain" />
      <Navbar active="watchlist" />

      <main className="flex-1 max-w-container-max mx-auto w-full px-margin-mobile md:px-margin-desktop pt-28 pb-24">
        <header className="mb-12">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <h1 className="font-display text-display-lg text-on-surface uppercase mb-2">
                Listelerim
              </h1>
              <p className="font-title text-title-md text-on-surface-variant italic">
                İzlemek istediğin filmler
              </p>
            </div>
            {!loading && items.length > 0 && (
              <div className="flex gap-4 flex-wrap">
                <span className="px-4 py-1.5 border border-primary text-primary font-label text-label-md tracking-widest uppercase bg-primary/5">
                  {movieCount} Film
                </span>
                <span className="px-4 py-1.5 border border-primary text-primary font-label text-label-md tracking-widest uppercase bg-primary/5">
                  {showCount} Dizi
                </span>
              </div>
            )}
          </div>
        </header>

        {!loading && items.length > 0 && (
          <section className="flex flex-col md:flex-row justify-between items-center py-6 mb-8 border-y border-outline-variant/30 gap-6">
            <div className="flex gap-3 overflow-x-auto w-full md:w-auto hide-scrollbar">
              {CONTENT_FILTERS.map(({ key, label }) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => setContentFilter(key)}
                  className={
                    contentFilter === key
                      ? 'bg-primary text-on-primary px-6 py-2 font-label text-label-md uppercase tracking-wider whitespace-nowrap'
                      : 'border border-outline-variant/50 text-on-surface-variant px-6 py-2 font-label text-label-md uppercase tracking-wider whitespace-nowrap hover:border-primary hover:text-primary transition-all'
                  }
                >
                  {label}
                </button>
              ))}
            </div>
          </section>
        )}

        {loading && (
          <div className="flex items-center justify-center gap-2 py-24 text-on-surface-variant font-body">
            <span className="material-symbols-outlined animate-spin text-primary">progress_activity</span>
            Yükleniyor...
          </div>
        )}

        {!loading && error && (
          <p className="text-error font-body text-center py-12">{error}</p>
        )}

        {!loading && !error && filtered.length === 0 && (
          <div className="flex flex-col items-center justify-center py-32 border border-dashed border-outline-variant/30 bg-surface-container-lowest/50">
            <div className="w-24 h-24 rounded-full border-2 border-primary/30 flex items-center justify-center mb-6">
              <span className="material-symbols-outlined text-primary text-5xl">movie_edit</span>
            </div>
            <h3 className="font-headline text-headline-lg text-on-surface mb-2">
              {items.length === 0 ? 'Listeniz henüz boş' : 'Bu filtrede içerik yok'}
            </h3>
            <p className="font-body text-on-surface-variant mb-8 max-w-sm text-center">
              {items.length === 0
                ? 'Henüz hiçbir içeriği listenize eklemediniz.'
                : 'Farklı bir filtre seçmeyi deneyin.'}
            </p>
            {items.length === 0 && (
              <Link
                to="/home"
                className="bg-primary text-on-primary px-10 py-3 font-label text-label-md uppercase tracking-widest hover:bg-primary-container transition-colors"
              >
                Film Keşfet
              </Link>
            )}
          </div>
        )}

        {!loading && filtered.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-gutter">
            {filtered.map((item) => (
              <div key={item.id} className="poster-card flex flex-col group">
                <div className="relative aspect-[2/3] overflow-hidden border border-outline-variant/30 group-hover:border-primary transition-all duration-300">
                  <Link to={`/movies/${item.id}`} className="block w-full h-full">
                    <img
                      alt={item.title}
                      src={posterSrc(item.poster_url)}
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                    />
                  </Link>
                  <span className="material-symbols-outlined material-symbols-filled absolute top-3 right-3 text-primary z-10 pointer-events-none">
                    bookmark
                  </span>
                  <div className="poster-overlay absolute inset-0 flex flex-col justify-end p-4 md:p-6 gap-4 z-20">
                    <div className="mb-2">
                      <h4 className="font-label text-primary text-lg uppercase leading-tight mb-1">
                        {item.title}
                      </h4>
                      <p className="text-on-surface-variant text-sm">
                        {item.release_year || '—'} • {firstGenre(item.genres)}
                      </p>
                    </div>
                    <div className="flex flex-col gap-2">
                      <button
                        type="button"
                        onClick={(e) => handleWatch(item.title, e)}
                        className="w-full bg-primary text-on-primary py-2.5 flex items-center justify-center gap-2 font-label text-label-md uppercase tracking-wider active:scale-95 transition-transform"
                      >
                        <span className="material-symbols-outlined material-symbols-filled text-sm">
                          play_arrow
                        </span>
                        İzle
                      </button>
                      <button
                        type="button"
                        disabled={removingId === item.id}
                        onClick={(e) => handleRemove(item.id, e)}
                        className="w-full border border-on-error/30 text-on-error-container py-2.5 flex items-center justify-center gap-2 font-label text-label-md uppercase tracking-wider hover:bg-on-error/10 transition-colors disabled:opacity-50"
                      >
                        <span className="material-symbols-outlined text-sm">close</span>
                        {removingId === item.id ? 'Çıkarılıyor...' : 'Listeden Çıkar'}
                      </button>
                    </div>
                  </div>
                </div>
                <Link to={`/movies/${item.id}`} className="mt-4 block">
                  <h3 className="font-label text-label-md text-on-surface tracking-wide truncate uppercase">
                    {item.title}
                  </h3>
                  <p className="text-on-surface-variant font-label text-xs mt-1">
                    {item.release_year || '—'}
                  </p>
                </Link>
              </div>
            ))}
          </div>
        )}
      </main>

      <Footer />
    </div>
  )
}
