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
  if (movie?.letterboxd_rating != null) return Math.round(movie.letterboxd_rating * 20)
  if (movie?.audience_score != null) return Math.round(movie.audience_score)
  return null
}

export function firstGenre(genres) {
  if (!genres) return 'Film'
  return genres.split(',')[0].trim()
}

export function parseGenres(genres) {
  if (!genres) return []
  return genres.split(',').map((g) => g.trim()).filter(Boolean)
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
  if (movie?.positive_pct != null) return movie.positive_pct / 20
  if (movie?.audience_score != null) return movie.audience_score / 20
  return 0
}

export function displayRatingLabel(movie) {
  const score = movieRatingScore(movie)
  if (!score) return null
  return (score * 2).toFixed(1)
}

export function genreSubtitle(genres, max = 2) {
  if (!genres) return ''
  return genres
    .split(',')
    .slice(0, max)
    .map((g) => g.trim())
    .join(' • ')
}
