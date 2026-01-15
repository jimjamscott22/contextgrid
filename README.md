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

## Core Features

- ✅ Project metadata (name, type, language, stack, location)
- ✅ Clear lifecycle status (idea → active → paused → archived)
- ✅ Timestamped notes and reflections
- ✅ Tag-based organization and filtering
- ✅ REST API for programmatic access
- ✅ MySQL-backed, production-ready storage
- ✅ Command-line interface
- ✅ Web-based interface
- ✅ Cross-device access via API

Simple to use, powerful to extend.

No accounts required.  
No cloud dependency.  
Your data, your control.

---

## Architecture

ContextGrid now uses an API-based architecture that enables cross-device access and scalability:

```
┌─────────────┐         ┌─────────────┐
│     CLI     │────────▶│             │
└─────────────┘         │             │
                        │  API Server │         ┌──────────┐
┌─────────────┐         │   (FastAPI) │────────▶│  MySQL   │
│   Web UI    │────────▶│             │         │ Database │
└─────────────┘         │             │         └──────────┘
                        └─────────────┘
```

**Components:**
- **CLI** (`src/main.py`, `src/cli.py`): Command-line interface that makes HTTP requests to the API
- **Web UI** (`web/app.py`): Web-based interface for browsing projects
- **API Server** (`api/server.py`): FastAPI REST API handling all business logic
- **Database**: MySQL database for persistent storage

### Benefits

- **Cross-device access**: Access your projects from any machine with network access
- **Scalability**: API server can handle multiple clients simultaneously
- **Separation of concerns**: Clean separation between UI, business logic, and data storage
- **Future-proof**: Easy to add mobile apps, integrations, or new clients

---

## Tech Stack

- **Language:** Python 3.8+
- **Database:** MySQL 8.0+
- **API Framework:** FastAPI
- **Web Server:** Uvicorn
- **Database Driver:** PyMySQL
- **CLI:** Pure Python with argparse

---

## Project Structure

```text
contextgrid/
├── README.md
├── API.md                        # API documentation
├── .env.example                  # Example environment variables
├── requirements.txt              # Python dependencies
├── api/
│   ├── __init__.py
│   ├── server.py                 # FastAPI application
│   ├── db.py                     # MySQL database layer
│   ├── models.py                 # Pydantic models
│   └── config.py                 # Configuration management
├── src/
│   ├── main.py                   # CLI entry point
│   ├── cli.py                    # CLI commands
│   ├── api_client.py             # HTTP client for API
│   ├── models.py                 # Model wrappers
│   └── db.py                     # Legacy SQLite support
├── web/
│   ├── app.py                    # Web UI
│   ├── static/                   # CSS, JS, images
│   └── templates/                # Jinja2 templates
└── scripts/
    ├── init_db.sql               # SQLite schema (legacy)
    ├── init_mysql.sql            # MySQL schema
    └── migrate_sqlite_to_mysql.py # Migration tool
```

---

## Quick Start

### Prerequisites

1. **Python 3.8+**
   ```bash
   python3 --version  # should be 3.8 or higher
   ```

2. **MySQL 8.0+**
   ```bash
   mysql --version
   ```

### Installation

Clone or download this repository:

```bash
git clone https://github.com/yourusername/contextgrid.git
cd contextgrid
```

### Setup

#### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Set Up MySQL Database

Create a MySQL database and user:

```sql
CREATE DATABASE contextgrid;
CREATE USER 'contextgrid_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON contextgrid.* TO 'contextgrid_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 4. Configure Environment

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` and set your database credentials:

```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=contextgrid
DB_USER=contextgrid_user
DB_PASSWORD=your_secure_password

API_HOST=0.0.0.0
API_PORT=8000
API_ENDPOINT=http://localhost:8000
```

#### 5. Initialize Database

The API server automatically creates tables on first run. Just start the server:

```bash
python api/server.py
```

Alternatively, you can manually run the schema:

```bash
mysql -u contextgrid_user -p contextgrid < scripts/init_mysql.sql
```

#### 6. Migrate Existing Data (Optional)

If you have existing SQLite data to migrate:

```bash
python scripts/migrate_sqlite_to_mysql.py
```

