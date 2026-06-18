import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import { getWatchHistory } from '../services/api'
import { formatShortWatchedDate, formatWatchedDate, posterSrc } from '../utils/movie'

const CONTENT_FILTERS = [
  { key: 'all', label: 'Tümü' },
  { key: 'Movie', label: 'Filmler' },
  { key: 'TV Show', label: 'Diziler' },
]

const SORT_OPTIONS = [
  { key: 'newest', label: 'En Yeni' },
  { key: 'oldest', label: 'En Eski' },
]

export default function HistoryPage() {
  const navigate = useNavigate()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [contentFilter, setContentFilter] = useState('all')
  const [sortOrder, setSortOrder] = useState('newest')

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError('')
      try {
        const { data } = await getWatchHistory()
        if (!cancelled) setItems(Array.isArray(data) ? data : [])
      } catch {
        if (!cancelled) setError('İzleme geçmişi yüklenemedi.')
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
    let list = contentFilter === 'all'
      ? [...items]
      : items.filter((item) => item.content_type === contentFilter)

    list.sort((a, b) => {
      const aTime = new Date(a.watched_at).getTime()
      const bTime = new Date(b.watched_at).getTime()
      return sortOrder === 'newest' ? bTime - aTime : aTime - bTime
    })
    return list
  }, [items, contentFilter, sortOrder])

  const movieCount = items.filter((item) => item.content_type !== 'TV Show').length
  const showCount = items.filter((item) => item.content_type === 'TV Show').length

  return (
    <div className="min-h-screen relative flex flex-col">
      <div className="film-grain" />
      <Navbar active="history" />

      <main className="flex-1 max-w-container-max mx-auto w-full px-margin-mobile md:px-margin-desktop pt-28 pb-24">
        <header className="mb-12 flex flex-col md:flex-row justify-between items-end gap-6">
          <div>
            <h1 className="font-display text-display-lg text-on-surface uppercase mb-4">
              İzlediklerim
            </h1>
            {!loading && items.length > 0 && (
              <div className="flex flex-wrap gap-4">
                <div className="px-4 py-2 border border-primary-container rounded flex items-center gap-2 bg-surface-container-high/50">
                  <span className="material-symbols-outlined material-symbols-filled text-primary text-sm">
                    movie
                  </span>
                  <span className="font-label text-label-md text-on-surface">
                    {movieCount} Film İzlendi
                  </span>
                </div>
                <div className="px-4 py-2 border border-primary-container rounded flex items-center gap-2 bg-surface-container-high/50">
                  <span className="material-symbols-outlined material-symbols-filled text-primary text-sm">
                    tv
                  </span>
                  <span className="font-label text-label-md text-on-surface">{showCount} Dizi</span>
                </div>
              </div>
            )}
          </div>
        </header>

        {!loading && items.length > 0 && (
          <section className="sticky top-[72px] z-30 bg-surface/90 backdrop-blur-md py-4 mb-8 border-b border-outline-variant/30 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex gap-2 overflow-x-auto w-full md:w-auto hide-scrollbar">
              {CONTENT_FILTERS.map(({ key, label }) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => setContentFilter(key)}
                  className={
                    contentFilter === key
                      ? 'px-4 py-2 rounded-full font-label text-label-md bg-primary-container text-on-primary-container font-bold whitespace-nowrap'
                      : 'px-4 py-2 rounded-full font-label text-label-md bg-secondary-container text-on-secondary-container border border-transparent hover:border-primary transition-colors whitespace-nowrap'
                  }
                >
                  {label}
                </button>
              ))}
            </div>
            <div className="flex items-center gap-3 w-full md:w-auto justify-end">
              <span className="text-on-surface-variant font-label text-label-md">Sırala:</span>
              <div className="relative">
                <select
                  value={sortOrder}
                  onChange={(e) => setSortOrder(e.target.value)}
                  className="bg-surface-container border-b border-outline-variant text-on-surface font-label text-label-md px-4 py-2 pr-10 focus:border-primary focus:ring-0 appearance-none cursor-pointer"
                >
                  {SORT_OPTIONS.map(({ key, label }) => (
                    <option key={key} value={key}>
                      {label}
                    </option>
                  ))}
                </select>
                <span className="material-symbols-outlined absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant">
                  expand_more
                </span>
              </div>
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
            <div className="w-24 h-24 rounded-full border-2 border-tertiary/30 flex items-center justify-center mb-6">
              <span className="material-symbols-outlined text-tertiary text-5xl">check_circle</span>
            </div>
            <h3 className="font-headline text-headline-lg text-on-surface mb-2">
              {items.length === 0 ? 'Henüz film izlemediniz' : 'Bu filtrede içerik yok'}
            </h3>
            <p className="font-body text-on-surface-variant mb-8 max-w-sm text-center">
              {items.length === 0
                ? 'İzlediğiniz filmler burada görünecek.'
                : 'Farklı bir filtre seçmeyi deneyin.'}
            </p>
            {items.length === 0 && (
              <Link
                to="/home"
                className="bg-primary text-on-primary px-10 py-3 font-label text-label-md uppercase tracking-widest hover:bg-primary-container transition-colors"
              >
                Keşfetmeye Başla
              </Link>
            )}
          </div>
        )}

        {!loading && filtered.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
            {filtered.map((item) => (
              <button
                key={`${item.id}-${item.watched_at}`}
                type="button"
                onClick={() => navigate(`/movies/${item.id}`)}
                className="history-card relative group cursor-pointer aspect-[2/3] rounded overflow-hidden transition-all duration-300 text-left"
              >
                <img
                  alt={item.title}
                  src={posterSrc(item.poster_url)}
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-2 left-2 bg-tertiary-container/90 backdrop-blur-sm rounded-full px-2 py-0.5 border border-tertiary flex items-center gap-1 z-10">
                  <span className="material-symbols-outlined material-symbols-filled text-on-tertiary-container text-xs">
                    check_circle
                  </span>
                  <span className="font-label text-[10px] text-on-tertiary-container uppercase tracking-wide">
                    İzlendi
                  </span>
                </div>
                <div className="absolute inset-0 bg-gradient-to-t from-background via-background/40 to-transparent opacity-80 group-hover:opacity-90 transition-opacity" />
                <div className="absolute bottom-0 left-0 w-full p-4 flex flex-col gap-1 z-10">
                  <h3 className="font-label text-label-md text-on-surface truncate uppercase">
                    {item.title}
                  </h3>
                  <p className="font-label text-[12px] text-on-surface-variant">
                    {item.release_year || '—'}
                  </p>
                  <span className="font-label text-label-md text-on-surface-variant">
                    {formatShortWatchedDate(item.watched_at)}
                  </span>
                  <span className="sr-only">{formatWatchedDate(item.watched_at)}</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </main>

      <Footer />
    </div>
  )
}
