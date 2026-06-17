import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { loginUser, registerUser } from '../services/api'

const CINEMA_BG =
  'https://lh3.googleusercontent.com/aida-public/AB6AXuCNQgGgdC2pdghzzKx2wqzBiLwpK39SheHwbeXnQy28HD7yRTCM-zVSF4pVFLv1izeqjl0HngyZw_etT1Ofjem1GLtPbwToTOhqmvvKeOUG431HZQBoTkK9CcU8fMqMtzAk3ywI5O_PAENg37d18LexnwV6Vq0Bo3fXSLCSuExMFnDvhAKhXoUv1_nT0tmWHtjZuT5DsUR78f_jOsfwKic_wZa5f6CJq4E2nN-LrnWVBTFCwmkF-tdIyz4D-8qybW6JJW1hi6HtybA'

export default function LoginPage() {
  const navigate = useNavigate()
  const [isRegistering, setIsRegistering] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (isRegistering) {
        await registerUser(email, password)
        localStorage.setItem('kineflix_user', email)
        navigate('/onboarding')
      } else {
        await loginUser(email, password)
        localStorage.setItem('kineflix_user', email)
        const genres = localStorage.getItem('kineflix_genres')
        navigate(genres ? '/' : '/onboarding')
      }
    } catch (err) {
      const msg = err.response?.data?.detail
      setError(typeof msg === 'string' ? msg : 'İşlem başarısız. Lütfen tekrar deneyin.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col relative overflow-x-hidden">
      <div className="film-grain" />
      <div
        className="fixed inset-0 z-0 bg-cover bg-center bg-no-repeat blur-sm opacity-30 scale-105"
        style={{ backgroundImage: `url('${CINEMA_BG}')` }}
      />
      <div className="fixed inset-0 z-0 bg-gradient-to-b from-surface/80 via-surface/90 to-surface" />

      <main className="flex-grow flex items-center justify-center relative z-10 px-margin-mobile md:px-margin-desktop py-12 md:py-24">
        <div className="w-full max-w-[480px] bg-surface-container-highest/60 backdrop-blur-md rounded-xl border border-outline-variant/30 p-8 md:p-12 shadow-2xl relative overflow-hidden group">
          <div className="absolute inset-0 border border-primary-container/0 group-hover:border-primary-container/20 transition-colors duration-700 rounded-xl pointer-events-none" />
          <div className="flex flex-col items-center mb-10 text-center">
            <h1 className="font-headline text-headline-lg text-primary tracking-widest mb-4">KineFlix</h1>
            <h2 className="font-body text-title-md text-on-surface font-semibold">
              Sinema Zekasına Hoş Geldiniz
            </h2>
            <p className="font-body text-body-md text-on-surface-variant mt-2">
              {isRegistering ? 'Yeni hesap oluşturun.' : 'Lütfen hesabınıza giriş yapın.'}
            </p>
          </div>

          <form className="space-y-6 flex flex-col" onSubmit={handleSubmit}>
            {error && (
              <p className="text-error font-body text-sm text-center bg-error-container/20 py-2 rounded">
                {error}
              </p>
            )}
            <div className="space-y-1">
              <label className="font-label text-label-md text-on-surface-variant block uppercase" htmlFor="email">
                E-posta Adresi
              </label>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-0 top-1/2 -translate-y-1/2 text-secondary-container">
                  mail
                </span>
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="ornek@kineflix.com"
                  className="w-full bg-transparent border-0 border-b border-secondary-container text-on-surface focus:ring-0 focus:border-primary-container transition-colors py-3 pl-8 font-body text-body-md placeholder-on-surface-variant/50 outline-none"
                />
              </div>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between items-baseline">
                <label className="font-label text-label-md text-on-surface-variant block uppercase" htmlFor="password">
                  Şifre
                </label>
                {!isRegistering && (
                  <span className="font-label text-[12px] text-primary opacity-60">Şifremi Unuttum</span>
                )}
              </div>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-0 top-1/2 -translate-y-1/2 text-secondary-container">
                  lock
                </span>
                <input
                  id="password"
                  type="password"
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-transparent border-0 border-b border-secondary-container text-on-surface focus:ring-0 focus:border-primary-container transition-colors py-3 pl-8 font-body text-body-md placeholder-on-surface-variant/50 outline-none"
                />
              </div>
            </div>
            <div className="pt-4">
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-primary-container text-on-primary-container font-label text-label-md py-4 rounded uppercase tracking-widest hover:bg-primary-fixed-dim transition-all flex justify-center items-center gap-2 active:scale-95 disabled:opacity-60"
              >
                <span>{isRegistering ? 'Kayıt Ol' : 'Giriş Yap'}</span>
                <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
              </button>
            </div>
          </form>

          <div className="mt-8 text-center border-t border-outline-variant/30 pt-6">
            <p className="font-body text-body-md text-on-surface-variant">
              {isRegistering ? 'Zaten hesabın var mı? ' : 'Hesabın yok mu? '}
              <button
                type="button"
                onClick={() => {
                  setIsRegistering(!isRegistering)
                  setError('')
                }}
                className="text-primary hover:text-primary-fixed-dim font-bold transition-colors"
              >
                {isRegistering ? 'Giriş Yap' : 'Kayıt Ol'}
              </button>
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
