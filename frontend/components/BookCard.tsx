import { Heart } from "lucide-react";
import Image from "next/image";

export interface BookCardProps {
  id?: string;
  title: string;
  author: string;
  coverUrl: string;
  emotionalMatch: number;
  matchExplanation: string;
  genres?: string[];
  rating?: number;
  onFavorite?: () => void;
  isFavorited?: boolean;
}

export function BookCard({
  title,
  author,
  coverUrl,
  emotionalMatch,
  matchExplanation,
  genres,
  rating,
  onFavorite,
  isFavorited = false,
}: BookCardProps) {
  return (
    <div className="flex items-start p-4 gap-4">
      {/* Book Cover */}
      <div className="relative w-20 h-28 flex-shrink-0">
        <Image
          src={coverUrl || 'https://via.placeholder.com/300x450?text=No+Cover+Available'}
          alt={`Cover of ${title}`}
          fill
          className="object-cover rounded-md"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            const formattedTitle = encodeURIComponent(title.replace(/\s+/g, '+'));
            target.src = `https://via.placeholder.com/300x450/e0e0e0/333333?text=${formattedTitle}`;
            target.onerror = null;
          }}
          unoptimized={true}
          loading="eager"
        />
      </div>

      {/* Book Info */}
      <div className="flex-grow min-w-0">
        <div className="flex justify-between items-start gap-4">
          <div className="min-w-0">
            <h3 className="text-lg font-medium mb-1 truncate">{title}</h3>
            <p className="text-text/70 text-sm mb-2">by {author}</p>
            
            {/* Genres */}
            {genres && genres.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-2">
                {genres.slice(0, 3).map((genre, i) => (
                  <span key={i} className="px-2 py-0.5 bg-gray-100 text-xs text-text/70 rounded-full">
                    {genre}
                  </span>
                ))}
                {genres.length > 3 && (
                  <span className="text-xs text-text/50">+{genres.length - 3}</span>
                )}
              </div>
            )}
          </div>

          {/* Heart Icon */}
          {onFavorite && (
            <button
              onClick={onFavorite}
              className="p-1.5 hover:bg-button-pink/10 rounded-full transition-colors flex-shrink-0"
              aria-label={isFavorited ? "Remove from favorites" : "Add to favorites"}
            >
              <Heart
                className={`w-5 h-5 ${
                  isFavorited
                    ? "fill-button-pink stroke-button-pink"
                    : "stroke-text/30 hover:stroke-button-pink"
                }`}
              />
            </button>
          )}
        </div>

        {/* Match Info */}
        <div className="flex items-center gap-2">
          <div className="h-1.5 flex-grow bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-button-green transition-all duration-500"
              style={{ width: `${emotionalMatch}%` }}
            />
          </div>
          <span className="text-xs font-medium text-button-green whitespace-nowrap">
            {emotionalMatch}% match
          </span>
        </div>
      </div>
    </div>
  );
} 