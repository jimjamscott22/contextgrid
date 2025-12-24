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
- Tag-based filtering
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
python --version  # should be 3.8 or higher
```

No external dependencies required - uses Python standard library only.

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

- Notes and reflections per project (schema ready, CLI coming soon)
- Tag-based filtering and search
- Timeline view of project activity
- Web UI or TUI for richer interaction
