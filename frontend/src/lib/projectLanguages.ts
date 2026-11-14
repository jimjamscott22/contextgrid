interface Language {
  name: string;
  logo?: string;
  color: string;
}

const languages: Record<string, Language> = {
  python: { name: "Python", logo: "python", color: "3776AB" },
  javascript: { name: "JavaScript", logo: "javascript", color: "323330" },
  typescript: { name: "TypeScript", logo: "typescript", color: "3178C6" },
  rust: { name: "Rust", logo: "rust", color: "000000" },
  go: { name: "Go", logo: "go", color: "007D9C" },
  java: { name: "Java", color: "B45309" },
  "c#": { name: "C#", color: "6D28D9" },
  "c++": { name: "C++", logo: "cplusplus", color: "00599C" },
  c: { name: "C", logo: "c", color: "00599C" },
  ruby: { name: "Ruby", logo: "ruby", color: "CC342D" },
  php: { name: "PHP", logo: "php", color: "575A89" },
  swift: { name: "Swift", logo: "swift", color: "A73521" },
  kotlin: { name: "Kotlin", logo: "kotlin", color: "7F52FF" },
  dart: { name: "Dart", logo: "dart", color: "0175C2" },
  html: { name: "HTML", logo: "html5", color: "B83B1C" },
  css: { name: "CSS", logo: "css", color: "663399" },
  shell: { name: "Shell", logo: "gnubash", color: "405B23" },
  powershell: { name: "PowerShell", color: "2167A6" },
  sql: { name: "SQL", color: "336791" },
  r: { name: "R", logo: "r", color: "276DC3" },
};

const aliases: Record<string, string> = {
  py: "python", js: "javascript", ts: "typescript", golang: "go",
  csharp: "c#", "c sharp": "c#", cpp: "c++", "c plus plus": "c++",
  "html5": "html", "css3": "css", bash: "shell", sh: "shell", pwsh: "powershell",
};

/** Normalize common aliases for both language grouping and badge labels. */
export function projectLanguage(value?: string | null): Language | null {
  const name = value?.trim();
  if (!name) return null;
  const key = name.toLowerCase();
  return languages[aliases[key] ?? key] ?? { name, color: "4B5563" };
}

/** Use Shields' query API to safely handle punctuation in arbitrary labels. */
export function languageBadgeUrl(language: Language): string {
  const query = new URLSearchParams({
    label: "", message: language.name, color: language.color,
    style: "flat", ...(language.logo ? { logo: language.logo, logoColor: "white" } : {}),
  });
  return `https://img.shields.io/static/v1?${query}`;
}
