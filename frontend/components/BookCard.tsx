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
    <div className="bg-white rounded-lg shadow-md p-4 mb-4 hover:shadow-lg transition-shadow">
      <div className="flex flex-col md:flex-row gap-4">
        {/* Book Cover */}
        <div className="relative w-full md:w-32 h-48 md:h-48 flex-shrink-0">
          <Image
            src={coverUrl || 'https://via.placeholder.com/300x450?text=No+Cover+Available'}
            alt={`Cover of ${title}`}
            fill
            className="object-cover rounded-md shadow-sm"
            onError={(e) => {
              // Enhanced fallback if image fails to load
              const target = e.target as HTMLImageElement;
              // Try to create a meaningful placeholder based on the book title
              const formattedTitle = encodeURIComponent(title.replace(/\s+/g, '+'));
              target.src = `https://via.placeholder.com/300x450/e0e0e0/333333?text=${formattedTitle}`;
              // Remove onerror handler to prevent infinite loops
              target.onerror = null;
            }}
            unoptimized={true} // Allows external URLs to work more reliably
            loading="eager" // Prioritize loading covers
          />
        </div>

        {/* Book Info */}
        <div className="flex flex-col flex-grow space-y-2">
          <div className="flex justify-between">
            <div>
              <h3 className="text-xl font-bold">{title}</h3>
              <p className="text-gray-600">by {author}</p>
              
              {/* Rating display with stars */}
              {rating !== undefined && rating > 0 && (
                <div className="flex items-center mt-1">
                  <div className="flex">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <span 
                        key={star} 
                        className={`text-lg ${
                          star <= Math.round(rating) 
                            ? 'text-yellow-400' 
                            : 'text-gray-300'
                        }`}
                      >
                        ★
                      </span>
                    ))}
                  </div>
                  <span className="ml-1 text-sm text-gray-600">
                    {rating.toFixed(1)}
                  </span>
                </div>
              )}
            </div>
            
            {onFavorite && (
              <button
                onClick={onFavorite}
                className="p-1 hover:bg-pink-100 rounded-full transition-colors"
              >
                <Heart
                  className={`w-6 h-6 ${
                    isFavorited
                      ? "fill-pink-500 stroke-pink-500"
                      : "stroke-gray-400"
                  }`}
                />
              </button>
            )}
          </div>
          
          {/* Genres */}
          {genres && genres.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1">
              {genres.slice(0, 3).map((genre, i) => (
                <span key={i} className="px-2 py-1 bg-gray-100 text-xs text-gray-700 rounded-full">
                  {genre}
                </span>
              ))}
              {genres.length > 3 && (
                <span className="text-xs text-gray-500 self-center">+{genres.length - 3} more</span>
              )}
            </div>
          )}
          
          {/* Emotional Match */}
          <div className="mt-auto">
            <div className="flex items-center gap-2 mb-1">
              <div className="h-2 flex-1 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-green-400 to-green-600 transition-all duration-500"
                  style={{ width: `${emotionalMatch}%` }}
                />
              </div>
              <span className="text-sm font-medium whitespace-nowrap">
                {emotionalMatch}% match
              </span>
            </div>
            <p className="text-sm text-gray-700 line-clamp-3 overflow-y-auto">
              {matchExplanation || "No explanation available."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
} 