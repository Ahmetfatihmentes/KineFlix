import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: { 'Content-Type': 'application/json' },
})

export const loginUser = (email, password) =>
  api.post('/auth/login', { email, password })

export const registerUser = (email, password) =>
  api.post('/auth/register', { email, password })

export const searchMovies = (query) =>
  api.get('/movies/search', { params: { query } })

export const getMovie = (id) => api.get(`/movies/${id}`)

export const getRecommendations = (id, limit = 10) =>
  api.get(`/movies/${id}/recommendations`, { params: { limit } })

export const getReviews = (id, limit = 10) =>
  api.get(`/movies/${id}/reviews`, { params: { limit } })

export default api
