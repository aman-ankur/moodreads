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
        <div className="animate-pulse text-xl text-gray-600">
          Finding your perfect books...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center space-y-6 p-8">
        <h1 className="text-3xl md:text-4xl font-serif text-red-600">Oops!</h1>
        <p className="text-gray-700 max-w-lg mx-auto">{error}</p>
        <div className="flex gap-4 justify-center">
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Try Again
          </button>
          <button
            onClick={() => window.history.back()}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col md:flex-row min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-full md:w-64 bg-white shadow-md p-6 flex flex-col space-y-6 md:fixed md:h-full">
        <div className="text-2xl font-bold text-indigo-700">MoodReads</div>
        <nav className="flex flex-col space-y-4">
          <Link href="/" className="flex items-center space-x-2 text-gray-700 hover:text-indigo-600">
            <Home size={20} />
            <span>Home</span>
          </Link>
          <Link href="/search" className="flex items-center space-x-2 text-gray-700 hover:text-indigo-600">
            <Search size={20} />
            <span>Search</span>
          </Link>
          <Link href="/library" className="flex items-center space-x-2 text-gray-700 hover:text-indigo-600">
            <BookOpen size={20} />
            <span>My Library</span>
          </Link>
          <Link href="/profile" className="flex items-center space-x-2 text-gray-700 hover:text-indigo-600">
            <User size={20} />
            <span>Profile</span>
          </Link>
        </nav>
        <div className="mt-auto pt-6 border-t">
          <div className="bg-gray-100 p-4 rounded-lg">
            <h3 className="font-medium text-gray-800 mb-2">Your Mood</h3>
            <p className="text-sm text-gray-600 italic">"{mood}"</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 md:ml-64 p-6">
        <div className="max-w-4xl mx-auto">
          <header className="mb-8 pb-4 border-b border-gray-200">
            <h1 className="text-3xl font-bold text-gray-900">Your Emotional Matches</h1>
            <p className="text-gray-600 mt-2">
              We've found {books.length} books that resonate with your mood:
              <span className="italic font-medium"> "{mood}"</span>
            </p>
          </header>

          <div className="space-y-4">
            {books.map((book) => (
              <BookCard
                key={book.id}
                onFavorite={() => {}}
                isFavorited={false}
                {...book}
              />
            ))}
          </div>

          <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-100">
            <h3 className="font-medium text-blue-800 mb-1">Looking for something else?</h3>
            <p className="text-sm text-blue-700">
              Head back to the home page to search for a different emotional experience.
            </p>
            <Link href="/" className="mt-2 inline-block px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700">
              New Search
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function ResultsPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="animate-pulse text-xl text-gray-600">
            Loading...
          </div>
        </div>
      }
    >
      <ResultsContent />
    </Suspense>
  );
} 