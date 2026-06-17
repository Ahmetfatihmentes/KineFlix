export default function GenreChip({ emoji, label, selected, onToggle }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className={`genre-chip flex flex-col items-center justify-center p-6 bg-surface-container border rounded-xl cursor-pointer group ${
        selected
          ? 'border-primary-container bg-primary-container text-on-primary-container'
          : 'border-surface-variant hover:border-primary-container hover:bg-primary-container/10'
      }`}
    >
      <span className="text-4xl mb-3 group-hover:scale-110 transition-transform duration-300">
        {emoji}
      </span>
      <span className="font-label text-label-md uppercase tracking-wider">{label}</span>
    </button>
  )
}
