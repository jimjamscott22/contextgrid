# ContextGrid API Documentation

## Overview

The ContextGrid API is a RESTful API built with FastAPI that provides access to project management functionality. It supports CRUD operations for projects, tags, and notes, with MySQL as the backend database.

**Base URL:** `http://localhost:8000`

## Authentication

Currently, the API does not require authentication. This may change in future versions.

## Response Formats

All responses are in JSON format. Successful requests return appropriate HTTP status codes (200, 201, etc.) and response data. Error responses include a `detail` field with error information.

### Success Response Example
```json
{
  "id": 1,
  "name": "My Project",
  "status": "active",
  ...
}
```

### Error Response Example
```json
{
  "detail": "Project 999 not found"
}
```

## Endpoints

### Health Check

#### `GET /api/health`

Check if the API server and database are healthy.

**Response:**
```json
{
  "status": "ok",
  "message": "API server and database are healthy"
}
```

---

## Projects

### List Projects

#### `GET /api/projects`

List all projects with optional filtering, pagination, and sorting.

**Query Parameters:**
- `status` (optional): Filter by status (`idea`, `active`, `paused`, `archived`)
- `tag` (optional): Filter by tag name
- `limit` (optional): Maximum number of results (1-100)
- `offset` (optional): Number of results to skip
- `sort_by` (optional): Field to sort by (`name`, `created_at`, `last_worked_at`, `status`). Default: `last_worked_at`
- `sort_order` (optional): Sort order (`asc`, `desc`). Default: `desc`

**Example Request:**
```bash
GET /api/projects?status=active&limit=10&sort_by=name&sort_order=asc
```

**Response:**
```json
{
  "projects": [
    {
      "id": 1,
      "name": "ContextGrid",
      "description": "Personal project tracker",
      "status": "active",
      "project_type": "web",
      "primary_language": "Python",
      "stack": "FastAPI + MySQL",
      "repo_url": "https://github.com/user/contextgrid",
      "local_path": "/home/user/projects/contextgrid",
      "scope_size": "medium",
      "learning_goal": "Learn FastAPI and MySQL",
      "created_at": "2024-01-15T10:30:00",
      "last_worked_at": "2024-01-20T14:45:00",
      "is_archived": 0
    }
  ],
  "total": 1
}
```

### Get Project

#### `GET /api/projects/{project_id}`

Get details of a specific project.

**Path Parameters:**
- `project_id` (integer): Project ID

**Example Request:**
```bash
GET /api/projects/1
```

**Response:**
```json
{
  "id": 1,
  "name": "ContextGrid",
  "description": "Personal project tracker",
  "status": "active",
  ...
}
```

**Status Codes:**
- `200 OK`: Project found and returned
- `404 Not Found`: Project does not exist

### Create Project

#### `POST /api/projects`

Create a new project.

**Request Body:**
```json
{
  "name": "New Project",
  "description": "Project description",
  "status": "idea",
  "project_type": "web",
  "primary_language": "Python",
  "stack": "FastAPI",
  "repo_url": "https://github.com/user/project",
  "local_path": "/home/user/projects/new-project",
  "scope_size": "medium",
  "learning_goal": "Learn new technology"
}
```

**Required Fields:**
- `name` (string): Project name

**Optional Fields:**
- `description` (string): Project description
- `status` (string): One of `idea`, `active`, `paused`, `archived`. Default: `idea`
- `project_type` (string): One of `web`, `cli`, `library`, `homelab`, `research`
- `primary_language` (string): Programming language
- `stack` (string): Technology stack
- `repo_url` (string): Repository URL
- `local_path` (string): Local filesystem path
- `scope_size` (string): One of `tiny`, `medium`, `long-haul`
- `learning_goal` (string): Learning objectives

**Response:**
```json
{
  "id": 2,
  "name": "New Project",
  ...
}
```

**Status Codes:**
- `201 Created`: Project created successfully
- `400 Bad Request`: Invalid input data
- `500 Internal Server Error`: Server error

### Update Project

#### `PUT /api/projects/{project_id}`

Update an existing project. Only include fields you want to update.

**Path Parameters:**
- `project_id` (integer): Project ID

**Request Body:**
```json
{
  "status": "active",
  "description": "Updated description"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "ContextGrid",
  "status": "active",
  "description": "Updated description",
  ...
}
```

**Status Codes:**
- `200 OK`: Project updated successfully
- `404 Not Found`: Project does not exist
- `400 Bad Request`: Invalid input data

### Delete Project

#### `DELETE /api/projects/{project_id}`

Delete a project and all associated data (notes, tags).

**Path Parameters:**
- `project_id` (integer): Project ID

**Response:**
```json
{
  "message": "Project 1 deleted successfully"
}
```

**Status Codes:**
- `200 OK`: Project deleted successfully
- `404 Not Found`: Project does not exist

### Touch Project

#### `POST /api/projects/{project_id}/touch`

Update the `last_worked_at` timestamp to the current time.

**Path Parameters:**
- `project_id` (integer): Project ID

**Response:**
```json
{
  "message": "Updated last_worked_at for project 1",
  "last_worked_at": "2024-01-20T15:30:00"
}
```

**Status Codes:**
- `200 OK`: Timestamp updated successfully
- `404 Not Found`: Project does not exist

---

## Tags

### List All Tags

#### `GET /api/tags`

List all tags with project counts.

**Response:**
```json
{
  "tags": [
    {
      "name": "python",
      "project_count": 5
    },
    {
      "name": "web",
      "project_count": 3
    }
  ],
  "total": 2
}
```

