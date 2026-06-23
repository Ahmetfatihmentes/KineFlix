import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      error.response?.status === 401 &&
      !error.config?.url?.includes('/auth/login')
    ) {
      localStorage.removeItem('kineflix_user')
      localStorage.removeItem('kineflix_user_id')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export const loginUser = (email, password) =>
  api.post('/auth/login', { email, password })

export const logoutUser = () => api.post('/auth/logout')

export const getMe = () => api.get('/auth/me')

export const registerUser = (email, password, fullName) =>
  api.post('/auth/register', { email, password, full_name: fullName || null })

export const searchMovies = (query, contentType = '') => {
  const params = { query }
  if (contentType) params.content_type = contentType
  return api.get('/movies/search', { params })
}

export const savePreferences = (genres) =>
  api.post('/users/preferences', { genres })

export const getMovieStats = () => api.get('/movies/stats')

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

export const removeFromWatchHistory = (movieId) =>
  api.delete(`/watch-history/${movieId}`)

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

export const uploadAvatar = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/auth/upload-avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const updateProfile = (data) => api.patch('/users/me', data)

export const toggleLike = (movieId) => api.post(`/likes/${movieId}`)
export const getLikeStatus = (movieId) => api.get(`/likes/${movieId}/status`)
export const getLikedMovies = () => api.get('/likes/my-liked-movies')

export const addUserReview = (movieId, reviewText) =>
  api.post('/user-reviews/', { movie_id: movieId, review_text: reviewText })

export const getUserReviews = (movieId) => api.get(`/user-reviews/${movieId}`)

export const deleteUserReview = (reviewId) => api.delete(`/user-reviews/${reviewId}`)

export default api
