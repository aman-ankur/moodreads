"use client";

import { BookOpen, Search, Sparkles } from "lucide-react";
import { useRouter } from "next/navigation";
import * as React from "react";

type MoodCategories = {
  [key: string]: string[];
};

const MOOD_CATEGORIES: MoodCategories = {
  "Uplifting": [
    "Looking for an inspiring story that will boost my spirits",
    "Need a book that will make me feel hopeful and motivated",
    "Want something uplifting and positive"
  ],
  "Relaxation": [
    "Need a calming book to help me unwind",
    "Looking for a peaceful and soothing story",
    "Want something gentle and comforting"
  ],
  "Adventure": [
    "Craving an exciting and thrilling adventure",
    "Want to escape into an epic journey",
    "Looking for action and suspense"
  ],
  "Personal Growth": [
    "Want a book that will help me understand myself better",
    "Looking for wisdom and life insights",
    "Need inspiration for personal transformation"
  ]
};

export default function Home() {
  const router = useRouter();
  const [mood, setMood] = React.useState("");
  const [selectedCategory, setSelectedCategory] = React.useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (mood.trim()) {
      router.push(`/results?mood=${encodeURIComponent(mood)}`);
    }
  };

  const handlePromptSelect = (prompt: string) => {
    setMood(prompt);
    router.push(`/results?mood=${encodeURIComponent(prompt)}`);
  };

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center space-y-6">
        <h1 className="text-5xl md:text-6xl font-bold font-serif">
          Find Your Next{" "}
          <span className="text-accent">Emotional Journey</span>
        </h1>
        <p className="text-xl md:text-2xl max-w-2xl mx-auto text-text/80">
          Discover books that resonate with your current emotional state and take you on a transformative reading experience.
        </p>
      </section>

      {/* Mood Categories Section */}
      <section className="max-w-4xl mx-auto">
        <div className="card space-y-6">
          <div className="space-y-4">
            <h2 className="text-2xl font-serif text-center">Choose Your Mood Category</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {Object.keys(MOOD_CATEGORIES).map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    selectedCategory === category
                      ? "border-button-green bg-button-green/10"
                      : "border-button-green/20 hover:border-button-green/40"
                  }`}
                >
                  <h3 className="text-lg font-medium">{category}</h3>
                </button>
              ))}
            </div>
          </div>

          {selectedCategory && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Select a Prompt</h3>
              <div className="space-y-3">
                {MOOD_CATEGORIES[selectedCategory].map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => handlePromptSelect(prompt)}
                    className="w-full text-left p-3 rounded-lg hover:bg-button-green/10 transition-colors flex items-center gap-2"
                  >
                    <Sparkles className="w-4 h-4 text-button-green flex-shrink-0" />
                    <span>{prompt}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-button-green/20"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-background text-text/70">or write your own</span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <label htmlFor="mood" className="block text-lg font-medium">
                How are you feeling today?
              </label>
              <textarea
                id="mood"
                value={mood}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setMood(e.target.value)}
                rows={4}
                className="w-full rounded-lg border-2 border-button-green/20 p-4 focus:border-button-green focus:ring-2 focus:ring-button-green/20 transition-colors"
                placeholder="Describe your mood or the emotional experience you're seeking..."
              />
            </div>
            <div className="flex gap-4">
              <button type="submit" className="btn btn-primary flex-1 flex items-center justify-center gap-2">
                <Search className="w-5 h-5" />
                Find Books
              </button>
              <button
                type="button"
                onClick={() => router.push("/browse")}
                className="btn btn-secondary flex items-center justify-center gap-2"
              >
                <BookOpen className="w-5 h-5" />
                Browse All
              </button>
            </div>
          </form>
        </div>
      </section>

      {/* Featured Section */}
      <section className="space-y-8">
        <h2 className="text-center">Popular Mood Journeys</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            "Seeking inspiration",
            "Need comfort",
            "Want adventure",
          ].map((moodPreset) => (
            <button
              key={moodPreset}
              onClick={() => {
                setMood(moodPreset);
                router.push(`/results?mood=${encodeURIComponent(moodPreset)}`);
              }}
              className="card hover:shadow-lg transition-shadow text-left"
            >
              <h3 className="text-xl font-serif mb-2">{moodPreset}</h3>
              <p className="text-text/70">
                Explore books that match this emotional state
              </p>
            </button>
          ))}
        </div>
      </section>
    </div>
  );
} 