import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import { getMe, getWatchHistory, getWatchlist, getLikedMovies, logoutUser, uploadAvatar } from '../services/api'
import { firstGenre, posterSrc } from '../utils/movie'

function computeTopGenres(watchHistory) {
  const genreCounts = {}
  watchHistory.forEach((item) => {
    item.genres?.split(',').forEach((g) => {
      const genre = g.trim()
      if (genre) genreCounts[genre] = (genreCounts[genre] || 0) + 1
    })
  })
  const topGenres = Object.entries(genreCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
  const total = topGenres.reduce((sum, [, count]) => sum + count, 0)
  return { topGenres, total, uniqueGenreCount: Object.keys(genreCounts).length }
}

function formatMemberSince(isoDate) {
  if (!isoDate) return ''
  const date = new Date(isoDate)
  const month = date.toLocaleDateString('tr-TR', { month: 'long' })
  const year = date.getFullYear()
  const capitalized = month.charAt(0).toUpperCase() + month.slice(1)
  return `${capitalized} ${year}'den beri üye`
}

export default function ProfilePage() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [watchHistory, setWatchHistory] = useState([])
  const [watchlist, setWatchlist] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [avatarUploading, setAvatarUploading] = useState(false)
  const [likedMovies, setLikedMovies] = useState([])

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError('')
      try {
        const [userRes, historyRes, watchlistRes, likedRes] = await Promise.all([
          getMe(),
          getWatchHistory(),
          getWatchlist(),
          getLikedMovies(),
        ])
        if (cancelled) return
        setUser(userRes.data)
        setWatchHistory(Array.isArray(historyRes.data) ? historyRes.data : [])
        setWatchlist(Array.isArray(watchlistRes.data) ? watchlistRes.data : [])
        setLikedMovies(Array.isArray(likedRes.data) ? likedRes.data : [])
      } catch {
        if (!cancelled) setError('Profil yüklenemedi.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [])

  const email = user?.email || localStorage.getItem('kineflix_user') || ''
  const displayName = email.split('@')[0] || 'Kullanıcı'
  const avatarLetter = email.charAt(0).toUpperCase() || 'K'

  const { topGenres, total: genreTotal, uniqueGenreCount } = useMemo(
    () => computeTopGenres(watchHistory),
    [watchHistory],
  )

  const recentHistory = watchHistory.slice(0, 6)
  const watchlistPreview = watchlist.slice(0, 4)
  const topGenreName = topGenres.length > 0 ? firstGenre(topGenres[0][0]) : 'Dram'
  const tasteText = `Ağırlıklı olarak ${topGenreName} türünde içerikler izleyen bir sinema tutkunusun.`
  const tasteBadges = topGenres.slice(0, 3).map(([name]) => firstGenre(name))

  const handleAvatarChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setAvatarUploading(true)
    try {
      const { data } = await uploadAvatar(file)
      setUser((prev) => ({ ...prev, avatar_url: data.avatar_url }))
    } catch {
      // sessiz hata
    } finally {
      setAvatarUploading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await logoutUser()
    } catch {
      // cookie silme başarısız olsa bile yerel temizliği yap
    }
    localStorage.removeItem('kineflix_user')
    localStorage.removeItem('kineflix_user_id')
    navigate('/login')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background relative flex flex-col">
        <div className="film-grain" />
        <Navbar active="profile" />
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
        <Navbar active="profile" />
        <div className="flex-1 flex items-center justify-center pt-24">
          <p className="text-error font-body">{error}</p>
        </div>
        <Footer />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background text-on-background relative overflow-x-hidden">
      <div className="film-grain" />
      <Navbar active="profile" />

      <main className="pt-24 pb-20">
        {/* Profile Hero */}
        <section className="relative w-full">
          <div className="absolute inset-0 z-0 h-[400px]">
            <div className="absolute inset-0 bg-gradient-to-br from-secondary-container/40 via-surface to-background" />
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-background" />
          </div>
          <div className="relative z-10 pt-32 pb-16 flex flex-col items-center px-margin-mobile md:px-margin-desktop max-w-container-max mx-auto">
            <div className="relative mb-6 group">
              <div className="w-[120px] h-[120px] rounded-full border-2 border-primary-container bg-primary flex items-center justify-center shadow-[0_0_20px_rgba(201,168,76,0.2)] overflow-hidden">
                {user?.avatar_url ? (
                  <img
                    src={`http://localhost:8000${user.avatar_url}`}
                    alt="avatar"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-5xl font-headline text-on-primary uppercase">{avatarLetter}</span>
                )}
              </div>
              <label className="absolute inset-0 flex items-center justify-center rounded-full cursor-pointer bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-white text-xs font-label uppercase tracking-wider text-center px-2">
                  {avatarUploading ? '...' : 'Değiştir'}
                </span>
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleAvatarChange}
                  disabled={avatarUploading}
                />
              </label>
            </div>
            <h1 className="font-display text-display-lg text-primary text-center uppercase tracking-widest mb-2">
              {displayName}
            </h1>
            <p className="font-label text-label-md text-on-surface-variant mb-2 uppercase">{email}</p>
            {user?.created_at && (
              <p className="font-label text-label-md text-on-surface-variant mb-12 uppercase">
                {formatMemberSince(user.created_at)}
              </p>
            )}

            <div className="flex gap-4 md:gap-8 flex-wrap justify-center">
              <div className="border border-primary-container/30 bg-surface-container/50 backdrop-blur-sm px-6 py-4 rounded text-center min-w-[140px]">
                <div className="font-headline text-headline-mobile text-on-surface mb-1">
                  {watchHistory.length}
                </div>
                <div className="font-label text-label-md text-primary tracking-widest">FİLM İZLENDİ</div>
              </div>
              <div className="border border-primary-container/30 bg-surface-container/50 backdrop-blur-sm px-6 py-4 rounded text-center min-w-[140px]">
                <div className="font-headline text-headline-mobile text-on-surface mb-1">
                  {watchlist.length}
                </div>
                <div className="font-label text-label-md text-primary tracking-widest">LİSTEDE</div>
              </div>
              <div className="border border-primary-container/30 bg-surface-container/50 backdrop-blur-sm px-6 py-4 rounded text-center min-w-[140px]">
                <div className="font-headline text-headline-mobile text-on-surface mb-1">
                  {uniqueGenreCount}
                </div>
                <div className="font-label text-label-md text-primary tracking-widest">TÜR KEŞFEDİLDİ</div>
              </div>
            </div>
          </div>
        </section>

        <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop grid grid-cols-1 md:grid-cols-12 gap-gutter mt-8">
          {/* Left column */}
          <div className="md:col-span-8 flex flex-col gap-16">
            {/* Favori Türler */}
            <section>
              <h2 className="font-headline text-headline-mobile text-primary tracking-widest mb-8 border-b border-outline-variant/30 pb-2 uppercase">
                Favori Türler
              </h2>
              {topGenres.length === 0 ? (
                <p className="font-body text-on-surface-variant">Henüz film izlemediniz.</p>
              ) : (
                <div className="flex flex-col gap-6">
                  {topGenres.map(([genre, count]) => {
                    const pct = genreTotal ? Math.round((count / genreTotal) * 100) : 0
                    return (
                      <div key={genre} className="flex items-center gap-4">
                        <span className="font-label text-label-md text-on-surface w-28 truncate">{firstGenre(genre)}</span>
                        <div className="flex-grow h-2 bg-surface-container-high rounded overflow-hidden">
                          <div
                            className="h-full bg-primary rounded"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <span className="font-label text-label-md text-primary w-12 text-right">%{pct}</span>
                      </div>
                    )
                  })}
                </div>
              )}
            </section>

            {/* Son İzlediklerim */}
            <section>
              <div className="flex items-center justify-between mb-8 border-b border-outline-variant/30 pb-2">
                <h2 className="font-headline text-headline-mobile text-primary tracking-widest uppercase">
                  Son İzlediklerim
                </h2>
                {watchHistory.length > 0 && (
                  <Link to="/history" className="font-label text-label-md text-primary hover:underline">
                    Tümünü Gör
                  </Link>
                )}
              </div>
              {recentHistory.length === 0 ? (
                <p className="font-body text-on-surface-variant">Henüz film izlemediniz.</p>
              ) : (
                <div className="flex gap-4 overflow-x-auto hide-scrollbar pb-4">
                  {recentHistory.map((movie) => (
                    <Link
                      key={movie.id}
                      to={`/movies/${movie.id}`}
                      className="flex-none w-32 md:w-40 flex flex-col gap-2 group"
                    >
                      <div className="relative aspect-[2/3] overflow-hidden rounded border border-[#1E3A5F]/50 group-hover:border-primary-container transition-colors">
                        <img
                          alt={movie.title}
                          src={posterSrc(movie.poster_url)}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                        <div className="absolute top-2 right-2 bg-background/80 rounded-full p-1 border border-primary-container/50">
                          <span className="material-symbols-outlined material-symbols-filled text-tertiary-container text-[16px]">
                            check_circle
                          </span>
                        </div>
                      </div>
                      <span className="font-title text-[16px] text-on-surface truncate group-hover:text-primary transition-colors">
                        {movie.title}
                      </span>
                    </Link>
                  ))}
                </div>
              )}
            </section>

            {/* Beğendiklerim */}
            <section>
              <div className="flex items-center justify-between mb-8 border-b border-outline-variant/30 pb-2">
                <h2 className="font-headline text-headline-mobile text-primary tracking-widest uppercase">
                  Beğendiklerim
                </h2>
              </div>
              {likedMovies.length === 0 ? (
                <p className="font-body text-on-surface-variant">Henüz beğenilen film yok.</p>
              ) : (
                <div className="flex gap-4 overflow-x-auto hide-scrollbar pb-4">
                  {likedMovies.slice(0, 6).map((movie) => (
                    <Link
                      key={movie.id}
                      to={`/movies/${movie.id}`}
                      className="flex-none w-32 md:w-40 flex flex-col gap-2 group"
                    >
                      <div className="relative aspect-[2/3] overflow-hidden rounded border border-[#1E3A5F]/50 group-hover:border-primary-container transition-colors">
                        <img
                          alt={movie.title}
                          src={posterSrc(movie.poster_url)}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                        <div className="absolute top-2 right-2 bg-background/80 rounded-full p-1 border border-red-500/50">
                          <span className="text-red-500 text-[14px] leading-none">♥</span>
                        </div>
                      </div>
                      <span className="font-title text-[16px] text-on-surface truncate group-hover:text-primary transition-colors">
                        {movie.title}
                      </span>
                    </Link>
                  ))}
                </div>
              )}
            </section>

            {/* Watchlist Özeti */}
            <section>
              <div className="flex items-center justify-between mb-8 border-b border-outline-variant/30 pb-2">
                <h2 className="font-headline text-headline-mobile text-primary tracking-widest uppercase">
                  Listem
                </h2>
                {watchlist.length > 0 && (
                  <Link to="/watchlist" className="font-label text-label-md text-primary hover:underline">
                    Tümünü Gör
                  </Link>
                )}
              </div>
              {watchlistPreview.length === 0 ? (
                <p className="font-body text-on-surface-variant">Listeniz henüz boş.</p>
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  {watchlistPreview.map((movie) => (
                    <Link
                      key={movie.id}
                      to={`/movies/${movie.id}`}
                      className="group flex flex-col gap-2"
                    >
                      <div className="aspect-[2/3] rounded border border-outline-variant/30 overflow-hidden group-hover:border-primary transition-colors">
                        <img
                          alt={movie.title}
                          src={posterSrc(movie.poster_url)}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                      </div>
                      <span className="font-body text-sm text-on-surface truncate group-hover:text-primary transition-colors">
                        {movie.title}
                      </span>
                      <span className="font-label text-[11px] text-on-surface-variant uppercase">
                        {firstGenre(movie.genres)}
                      </span>
                    </Link>
                  ))}
                </div>
              )}
            </section>
          </div>

          {/* Right column — Zevk Profili */}
          <div className="md:col-span-4 mt-8 md:mt-0">
            <div className="bg-[#0D1520] border border-primary-container rounded-lg p-8 sticky top-32 shadow-[0_4px_30px_rgba(201,168,76,0.05)] relative overflow-hidden">
              <div className="absolute -top-10 -right-10 w-32 h-32 bg-primary-container/10 rounded-full blur-2xl" />
              <div className="flex items-center gap-2 mb-6">
                <span className="material-symbols-outlined material-symbols-filled text-primary">auto_awesome</span>
                <h3 className="font-headline text-headline-mobile text-primary tracking-widest uppercase">
                  Zevk Profili
                </h3>
              </div>
              <p className="font-body text-body-lg text-on-surface mb-8 italic leading-relaxed border-l-2 border-primary-container pl-4">
                &ldquo;{tasteText}&rdquo;
              </p>
              {tasteBadges.length > 0 && (
                <div className="flex flex-wrap gap-3 mb-6">
                  {tasteBadges.map((badge) => (
                    <span
                      key={badge}
                      className="bg-[#1E3A5F] text-on-surface border border-primary-container/30 px-4 py-2 rounded-full font-label text-[12px] uppercase tracking-wider"
                    >
                      {badge}
                    </span>
                  ))}
                </div>
              )}
              <button
                type="button"
                onClick={() => navigate('/stats')}
                className="w-full border border-primary/50 hover:border-primary-container bg-primary/5 text-primary font-label text-label-md py-3 rounded transition-all duration-300 uppercase tracking-widest text-center mb-4"
              >
                İstatistiklerimi Gör →
              </button>
              <button
                type="button"
                onClick={handleLogout}
                className="w-full border border-[#1E3A5F] hover:border-primary-container bg-transparent text-on-surface hover:text-primary font-label text-label-md py-4 rounded transition-all duration-300 uppercase tracking-widest text-center"
              >
                Çıkış Yap
              </button>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
