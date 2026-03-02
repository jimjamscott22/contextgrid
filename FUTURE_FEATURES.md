# ContextGrid - Future Features & Upgrades

This document tracks planned features and enhancements for ContextGrid. Features are organized by priority and category.

---

## Recently Completed

- ✅ **Side Navigation Menu** (Completed: 2026-01-24)
  - Collapsible sidebar with project list
  - Search functionality
  - Grouped by status (Active, Ideas, Paused, Archived)
  - Responsive design (persistent on desktop, drawer on mobile)
  - localStorage persistence for open/closed state

- ✅ **Charts & Analytics** (Completed: 2026-03-01)
  - Analytics dashboard at `/analytics` with Chart.js
  - Summary stat cards (total, active, ideas, avg progress)
  - 6 charts: status distribution (doughnut), by language (bar), by type (pie), activity over time (line), progress distribution (bar), top tags (bar)
  - Full dark mode support via CSS variable detection
  - Responsive grid layout

---

## High Priority (Quick Wins)

### 1. Kanban Board View
**Description:** Visual drag-and-drop board for managing project status

**Features:**
- Drag projects between status columns (Idea → Active → Paused → Archived)
- Card view showing project name, tags, last worked date
- Toggle between list view and board view
- Visual workflow management

**Implementation:**
- Add new route `/projects/board`
- Use HTML5 drag-and-drop API or library like SortableJS
- Update status via API when cards are moved
- Store view preference (list vs board) in localStorage

**Files to modify:**
- `web/app.py` - Add board view route
- `web/templates/board.html` - New board template
- `web/static/css/style.css` - Board styling
- API already supports status updates

---

### 2. Activity Heatmap
**Description:** GitHub-style contribution calendar showing project activity

**Features:**
- Visual calendar showing which days you worked on projects
- Color intensity based on activity level
- Hover to see project names and notes
- Motivational streak tracking

**Implementation:**
- Add activity tracking to notes/touch events
- Generate calendar grid with CSS Grid
- Fetch activity data grouped by date
- Color scale based on activity count

**Files to modify:**
- `web/templates/home.html` - Add heatmap section
- `web/static/css/style.css` - Calendar styling
- `api/server.py` - Add activity summary endpoint
- `api/db.py` - Query for activity aggregation

---

### 3. Project Progress Tracker
**Description:** Visual progress tracking for projects

**Features:**
- Add progress percentage field (0-100%) to projects
- Display progress bars on cards
- Milestone tracking
- Progress history

**Implementation:**
- Add `progress` column to projects table (INT 0-100)
- Update Pydantic models to include progress
- Add progress bar component to project cards
- Allow progress updates via web UI

**Files to modify:**
- `scripts/init_mysql.sql` - Add progress column
- `api/models.py` - Add progress field
- `api/db.py` - Include in queries
- `web/templates/project_*.html` - Show progress bars

---

### 4. Markdown Support in Notes
**Description:** Rich formatting for notes using Markdown

**Features:**
- Markdown rendering in note display
- Code snippets with syntax highlighting
- Links, lists, headers, bold/italic
- Preview while editing

**Implementation:**
- Use markdown library (e.g., Python-Markdown or marked.js)
- Render markdown on server-side or client-side
- Add syntax highlighting (Prism.js or Highlight.js)
- Keep plain text in database

**Files to modify:**
- `requirements.txt` - Add markdown library
- `web/templates/project_detail.html` - Render markdown
- `web/static/css/style.css` - Code block styling

---

### 5. Saved Filters
**Description:** Save custom filter combinations for quick access

**Features:**
- Save filter combinations (status + tags + search)
- Name saved filters
- Quick access dropdown
- Share filter URLs

**Implementation:**
- Store filters in localStorage
- Add UI for managing saved filters
- Generate shareable URLs with query params
- Optional: Store in database for cross-device sync

**Files to modify:**
- `web/templates/projects.html` - Add filter management UI
- `web/static/js/filters.js` - New JS module
- `web/static/css/style.css` - Filter UI styling

---

## Medium Priority (Enhanced Features)

### 6. Project Relationships & Dependencies
**Description:** Link related projects together

**Features:**
- Parent/child project relationships
- Dependency tracking (Project A depends on Project B)
- Visual dependency graph
- Relationship types (related, depends-on, part-of)