---

## Running ContextGrid

### Start the API Server

```bash
# Run as a module
python -m api.server
```

The API will be available at `http://localhost:8000`.
API documentation is available at `http://localhost:8000/docs`.

### Using the CLI

With the API server running, use the CLI:

```bash
python src/main.py add "My Project"
python src/main.py list
python src/main.py show 1
```

All CLI commands now communicate with the API server.

### Start the Web UI (Optional)

In a separate terminal:

```bash
python web/app.py
```

The web interface will be available at `http://localhost:8080`.

---

## API Server

The API server provides a REST API for all project management operations.

### Endpoints

See [API.md](API.md) for complete API documentation.

**Key Endpoints:**
- `GET /api/health` - Health check
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project
- `POST /api/projects/{id}/touch` - Update last worked timestamp
- `GET /api/tags` - List tags
- `POST /api/projects/{id}/tags` - Add tag
- `GET /api/projects/{id}/notes` - List notes
- `POST /api/projects/{id}/notes` - Add note

### Configuration

Configure the API server via environment variables in `.env`:

- `API_HOST`: API server host (default: `0.0.0.0`)
- `API_PORT`: API server port (default: `8000`)
- `DB_HOST`: MySQL host (default: `localhost`)
- `DB_PORT`: MySQL port (default: `3306`)
- `DB_NAME`: MySQL database name
- `DB_USER`: MySQL username
- `DB_PASSWORD`: MySQL password

---

## CLI Usage

### Using the CLI

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

ContextGrid includes a beautiful web interface for browsing and managing your projects.

### Starting the Web UI

```bash
# Make sure the API server is running first!
python api/server.py

# Then in another terminal, start the web UI
python web/app.py
```

The web interface will be available at: **http://127.0.0.1:8080**

**Note:** The Web UI requires the API server to be running on `http://localhost:8000`.

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

- Enhanced full-text search across projects and notes via API
- Timeline view of project activity
- Authentication and multi-user support
- Export/import functionality for backups
- Mobile app
- Desktop app (Electron or Tauri)
- Integration with Git for auto-tracking
- Webhooks for external integrations

---

## Troubleshooting

### API Server Won't Start

**Problem:** `Database connection failed` error

**Solution:**
1. Check that MySQL is running: `systemctl status mysql` (Linux) or `brew services list` (Mac)
2. Verify database credentials in `.env` file
3. Ensure database exists: `mysql -u root -p -e "SHOW DATABASES;"`
4. Test connection: `mysql -u contextgrid_user -p contextgrid`

### CLI Commands Fail

**Problem:** `Cannot connect to API server` error

**Solution:**
1. Ensure API server is running: `python api/server.py`
2. Check `API_ENDPOINT` in `.env` matches the server address
3. Verify API server is listening: `curl http://localhost:8000/api/health`

### Web UI Shows Empty Data

**Problem:** Web UI loads but shows no projects

**Solution:**
1. Verify API server is running on the expected port (8000)
2. Check browser console for errors (F12)
3. Ensure Web UI is configured to connect to the correct API endpoint

### Migration Issues

**Problem:** Migration script fails

**Solution:**
1. Ensure SQLite database exists at `data/projects.db`
2. Verify MySQL database is empty or doesn't have conflicting data
3. Check that user has sufficient permissions on MySQL database
4. Run migration with verbose output for debugging

### Port Conflicts

**Problem:** `Address already in use` error

**Solution:**
1. API server uses port 8000, Web UI uses port 8080
2. Change ports in `.env` or when starting servers
3. Kill existing processes: `lsof -i :8000` and `kill <PID>`

---

## Development

### Running Tests

```bash
# TODO: Add tests
pytest
```

### Code Style

This project uses:
- PEP 8 for Python code style
- Type hints where appropriate
- Docstrings for all public functions

### Contributing

This is a personal project, but suggestions and feedback are welcome!

---

## License

[License information here]

---

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [PyMySQL](https://github.com/PyMySQL/PyMySQL) - Pure Python MySQL client
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [Uvicorn](https://www.uvicorn.org/) - ASGI server

---

*ContextGrid - Track what you're building, where it lives, and what's next.*
