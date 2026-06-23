import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getMovieStats } from '../services/api'

const HERO_BG =
  'https://lh3.googleusercontent.com/aida-public/AB6AXuDKeK7034oqBrcEmXTeAZez4z4rObxhjPfW1SlpPhrmS21reBmIDAw_MH39yehbCtH_0t75IhV_MEsWZnf-3GhgFCWf8ya1ukjmyJQU_EosfIcQsazGy3nrkMzxHpXqpjz4ava3W0dOGKqIFzGAwKX1xdwSV4qroupO2euI0UBXTUrafUOVQ8IpSGrbQT5ZaoufQhscnWfYZ1h2xXgXlLiRNmo6Wt9e81W6mhPDUoUOt-I8hzHBCYlUjOqOHtpmEu9XJlJelv0RZfs'

const FEATURES = [
  {
    icon: 'movie',
    title: 'Yapay Zeka Önerileri',
    text: 'İzleme geçmişine ve zevkine göre kişiselleştirilmiş film önerileri.',
  },
  {
    icon: 'forum',
    title: 'Seyirci Kararı',
    text: '238.000+ eleştirmen yorumu ile filmlerin gerçek değerini keşfet.',
  },
  {
    icon: 'track_changes',
    title: 'Uyum Skoru',
    text: 'Her film için sana özel uyum yüzdesi. %96 uyumlu filmler seni bekliyor.',
  },
]

const STEPS = [
  {
    num: 1,
    title: 'Kayıt Ol',
    text: 'Ücretsiz hesap oluştur, e-posta ve şifrenle saniyeler içinde başla',
  },
  {
    num: 2,
    title: 'Zevkini Söyle',
    text: 'Favori film türlerini seç, yapay zeka seni tanısın ve öğrensin',
  },
  {
    num: 3,
    title: 'Keşfet',
    text: 'Kişiselleştirilmiş uyum skorlu film önerileri seni bekliyor',
  },
]

const STATS_FALLBACK = [
  { value: '10.004+', label: 'Film & Dizi' },
  { value: '238.000+', label: 'Eleştirmen Yorumu' },
  { value: '%94', label: 'Ortalama Memnuniyet' },
]

function buildStats(data) {
  return [
    {
      value: data.movie_count ? data.movie_count.toLocaleString('tr-TR') + '+' : STATS_FALLBACK[0].value,
      label: 'Film & Dizi',
    },
    {
      value: data.review_count ? data.review_count.toLocaleString('tr-TR') + '+' : STATS_FALLBACK[1].value,
      label: 'Eleştirmen Yorumu',
    },
    {
      value: data.avg_satisfaction_pct != null ? `%${data.avg_satisfaction_pct}` : STATS_FALLBACK[2].value,
      label: 'Ortalama Memnuniyet',
    },
  ]
}

