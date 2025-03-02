"use client";

import { BookCard } from "@/components/BookCard";
import { getRecommendations, type Book } from "@/lib/api";
import { useSearchParams } from "next/navigation";
import React, { Suspense, useEffect, useState } from "react";

function ResultsContent() {
  const searchParams = useSearchParams();
  const mood = searchParams.get("mood") || "";
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchBooks() {
      if (!mood) {
        setError("No mood specified. Please return to the home page and try again.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        console.log("Fetching recommendations for mood:", mood);
        const results = await getRecommendations(mood);
        console.log("Received recommendations:", results);
        
        if (results.length === 0) {
          setError("No books found matching your mood. Please try a different description.");
        } else {
          setBooks(results);
        }
      } catch (err) {
        console.error("Error loading recommendations:", err);
        const errorMessage = err instanceof Error ? err.message : "Unknown error";
        setError(
          "We're having trouble connecting to our recommendation service. " +
          "This might be due to high demand. Please try again in a few moments. " +
          `(Error: ${errorMessage})`
        );
      } finally {
        setLoading(false);
      }
    }

    fetchBooks();
  }, [mood]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-pulse text-xl text-text/70">
          Finding your perfect books...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center space-y-6">
        <h1 className="text-3xl md:text-4xl font-serif text-accent">Oops!</h1>
        <p className="text-text/70 max-w-lg mx-auto">{error}</p>
        <div className="flex gap-4 justify-center">
          <button
            onClick={() => window.location.reload()}
            className="btn btn-primary"
          >
            Try Again
          </button>
          <button
            onClick={() => window.history.back()}
            className="btn btn-secondary"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <header className="text-center space-y-4">
        <h1 className="text-3xl md:text-4xl font-serif">Your Emotional Matches</h1>
        <p className="text-text/70 max-w-2xl mx-auto">
          We've found books that resonate with your mood: "{mood}".
          Each recommendation is carefully matched to provide the experience you're seeking.
        </p>
      </header>

      <div className="space-y-6">
        {books.map((book) => (
          <BookCard
            key={book.id}
            onFavorite={() => {}}
            isFavorited={false}
            {...book}
          />
        ))}
      </div>
    </div>
  );
}

export default function ResultsPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="animate-pulse text-xl text-text/70">
            Loading...
          </div>
        </div>
      }
    >
      <ResultsContent />
    </Suspense>
  );
} 