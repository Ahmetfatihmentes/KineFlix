export default function AIStrip({ message }) {
  return (
    <div className="w-full bg-surface-container border-y border-outline-variant/30 py-4 z-20 relative">
      <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/30 flex items-center justify-center shrink-0">
          <span className="material-symbols-outlined text-primary text-[18px]">psychology</span>
        </div>
        <p className="font-body text-body-md text-on-surface-variant">
          <span className="text-primary opacity-80">Bu öneriyi şundan dolayı yaptım:</span>{' '}
          {message}
        </p>
      </div>
    </div>
  )
}
