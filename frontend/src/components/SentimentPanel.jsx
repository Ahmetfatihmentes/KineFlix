export default function SentimentPanel({ positivePct, rating }) {
  const pct = positivePct != null ? Math.round(positivePct) : null
  const stars = rating != null ? Math.min(5, Math.round(rating)) : null

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
      {stars != null && (
        <div className="flex items-center mb-4 relative z-10">
          <div className="flex gap-1 text-primary-container">
            {Array.from({ length: 5 }).map((_, i) => (
              <span
                key={i}
                className={`material-symbols-outlined ${
                  i < stars ? 'material-symbols-filled' : ''
                }`}
              >
                {i < stars ? 'star' : 'star'}
              </span>
            ))}
          </div>
          {rating != null && (
            <span className="ml-3 font-body text-title-md text-on-surface font-semibold">
              {rating.toFixed(1)}{' '}
              <span className="text-on-surface-variant text-sm font-normal">/ 5</span>
            </span>
          )}
        </div>
      )}
      {pct != null && (
        <>
          <p className="font-headline text-headline-lg text-on-surface uppercase mb-6 leading-tight relative z-10">
            Kullanıcıların %{pct}&apos;ü bu filmi beğendi
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
