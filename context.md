# PROJECT CONTEXT — GlobeTrotter
# Odoo x LDCE Ahmedabad Hackathon 2026


## Problem Statement
GlobeTrotter — Smart Travel Planning Web Application

## Tech Stack
- Backend:  Python Flask (port 5000)
- Database: SQLite (file: globetrotter.db)
- Frontend: HTML + CSS + Vanilla JavaScript
- CORS:     Enabled

## Database Tables
### users
| column     | type      | notes               |
|------------|-----------|---------------------|
| id         | INTEGER   | PK, autoincrement   |
| name       | TEXT      | NOT NULL            |
| email      | TEXT      | UNIQUE, NOT NULL    |
| password   | TEXT      | sha256 hashed       |
| created_at | TIMESTAMP | DEFAULT NOW         |

### trips
| column      | type      | notes               |
|-------------|-----------|---------------------|
| id          | INTEGER   | PK, autoincrement   |
| user_id     | INTEGER   | FK → users.id       |
| title       | TEXT      | NOT NULL            |
| description | TEXT      |                     |
| start_date  | TEXT      | YYYY-MM-DD          |
| end_date    | TEXT      | YYYY-MM-DD          |
| is_public   | INTEGER   | 0=private, 1=public |
| created_at  | TIMESTAMP | DEFAULT NOW         |

## API Endpoints
```
GET    /api/health
POST   /api/auth/register   { name, email, password }
POST   /api/auth/login      { email, password }
GET    /api/trips            → list user's trips
POST   /api/trips            { user_id, title, description, start_date, end_date }
GET    /api/trips/<id>       → trip detail + cities + activities
PUT    /api/trips/<id>       → update trip
DELETE /api/trips/<id>       → delete trip
```

## API Response Format
```json
{ "success": true,  "data": [...], "message": "..." }
{ "success": false, "message": "Error description"  }
```

## Fetch Base URL
```
http://localhost:5000
```

## Coding Rules
- DB columns:     snake_case
- All routes:     /api/ prefix
- Passwords:      sha256 hashed before storing
- Error response: { "success": false, "message": "..." }

## Member Roles
- M1: Backend  — app.py, database.py, routes/auth.py, routes/trips.py
- M2: Frontend — static/index.html, dashboard.html, trip.html, style.css
- M3: Integration — static/app.js, bug fixes, CORS, fetch wiring
- M4: DevOps   — README.md, seed_data.py, Git setup, demo video
