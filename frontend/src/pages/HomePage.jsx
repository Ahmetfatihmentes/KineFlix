import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import { addToWatchlist, searchMovies } from '../services/api'
import {
  displayOverview,
  displayRatingLabel,
  firstGenre,
  genreSubtitle,
  movieRatingScore,
  posterSrc,
} from '../utils/movie'

const MOODS = [
  { key: 'Duygusal', emoji: '🎭' },
  { key: 'Heyecanlı', emoji: '⚡' },
  { key: 'Eğlenceli', emoji: '😂' },
  { key: 'Düşündürücü', emoji: '🤔' },
  { key: 'Gerilimli', emoji: '😰' },
  { key: 'Epik', emoji: '🌍' },
]

const moodGenreMap = {
  Duygusal: 'Drama',
  Heyecanlı: 'Action',
  Eğlenceli: 'Comedy',
  Düşündürücü: 'Science Fiction',
  Gerilimli: 'Thriller',
  Epik: 'Adventure',
}

const GENRE_PILLS = [
  'Gerilim',
  'Dram',
  'Komedi',
  'Aksiyon',
  'Bilim Kurgu',
  'Romantik',
  'Belgesel',
  'Animasyon',
]

const genrePillToMood = {
  Gerilim: 'Gerilimli',
  Dram: 'Duygusal',
  Komedi: 'Eğlenceli',
  Aksiyon: 'Heyecanlı',
  'Bilim Kurgu': 'Düşündürücü',
}

const genrePillToEnglish = {
  Romantik: 'Romance',
  Belgesel: 'Documentary',
  Animasyon: 'Animation',
}

function matchesGenre(movie, genreNeedle) {
  return movie.genres?.toLowerCase().includes(genreNeedle.toLowerCase())
}

