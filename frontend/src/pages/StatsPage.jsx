import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import { getWatchHistory, getWatchlist } from '../services/api'
import { displayRatingLabel, genreSubtitle, posterSrc } from '../utils/movie'

const GENRE_TR = {
  Thriller: 'GERİLİM',
  Drama: 'DRAM',
  Action: 'AKSİYON',
  Comedy: 'KOMEDİ',
  'Science Fiction': 'BİLİM KURGU',
  Romance: 'ROMANTİK',
  Horror: 'KORKU',
  Adventure: 'MACERA',
  Documentary: 'BELGESEL',
  Animation: 'ANİMASYON',
  Crime: 'SUÇ',
  Mystery: 'GİZEM',
  Fantasy: 'FANTASTİK',
  War: 'SAVAŞ',
  Music: 'MÜZİK',
  History: 'TARİH',
}

const MONTH_LABELS = ['O', 'Ş', 'M', 'N', 'M', 'H', 'T', 'A', 'E', 'E', 'K', 'A']
const DONUT_COLORS = ['text-primary', 'text-primary-fixed', 'text-primary-fixed-dim', 'text-outline', 'text-outline-variant']

function genreDisplayName(genre) {
  return GENRE_TR[genre] || genre.toUpperCase()
}

function computeTopGenres(watchHistory) {
  const genreCounts = {}
  watchHistory.forEach((item) => {
    item.genres?.split(',').forEach((g) => {
      const genre = g.trim()
      if (genre) genreCounts[genre] = (genreCounts[genre] || 0) + 1
    })
  })
  const total = Object.values(genreCounts).reduce((a, b) => a + b, 0)
  return Object.entries(genreCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([genre, count]) => ({
      genre,
      displayName: genreDisplayName(genre),
      count,
      percent: total ? Math.round((count / total) * 100) : 0,
    }))
}

function computeDecades(watchHistory) {
  const decadeCounts = {}
  watchHistory.forEach((m) => {
    if (!m.release_year) return
    const decade = Math.floor(m.release_year / 10) * 10
    const label = `${decade}'ler`
    decadeCounts[label] = (decadeCounts[label] || 0) + 1
  })
  const total = Object.values(decadeCounts).reduce((a, b) => a + b, 0)
  return Object.entries(decadeCounts)
    .sort((a, b) => b[0].localeCompare(a[0]))
    .map(([label, count], index) => ({
      label,
      count,
      percent: total ? Math.round((count / total) * 100) : 0,
      colorClass: DONUT_COLORS[index % DONUT_COLORS.length],
    }))
}

function computeMonthlyActivity(watchHistory) {
  const monthlyActivity = {}
  watchHistory.forEach((m) => {
    if (!m.watched_at) return
    const date = new Date(m.watched_at)
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    monthlyActivity[key] = (monthlyActivity[key] || 0) + 1
  })

  const last12Months = Array.from({ length: 12 }, (_, i) => {
    const d = new Date()
    d.setMonth(d.getMonth() - (11 - i))
    return {
      key: `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`,
      monthIndex: d.getMonth(),
      year: d.getFullYear(),
    }
  })

  return last12Months.map(({ key, monthIndex, year }) => ({
    key,
    monthIndex,
    year,
    count: monthlyActivity[key] || 0,
  }))
}

function CornerAccents() {
  return (
    <>
      <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-primary/50" />
      <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-primary/50" />
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-primary/50" />
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-primary/50" />
    </>
  )
}

