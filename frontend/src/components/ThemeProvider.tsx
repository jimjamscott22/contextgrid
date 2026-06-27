import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

export type ThemeId =
  | "light-plus"
  | "dark-plus"
  | "monokai"
  | "solarized-light"
  | "solarized-dark"
  | "github-light"
  | "github-dark"
  | "high-contrast"
  | "ocean-light"
  | "ocean-dark"
  | "coffee-light"
  | "coffee-dark"
  | "forest-light"
  | "forest-dark"
  | "cyberpunk"
  | "rose";

export type ThemeMode = "light" | "dark";
export type ThemeGroup = "editor" | "lifestyle";

export interface ThemeOption {
  id: ThemeId;
  label: string;
  mode: ThemeMode;
  group: ThemeGroup;
}

export const THEME_OPTIONS: ThemeOption[] = [
  { id: "light-plus", label: "Light+", mode: "light", group: "editor" },
  { id: "dark-plus", label: "Dark+", mode: "dark", group: "editor" },
  { id: "monokai", label: "Monokai", mode: "dark", group: "editor" },
  { id: "solarized-light", label: "Solarized Light", mode: "light", group: "editor" },
  { id: "solarized-dark", label: "Solarized Dark", mode: "dark", group: "editor" },
  { id: "github-light", label: "GitHub Light", mode: "light", group: "editor" },
  { id: "github-dark", label: "GitHub Dark", mode: "dark", group: "editor" },
  { id: "high-contrast", label: "High Contrast", mode: "dark", group: "editor" },
  { id: "ocean-light", label: "Ocean Light", mode: "light", group: "lifestyle" },
  { id: "ocean-dark", label: "Ocean Dark", mode: "dark", group: "lifestyle" },
  { id: "coffee-light", label: "Coffee Light", mode: "light", group: "lifestyle" },
  { id: "coffee-dark", label: "Coffee Dark", mode: "dark", group: "lifestyle" },
  { id: "forest-light", label: "Forest Light", mode: "light", group: "lifestyle" },
  { id: "forest-dark", label: "Forest Dark", mode: "dark", group: "lifestyle" },
  { id: "cyberpunk", label: "Cyberpunk", mode: "dark", group: "lifestyle" },
  { id: "rose", label: "Rose", mode: "light", group: "lifestyle" },
];

const DEFAULT_LIGHT_THEME: ThemeId = "light-plus";
const DEFAULT_DARK_THEME: ThemeId = "dark-plus";

interface ThemeContextValue {
  theme: ThemeId;
  themeMode: ThemeMode;
  themes: ThemeOption[];
  setTheme: (t: ThemeId) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

function isThemeId(value: string | null): value is ThemeId {
  return THEME_OPTIONS.some((option) => option.id === value);
}

function getThemeMode(theme: ThemeId): ThemeMode {
  return THEME_OPTIONS.find((option) => option.id === theme)?.mode || "light";
}

function readInitialTheme(): ThemeId {
  if (typeof document === "undefined") return DEFAULT_LIGHT_THEME;
  const attr = document.documentElement.getAttribute("data-theme");
  if (isThemeId(attr)) return attr;

  try {
    const stored = localStorage.getItem("cg-theme");
    if (isThemeId(stored)) return stored;
    if (stored === "dark") return DEFAULT_DARK_THEME;
    if (stored === "light") return DEFAULT_LIGHT_THEME;
  } catch {
    // localStorage unavailable; fall through to system preference
  }

  if (
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-color-scheme: dark)").matches
  ) {
    return DEFAULT_DARK_THEME;
  }
  return DEFAULT_LIGHT_THEME;
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<ThemeId>(readInitialTheme);

  const setTheme = useCallback((next: ThemeId) => {
    document.documentElement.setAttribute("data-theme", next);
    document.documentElement.setAttribute("data-theme-mode", getThemeMode(next));
    try {
      localStorage.setItem("cg-theme", next);
    } catch {
      // localStorage unavailable; theme persists for session only
    }
    setThemeState(next);
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    document.documentElement.setAttribute("data-theme-mode", getThemeMode(theme));
  }, [theme]);

  useEffect(() => {
    // Stay in sync with system theme when user hasn't picked one.
    let stored: string | null = null;
    try {
      stored = localStorage.getItem("cg-theme");
    } catch {
      stored = null;
    }
    if (isThemeId(stored) || stored === "dark" || stored === "light") return;

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = (e: MediaQueryListEvent) =>
      setTheme(e.matches ? DEFAULT_DARK_THEME : DEFAULT_LIGHT_THEME);
    media.addEventListener("change", handler);
    return () => media.removeEventListener("change", handler);
  }, [setTheme]);

  return (
    <ThemeContext.Provider
      value={{ theme, themeMode: getThemeMode(theme), themes: THEME_OPTIONS, setTheme }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used inside ThemeProvider");
  return ctx;
}
