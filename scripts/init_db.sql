-- ContextGrid database schema
-- Version: v1
-- Purpose: Track projects, their status, context, and notes
-- Database: SQLite

PRAGMA foreign_keys = ON;

-- =========================
-- Projects
-- =========================
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,
    description TEXT,

    status TEXT NOT NULL,                -- idea, active, paused, archived
    project_type TEXT,                   -- web, cli, library, homelab, research

    primary_language TEXT,               -- Python, Java, JS, etc
    stack TEXT,                          -- FastAPI + SQLite, React, etc

    repo_url TEXT,
    local_path TEXT,

    scope_size TEXT,                     -- tiny, medium, long-haul
    learning_goal TEXT,

    created_at TEXT NOT NULL,             -- ISO-8601 timestamp
    last_worked_at TEXT,                 -- ISO-8601 timestamp

    is_archived INTEGER DEFAULT 0         -- 0 = false, 1 = true
);

-- =========================
-- Project Notes
-- =========================
CREATE TABLE IF NOT EXISTS project_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,

    note_type TEXT,                      -- log, idea, blocker, reflection
    content TEXT NOT NULL,

    created_at TEXT NOT NULL,

    FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE
);

-- =========================
-- Tags
-- =========================
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- =========================
-- Project <-> Tags (many-to-many)
-- =========================
CREATE TABLE IF NOT EXISTS project_tags (
    project_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,

    PRIMARY KEY (project_id, tag_id),

    FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE,

    FOREIGN KEY (tag_id)
        REFERENCES tags(id)
        ON DELETE CASCADE
);

-- =========================
-- Indexes for Performance
-- =========================
CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);
CREATE INDEX IF NOT EXISTS idx_projects_last_worked_at ON projects(last_worked_at);
CREATE INDEX IF NOT EXISTS idx_projects_is_archived ON projects(is_archived);
CREATE INDEX IF NOT EXISTS idx_project_notes_project_id ON project_notes(project_id);
CREATE INDEX IF NOT EXISTS idx_project_tags_project_id ON project_tags(project_id);
CREATE INDEX IF NOT EXISTS idx_project_tags_tag_id ON project_tags(tag_id);
