import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import { searchMovies } from '../services/api'
import { displayRatingLabel, firstGenre, posterSrc } from '../utils/movie'

const CONTENT_FILTERS = [
  { key: 'Tümü', apiValue: '' },
  { key: 'Filmler', apiValue: 'Movie' },
  { key: 'Diziler', apiValue: 'TV Show' },
]

const GENRE_CHIPS = [
  'Bilim Kurgu',
  'Aksiyon',
  'Gerilim',
  'Dram',
  'Komedi',
  'Romantik',
  'Macera',
  'Belgesel',
]

const genreEnglishMap = {
  'Bilim Kurgu': 'Science Fiction',
  Aksiyon: 'Action',
  Gerilim: 'Thriller',
  Dram: 'Drama',
  Komedi: 'Comedy',
  Romantik: 'Romance',
  Macera: 'Adventure',
  Belgesel: 'Documentary',
}

const SORT_OPTIONS = ['Alaka', 'Puan', 'Yıl']
const PAGE_SIZE = 24

function matchesGenre(movie, chipLabel) {
  const english = genreEnglishMap[chipLabel] || chipLabel
  return movie.genres?.toLowerCase().includes(english.toLowerCase())
}

export default function SearchPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const inputRef = useRef(null)

  const initialQuery = searchParams.get('q') || ''

  const [query, setQuery] = useState(initialQuery)
  const [allResults, setAllResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(initialQuery.length >= 2)
  const [contentFilter, setContentFilter] = useState('Tümü')
  const [selectedGenre, setSelectedGenre] = useState(null)
  const [sortBy, setSortBy] = useState('Alaka')
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  useEffect(() => {
    const q = searchParams.get('q') || ''
    if (q !== query) setQuery(q)
  }, [searchParams])

  useEffect(() => {
    if (query.trim().length < 2) {
      setAllResults([])
      setHasSearched(false)
      setLoading(false)
      return
    }

    setLoading(true)
    const timer = setTimeout(async () => {
      try {
        const filter = CONTENT_FILTERS.find((f) => f.key === contentFilter)
        const { data } = await searchMovies(query.trim(), filter?.apiValue || '')
        setAllResults(Array.isArray(data) ? data : [])
        setHasSearched(true)
        setVisibleCount(PAGE_SIZE)
      } catch {
        setAllResults([])
        setHasSearched(true)
      } finally {
        setLoading(false)
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [query, contentFilter])

  useEffect(() => {
    const trimmed = query.trim()
    if (trimmed.length >= 2) {
      setSearchParams({ q: trimmed }, { replace: true })
    } else if (searchParams.get('q')) {
      setSearchParams({}, { replace: true })
    }
  }, [query, setSearchParams])

  const filteredResults = useMemo(() => {
    let list = [...allResults]
    if (selectedGenre) {
      list = list.filter((m) => matchesGenre(m, selectedGenre))
    }
    if (sortBy === 'Puan') {
      list.sort((a, b) => {
        const ra = a.letterboxd_rating ?? 0
        const rb = b.letterboxd_rating ?? 0
        return rb - ra
      })
    } else if (sortBy === 'Yıl') {
      list.sort((a, b) => (b.release_year ?? 0) - (a.release_year ?? 0))
    }
    return list
  }, [allResults, selectedGenre, sortBy])

  const visibleResults = filteredResults.slice(0, visibleCount)
  const hasMore = visibleCount < filteredResults.length

  const handleClear = () => {
    setQuery('')
    setAllResults([])
    setHasSearched(false)
    setSelectedGenre(null)
    setVisibleCount(PAGE_SIZE)
    setSearchParams({}, { replace: true })
    inputRef.current?.focus()
  }

  const handleGenreChip = (chip) => {
    setSelectedGenre((prev) => (prev === chip ? null : chip))
    setVisibleCount(PAGE_SIZE)
  }

  const handleContentFilter = (key) => {
    setContentFilter(key)
    setVisibleCount(PAGE_SIZE)
  }

  const handleSortChange = (value) => {
    setSortBy(value)
    setVisibleCount(PAGE_SIZE)
  }

  const handleSuggestionClick = (chip) => {
    const english = genreEnglishMap[chip] || chip
    setQuery(english.split(' ')[0])
    setSelectedGenre(chip)
    inputRef.current?.focus()
  }

  useEffect(() => {
    setVisibleCount(PAGE_SIZE)
  }, [selectedGenre, sortBy])

  const trimmedQuery = query.trim()
  const showEmptyPrompt = trimmedQuery.length < 2 && !loading
  const showNoResults = hasSearched && !loading && trimmedQuery.length >= 2 && filteredResults.length === 0

  return (
    <div className="min-h-screen bg-background text-on-background flex flex-col relative">
      <div className="film-grain" />
      <Navbar active="search" />

      <main className="flex-grow w-full max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-12 flex flex-col gap-12 pt-28">
        {/* Search Header */}
        <section className="flex flex-col gap-6">
          <div className="relative w-full max-w-4xl mx-auto">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-primary">
              <span className="material-symbols-outlined text-[24px]">search</span>
            </div>
            <input
              ref={inputRef}
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Film, dizi, yönetmen, oyuncu ara..."
              className="w-full h-14 bg-surface-container text-on-surface font-body text-body-lg pl-12 pr-12 rounded-t border-0 border-b-2 border-primary focus:ring-0 focus:border-primary-container focus:bg-surface-container-high transition-colors outline-none"
            />
            {query && (
              <button
                type="button"
                onClick={handleClear}
                className="absolute inset-y-0 right-0 pr-4 flex items-center text-on-surface-variant hover:text-on-surface transition-colors"
                aria-label="Temizle"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            )}
          </div>

          {hasSearched && trimmedQuery.length >= 2 && !loading && (
            <div className="text-center">
              <p className="font-body text-body-md text-on-surface-variant">
                &ldquo;{trimmedQuery}&rdquo; için{' '}
                <span className="text-primary font-semibold">
                  {filteredResults.length} sonuç bulundu
                </span>
              </p>
            </div>
          )}
        </section>

        {/* Empty prompt — no search yet */}
        {showEmptyPrompt && (
          <section className="flex flex-col items-center justify-center py-16 gap-8">
            <p className="font-headline text-headline-mobile md:text-headline-lg text-on-surface-variant">
              Ne aramak istersiniz?
            </p>
            <div className="flex flex-wrap justify-center gap-3 max-w-2xl">
              {GENRE_CHIPS.slice(0, 6).map((chip) => (
                <button
                  key={chip}
                  type="button"
                  onClick={() => handleSuggestionClick(chip)}
                  className="px-4 py-2 rounded-full border border-primary text-primary font-label text-label-md hover:bg-primary hover:text-on-primary-fixed transition-colors duration-300"
                >
                  {chip}
                </button>
              ))}
            </div>
          </section>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center gap-2 py-12 text-on-surface-variant font-body">
            <span className="material-symbols-outlined animate-spin text-primary">progress_activity</span>
            Aranıyor...
          </div>
        )}

        {/* No results */}
        {showNoResults && (
          <section className="flex flex-col items-center justify-center py-16 gap-6 text-center">
            <h2 className="font-headline text-headline-lg text-on-surface uppercase">Sonuç bulunamadı</h2>
            <p className="font-body text-body-md text-on-surface-variant max-w-md">
              &ldquo;{trimmedQuery}&rdquo; için herhangi bir içerik bulunamadı
            </p>
            <Link
              to="/home"
              className="bg-primary text-on-primary px-8 py-3 font-label text-label-md uppercase tracking-widest hover:bg-primary-container transition-colors"
            >
              Keşfet&apos;e Dön
            </Link>
          </section>
        )}

        {/* Filters + Results */}
        {hasSearched && trimmedQuery.length >= 2 && !loading && filteredResults.length > 0 && (
          <>
            <section className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-y border-outline-variant/30 py-4">
              <div className="flex bg-surface-container-low rounded-lg p-1 border border-outline-variant/20">
                {CONTENT_FILTERS.map(({ key }) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => handleContentFilter(key)}
                    className={
                      contentFilter === key
                        ? 'font-label text-label-md px-6 py-2 rounded bg-surface-container-highest text-primary shadow-sm'
                        : 'font-label text-label-md px-6 py-2 rounded text-on-surface-variant hover:text-on-surface transition-colors'
                    }
                  >
                    {key}
                  </button>
                ))}
              </div>

              <div className="flex-grow overflow-x-auto hide-scrollbar w-full md:w-auto">
                <div className="flex gap-2 min-w-max px-2">
                  {GENRE_CHIPS.map((chip) => (
                    <button
                      key={chip}
                      type="button"
                      onClick={() => handleGenreChip(chip)}
                      className={
                        selectedGenre === chip
                          ? 'font-label text-[12px] px-4 py-1.5 rounded-full bg-primary text-on-primary border border-primary'
                          : 'font-label text-[12px] px-4 py-1.5 rounded-full bg-surface-container text-on-surface-variant border border-outline-variant/30 hover:border-primary/50 transition-colors'
                      }
                    >
                      {chip}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0">
                <span className="font-label text-label-md text-on-surface-variant">Sırala:</span>
                <select
                  value={sortBy}
                  onChange={(e) => handleSortChange(e.target.value)}
                  className="bg-surface-container text-on-surface font-label text-label-md border border-outline-variant/30 rounded py-2 pl-4 pr-8 focus:ring-0 focus:border-primary focus:outline-none appearance-none cursor-pointer"
                >
                  {SORT_OPTIONS.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              </div>
            </section>

            <section className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-x-4 gap-y-10">
              {visibleResults.map((movie) => {
                const rating = displayRatingLabel(movie)
                const genre = firstGenre(movie.genres)
                return (
                  <article key={movie.id} className="flex flex-col gap-3 group">
                    <button
                      type="button"
                      onClick={() => navigate(`/movies/${movie.id}`)}
                      className="text-left"
                    >
                      <div className="relative w-full aspect-[2/3] rounded bg-surface-container overflow-hidden search-card-hover">
                        <img
                          alt={movie.title}
                          src={posterSrc(movie.poster_url)}
                          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                        />
                        {rating && (
                          <div className="absolute top-2 right-2 bg-surface-container/90 backdrop-blur-sm border border-primary/50 text-primary font-label text-[12px] px-2 py-1 rounded flex items-center gap-1">
                            <span className="material-symbols-outlined material-symbols-filled text-[14px]">
                              star
                            </span>
                            {rating}
                          </div>
                        )}
                        <div className="absolute inset-0 bg-gradient-to-t from-background/90 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
                          <span className="w-full bg-primary/90 text-on-primary-fixed py-2 rounded-sm font-label text-xs uppercase backdrop-blur-sm text-center">
                            İncele
                          </span>
                        </div>
                      </div>
                      <div className="flex flex-col gap-1 mt-3">
                        <h3 className="font-title text-title-md text-on-surface line-clamp-1 group-hover:text-primary transition-colors">
                          {movie.title}
                        </h3>
                        <div className="flex items-center gap-2 font-label text-[12px] text-on-surface-variant">
                          <span>{movie.release_year || '—'}</span>
                          <span className="w-1 h-1 rounded-full bg-outline-variant/50" />
                          <span className="px-2 py-0.5 rounded bg-secondary-container/30 text-secondary truncate">
                            {genre}
                          </span>
                        </div>
                      </div>
                    </button>
                  </article>
                )
              })}
            </section>

            {hasMore && (
              <div className="flex justify-center pb-8">
                <button
                  type="button"
                  onClick={() => setVisibleCount((prev) => prev + PAGE_SIZE)}
                  className="border border-primary text-primary px-10 py-3 font-label text-label-md uppercase tracking-widest hover:bg-primary hover:text-on-primary transition-colors"
                >
                  Daha Fazla Yükle
                </button>
              </div>
            )}
          </>
        )}
      </main>

      <Footer />
    </div>
  )
}
