# Python App Run Modes

This guide explains common ways to run Python applications, especially when
they include a user interface. It is meant as a practical map for recognizing
what kind of app you are looking at when an AI tool creates a project for you.

Python can be the whole app, the backend of a larger app, or just one part of
a multi-language system. The right structure depends on how interactive the UI
needs to be, where the app will run, and how many clients need to talk to the
same data.

---

## Quick Comparison

| Shape | Main UI | Backend | Best For |
| --- | --- | --- | --- |
| CLI-only Python app | Terminal | Python | Scripts, tools, automation, local workflows |
| Python web app with server-rendered HTML | Browser | Python | Dashboards, admin tools, read-heavy apps, simple forms |
| Python API plus React frontend | Browser | Python + JavaScript/TypeScript | Highly interactive apps, rich client state, polished web products |
| Python desktop app | Native window | Python | Local tools, offline workflows, file utilities |
| Python backend plus desktop shell | Desktop window with web UI | Python + web frontend | Desktop apps that want modern web-style UI |

---

## Option 1: CLI-Only Python App

```
User
  |
  v
Terminal command
  |
  v
Python code
  |
  v
Files / database / APIs
```

A CLI-only app is controlled through terminal commands. There is no browser UI
or desktop window.

This is often the simplest structure because Python can directly handle the
command, run business logic, and read or write data.

Good fit when:

- The app is mainly for one person or a technical user.
- The workflow is command-driven, repeatable, or scriptable.
- You want minimal moving parts.
- The app works well as part of shell scripts or automation.

Common tools:

- `argparse`, `click`, or `typer` for command parsing.
- SQLite, JSON, CSV, or local files for storage.
- `uv` for dependency and script management.

Example shape:

```
python src/main.py list
python src/main.py add "New project"
```

ContextGrid has this mode through its CLI in `src/main.py` and `src/cli.py`.

---

## Option 2: Python Web App With Server-Rendered HTML

```
Browser
  |
  v
Python web server
  |
  v
HTML templates
  |
  v
Database / files / APIs
```

In this structure, Python serves complete HTML pages to the browser. The
frontend is usually built with templates rather than a separate React app.

This is the structure used by many Flask, Django, and FastAPI + Jinja apps.
The browser receives HTML, CSS, and maybe a small amount of JavaScript.

Good fit when:

- The UI is mostly pages, lists, forms, dashboards, or reports.
- You want a browser interface without maintaining a separate frontend app.
- The app does not need complex client-side state.
- You want the backend and frontend logic to stay close together.

Common tools:

- FastAPI, Flask, or Django for the web server.
- Jinja2 or Django templates for HTML rendering.
- Static CSS and JavaScript for styling and light interaction.
- Uvicorn or Gunicorn for serving the app.

Example shape:

```
uv run uvicorn web.app:app --host 0.0.0.0 --port 8081
```

ContextGrid uses this pattern for its web UI. The browser talks to
`web/app.py`, and `web/app.py` renders templates from `web/templates`.

This does not mean the app has no frontend. It means the frontend is rendered
by Python on the server instead of compiled from a JavaScript framework.

---

## Option 3: Python API Plus React Frontend

```
Browser
  |
  v
React app
  |
  v
HTTP requests
  |
  v
Python API
  |
  v
Database / files / external services
```

This is a split frontend/backend architecture. Python exposes an API, and
React controls the browser experience.

The Python side usually returns JSON instead of full HTML pages. The React
side handles screens, navigation, form state, loading states, client-side
interactions, and visual components.

Good fit when:

- The frontend is highly interactive.
- You want a polished single-page app experience.
- The app has complex UI state, drag-and-drop, realtime updates, charts, maps,
  editors, or rich controls.
- You want to share the same API with a mobile app, desktop app, or other
  clients later.
- The project benefits from the JavaScript and TypeScript ecosystem.

Common tools:

- FastAPI or Django REST Framework for the Python API.
- React, Next.js, Vite, or Remix for the frontend.
- `fetch`, Axios, TanStack Query, or similar libraries for API calls.
- OpenAPI schemas to document the API contract.

Example development shape:

```
uv run uvicorn api.server:app --port 8000
npm run dev
```

In this setup, there are usually two development servers:

- The Python API server.
- The JavaScript frontend dev server.

This adds complexity, but it can make the UI much more capable.

---

## Option 4: Python Desktop App

```
User
  |
  v
Desktop window
  |
  v
Python UI framework
  |
  v
Python logic
  |
  v
Files / database / APIs
```

A desktop app runs as a native application on the user's machine. Instead of
opening a browser tab, the user opens an app window.

Good fit when:

- The app is local-first or offline-first.
- The app works heavily with local files.
- You want a familiar desktop-window experience.
- You do not need the app to be accessed from many devices at once.

Common tools:

- Tkinter for simple built-in desktop interfaces.
- PySide or PyQt for fuller native desktop apps.
- Kivy for touch-oriented or cross-platform UI.
- Toga or BeeWare for native cross-platform packaging.

Example shape:

```
uv run python app.py
```

Desktop apps can feel simpler for local tools, but packaging can become its own
project. Creating installers for Windows, macOS, and Linux often takes more
care than running a web app locally.

---

## Option 5: Python Backend Plus Desktop Shell

```
Desktop app shell
  |
  v
Web-based UI
  |
  v
Python backend
  |
  v
Files / database / APIs
```

Some desktop apps are really web apps packaged inside a desktop shell. The UI
is built with web technology, while Python handles local logic or data.

Good fit when:

- You want a modern web-style UI in a desktop app.
- The app needs local filesystem access.
- You want to reuse a React or HTML frontend.
- You want the app to feel installable rather than browser-based.

Common tools:

- Electron or Tauri for the desktop shell.
- React, Vue, Svelte, or plain HTML/CSS for the UI.
- FastAPI, Flask, or a local Python process for backend logic.

This can be powerful, but it has more moving parts than a pure Python desktop
app or a pure Python web app.

---

## How ContextGrid Fits In

ContextGrid is a Python-first app with multiple access paths:

```
CLI
  |
  v
Python models
  |
  v
API or direct database access
```

```
Browser
  |
  v
FastAPI web UI
  |
  v
FastAPI API server
  |
  v
Database
```

The important idea is that ContextGrid is not using React because the web UI is
not the main source of complexity. The app is centered around project data,
CLI workflows, local-first usage, and a simple browser dashboard.

That makes server-rendered FastAPI a reasonable choice:

- One main language: Python.
- Fewer build tools.
- Easy access to existing Python models and API clients.
- A simple web UI that does not need a full frontend framework.

If ContextGrid later needed heavy browser interaction, a React frontend could
be added without throwing away the Python API. The API would become the stable
contract, and React would become another client.

---

## Choosing A Structure

Use a CLI when the app is mostly a tool.

Use server-rendered Python HTML when the app needs a practical browser UI but
does not need lots of client-side interaction.

Use Python plus React when the browser experience is the product and the UI
needs to feel dynamic, fast, and component-driven.

Use a desktop UI when the app is mainly local, offline, or file-centered.

Use a desktop shell with a web frontend when you want installable desktop
behavior with a modern web UI.

---

## Questions To Ask When Looking At An App

- Where does the user interface live: terminal, browser, or desktop window?
- Does the backend return HTML pages or JSON data?
- Is there one server process or separate frontend and backend servers?
- Is the database accessed directly by Python or through an API?
- Is the frontend mostly static pages, simple forms, or rich interactive state?
- Can more than one kind of client use the same backend?

Those questions usually reveal the real structure quickly.

