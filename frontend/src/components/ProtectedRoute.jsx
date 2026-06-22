import { Navigate } from 'react-router-dom'

export default function ProtectedRoute({ children }) {
  const token = localStorage.getItem('kineflix_user')
  if (!token) {
    return <Navigate to="/login" replace />
  }
  return children
}
