import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('kineflix_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const loginUser = (email, password) =>
  api.post('/auth/login', { email, password })

export const getMe = () => api.get('/auth/me')

export const registerUser = (email, password) =>
  api.post('/auth/register', { email, password })

export const searchMovies = (query, contentType = '') => {
  const params = { query }
  if (contentType) params.content_type = contentType
  return api.get('/movies/search', { params })
}

export const savePreferences = (genres) =>
  api.post('/users/preferences', { genres })

export const getMovie = (id) => api.get(`/movies/${id}`)

export const getRecommendations = (id, limit = 10) =>
  api.get(`/movies/${id}/recommendations`, { params: { limit } })

export const getPersonalizedRecommendation = () => api.get('/recommendations/personalized')

export const getRecommendationReason = (sourceId, recommendedId, short = false) =>
  api.get(`/movies/${sourceId}/recommendation-reason`, {
    params: { recommended_id: recommendedId, short },
  })

export const getReviews = (id, limit = 10) =>
  api.get(`/movies/${id}/reviews`, { params: { limit } })

export const getAiReview = (id) => api.get(`/movies/${id}/ai-review`)

export const getTrailer = (id) => api.get(`/movies/${id}/trailer`)

export const addToWatchHistory = (movieId) =>
  api.post('/watch-history/', { movie_id: movieId })

export const getWatchStatus = (movieId) =>
  api.get(`/watch-history/${movieId}/status`)

export const addToWatchlist = (movieId) =>
  api.post('/watchlist/', { movie_id: movieId })

export const removeFromWatchlist = (movieId) =>
  api.delete(`/watchlist/${movieId}`)

export const getWatchlistStatus = (movieId) =>
  api.get(`/watchlist/${movieId}/status`)

export const getWatchlist = () => api.get('/watchlist/')

export const getWatchHistory = () => api.get('/watch-history/')

export default api
