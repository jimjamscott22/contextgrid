import type { Config } from "tailwindcss";
import animate from "tailwindcss-animate";

const config: Config = {
  darkMode: ["class", '[data-theme="dark"]'],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    container: {
      center: true,
      padding: "1rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        // ContextGrid palette mirrors web/static/css/style.css :root vars.
        // Values are CSS variables so dark/light theming flips via [data-theme].
        bg: "rgb(var(--cg-bg) / <alpha-value>)",
        surface: "rgb(var(--cg-surface) / <alpha-value>)",
        "surface-alt": "rgb(var(--cg-surface-alt) / <alpha-value>)",
        border: "rgb(var(--cg-border) / <alpha-value>)",
        muted: "rgb(var(--cg-muted) / <alpha-value>)",
        fg: "rgb(var(--cg-fg) / <alpha-value>)",
        "fg-soft": "rgb(var(--cg-fg-soft) / <alpha-value>)",
        primary: {
          DEFAULT: "rgb(var(--cg-primary) / <alpha-value>)",
          foreground: "rgb(var(--cg-primary-fg) / <alpha-value>)",
        },
        accent: "rgb(var(--cg-accent) / <alpha-value>)",
        success: "rgb(var(--cg-success) / <alpha-value>)",
        warning: "rgb(var(--cg-warning) / <alpha-value>)",
        danger: "rgb(var(--cg-danger) / <alpha-value>)",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: [
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
        mono: [
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Consolas",
          "monospace",
        ],
      },
    },
  },
  plugins: [animate],
};

export default config;
