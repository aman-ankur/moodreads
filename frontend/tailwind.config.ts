import type { Config } from "tailwindcss";
import defaultTheme from "tailwindcss/defaultTheme";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#c5f1d5",
        text: "#222222",
        accent: "#ff6b4a",
        button: {
          green: "#4eca8c",
          peach: "#ffdfcc",
          pink: "#ffd1e0",
        },
      },
      borderRadius: {
        'card': '1.25rem', // 20px
        'button': '9999px', // Pill shape
      },
      spacing: {
        'card-padding': '1.5rem', // 24px
        'button-height': '3.25rem', // 52px
      },
      boxShadow: {
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      },
      fontFamily: {
        'sans': ['var(--font-inter)', ...defaultTheme.fontFamily.sans],
        'serif': ['var(--font-playfair)', ...defaultTheme.fontFamily.serif],
      },
    },
  },
  plugins: [],
};

export default config; 