**Implementation:**
- New `project_relationships` table
- Graph visualization (D3.js or vis.js)
- Relationship management UI
- Circular dependency detection

**Files to create/modify:**
- `scripts/init_mysql.sql` - New table
- `api/models.py` - Relationship models
- `api/server.py` - Relationship endpoints
- `web/templates/project_detail.html` - Show relationships

---

### 7. Resource Links
**Description:** Attach multiple URLs to projects

**Features:**
- Multiple URL types (docs, deployment, design, board)
- Quick access links on project detail page
- Link categories
- Link icons based on type

**Implementation:**
- New `project_links` table (id, project_id, url, title, type)
- CRUD endpoints for links
- Display on project detail page
- Auto-detect link type from URL

**Files to create/modify:**
- `scripts/init_mysql.sql` - New table
- `api/models.py` - Link models
- `api/server.py` - Link endpoints
- `web/templates/project_detail.html` - Links section

---

### 8. Enhanced Search
**Description:** Powerful global search across all content

**Features:**
- Search projects, notes, and tags simultaneously
- Search syntax (tag:python status:active)
- Recent searches dropdown
- Search suggestions
- Fuzzy matching

**Implementation:**
- Full-text search indexes in MySQL
- Search parser for query syntax
- Autocomplete using existing data
- Search history in localStorage

**Files to modify:**
- `api/server.py` - Enhanced search endpoint
- `api/db.py` - Full-text search queries
- `web/templates/base.html` - Global search bar
- `web/static/js/search.js` - New JS module

---

### 9. Time Tracking
**Description:** Track time invested in projects

**Features:**
- Add "time spent" field (hours/minutes)
- Time entry log
- Visual time distribution charts
- Automatic time tracking based on activity

**Implementation:**
- New `time_entries` table
- Add time tracking UI to project detail
- Aggregate time by project/status
- Charts using Chart.js

**Files to create/modify:**
- `scripts/init_mysql.sql` - New table
- `api/models.py` - Time entry models
- `api/server.py` - Time tracking endpoints
- `web/templates/project_detail.html` - Time tracking UI

---

### 10. Project Templates
**Description:** Quick-start templates for common project types

**Features:**
- Pre-filled project templates (Python CLI, Web App, etc.)
- Custom template creation
- Clone existing project as template
- Template library

**Implementation:**
- Store templates as JSON
- Template selection during project creation
- Template CRUD operations
- Export/import templates

**Files to create/modify:**
- `api/models.py` - Template models
- `api/server.py` - Template endpoints
- `web/templates/project_new.html` - Template selection
- `templates/` directory for default templates

---

## Lower Priority (Nice to Have)

### 11. Data Export & Backup
**Description:** Export and backup project data

**Features:**
- One-click backup to JSON/YAML
- Export individual project as Markdown
- Import projects from JSON
- Scheduled automatic backups
- GitHub/GitLab sync to auto-discover repos

**Implementation:**
- Export endpoints in API
- Backup scheduler (cron or Python scheduler)
- Import validation and conflict resolution
- Git integration using GitHub/GitLab API

---

### 12. Charts & Analytics
**Description:** Visual insights into project portfolio

**Features:**
- Projects by type (pie chart)
- Projects by language (bar chart)
- Activity over time (line graph)
- Status distribution
- Tag usage analytics

**Implementation:**
- Add analytics endpoints to API
- Use Chart.js or D3.js
- Add analytics page to web UI
- Cached aggregation for performance

---

### 13. Goals & Milestones
**Description:** Track project milestones and goals

**Features:**
- Add milestones to projects
- Track completion status
- Set target dates
- Progress tracking
- Overdue notifications

**Implementation:**
- New `project_milestones` table
- Milestone CRUD operations
- Progress calculation
- Notification system

---

### 14. PWA Support
**Description:** Progressive Web App for offline access

**Features:**
- Install as standalone app
- Offline functionality
- Service worker caching
- App manifest
- Push notifications

**Implementation:**
- Add service worker
- Create manifest.json
- Cache static assets and API responses
- Background sync

---

### 15. Theme Customization
**Description:** More theme options beyond light/dark

**Features:**
- Multiple color themes
- Custom accent colors
- Theme presets
- User-defined CSS variables
- Theme sharing

