import { Link } from 'react-router-dom'
import { firstGenre, formatScore, displayOverview, posterSrc } from '../utils/movie'

export default function MovieTicketCard({ movie }) {
  const score = formatScore(movie)
  const genre = firstGenre(movie.genres)
  const typeBadge =
    movie.content_type === 'TV Show' ? 'DİZİ' : movie.content_type === 'Movie' ? 'FİLM' : null

  return (
    <article className="flex-shrink-0 w-[85vw] md:w-[600px] h-[280px] flex bg-surface-container border border-secondary-container rounded snap-center group hover:border-primary/50 transition-colors relative">
      <Link to={`/movies/${movie.id}`} className="w-1/3 h-full relative overflow-hidden rounded-l block">
        <img
          alt={movie.title}
          src={posterSrc(movie.poster_url)}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-transparent to-surface-container opacity-50" />
      </Link>
      <div className="w-px h-[90%] my-auto border-l-2 border-dashed border-outline-variant/30 relative z-10">
        <div className="absolute -top-4 -left-[6px] w-3 h-3 rounded-full bg-surface border border-b-0 border-secondary-container group-hover:border-primary/50 transition-colors" />
        <div className="absolute -bottom-4 -left-[6px] w-3 h-3 rounded-full bg-surface border border-t-0 border-secondary-container group-hover:border-primary/50 transition-colors" />
      </div>
      <div className="w-2/3 p-6 flex flex-col justify-between relative overflow-hidden">
        <span className="material-symbols-outlined absolute -bottom-10 -right-10 text-[120px] text-surface-container-highest opacity-20 transform -rotate-12 select-none">
          local_movies
        </span>
        <div className="relative z-10">
          <div className="flex justify-between items-start mb-2 gap-2">
            <span className="font-label text-[10px] text-on-surface-variant uppercase tracking-widest">
              {genre}
              {movie.release_year ? ` • ${movie.release_year}` : ''}
            </span>
            <div className="flex items-center gap-2 shrink-0">
              {typeBadge && (
                <span className="px-2 py-0.5 rounded bg-primary/10 border border-primary/40 text-primary font-label text-[10px] uppercase">
                  {typeBadge}
                </span>
              )}
              {score != null && (
              <div className="flex items-center gap-1 bg-surface border border-primary/30 px-2 py-1 rounded">
                <span className="material-symbols-outlined text-primary text-[14px] material-symbols-filled">
                  star
                </span>
                <span className="font-label text-primary text-[12px]">%{score}</span>
              </div>
              )}
            </div>
          </div>
          <Link to={`/movies/${movie.id}`}>
            <h3 className="font-body text-title-md text-on-surface mb-2 leading-tight font-semibold hover:text-primary transition-colors">
              {movie.title}
            </h3>
          </Link>
          <p className="font-body text-[14px] text-on-surface-variant line-clamp-3 opacity-80">
            {displayOverview(movie) || 'Özet mevcut değil.'}
          </p>
        </div>
        <div className="relative z-10 flex items-center justify-end mt-4">
          <Link
            to={`/movies/${movie.id}`}
            className="w-10 h-10 rounded-full border border-primary text-primary flex items-center justify-center hover:bg-primary/10 transition-colors"
            aria-label="Detay"
          >
            <span className="material-symbols-outlined">arrow_forward</span>
          </Link>
        </div>
      </div>
    </article>
  )
}
