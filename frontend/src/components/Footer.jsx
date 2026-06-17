export default function Footer() {
  return (
    <footer className="bg-surface-container-lowest border-t border-outline-variant/30 relative z-40 mt-12">
      <div className="flex flex-col md:flex-row justify-between items-center w-full px-margin-mobile md:px-margin-desktop py-gutter max-w-container-max mx-auto gap-6">
        <div className="font-headline text-headline-mobile md:text-headline-lg text-primary tracking-widest opacity-80">
          KineFlix
        </div>
        <nav className="flex flex-wrap justify-center gap-6 font-label text-label-md">
          <span className="text-on-surface-variant opacity-80">Hakkımızda</span>
          <span className="text-on-surface-variant opacity-80">Gizlilik</span>
          <span className="text-on-surface-variant opacity-80">İletişim</span>
        </nav>
        <div className="font-body text-body-md text-on-surface-variant text-sm opacity-60">
          © 2024 KineFlix. Sinema Zekası.
        </div>
      </div>
    </footer>
  )
}