### Get Project Tags

#### `GET /api/projects/{project_id}/tags`

Get all tags for a specific project.

**Path Parameters:**
- `project_id` (integer): Project ID

**Response:**
```json
[
  {"name": "python"},
  {"name": "web"}
]
```

**Status Codes:**
- `200 OK`: Tags returned successfully
- `404 Not Found`: Project does not exist

### Add Tag to Project

#### `POST /api/projects/{project_id}/tags`

Add a tag to a project. If the tag doesn't exist, it will be created.

**Path Parameters:**
- `project_id` (integer): Project ID

**Request Body:**
```json
{
  "name": "python"
}
```

**Response:**
```json
{
  "message": "Tag 'python' added to project 1"
}
```

**Status Codes:**
- `201 Created`: Tag added successfully
- `404 Not Found`: Project does not exist

### Remove Tag from Project

#### `DELETE /api/projects/{project_id}/tags/{tag_name}`

Remove a tag from a project.

**Path Parameters:**
- `project_id` (integer): Project ID
- `tag_name` (string): Tag name

**Example Request:**
```bash
DELETE /api/projects/1/tags/python
```

**Response:**
```json
{
  "message": "Tag 'python' removed from project 1"
}
```

**Status Codes:**
- `200 OK`: Tag removed successfully
- `404 Not Found`: Tag or project does not exist

---

## Notes

### Get Project Notes

#### `GET /api/projects/{project_id}/notes`

Get all notes for a project, ordered by creation date (newest first).

**Path Parameters:**
- `project_id` (integer): Project ID

**Response:**
```json
{
  "notes": [
    {
      "id": 1,
      "project_id": 1,
      "note_type": "log",
      "content": "Started working on the API",
      "created_at": "2024-01-20T14:30:00"
    }
  ],
  "total": 1
}
```

**Status Codes:**
- `200 OK`: Notes returned successfully
- `404 Not Found`: Project does not exist

### Create Note

#### `POST /api/projects/{project_id}/notes`

Create a new note for a project.

**Path Parameters:**
- `project_id` (integer): Project ID

**Request Body:**
```json
{
  "content": "Completed the authentication module",
  "note_type": "log"
}
```

**Required Fields:**
- `content` (string): Note content

**Optional Fields:**
- `note_type` (string): One of `log`, `idea`, `blocker`, `reflection`. Default: `log`

**Response:**
```json
{
  "id": 2,
  "project_id": 1,
  "note_type": "log",
  "content": "Completed the authentication module",
  "created_at": "2024-01-20T15:00:00"
}
```

**Status Codes:**
- `201 Created`: Note created successfully
- `404 Not Found`: Project does not exist
- `400 Bad Request`: Invalid input data

### Get Note

#### `GET /api/notes/{note_id}`

Get a specific note by ID.

**Path Parameters:**
- `note_id` (integer): Note ID

**Response:**
```json
{
  "id": 1,
  "project_id": 1,
  "note_type": "log",
  "content": "Started working on the API",
  "created_at": "2024-01-20T14:30:00"
}
```

**Status Codes:**
- `200 OK`: Note found and returned
- `404 Not Found`: Note does not exist

### Delete Note

#### `DELETE /api/notes/{note_id}`

Delete a note by ID.

**Path Parameters:**
- `note_id` (integer): Note ID

**Response:**
```json
{
  "message": "Note 1 deleted successfully"
}
```

**Status Codes:**
- `200 OK`: Note deleted successfully
- `404 Not Found`: Note does not exist

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 OK | Request successful |
| 201 Created | Resource created successfully |
| 400 Bad Request | Invalid request data |
| 404 Not Found | Resource not found |
| 500 Internal Server Error | Server error |
| 503 Service Unavailable | Database connection failed |

---

## Rate Limiting

Currently, there is no rate limiting implemented. This may change in future versions.

---

## Data Types

### Project Status Values
- `idea`: Early concept, not yet started
- `active`: Currently being worked on
- `paused`: On hold, may resume later
- `archived`: Completed or abandoned

### Project Type Values
- `web`: Web application
- `cli`: Command-line tool
- `library`: Library or package
- `homelab`: Home lab infrastructure
- `research`: Research or experimental project

### Scope Size Values
- `tiny`: Quick, small project
- `medium`: Medium-sized project
- `long-haul`: Long-term, complex project

### Note Type Values
- `log`: General work log
- `idea`: Idea or brainstorm
- `blocker`: Blocking issue
- `reflection`: Reflection or learning

---

## Future Features

The following features are planned for future versions:

- Search API endpoint for full-text search
- Authentication and authorization
- Webhooks for project events
- Bulk operations
- Export/import functionality
- GraphQL API

---

## Getting Started

### Prerequisites

- MySQL database server
- Python 3.8+
- Required Python packages (see `requirements.txt`)

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create `.env` file with database credentials:
   ```
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=contextgrid
   DB_USER=contextgrid_user
   DB_PASSWORD=your_password
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

3. Start the API server:
   ```bash
   python api/server.py
   ```

4. The API will be available at `http://localhost:8000`

### Testing the API

You can test the API using curl, HTTPie, Postman, or any HTTP client:

```bash
# Health check
curl http://localhost:8000/api/health

# List projects
curl http://localhost:8000/api/projects

# Create a project
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project", "status": "idea"}'
```

---

## Support

For issues and questions, please open an issue on the GitHub repository.
