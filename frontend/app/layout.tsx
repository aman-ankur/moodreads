import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";
import { Navigation } from "@/components/Navigation";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-playfair",
});

export const metadata: Metadata = {
  title: "MoodReads - Find Books Based on Your Mood",
  description: "Discover books that match your emotional state and preferences",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${playfair.variable} font-sans min-h-screen bg-background text-text`}
      >
        <main className="container mx-auto max-w-lg px-4 pb-24">
          {children}
        </main>
        <Navigation />
      </body>
    </html>
  );
} 