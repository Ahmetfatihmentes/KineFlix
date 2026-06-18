import { Link, useNavigate } from 'react-router-dom'

export default function Navbar({ active = 'discover' }) {
  const navigate = useNavigate()

  return (
    <header className="bg-surface/80 backdrop-blur-md sticky top-0 border-b border-outline-variant/50 z-40">
      <div className="flex flex-col w-full px-margin-mobile md:px-margin-desktop py-4 max-w-container-max mx-auto">
        <div className="flex justify-between items-center w-full">
          <Link
            to="/home"
            className="font-headline text-headline-mobile md:text-headline-lg text-primary tracking-widest"
          >
            KineFlix
          </Link>
          <nav className="hidden md:flex items-center gap-8 font-label text-label-md">
            <Link
              to="/home"
              className={
                active === 'discover'
                  ? 'text-primary font-bold border-b-2 border-primary pb-1'
                  : 'text-on-surface-variant hover:text-primary-fixed-dim transition-colors'
              }
            >
              Keşfet
            </Link>
            <Link
              to="/watchlist"
              className={
                active === 'watchlist'
                  ? 'text-primary font-bold border-b-2 border-primary pb-1'
                  : 'text-on-surface-variant hover:text-primary-fixed-dim transition-colors'
              }
            >
              Listelerim
            </Link>
            <Link
              to="/history"
              className={
                active === 'history'
                  ? 'text-primary font-bold border-b-2 border-primary pb-1'
                  : 'text-on-surface-variant hover:text-primary-fixed-dim transition-colors'
              }
            >
              İzlediklerim
            </Link>
          </nav>
          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={() => navigate('/search')}
              className={`text-primary hover:text-primary-fixed-dim transition-colors flex items-center justify-center w-10 h-10 rounded-full border ${
                active === 'search'
                  ? 'border-primary bg-primary/10'
                  : 'border-outline-variant/50 hover:border-primary/50'
              }`}
              aria-label="Ara"
            >
              <span className="material-symbols-outlined">search</span>
            </button>
            <button
              type="button"
              onClick={() => navigate('/profile')}
              className={`w-10 h-10 rounded-full border-2 flex items-center justify-center font-label text-sm uppercase transition-opacity hover:opacity-80 ${
                active === 'profile'
                  ? 'border-primary bg-primary text-on-primary'
                  : 'border-primary-container bg-surface-container-highest text-primary'
              }`}
              aria-label="Profil"
            >
              {(localStorage.getItem('kineflix_user') || 'K').charAt(0).toUpperCase()}
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
