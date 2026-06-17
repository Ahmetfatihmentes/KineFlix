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
