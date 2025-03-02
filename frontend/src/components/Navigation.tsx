"use client";

import { Home, BookOpen, Heart, User } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  { name: "Home", href: "/", icon: Home },
  { name: "Browse", href: "/browse", icon: BookOpen },
  { name: "Favorites", href: "/favorites", icon: Heart },
  { name: "Profile", href: "/profile", icon: User },
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200">
      <div className="container mx-auto max-w-lg">
        <div className="flex justify-around">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex flex-col items-center py-4 px-6 transition-colors ${
                  isActive
                    ? "text-button-green"
                    : "text-text/50 hover:text-text/70"
                }`}
              >
                <item.icon className="w-6 h-6" />
                <span className="text-xs mt-1">{item.name}</span>
                {isActive && (
                  <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-12 h-0.5 bg-button-green rounded-full" />
                )}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
} 