export default function StatsPage() {
  const [watchHistory, setWatchHistory] = useState([])
  const [watchlist, setWatchlist] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError('')
      try {
        const [historyRes, watchlistRes] = await Promise.all([
          getWatchHistory(),
          getWatchlist(),
        ])
        if (cancelled) return
        setWatchHistory(Array.isArray(historyRes.data) ? historyRes.data : [])
        setWatchlist(Array.isArray(watchlistRes.data) ? watchlistRes.data : [])
      } catch {
        if (!cancelled) setError('İstatistikler yüklenemedi.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [])

  const totalWatched = watchHistory.length
  const totalMinutes = watchHistory.reduce((sum, m) => sum + (m.runtime || 0), 0)
  const totalHours = Math.round(totalMinutes / 60)
  const ratedMovies = watchHistory.filter((m) => m.letterboxd_rating != null)
  const avgRating = ratedMovies.length
    ? (ratedMovies.reduce((sum, m) => sum + m.letterboxd_rating, 0) / ratedMovies.length).toFixed(1)
    : '—'
  const totalWatchlist = watchlist.length

  const topGenres = useMemo(() => computeTopGenres(watchHistory), [watchHistory])
  const decades = useMemo(() => computeDecades(watchHistory), [watchHistory])
  const decadesWithOffset = useMemo(() => {
    let offset = 0
    return decades.map((d) => {
      const segment = { ...d, offset }
      offset += d.percent
      return segment
    })
  }, [decades])
  const activityData = useMemo(() => computeMonthlyActivity(watchHistory), [watchHistory])
  const maxActivity = Math.max(...activityData.map((d) => d.count), 1)

  const movieCount = watchHistory.filter((m) => m.content_type !== 'TV Show').length
  const showCount = watchHistory.filter((m) => m.content_type === 'TV Show').length
  const moviePct = totalWatched ? Math.round((movieCount / totalWatched) * 100) : 0
  const showPct = totalWatched ? 100 - moviePct : 0

  const topRated = useMemo(
    () =>
      [...watchHistory]
        .filter((m) => m.letterboxd_rating != null)
        .sort((a, b) => b.letterboxd_rating - a.letterboxd_rating)
        .slice(0, 5),
    [watchHistory],
  )

  const dominantDecade = decades[0]

  const activityYear =
    activityData.length > 0 ? activityData[activityData.length - 1].year : new Date().getFullYear()

  if (loading) {
    return (
      <div className="min-h-screen bg-background relative flex flex-col">
        <div className="film-grain" />
        <Navbar active="stats" />
        <div className="flex-1 flex items-center justify-center gap-2 text-on-surface-variant font-body pt-24">
          <span className="material-symbols-outlined animate-spin text-primary">progress_activity</span>
          Yükleniyor...
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background relative flex flex-col">
        <div className="film-grain" />
        <Navbar active="stats" />
        <div className="flex-1 flex items-center justify-center pt-24">
          <p className="text-error font-body">{error}</p>
        </div>
        <Footer />
      </div>
    )
  }

  if (totalWatched === 0) {
    return (
      <div className="min-h-screen bg-background relative flex flex-col">
        <div className="film-grain" />
        <Navbar active="stats" />
        <main className="flex-1 flex flex-col items-center justify-center gap-6 pt-24 px-margin-mobile">
          <h2 className="font-headline text-headline-lg text-on-surface uppercase">Henüz istatistik yok</h2>
          <p className="font-body text-on-surface-variant text-center max-w-md">
            Film izlemeye başladığınızda istatistikleriniz burada görünecek.
          </p>
          <Link
            to="/home"
            className="bg-primary text-on-primary px-8 py-3 font-label text-label-md uppercase tracking-widest hover:bg-primary-container transition-colors"
          >
            Film Keşfet
          </Link>
        </main>
        <Footer />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background text-on-background relative overflow-x-hidden">
      <div className="film-grain" />
      <Navbar active="stats" />

      <main className="w-full max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-12 md:py-16 space-y-16 pt-28">
        <div className="flex flex-col gap-base border-b border-outline-variant/30 pb-8">
          <h1 className="font-headline text-headline-mobile md:text-headline-lg text-on-background uppercase">
            İstatistiklerim
          </h1>
          <p className="font-body text-body-lg text-on-surface-variant max-w-2xl">
            Kişisel sinema yolculuğunuzun derinliklerine inin. Analizler, eğilimler ve favorileriniz bir arada.
          </p>
          <p className="font-label text-[12px] text-on-surface-variant/70 uppercase tracking-widest">
            Son 100 izlemeye dayanır
          </p>
        </div>

        {/* Hero Stats */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-gutter">
          {[
            { label: 'İzlenen Film', value: totalWatched },
            {
              label: 'Toplam Süre',
              value: (
                <>
                  {totalHours}
                  <span className="text-2xl ml-1 text-on-surface-variant font-body">Saat</span>
                </>
              ),
            },
            {
              label: 'Ortalama Puan',
              value: (
                <>
                  {avgRating}
                  <span className="text-2xl text-on-surface-variant font-body">/5</span>
                </>
              ),
            },
            { label: 'Listemdeki Film', value: totalWatchlist },
          ].map(({ label, value }) => (
            <div
              key={label}
              className="bg-surface-container rounded border-t-2 border-primary p-6 flex flex-col items-center justify-center text-center shadow-sm relative overflow-hidden group"
            >
              <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <span className="font-label text-label-md text-on-surface-variant mb-2 uppercase tracking-wider">
                {label}
              </span>
              <span className="font-display text-display-lg text-primary leading-none">{value}</span>
            </div>
          ))}
        </section>

        {/* Genre + Decades */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-16">
          <div className="space-y-8 bg-surface p-8 border border-outline-variant/30 rounded relative">
            <CornerAccents />
            <div className="flex items-center justify-between border-b border-outline-variant/20 pb-4">
              <h2 className="font-headline text-headline-mobile text-on-background uppercase">Tür Dağılımı</h2>
              <span className="material-symbols-outlined text-primary/70">movie_filter</span>
            </div>
            <div className="space-y-6">
              {topGenres.map(({ displayName, percent }, index) => (
                <div key={displayName}>
                  <div className="flex justify-between font-label text-label-md mb-2">
                    <span className="text-on-background">{displayName}</span>
                    <span className="text-primary">%{percent}</span>
                  </div>
                  <div className="h-2 w-full bg-surface-container-high rounded-full overflow-hidden">
                    <div
                      className={`h-full bg-primary rounded-full animate-bar ${index >= 4 ? 'bg-primary/60' : ''}`}
                      style={{ width: `${percent}%`, animationDelay: `${index * 0.1}s` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-8 bg-surface p-8 border border-outline-variant/30 rounded relative flex flex-col items-center">
            <CornerAccents />
            <div className="w-full flex items-center justify-between border-b border-outline-variant/20 pb-4">
              <h2 className="font-headline text-headline-mobile text-on-background uppercase">Hangi Dönemden?</h2>
              <span className="material-symbols-outlined text-primary/70">history</span>
            </div>
            {decades.length > 0 ? (
              <>
                <div className="relative w-64 h-64 flex items-center justify-center mt-4">
                  <svg className="w-full h-full transform -rotate-90 drop-shadow-lg" viewBox="0 0 36 36">
                    <path
                      className="text-surface-container-high"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    {decadesWithOffset.map(({ percent, colorClass, label, offset }) => (
                      <path
                        key={label}
                        className={`animate-donut ${colorClass}`}
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="4"
                        strokeDasharray={`${percent} 100`}
                        strokeDashoffset={-offset}
                      />
                    ))}
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                    <span className="font-display text-primary leading-none block">
                      {dominantDecade?.label.replace("'ler", '') || '—'}
                      <span className="text-2xl">s</span>
                    </span>
                    <span className="font-label text-on-surface-variant text-xs tracking-widest mt-1 uppercase">
                      Baskın Dönem
                    </span>
                  </div>
                </div>
                <div className="flex flex-wrap justify-center gap-4 mt-2">
                  {decades.map(({ label, colorClass }) => (
                    <div key={label} className="flex items-center gap-2">
                      <span className={`w-3 h-3 rounded-full bg-current ${colorClass}`} />
                      <span className="font-label text-xs text-on-surface-variant">{label}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <p className="font-body text-on-surface-variant py-12">Yıl bilgisi olan film yok.</p>
            )}
          </div>
        </section>

        {/* Monthly Activity */}
        <section className="space-y-8">
          <div className="flex items-center justify-between border-b border-outline-variant/30 pb-4">
            <h2 className="font-headline text-headline-mobile md:text-headline-lg text-on-background uppercase">
              Aylık Aktivite
            </h2>
            <span className="font-label text-label-md text-on-surface-variant">{activityYear} YILI</span>
          </div>
          <div className="bg-surface-container-low p-8 rounded border border-outline-variant/20 h-64 flex items-end justify-between gap-2 md:gap-6 relative overflow-hidden">
            <div
              className="absolute inset-0 w-full h-full pointer-events-none"
              style={{
                backgroundImage:
                  'linear-gradient(to bottom, transparent 95%, rgba(201, 168, 76, 0.05) 95%)',
                backgroundSize: '100% 25%',
              }}
            />
            <div className="w-full flex justify-between items-end h-full z-10 px-2 md:px-8">
              {activityData.map(({ key, count }) => {
                const heightPct = maxActivity ? (count / maxActivity) * 100 : 0
                const isPeak = count === maxActivity && count > 0
                return (
                  <div
                    key={key}
                    title={`${count} film`}
                    className={`w-1/12 md:w-8 rounded-t transition-colors cursor-pointer ${
                      isPeak
                        ? 'bg-primary'
                        : 'bg-primary-fixed-dim/20 hover:bg-primary'
                    }`}
                    style={{
                      height: `${Math.max(heightPct, count > 0 ? 8 : 2)}%`,
                      boxShadow: isPeak ? '0 0 15px rgba(201,168,76,0.3)' : undefined,
                    }}
                  />
                )
              })}
            </div>
          </div>
          <div className="flex justify-between px-4 md:px-10 mt-2 font-label text-xs text-on-surface-variant uppercase tracking-widest">
            {activityData.map(({ key, monthIndex, count }) => (
              <span key={key} className={count === maxActivity && count > 0 ? 'text-primary' : ''}>
                {MONTH_LABELS[monthIndex]}
              </span>
            ))}
          </div>
        </section>

        {/* Film / Dizi + Top Rated */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-4 space-y-6">
            <div className="flex items-center justify-between border-b border-outline-variant/30 pb-4">
              <h2 className="font-headline text-headline-mobile text-on-background uppercase">
                Film / Dizi
              </h2>
            </div>
            <div className="bg-surface-container p-6 rounded border border-outline-variant/30 space-y-4">
              <div>
                <div className="flex justify-between font-label text-label-md mb-2">
                  <span>Film</span>
                  <span className="text-primary">%{moviePct}</span>
                </div>
                <div className="h-2 bg-surface-container-high rounded-full overflow-hidden">
                  <div className="h-full bg-primary rounded-full" style={{ width: `${moviePct}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between font-label text-label-md mb-2">
                  <span>Dizi</span>
                  <span className="text-secondary">%{showPct}</span>
                </div>
                <div className="h-2 bg-surface-container-high rounded-full overflow-hidden">
                  <div className="h-full bg-secondary-container rounded-full" style={{ width: `${showPct}%` }} />
                </div>
              </div>
              <p className="font-label text-xs text-on-surface-variant pt-2">
                {movieCount} film · {showCount} dizi
              </p>
            </div>
          </div>

          <div className="lg:col-span-8 space-y-6">
            <div className="flex items-center justify-between border-b border-outline-variant/30 pb-4">
              <h2 className="font-headline text-headline-mobile text-on-background uppercase">
                En Yüksek Puanladıklarım
              </h2>
              <Link to="/history" className="font-label text-label-md text-primary hover:underline">
                Tümünü Gör
              </Link>
            </div>
            {topRated.length === 0 ? (
              <p className="font-body text-on-surface-variant">Puanlı film yok.</p>
            ) : (
              <div className="flex flex-col gap-4">
                {topRated.map((movie, index) => (
                  <Link
                    key={movie.id}
                    to={`/movies/${movie.id}`}
                    className="flex items-center gap-6 p-4 bg-surface hover:bg-surface-container-low transition-colors rounded border-l-2 border-transparent hover:border-primary group"
                  >
                    <div className="font-display text-display-lg text-primary opacity-50 group-hover:opacity-100 transition-opacity w-12 text-center">
                      {index + 1}
                    </div>
                    <div className="w-16 h-24 flex-shrink-0 rounded overflow-hidden shadow-md">
                      <img
                        alt={movie.title}
                        src={posterSrc(movie.poster_url)}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="flex-grow min-w-0">
                      <h3 className="font-title text-title-md text-on-background group-hover:text-primary transition-colors truncate">
                        {movie.title}
                      </h3>
                      <p className="font-label text-xs text-on-surface-variant mt-1 uppercase">
                        {movie.release_year || '—'} • {genreSubtitle(movie.genres)}
                      </p>
                      {displayRatingLabel(movie) && (
                        <p className="font-label text-primary mt-2 text-sm">
                          ★ {displayRatingLabel(movie)} / 10
                        </p>
                      )}
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}
