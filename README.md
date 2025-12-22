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
├── data/
│   └── projects.db          # local only (not committed)
├── src/
│   ├── main.py              # entry point
│   ├── db.py                # DB connection + initialization
│   ├── models.py            # schema helpers / queries
│   └── cli.py               # command-line interface
└── scripts/
    └── init_db.sql           # database schema

