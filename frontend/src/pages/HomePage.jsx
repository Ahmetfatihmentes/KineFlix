import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import AIStrip from '../components/AIStrip'
import Footer from '../components/Footer'
import MovieTicketCard from '../components/MovieTicketCard'
import Navbar from '../components/Navbar'
import { getRecommendations, searchMovies } from '../services/api'
import { formatScore } from '../utils/movie'
import heroBg from '../assets/hero.png'

const FILTER_CHIPS = ['Tümü', 'Aksiyon', 'Drama', 'Bilim Kurgu', 'Gerilim', 'Belgesel']

export default function HomePage() {
  const [movies, setMovies] = useState([])
  const [picks, setPicks] = useState([])
  const [activeFilter, setActiveFilter] = useState('Tümü')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const userGenres = useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem('kineflix_genres') || '[]')
    } catch {
      return []
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError('')
      try {
        const query = userGenres[0]?.slice(0, 3) || 'the'
        const { data } = await searchMovies(query)
        if (cancelled) return
        setMovies(data)
        if (data.length > 0) {
          const recRes = await getRecommendations(data[0].id, 8)
          if (!cancelled) {
            const recData = recRes.data
            if (Array.isArray(recData)) setPicks(recData)
            else if (recData?.status === 'loading') setPicks(data.slice(0, 6))
            else setPicks(data.slice(0, 6))
          }
        }
      } catch {
        if (!cancelled) setError('Filmler yüklenemedi. Backend çalışıyor mu?')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [userGenres])

  const filtered = useMemo(() => {
    if (activeFilter === 'Tümü') return movies
    return movies.filter((m) => m.genres?.toLowerCase().includes(activeFilter.toLowerCase()))
  }, [movies, activeFilter])

  const hero = filtered[0] || movies[0]
  const heroScore = hero ? formatScore(hero) : 96
  const aiMessage =
    userGenres.length > 0
      ? `${userGenres.slice(0, 2).join(' + ')} tercihlerin + yüksek seyirci puanı`
      : 'Bilim Kurgu izleme geçmişin + %94 pozitif seyirci yorumu'

  return (
    <div className="overflow-x-hidden relative min-h-screen">
      <div className="film-grain" />
      <Navbar active="discover" />

      <main className="w-full">
        <section className="relative w-full h-[716px] min-h-[500px] flex items-end pb-12 md:pb-24 pt-32">
          <div className="absolute inset-0 z-0">
            <img alt="" src={heroBg} className="w-full h-full object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-surface via-surface/80 to-transparent" />
          </div>
          <div className="relative z-10 w-full px-margin-mobile md:px-margin-desktop max-w-container-max mx-auto">
            <div className="max-w-3xl">
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-surface/60 backdrop-blur-md border border-primary text-primary font-label text-label-md rounded mb-4">
                <span className="material-symbols-outlined text-[16px] material-symbols-filled">auto_awesome</span>
                Yapay Zeka Uyum Skoru: %{heroScore ?? 96}
              </div>
              {hero ? (
                <>
                  <h1 className="font-display text-display-lg text-on-surface uppercase tracking-wider mb-2 leading-none drop-shadow-lg">
                    {hero.title.split(' ').slice(0, 2).join(' ')}
                    <br />
                    <span className="text-primary">{hero.title.split(' ').slice(2).join(' ') || 'KEŞFET'}</span>
                  </h1>
                  <p className="font-body text-body-lg text-on-surface-variant max-w-xl mt-4 line-clamp-2">
                    {hero.overview}
                  </p>
                  <div className="mt-8 flex flex-wrap gap-4">
                    <Link
                      to={`/movies/${hero.id}`}
                      className="bg-primary text-on-primary font-label text-label-md px-8 py-3 rounded uppercase tracking-wider flex items-center gap-2 hover:bg-primary-fixed transition-colors"
                    >
                      <span className="material-symbols-outlined material-symbols-filled">play_arrow</span>
                      Hemen İzle
                    </Link>
                    <Link
                      to={`/movies/${hero.id}`}
                      className="bg-surface-container/50 backdrop-blur-sm border border-secondary-container text-on-surface font-label text-label-md px-8 py-3 rounded uppercase tracking-wider hover:border-primary transition-colors"
                    >
                      Detaylar
                    </Link>
                  </div>
                </>
              ) : (
                <h1 className="font-display text-display-lg text-on-surface uppercase">KineFlix</h1>
              )}
            </div>
          </div>
        </section>

        <AIStrip message={aiMessage} />

        <section className="py-12 max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop">
          <div className="flex gap-3 overflow-x-auto hide-scrollbar pb-2">
            {FILTER_CHIPS.map((chip) => (
              <button
                key={chip}
                type="button"
                onClick={() => setActiveFilter(chip)}
                className={`px-6 py-2 rounded-full font-label text-label-md border whitespace-nowrap transition-colors ${
                  activeFilter === chip
                    ? 'bg-secondary-container text-on-surface border-primary/50'
                    : 'bg-surface-container text-on-surface-variant border-outline-variant/30 hover:border-primary/50 hover:text-on-surface'
                }`}
              >
                {chip}
              </button>
            ))}
          </div>
        </section>

        <section className="pb-16 max-w-container-max mx-auto pl-margin-mobile md:pl-margin-desktop pr-0 overflow-hidden">
          <div className="flex items-center gap-2 mb-8 pr-margin-mobile md:pr-margin-desktop">
            <h2 className="font-headline text-headline-mobile md:text-headline-lg text-on-surface uppercase tracking-wide">
              Yapay Zeka Seçimleri
            </h2>
            <span className="text-[24px]">🎬</span>
          </div>
          {error && <p className="text-error px-margin-mobile mb-4">{error}</p>}
          {loading ? (
            <p className="font-body text-on-surface-variant px-margin-mobile">Filmler yükleniyor...</p>
          ) : (
            <div className="flex gap-6 overflow-x-auto hide-scrollbar pb-8 pr-margin-mobile md:pr-margin-desktop snap-x">
              {(picks.length ? picks : filtered).map((movie) => (
                <MovieTicketCard key={movie.id} movie={movie} />
              ))}
            </div>
          )}
        </section>
      </main>

      <Footer />
    </div>
  )
}
