function getPctSuffix(pct) {
  const lastDigit = pct % 10
  if (lastDigit === 0) return 'ı'
  if (lastDigit === 1) return 'i'
  if (lastDigit === 2) return 'si'
  if (lastDigit === 3) return 'ü'
  if (lastDigit === 4) return 'ü'
  if (lastDigit === 5) return 'i'
  if (lastDigit === 6) return 'sı'
  if (lastDigit === 7) return 'si'
  if (lastDigit === 8) return 'i'
  if (lastDigit === 9) return 'u'
  return 'i'
}

function HalfStar() {
  return (
    <span style={{ position: 'relative', display: 'inline-block', color: 'transparent', WebkitTextStroke: '1px #e6c364', fontSize: 'inherit' }}>
      ★
      <span style={{ position: 'absolute', left: 0, top: 0, width: '50%', overflow: 'hidden', color: '#e6c364', WebkitTextStroke: '0px' }}>★</span>
    </span>
  )
}

export default function SentimentPanel({ positivePct, rating }) {
  const pct = positivePct != null ? Math.round(positivePct) : null

  const starValue = rating != null ? (rating / 10) * 5 : null
  const fullStars = starValue != null ? Math.floor(starValue) : null
  const hasHalf = starValue != null ? (starValue - fullStars) >= 0.5 : false
  const emptyStars = starValue != null ? 5 - fullStars - (hasHalf ? 1 : 0) : 0

  return (
    <div className="bg-surface-container/50 backdrop-blur-md border border-primary-container rounded p-6 lg:p-8 flex flex-col justify-center relative overflow-hidden group">
      <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      <div className="flex items-center gap-2 mb-6 relative z-10">
        <span className="material-symbols-outlined text-primary-container material-symbols-filled">
          smart_toy
        </span>
        <h3 className="font-label text-label-md text-primary-container uppercase tracking-widest">
          Seyirci Kararı (AI Analizi)
        </h3>
      </div>
      {starValue != null && (
        <div className="flex items-center mb-4 relative z-10">
          <div className="flex gap-1" style={{ fontSize: '1.25rem', lineHeight: 1 }}>
            {Array.from({ length: fullStars }).map((_, i) => (
              <span key={`full-${i}`} style={{ color: '#e6c364' }}>★</span>
            ))}
            {hasHalf && <HalfStar />}
            {Array.from({ length: emptyStars }).map((_, i) => (
              <span key={`empty-${i}`} style={{ color: 'transparent', WebkitTextStroke: '1px #e6c364' }}>★</span>
            ))}
          </div>
          {rating != null && (
            <span className="ml-3 font-body text-title-md text-on-surface font-semibold">
              {rating.toFixed(1)}{' '}
              <span className="text-on-surface-variant text-sm font-normal">/ 10</span>
            </span>
          )}
        </div>
      )}
      {pct != null && (
        <>
          <p className="font-headline text-headline-lg text-on-surface uppercase mb-6 leading-tight relative z-10">
            KULLANICILARIN %{pct}&apos;{getPctSuffix(pct)} BU FİLMİ BEĞENDİ
          </p>
          <div className="w-full h-1.5 bg-surface-container-highest rounded-full overflow-hidden flex relative z-10">
            <div className="h-full bg-tertiary-container" style={{ width: `${pct}%` }} />
            <div className="h-full bg-error-container" style={{ width: `${100 - pct}%` }} />
          </div>
          <div className="flex justify-between mt-2 font-label text-[10px] uppercase text-on-surface-variant relative z-10">
            <span className="text-tertiary-container">Pozitif Duygu</span>
            <span className="text-error">Negatif</span>
          </div>
        </>
      )}
      {pct == null && (
        <p className="font-body text-body-md text-on-surface-variant relative z-10">
          Henüz yeterli yorum verisi yok.
        </p>
      )}
    </div>
  )
}