export default function HomePage() {
  const [allMovies, setAllMovies] = useState([])
  const [selectedMood, setSelectedMood] = useState(null)
  const [selectedGenrePill, setSelectedGenrePill] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [watchlistLoading, setWatchlistLoading] = useState(false)
  const [featuredInWatchlist, setFeaturedInWatchlist] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError('')
      try {
        const { data } = await searchMovies('', 'Movie')
        if (!cancelled) setAllMovies(Array.isArray(data) ? data : [])
      } catch {
        if (!cancelled) setError('İçerik yüklenemedi, lütfen tekrar deneyin.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [])

  const filteredMovies = useMemo(() => {
    if (selectedMood) {
      const genre = moodGenreMap[selectedMood]
      return allMovies.filter((m) => matchesGenre(m, genre))
    }
    if (selectedGenrePill) {
      const mood = genrePillToMood[selectedGenrePill]
      if (mood) {
        const genre = moodGenreMap[mood]
        return allMovies.filter((m) => matchesGenre(m, genre))
      }
      const english = genrePillToEnglish[selectedGenrePill]
      if (english) {
        return allMovies.filter((m) => matchesGenre(m, english))
      }
    }
    return allMovies
  }, [allMovies, selectedMood, selectedGenrePill])

  const featured = filteredMovies[0]
  const secondaryMovies = filteredMovies.slice(1, 5)

  const trendingMovies = useMemo(
    () =>
      [...allMovies]
        .sort((a, b) => movieRatingScore(b) - movieRatingScore(a))
        .slice(0, 6),
    [allMovies],
  )

  const handleMoodClick = (moodKey) => {
    setSelectedGenrePill(null)
    setSelectedMood((prev) => (prev === moodKey ? null : moodKey))
  }

  const handleGenrePillClick = (pill) => {
    if (genrePillToMood[pill]) {
      const mood = genrePillToMood[pill]
      setSelectedGenrePill(null)
      setSelectedMood((prev) => (prev === mood ? null : mood))
      return
    }
    setSelectedMood(null)
    setSelectedGenrePill((prev) => (prev === pill ? null : pill))
  }

  const handleWatch = (title) => {
    const query = encodeURIComponent(title || '')
    window.open(`https://www.justwatch.com/tr/search?q=${query}`, '_blank')
  }

  const handleAddToWatchlist = async () => {
    if (!featured || featuredInWatchlist) return
    setWatchlistLoading(true)
    try {
      await addToWatchlist(featured.id)
      setFeaturedInWatchlist(true)
    } catch {
      setError('Listeye eklenemedi.')
    } finally {
      setWatchlistLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background relative flex flex-col">
        <div className="film-grain" />
        <Navbar active="discover" />
        <div className="flex-1 flex items-center justify-center gap-2 text-on-surface-variant font-body">
          <span className="material-symbols-outlined animate-spin text-primary">progress_activity</span>
          Yükleniyor...
        </div>
      </div>
    )
  }

  if (error && allMovies.length === 0) {
    return (
      <div className="min-h-screen bg-background relative flex flex-col">
        <div className="film-grain" />
        <Navbar active="discover" />
        <div className="flex-1 flex items-center justify-center">
          <p className="text-error font-body">{error}</p>
        </div>
        <Footer />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background text-on-background relative flex flex-col antialiased">
      <div className="film-grain" />
      <Navbar active="discover" />

      <main className="flex-grow pt-[100px] pb-gutter w-full max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop">
        {/* Mood Selector */}
        <section className="py-12 md:py-20 flex flex-col items-center text-center">
          <h1 className="font-headline text-headline-mobile md:font-display md:text-display-lg text-on-surface mb-8">
            BUGÜN NE İZLEMEK İSTİYORSUN?
          </h1>
          <div className="flex flex-wrap justify-center gap-4 max-w-4xl mx-auto">
            {MOODS.map(({ key, emoji }) => (
              <button
                key={key}
                type="button"
                onClick={() => handleMoodClick(key)}
                className={
                  selectedMood === key
                    ? 'px-6 py-3 rounded-full bg-primary border border-primary text-surface font-label text-label-md flex items-center gap-2 shadow-[0_0_15px_rgba(201,168,76,0.3)] scale-105 transition-all'
                    : 'px-6 py-3 rounded-full bg-surface-container-high border border-outline-variant/50 hover:border-primary text-on-surface hover:text-primary transition-all duration-300 font-label text-label-md flex items-center gap-2'
                }
              >
                <span className="text-xl">{emoji}</span>
                {key}
              </button>
            ))}
          </div>
        </section>

        {/* Senin İçin Seçtiklerim */}
        <section className="py-12">
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-2">
              <span className="material-symbols-outlined material-symbols-filled text-primary text-3xl">
                smart_toy
              </span>
              <h2 className="font-headline text-headline-mobile md:text-headline-lg text-on-surface">
                SENİN İÇİN SEÇTİKLERİM
              </h2>
            </div>
            <p className="font-body text-body-lg text-on-surface-variant">
              Zevklerine göre kişisel öneriler
              {selectedMood ? ` • ${selectedMood}` : ''}
            </p>
          </div>

          {featured ? (
            <>
              <div className="flex flex-col md:flex-row bg-surface-container-low border border-outline-variant/50 rounded-lg overflow-hidden group mb-12 hover:border-primary/50 transition-colors duration-500">
                <Link
                  to={`/movies/${featured.id}`}
                  className="w-full md:w-2/5 aspect-[16/9] md:aspect-auto md:min-h-[400px] relative overflow-hidden block"
                >
                  <img
                    alt={featured.title}
                    src={posterSrc(featured.poster_url)}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t md:bg-gradient-to-r from-surface-container-low to-transparent pointer-events-none" />
                </Link>
                <div className="w-full md:w-3/5 p-8 md:p-12 flex flex-col justify-center">
                  <div className="flex gap-2 mb-4 flex-wrap">
                    <span className="px-2 py-1 bg-[#1E3A5F] text-inverse-surface font-label text-xs uppercase rounded-sm">
                      {firstGenre(featured.genres)}
                    </span>
                    {displayRatingLabel(featured) && (
                      <span className="px-2 py-1 bg-surface-container-high border border-primary/50 text-primary font-label text-xs uppercase rounded-sm">
                        Puan {displayRatingLabel(featured)}
                      </span>
                    )}
                  </div>
                  <h3 className="font-headline text-headline-mobile md:text-headline-lg text-on-surface mb-4 uppercase">
                    {featured.title}
                  </h3>
                  <p className="font-body text-body-md text-on-surface-variant mb-8 line-clamp-3 md:line-clamp-4">
                    {displayOverview(featured) || 'Özet mevcut değil.'}
                  </p>
                  <div className="border border-primary/30 bg-primary/5 p-4 rounded-sm mb-8 relative before:content-[''] before:absolute before:-left-px before:top-4 before:bottom-4 before:w-0.5 before:bg-primary">
                    <h4 className="font-label text-primary mb-1 text-xs uppercase tracking-widest">
                      NEDEN ÖNERİLDİ?
                    </h4>
                    <p className="font-body text-sm text-on-surface-variant italic">
                      Türünde yüksek puan alan ve çok izlenen bir yapım
                    </p>
                  </div>
                  <div className="flex flex-col sm:flex-row gap-4 mt-auto">
                    <button
                      type="button"
                      onClick={() => handleWatch(featured.title)}
                      className="bg-primary text-on-primary-fixed px-8 py-3 rounded-sm font-label text-label-md uppercase hover:bg-primary-fixed transition-colors flex items-center justify-center gap-2 shadow-[0_0_10px_rgba(201,168,76,0.2)]"
                    >
                      <span className="material-symbols-outlined material-symbols-filled">play_arrow</span>
                      İzle
                    </button>
                    <button
                      type="button"
                      onClick={handleAddToWatchlist}
                      disabled={watchlistLoading || featuredInWatchlist}
                      className="border border-[#1E3A5F] text-on-surface px-8 py-3 rounded-sm font-label text-label-md uppercase hover:bg-surface-container-highest transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                      <span className="material-symbols-outlined">
                        {featuredInWatchlist ? 'check' : 'add'}
                      </span>
                      {featuredInWatchlist ? 'Listemde' : 'Listeye Ekle'}
                    </button>
                  </div>
                </div>
              </div>

              {secondaryMovies.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  {secondaryMovies.map((movie, index) => (
                    <Link
                      key={movie.id}
                      to={`/movies/${movie.id}`}
                      className={`group cursor-pointer ${index >= 2 ? 'hidden md:block' : ''}`}
                    >
                      <div className="aspect-[2/3] relative rounded-sm overflow-hidden mb-3 border border-outline-variant/30 group-hover:border-primary/70 transition-colors duration-300">
                        <img
                          alt={movie.title}
                          src={posterSrc(movie.poster_url)}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-background/90 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
                          <span className="w-full bg-primary/90 text-on-primary-fixed py-2 rounded-sm font-label text-xs uppercase backdrop-blur-sm text-center">
                            İncele
                          </span>
                        </div>
                      </div>
                      <h4 className="font-title text-title-md text-on-surface group-hover:text-primary transition-colors truncate">
                        {movie.title}
                      </h4>
                      <p className="font-label text-xs text-on-surface-variant/70 mt-1 uppercase">
                        {genreSubtitle(movie.genres)}
                      </p>
                    </Link>
                  ))}
                </div>
              )}
            </>
          ) : (
            <p className="font-body text-on-surface-variant py-8 text-center">
              Bu mood için film bulunamadı. Başka bir mood deneyin.
            </p>
          )}
        </section>

        {/* Bu Hafta Trend */}
        {trendingMovies.length > 0 && (
          <section className="py-12 md:py-16">
            <h2 className="font-headline text-headline-mobile md:text-headline-lg text-on-surface mb-8 uppercase">
              Bu Hafta Trend
            </h2>
            <div className="flex overflow-x-auto gap-6 pb-8 hide-scrollbar snap-x snap-mandatory">
              {trendingMovies.map((movie, index) => (
                <Link
                  key={movie.id}
                  to={`/movies/${movie.id}`}
                  className="min-w-[200px] md:min-w-[240px] snap-start relative group cursor-pointer"
                >
                  <span className="absolute -left-4 -top-6 font-display text-[80px] leading-none text-primary/80 z-10 drop-shadow-md group-hover:text-primary transition-colors">
                    {String(index + 1).padStart(2, '0')}
                  </span>
                  <div className="aspect-[2/3] relative rounded-sm overflow-hidden border border-outline-variant/30 group-hover:border-primary/50 transition-colors z-0">
                    <img
                      alt={movie.title}
                      src={posterSrc(movie.poster_url)}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent opacity-80" />
                    <div className="absolute bottom-4 left-4 right-4">
                      <h4 className="font-title text-title-md text-on-surface truncate">{movie.title}</h4>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Türe Göre Keşfet */}
        <section className="py-12 border-t border-outline-variant/20">
          <h2 className="font-headline text-headline-mobile md:text-headline-lg text-on-surface mb-8 text-center md:text-left uppercase">
            Türe Göre Keşfet
          </h2>
          <div className="flex flex-wrap justify-center md:justify-start gap-4">
            {GENRE_PILLS.map((pill) => {
              const mood = genrePillToMood[pill]
              const isActive =
                (mood && selectedMood === mood) ||
                (selectedGenrePill === pill && !mood)
              return (
                <button
                  key={pill}
                  type="button"
                  onClick={() => handleGenrePillClick(pill)}
                  className={
                    isActive
                      ? 'px-6 py-2 rounded-full bg-primary text-on-primary-fixed font-label text-label-md transition-colors duration-300'
                      : 'px-6 py-2 rounded-full border border-primary text-primary font-label text-label-md hover:bg-primary hover:text-on-primary-fixed transition-colors duration-300'
                  }
                >
                  {pill}
                </button>
              )
            })}
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}
