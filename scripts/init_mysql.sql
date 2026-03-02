-- ContextGrid MySQL database schema
-- Version: v1
-- Purpose: Track projects, their status, context, and notes
-- Database: MySQL

-- =========================
-- Projects Table
-- =========================
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    status VARCHAR(50) NOT NULL DEFAULT 'idea',  -- idea, active, paused, archived
    project_type VARCHAR(50),                     -- web, cli, library, homelab, research
    
    primary_language VARCHAR(100),                -- Python, Java, JS, etc
    stack TEXT,                                    -- FastAPI + SQLite, React, etc
    
    repo_url VARCHAR(500),
    local_path VARCHAR(500),
    
    scope_size VARCHAR(50),                       -- tiny, medium, long-haul
    learning_goal TEXT,
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_worked_at DATETIME,
    
    is_archived TINYINT(1) DEFAULT 0,             -- 0 = false, 1 = true

    progress INT DEFAULT 0,                        -- 0-100 percentage completion

    INDEX idx_projects_name (name),
    INDEX idx_projects_status (status),
    INDEX idx_projects_created_at (created_at),
    INDEX idx_projects_last_worked_at (last_worked_at),
    INDEX idx_projects_is_archived (is_archived)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- Project Notes Table
-- =========================
CREATE TABLE IF NOT EXISTS project_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    
    note_type VARCHAR(50),                        -- log, idea, blocker, reflection, future_idea
    content TEXT NOT NULL,
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) 
        REFERENCES projects(id) 
        ON DELETE CASCADE,
    
    INDEX idx_project_notes_project_id (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- Tags Table
-- =========================
CREATE TABLE IF NOT EXISTS tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    
    INDEX idx_tags_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- Project Tags Junction Table (many-to-many)
-- =========================
CREATE TABLE IF NOT EXISTS project_tags (
    project_id INT NOT NULL,
    tag_id INT NOT NULL,
    
    PRIMARY KEY (project_id, tag_id),
    
    FOREIGN KEY (project_id) 
        REFERENCES projects(id) 
        ON DELETE CASCADE,
    
    FOREIGN KEY (tag_id) 
        REFERENCES tags(id) 
        ON DELETE CASCADE,
    
    INDEX idx_project_tags_project_id (project_id),
    INDEX idx_project_tags_tag_id (tag_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- Project Relationships Table
-- =========================
CREATE TABLE IF NOT EXISTS project_relationships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_project_id INT NOT NULL,
    target_project_id INT NOT NULL,
    relationship_type ENUM('related_to', 'depends_on', 'part_of') NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (source_project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE,

    FOREIGN KEY (target_project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE,

    UNIQUE KEY unique_relationship (source_project_id, target_project_id, relationship_type),

    INDEX idx_project_relationships_source (source_project_id),
    INDEX idx_project_relationships_target (target_project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- Project Links Table
-- =========================
CREATE TABLE IF NOT EXISTS project_links (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,

    title VARCHAR(255) NOT NULL,
    url VARCHAR(2000) NOT NULL,
    link_type ENUM('docs', 'deployment', 'design', 'board', 'repo', 'other') NOT NULL DEFAULT 'other',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE,

    INDEX idx_project_links_project_id (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- Project Templates Table
-- =========================
CREATE TABLE IF NOT EXISTS project_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Default project field values
    default_status VARCHAR(50) DEFAULT 'idea',
    default_project_type VARCHAR(50),
    default_primary_language VARCHAR(100),
    default_stack TEXT,
    default_scope_size VARCHAR(50),
    default_learning_goal TEXT,
    default_tags TEXT,           -- comma-separated list of default tags

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_project_templates_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