export default function LandingPage() {
  const [stats, setStats] = useState(STATS_FALLBACK)

  useEffect(() => {
    getMovieStats()
      .then(({ data }) => setStats(buildStats(data)))
      .catch(() => {})
  }, [])

  useEffect(() => {
    const onScroll = () => {
      const navbar = document.getElementById('landing-navbar')
      if (!navbar) return
      if (window.scrollY > 50) {
        navbar.classList.add('shadow-lg', 'bg-surface/95')
        navbar.classList.remove('bg-surface/80')
      } else {
        navbar.classList.remove('shadow-lg', 'bg-surface/95')
        navbar.classList.add('bg-surface/80')
      }
    }
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <div className="antialiased min-h-screen relative overflow-x-hidden selection:bg-primary selection:text-on-primary bg-[#070B14] text-[#F0EDE4]">
      <div className="film-grain" />

      <nav
        id="landing-navbar"
        className="fixed top-0 w-full z-40 bg-surface/80 backdrop-blur-md border-b border-outline-variant/50 px-margin-mobile md:px-margin-desktop py-4 transition-all duration-300"
      >
        <div className="max-w-container-max mx-auto flex justify-between items-center">
          <Link
            to="/"
            className="font-headline text-headline-lg text-primary tracking-widest hover:text-primary-fixed-dim transition-colors duration-300"
          >
            KineFlix
          </Link>
          <div className="hidden md:flex items-center gap-6">
            <Link
              to="/login"
              className="font-label text-label-md text-primary border border-primary px-6 py-2 rounded hover:bg-primary hover:text-on-primary transition-all duration-300 transform hover:scale-95"
            >
              Giriş Yap
            </Link>
            <Link
              to="/register"
              className="font-label text-label-md bg-primary text-on-primary px-6 py-2 rounded hover:bg-primary-fixed-dim transition-all duration-300 transform hover:scale-95 font-bold"
            >
              Kayıt Ol
            </Link>
          </div>
          <button type="button" className="md:hidden text-primary p-2" aria-label="Menü">
            <span className="material-symbols-outlined material-symbols-filled">menu</span>
          </button>
        </div>
      </nav>

      <header className="relative min-h-[921px] flex items-center justify-center pt-24 overflow-hidden">
        <img
          alt="Karanlık sinematik arka plan"
          src={HERO_BG}
          className="absolute inset-0 w-full h-full object-cover -z-20"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#070B14] via-transparent to-transparent -z-10" />
        <div className="absolute inset-0 bg-background/40 -z-10" />
        <div className="relative z-10 max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop text-center flex flex-col items-center">
          <h1 className="font-display text-[48px] md:text-display-lg text-on-surface mb-6 max-w-4xl drop-shadow-lg leading-tight uppercase">
            SİNEMANIN ZEKASI, <span className="text-primary">SENİN İÇİN</span>
          </h1>
          <p className="font-body text-body-lg text-on-surface-variant max-w-2xl mx-auto mb-12">
            Yapay zeka destekli içerik öneri sistemi. 10.004+ Film & Dizi, kişisel zevkine göre seçilmiş.
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center w-full sm:w-auto">
            <Link
              to="/register"
              className="font-label text-label-md bg-primary text-on-primary px-8 py-4 rounded hover:bg-primary-fixed-dim transition-all duration-300 flex items-center justify-center gap-2 transform hover:scale-95"
            >
              Ücretsiz Başla
              <span className="material-symbols-outlined text-sm">arrow_forward</span>
            </Link>
            <a
              href="#nasil-calisir"
              className="font-label text-label-md border border-primary text-primary px-8 py-4 rounded hover:bg-primary/10 transition-all duration-300 flex items-center justify-center transform hover:scale-95"
            >
              Nasıl Çalışır?
            </a>
          </div>
        </div>
      </header>

      <section className="py-24 bg-background relative" id="ozellikler">
        <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop">
          <div className="text-center mb-16">
            <h2 className="font-headline text-headline-lg text-primary uppercase tracking-widest">
              NEDEN KİNEFLİX?
            </h2>
            <div className="w-16 h-px bg-primary mx-auto mt-4" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {FEATURES.map((feature) => (
              <div
                key={feature.title}
                className="bg-surface-container border border-outline-variant/50 p-8 rounded-lg hover:border-primary transition-colors duration-500 group relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="relative z-10 flex flex-col items-center text-center">
                  <div className="w-16 h-16 rounded-full bg-background border border-outline-variant flex items-center justify-center mb-6 group-hover:border-primary transition-colors duration-300 drop-shadow-[0_0_10px_rgba(201,168,76,0.3)]">
                    <span className="material-symbols-outlined text-primary text-[40px] material-symbols-filled">
                      {feature.icon}
                    </span>
                  </div>
                  <h3 className="font-body text-title-md text-on-surface mb-4 font-semibold">
                    {feature.title}
                  </h3>
                  <p className="font-body text-body-md text-on-surface-variant">{feature.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section
        className="py-24 bg-surface-container relative border-y border-outline-variant/30"
        id="nasil-calisir"
      >
        <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop">
          <div className="text-center mb-20">
            <h2 className="font-headline text-headline-lg text-primary uppercase tracking-widest">
              NASIL ÇALIŞIR?
            </h2>
            <div className="w-16 h-px bg-primary mx-auto mt-4" />
          </div>
          <div className="relative max-w-4xl mx-auto">
            <div className="hidden md:block absolute top-8 left-0 w-full h-px bg-outline-variant z-0">
              <div className="absolute top-0 left-0 h-full bg-primary w-full opacity-50" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-12 relative z-10">
              {STEPS.map((step) => (
                <div key={step.num} className="flex flex-col items-center text-center">
                  <div className="w-16 h-16 rounded-full bg-background border-2 border-primary flex items-center justify-center mb-6 font-headline text-headline-lg text-primary shadow-[0_0_15px_rgba(201,168,76,0.3)]">
                    {step.num}
                  </div>
                  <h3 className="font-body text-title-md text-on-surface mb-2 font-semibold">
                    {step.title}
                  </h3>
                  <p className="font-body text-body-md text-on-surface-variant">{step.text}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="py-24 bg-background border-b border-outline-variant/30">
        <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 divide-y md:divide-y-0 md:divide-x divide-outline-variant/30 text-center">
            {stats.map((stat) => (
              <div key={stat.label} className="flex flex-col items-center py-6 md:py-0">
                <div className="font-display text-[48px] md:text-display-lg text-primary mb-2">
                  {stat.value}
                </div>
                <div className="font-label text-label-md text-on-surface-variant tracking-widest uppercase">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-32 bg-surface-container relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary/10 via-background to-background pointer-events-none" />
        <div className="max-w-4xl mx-auto px-margin-mobile md:px-margin-desktop text-center relative z-10">
          <h2 className="font-display text-[40px] md:text-display-lg text-on-surface mb-6 uppercase tracking-wider">
            SİNEMA YOLCULUĞUNA BAŞLA
          </h2>
          <p className="font-body text-body-lg text-on-surface-variant mb-12">
            Yapay zeka seni bekliyor.
          </p>
          <Link
            to="/register"
            className="inline-flex items-center justify-center gap-3 font-label text-label-md bg-primary text-on-primary px-10 py-5 rounded hover:bg-primary-fixed-dim transition-all duration-300 transform hover:scale-95 font-bold shadow-[0_0_30px_rgba(201,168,76,0.2)] hover:shadow-[0_0_40px_rgba(201,168,76,0.4)]"
          >
            Hemen Başla
            <span className="material-symbols-outlined material-symbols-filled">arrow_forward</span>
          </Link>
        </div>
      </section>

      <footer className="bg-surface-container-lowest border-t border-outline-variant/30 w-full px-margin-mobile md:px-margin-desktop py-gutter">
        <div className="max-w-container-max mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex flex-col items-center md:items-start">
            <Link
              to="/"
              className="font-headline text-headline-lg text-primary tracking-widest opacity-80 hover:opacity-100 transition-opacity"
            >
              KineFlix
            </Link>
            <span className="font-label text-label-md text-on-surface-variant mt-1">Sinema Zekası</span>
          </div>
          <nav className="flex gap-8">
            <span className="font-label text-label-md text-on-surface-variant opacity-80">Hakkımızda</span>
            <span className="font-label text-label-md text-on-surface-variant opacity-80">Gizlilik</span>
            <span className="font-label text-label-md text-on-surface-variant opacity-80">İletişim</span>
          </nav>
          <div className="font-body text-body-md text-on-surface-variant opacity-80">
            © 2024 KineFlix. Sinema Zekası.
          </div>
        </div>
      </footer>
    </div>
  )
}
