import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    borderRadius: {
      none: "0px",
      DEFAULT: "0px",
    },
    extend: {
      colors: {
        major: {
          black: "#000000",
          dark: "#121212",
          card: "#18181B",
          border: "#27272A",
          lightBorder: "#E4E4E7",
          white: "#FFFFFF",
          red: "#D00000",       // Crisp authoritative red
          blue: "#0038FF",      // Pure cobalt blue
          emerald: "#059669",   // Crisp green
          yellow: "#EAB308",    // Major amber
          surface: "#F4F4F5",   // Neutral crisp surface
        },
      },
      fontFamily: {
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "monospace"],
      },
      boxShadow: {
        flat: "4px 4px 0px 0px #000000",
        flatRed: "4px 4px 0px 0px #D00000",
        flatHover: "2px 2px 0px 0px #000000",
      },
    },
  },
  plugins: [],
};
export default config;
