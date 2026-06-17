import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import GenreChip from '../components/GenreChip'

const GENRES = [
  { id: 'sci-fi', emoji: '🚀', label: 'Bilim Kurgu' },
  { id: 'action', emoji: '💥', label: 'Aksiyon' },
  { id: 'drama', emoji: '🎭', label: 'Drama' },
  { id: 'thriller', emoji: '😱', label: 'Gerilim' },
  { id: 'comedy', emoji: '😂', label: 'Komedi' },
  { id: 'mystery', emoji: '🔍', label: 'Gizem' },
  { id: 'documentary', emoji: '📽️', label: 'Belgesel' },
  { id: 'fantasy', emoji: '🧪', label: 'Fantastik' },
]

export default function OnboardingPage() {
  const navigate = useNavigate()
  const [selected, setSelected] = useState(() => new Set(['action', 'drama', 'mystery']))

  const count = selected.size
  const total = GENRES.length
  const canSubmit = count >= 3
  const progress = (count / total) * 100

  const toggle = (id) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const selectedLabels = useMemo(
    () => GENRES.filter((g) => selected.has(g.id)).map((g) => g.label),
    [selected],
  )

  const handleSubmit = () => {
    if (!canSubmit) return
    localStorage.setItem('kineflix_genres', JSON.stringify(selectedLabels))
    navigate('/home')
  }

  return (
    <div className="min-h-screen flex flex-col relative overflow-x-hidden bg-[#070B14]">
      <div className="film-grain" />
      <main className="flex-grow flex flex-col justify-center items-center px-margin-mobile md:px-margin-desktop py-12 md:py-24 relative z-10 w-full max-w-container-max mx-auto">
        <header className="text-center mb-12 md:mb-16 max-w-2xl">
          <h1 className="font-display text-display-lg text-primary mb-4 tracking-widest uppercase">
            Sinema Zevkini Öğren
          </h1>
          <p className="font-body text-title-md text-on-surface-variant font-semibold">
            En az 3 tür seç, yapay zeka seni tanısın
          </p>
        </header>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 w-full max-w-4xl mb-16">
          {GENRES.map((genre) => (
            <GenreChip
              key={genre.id}
              emoji={genre.emoji}
              label={genre.label}
              selected={selected.has(genre.id)}
              onToggle={() => toggle(genre.id)}
            />
          ))}
        </div>

        <div className="h-24" />
      </main>

      <div className="fixed bottom-0 left-0 w-full bg-surface/90 backdrop-blur-md border-t border-surface-variant/50 p-4 md:p-6 flex flex-col md:flex-row items-center justify-between z-40">
        <div className="mb-4 md:mb-0 flex items-center">
          <div className="w-32 h-1 bg-surface-variant rounded-full mr-4 overflow-hidden">
            <div className="h-full bg-primary transition-all duration-300" style={{ width: `${progress}%` }} />
          </div>
          <span className="font-label text-label-md text-on-surface-variant tracking-widest uppercase">
            {count}/{total} seçildi
          </span>
        </div>
        <button
          type="button"
          onClick={handleSubmit}
          disabled={!canSubmit}
          className={`bg-primary-container text-on-primary-container font-label text-label-md uppercase tracking-wider py-4 px-8 rounded flex items-center ${
            canSubmit
              ? 'hover:bg-primary shadow-[0_0_15px_rgba(201,168,76,0.3)]'
              : 'opacity-50 cursor-not-allowed'
          }`}
        >
          Keşfetmeye Başla
          <span className="material-symbols-outlined ml-2">arrow_forward</span>
        </button>
      </div>
    </div>
  )
}
