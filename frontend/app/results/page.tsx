"use client";

import { BookCard } from "@/components/BookCard";
import { getRecommendations, type Book } from "@/lib/api";
import { useSearchParams } from "next/navigation";
import React, { Suspense, useEffect, useState } from "react";
import { BookOpen, Home, Search, User } from "lucide-react";
import Link from "next/link";

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
        <div className="animate-pulse text-xl text-text/60">
          Finding your perfect books...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center space-y-6 p-8">
        <h1 className="text-3xl md:text-4xl font-serif text-red-600">Oops!</h1>
        <p className="text-text max-w-lg mx-auto">{error}</p>
        <div className="flex gap-4 justify-center">
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-button-green text-white rounded-button hover:bg-button-green/90"
          >
            Try Again
          </button>
          <button
            onClick={() => window.history.back()}
            className="px-4 py-2 bg-white text-text rounded-button hover:bg-gray-100"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Simple Navigation */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-button-green">
            MoodReads
          </Link>
          <nav className="flex items-center gap-6">
            <Link href="/" className="text-text/70 hover:text-button-green transition-colors">
              Home
            </Link>
            <Link href="/search" className="text-text/70 hover:text-button-green transition-colors">
              Search
            </Link>
            <Link href="/library" className="text-text/70 hover:text-button-green transition-colors">
              My Library
            </Link>
            <Link href="/profile" className="text-text/70 hover:text-button-green transition-colors">
              Profile
            </Link>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Your Mood Section */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <p className="text-text/70 text-sm">Your Mood</p>
          <p className="text-text/90 italic">"{mood}"</p>
        </div>

        {/* Results Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-serif mb-2">Your Emotional Matches</h1>
          <p className="text-text/70">
            We've found {books.length} books that resonate with your mood
          </p>
        </div>

        {/* Book Cards */}
        <div className="space-y-4">
          {books.map((book) => (
            <div key={book.id} className="bg-white rounded-lg shadow-sm overflow-hidden">
              <BookCard
                {...book}
                onFavorite={() => {}}
                isFavorited={false}
              />
            </div>
          ))}
        </div>

        {/* Looking for something else */}
        <div className="mt-8 text-center space-y-3">
          <h3 className="text-lg font-serif">Looking for something else?</h3>
          <p className="text-text/70 text-sm">
            Head back to the home page to search for a different emotional experience.
          </p>
          <Link 
            href="/" 
            className="inline-block px-4 py-2 bg-button-green text-white text-sm rounded-full hover:bg-button-green/90 transition-colors"
          >
            New Search
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function ResultsPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="animate-pulse text-xl text-text/60">
            Loading...
          </div>
        </div>
      }
    >
      <ResultsContent />
    </Suspense>
  );
} 