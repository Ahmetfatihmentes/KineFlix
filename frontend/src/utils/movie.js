const GENRE_MAP = {
  'Action': 'Aksiyon',
  'Adventure': 'Macera',
  'Animation': 'Animasyon',
  'Comedy': 'Komedi',
  'Crime': 'Suç',
  'Documentary': 'Belgesel',
  'Drama': 'Dram',
  'Fantasy': 'Fantastik',
  'Horror': 'Korku',
  'Music': 'Müzik',
  'Mystery': 'Gizem',
  'Romance': 'Romantik',
  'Science Fiction': 'Bilim Kurgu',
  'Thriller': 'Gerilim',
  'War': 'Savaş',
  'Western': 'Western',
  'Family': 'Aile',
  'History': 'Tarih',
  'Biography': 'Biyografi',
  'Sport': 'Spor',
  'Musical': 'Müzikal',
  'TV Movie': 'TV Filmi',
  'Crime TV Shows': 'Suç Dizisi',
  'TV Dramas': 'Drama Dizisi',
  'TV Thrillers': 'Gerilim Dizisi',
  'TV Comedies': 'Komedi Dizisi',
  'Anime Series': 'Anime',
  'Reality TV': 'Gerçeklik TV',
  'Talk Shows': 'Talk Show',
  'Kids': 'Çocuk',
  'International': 'Uluslararası',
}

function translateGenre(g) {
  const key = g.trim()
  return GENRE_MAP[key] || key
}

const PLACEHOLDER =
  'data:image/svg+xml,' +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="600" viewBox="0 0 400 600">
      <rect fill="#1b2029" width="400" height="600"/>
      <text x="200" y="300" text-anchor="middle" fill="#e6c364" font-family="sans-serif" font-size="48">🎬</text>
    </svg>`,
  )

export function posterSrc(url) {
  return url || PLACEHOLDER
}

export function formatScore(movie) {
  if (movie?.positive_pct != null) return Math.round(movie.positive_pct)
  if (movie?.letterboxd_rating != null) return Math.round(movie.letterboxd_rating * 10)
  if (movie?.audience_score != null) return Math.round(movie.audience_score)
  return null
}

export function firstGenre(genres) {
  if (!genres) return 'Film'
  return translateGenre(genres.split(',')[0])
}

export function parseGenres(genres) {
  if (!genres) return []
  return genres.split(',').map(translateGenre).filter(Boolean)
}

export function displayOverview(movie) {
  return movie?.overview_tr || movie?.overview || null
}

export function displayTagline(movie) {
  return movie?.tagline_tr || movie?.tagline || null
}

export function formatWatchedDate(isoDate) {
  if (!isoDate) return ''
  return new Date(isoDate).toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

export function formatShortWatchedDate(isoDate) {
  if (!isoDate) return ''
  return new Date(isoDate).toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'short',
  })
}

export function movieRatingScore(movie) {
  if (movie?.letterboxd_rating != null) return movie.letterboxd_rating
  if (movie?.positive_pct != null) return movie.positive_pct / 10
  if (movie?.audience_score != null) return movie.audience_score / 10
  return 0
}

export function displayRatingLabel(movie) {
  const score = movieRatingScore(movie)
  if (!score) return null
  return score.toFixed(1)
}

export function genreSubtitle(genres, max = 2) {
  if (!genres) return ''
  return genres
    .split(',')
    .slice(0, max)
    .map(translateGenre)
    .join(' • ')
}
