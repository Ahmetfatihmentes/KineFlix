import { Link } from 'react-router-dom'

export default function Navbar({ active = 'discover' }) {
  return (
    <header className="bg-surface/80 backdrop-blur-md sticky top-0 border-b border-outline-variant/50 z-40">
      <div className="flex justify-between items-center w-full px-margin-mobile md:px-margin-desktop py-4 max-w-container-max mx-auto">
        <Link
          to="/"
          className="font-headline text-headline-mobile md:text-headline-lg text-primary tracking-widest"
        >
          KineFlix
        </Link>
        <nav className="hidden md:flex items-center gap-8 font-label text-label-md">
          <Link
            to="/"
            className={
              active === 'discover'
                ? 'text-primary font-bold border-b-2 border-primary pb-1'
                : 'text-on-surface-variant hover:text-primary-fixed-dim transition-colors'
            }
          >
            Keşfet
          </Link>
          <span className="text-on-surface-variant opacity-50 cursor-not-allowed">Listelerim</span>
        </nav>
        <div className="flex items-center gap-4">
          <button
            type="button"
            className="text-primary hover:text-primary-fixed-dim transition-colors flex items-center justify-center w-10 h-10 rounded-full border border-outline-variant/50 hover:border-primary/50"
            aria-label="Ara"
          >
            <span className="material-symbols-outlined">search</span>
          </button>
          <div className="w-10 h-10 rounded-full bg-surface-container-highest border border-primary/30 flex items-center justify-center text-primary font-label text-sm">
            K
          </div>
        </div>
      </div>
    </header>
  )
}
