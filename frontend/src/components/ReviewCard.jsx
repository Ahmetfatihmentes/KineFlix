function sentimentStyle(sentiment) {
  const s = (sentiment || '').toLowerCase()
  if (s.includes('neg') || s.includes('kötü')) {
    return 'bg-error-container/10 border-error-container text-error'
  }
  if (s.includes('karış') || s.includes('mixed')) {
    return 'bg-error-container/10 border-error-container text-error'
  }
  return 'bg-tertiary-container/10 border-tertiary-container text-tertiary'
}

function sentimentLabel(sentiment) {
  if (!sentiment) return 'Nötr'
  const s = sentiment.toLowerCase()
  if (s.includes('pos') || s.includes('pozitif')) return 'Pozitif'
  if (s.includes('neg')) return 'Negatif'
  if (s.includes('mixed') || s.includes('karış')) return 'Karmaşık'
  return sentiment
}

export default function ReviewCard({ review }) {
  return (
    <div className="bg-surface-container p-6 border border-outline-variant/20 hover:border-primary-container/50 transition-colors rounded group relative">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h4 className="font-body text-title-md text-on-surface font-semibold">
            {review.critic_name || 'Anonim'}
          </h4>
        </div>
        <span
          className={`px-2 py-1 border font-label text-[10px] rounded uppercase ${sentimentStyle(review.sentiment)}`}
        >
          {sentimentLabel(review.sentiment)}
        </span>
      </div>
      <p className="font-body text-body-md text-on-surface-variant italic line-clamp-4">
        &ldquo;{review.review_text}&rdquo;
      </p>
    </div>
  )
}