**Implementation:**
- Extend CSS variables
- Theme selector UI
- Store theme preferences
- Theme gallery

---

## Sidebar Enhancements

Since the sidebar was just implemented, here are additional features specifically for it:

### Sidebar Feature Ideas

1. **Pin/Favorite Projects**
   - Star projects to pin them to the top of the sidebar
   - Separate "Pinned" section above status groups
   - Pin state stored in localStorage or database

2. **Recently Worked Indicator**
   - Visual dot or badge for projects worked on in last 7 days
   - Highlight projects with recent activity

3. **Drag to Resize**
   - Allow users to resize sidebar width
   - Store width preference in localStorage
   - Min/max width constraints

4. **Quick Actions on Hover**
   - Show quick action icons when hovering project
   - Touch to mark as worked
   - Quick edit
   - Quick delete

5. **Project Count Badges**
   - Show total count in sidebar header
   - Count per status group
   - Active filters indicator

---

## Database Schema Changes Needed

### For Progress Tracking
```sql
ALTER TABLE projects ADD COLUMN progress INT DEFAULT 0;
ALTER TABLE projects ADD CONSTRAINT check_progress CHECK (progress >= 0 AND progress <= 100);
```

### For Time Tracking
```sql
CREATE TABLE time_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    duration_minutes INT NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project_date (project_id, date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### For Project Relationships
```sql
CREATE TABLE project_relationships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_project_id INT NOT NULL,
    target_project_id INT NOT NULL,
    relationship_type ENUM('related', 'depends_on', 'part_of') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (target_project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE KEY unique_relationship (source_project_id, target_project_id, relationship_type),
    INDEX idx_source (source_project_id),
    INDEX idx_target (target_project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### For Project Links
```sql
CREATE TABLE project_links (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    link_type ENUM('docs', 'deployment', 'design', 'board', 'other') DEFAULT 'other',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### For Milestones
```sql
CREATE TABLE project_milestones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_date DATE,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id),
    INDEX idx_target_date (target_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## API Endpoints to Add

### Analytics
- `GET /api/analytics/summary` - Overall statistics
- `GET /api/analytics/activity` - Activity heatmap data
- `GET /api/analytics/by-type` - Projects grouped by type
- `GET /api/analytics/by-language` - Projects grouped by language

### Time Tracking
- `GET /api/projects/{id}/time-entries` - List time entries
- `POST /api/projects/{id}/time-entries` - Add time entry
- `DELETE /api/time-entries/{id}` - Delete time entry

### Relationships
- `GET /api/projects/{id}/relationships` - Get project relationships
- `POST /api/projects/{id}/relationships` - Create relationship
- `DELETE /api/relationships/{id}` - Remove relationship

### Links
- `GET /api/projects/{id}/links` - List project links
- `POST /api/projects/{id}/links` - Add link
- `DELETE /api/links/{id}` - Remove link

### Milestones
- `GET /api/projects/{id}/milestones` - List milestones
- `POST /api/projects/{id}/milestones` - Create milestone
- `PUT /api/milestones/{id}` - Update milestone
- `DELETE /api/milestones/{id}` - Delete milestone

---

## UI/UX Improvements

1. **Loading States**
   - Skeleton screens while loading
   - Progress indicators for long operations
   - Optimistic UI updates

2. **Error Handling**
   - User-friendly error messages
   - Retry mechanisms
   - Offline indicators

3. **Accessibility**
   - ARIA labels
   - Keyboard navigation
   - Screen reader support
   - Focus management

4. **Animations**
   - Smooth transitions
   - Micro-interactions
   - Loading animations

5. **Mobile Optimizations**
   - Touch-friendly buttons
   - Swipe gestures
   - Mobile-first design
   - Bottom navigation on mobile

---

## Performance Optimizations

1. **Caching**
   - API response caching
   - Browser caching
   - Service worker caching

2. **Database**
   - Query optimization
   - Proper indexing
   - Connection pooling

3. **Frontend**
   - Code splitting
   - Lazy loading
   - Image optimization
   - Minification

---

## Notes

- This is a living document - add/remove features as priorities change
- Check off items as they're completed
- Add implementation notes and decisions as you go
- Consider user feedback when prioritizing

---

Last updated: 2026-01-24
