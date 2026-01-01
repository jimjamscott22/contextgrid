# ContextGrid

ContextGrid is a personal, local-first application for tracking coding projects across time, tools, and mental states.

It exists to answer a few simple questions clearly:

- What am I building?
- Where does it live?
- What state is it really in?
- What’s the next honest step?

Not a task manager.  
Not a SaaS clone.  
A thinking tool.

---

## Goals

- Track projects across languages, machines, and environments
- Emphasize **status and momentum**, not just completion
- Preserve context: notes, blockers, reflections
- Stay simple, local, and hackable

ContextGrid is designed for one user: me.

---

## Core Features (Planned)

- Project metadata (name, type, language, stack, location)
- Clear lifecycle status (idea → active → paused → archived)
- Timestamped notes and reflections
- Tag-based organization and filtering ✅
- SQLite-backed, local-first storage

No accounts.  
No authentication.  
No cloud dependency.

---

## Tech Stack

- **Language:** Python
- **Database:** SQLite
- **Interface:** CLI initially (API/UI later if it earns its keep)

---

## Project Structure

```text
contextgrid/
├── README.md
├── .gitignore
├── requirements.txt         # dependencies (stdlib only for now)
├── data/
│   └── projects.db          # local only (not committed)
├── src/
│   ├── main.py              # entry point
│   ├── db.py                # DB connection + initialization
│   ├── models.py            # schema helpers / queries
│   └── cli.py               # command-line interface
└── scripts/
    └── init_db.sql          # database schema
```

---

## Quick Start

### Installation

Clone or download this repository, then ensure you have Python 3.8+ installed:

```bash
python3 --version  # should be 3.8 or higher
```

### Setup (First Time Only)

```bash
# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Using the CLI

No installation needed for CLI-only usage (uses Python stdlib only).

### Basic Usage

**Create your first project:**

```bash
python src/main.py add "ContextGrid"
# Follow the interactive prompts to add details
```

**List all projects:**

```bash
python src/main.py list
```

**Filter by status:**

```bash
python src/main.py list --status active
```

**View project details:**

```bash
python src/main.py show 1
```

**Update a project:**

```bash
python src/main.py update 1
# Follow prompts to change any field
```

**Touch timestamp (mark as recently worked on):**

```bash
python src/main.py touch 1
```

**Add tags to organize projects:**

```bash
# Add a tag to a project
python src/main.py tag add 1 python

# Add multiple tags
python src/main.py tag add 1 web
python src/main.py tag add 1 backend

# List all tags
python src/main.py tag list

# List tags for a specific project
python src/main.py tag list 1

# Remove a tag
python src/main.py tag remove 1 python

# Filter projects by tag
python src/main.py list --tag python

# Combine filters
python src/main.py list --status active --tag web
```

**Generate a visual roadmap:**

```bash
python src/main.py roadmap
# Creates ROADMAP.md with all projects organized by status

# Custom output location:
python src/main.py roadmap --output docs/MY_ROADMAP.md
```

### Example Session

```bash
# Add a new project
$ python src/main.py add "Personal Dashboard"

Creating project: Personal Dashboard
==================================================
Description (optional): Web app to track my projects
Status [idea]: active
Type (optional): web
Primary language (optional): Python
Stack/tech (optional): FastAPI + SQLite
...

[OK] Project created with ID: 1

# List projects
$ python src/main.py list

All Projects:
================================================================================

[1] Personal Dashboard
    Status: active | Type: web | Language: Python
    Web app to track my projects
    Created: 2024-12-24T10:30:00.000000

# Touch it after working
$ python src/main.py touch 1
[OK] Updated last_worked_at for project 1

# Generate roadmap visualization
$ python src/main.py roadmap
[OK] Roadmap generated: D:\Code\Python\PythonApps\contextgrid\ROADMAP.md
     Projects: 1
     Active: 1, Ideas: 0
```

---

## Web UI

ContextGrid now includes a beautiful web interface for browsing and managing your projects!

### Starting the Web UI

```bash
# Make sure you're in the project directory
cd contextgrid

# Activate virtual environment
source venv/bin/activate

# Start the web server
python3 web/app.py

# Or use uvicorn directly
uvicorn web.app:app --reload
```

The web interface will be available at: **http://127.0.0.1:8000**

### Features

- 📊 **Dashboard** - Quick stats and recent activity
- 📁 **Projects List** - Browse all projects with filters
- 🏷️ **Tags** - Organize and filter by tags
- 📝 **Project Details** - View full project information and notes
- 📱 **Responsive** - Works great on mobile devices
- 🎨 **Modern Design** - Clean, beautiful interface

The web UI is **read-focused** - for creating/editing projects, use the CLI commands. This keeps the web interface simple and the CLI powerful.

---

## Tag Management

Tags help you organize and filter projects by categories, technologies, or any custom labels.

### Adding Tags

```bash
# Add a tag to a project
python src/main.py tag add <project_id> <tag_name>

# Example: tag project 1 with "python" and "web"
python src/main.py tag add 1 python
python src/main.py tag add 1 web
```

### Viewing Tags

```bash
# List all tags with project counts
python src/main.py tag list

# Output:
# All Tags:
# ================================================================================
#   • python (3 projects)
#   • web (2 projects)
#   • cli (1 project)

# List tags for a specific project
python src/main.py tag list 1

# Output:
# Tags for project: ContextGrid
# ================================================================================
#   • python
#   • cli
```

### Filtering by Tags

```bash
# Show all projects with a specific tag
python src/main.py list --tag python

# Combine with status filter
python src/main.py list --status active --tag web
```

### Removing Tags

```bash
# Remove a tag from a project
python src/main.py tag remove <project_id> <tag_name>

# Example:
python src/main.py tag remove 1 web
```

---

## Roadmap Visualization

ContextGrid can generate a beautiful `ROADMAP.md` file that visualizes all your projects:

- **Organized by status** (Active → Ideas → Paused → Archived)
- **Rich metadata tables** with all project details
- **Timeline information** showing when projects were created/worked on
- **Summary statistics** showing project counts by status
- **Emoji indicators** for quick visual scanning

The roadmap is perfect for:

- Getting a bird's-eye view of all your work
- Sharing your project portfolio
- Tracking progress over time
- Making decisions about what to focus on next

---

## Future Plans

- Enhanced search capabilities across projects and notes
- Timeline view of project activity
- Web UI or TUI for richer interaction
- Export/import functionality for backups
