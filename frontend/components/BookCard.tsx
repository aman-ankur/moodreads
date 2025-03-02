import { Heart } from "lucide-react";
import Image from "next/image";

export interface BookCardProps {
  id?: number;
  title: string;
  author: string;
  coverUrl: string;
  emotionalMatch: number;
  matchExplanation: string;
  onFavorite?: () => void;
  isFavorited?: boolean;
}

export function BookCard({
  title,
  author,
  coverUrl,
  emotionalMatch,
  matchExplanation,
  onFavorite,
  isFavorited = false,
}: BookCardProps) {
  return (
    <div className="card hover:shadow-lg transition-shadow">
      <div className="flex gap-6">
        {/* Book Cover */}
        <div className="relative w-32 h-48 flex-shrink-0">
          <Image
            src={coverUrl}
            alt={`Cover of ${title}`}
            fill
            className="object-cover rounded-lg shadow-md"
          />
        </div>

        {/* Book Info */}
        <div className="flex-1 space-y-4">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-serif text-xl">{title}</h3>
              <p className="text-text/70">{author}</p>
            </div>
            {onFavorite && (
              <button
                onClick={onFavorite}
                className="p-2 hover:bg-button-pink/20 rounded-full transition-colors"
              >
                <Heart
                  className={`w-6 h-6 ${
                    isFavorited
                      ? "fill-accent stroke-accent"
                      : "stroke-text/50"
                  }`}
                />
              </button>
            )}
          </div>

          {/* Emotional Match */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="h-2 flex-1 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-button-green transition-all duration-500"
                  style={{ width: `${emotionalMatch}%` }}
                />
              </div>
              <span className="text-sm font-medium text-text/70">
                {emotionalMatch}% match
              </span>
            </div>
            <p className="text-sm text-text/80">{matchExplanation}</p>
          </div>
        </div>
      </div>
    </div>
  );
} 