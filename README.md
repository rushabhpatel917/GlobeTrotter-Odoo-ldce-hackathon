# 🌍 GlobeTrotter — Smart Multi-City Travel Planner & Budget Engine

> **Odoo x LDCE Hackathon 2026 Official Submission**  
> *A high-performance, web-based travel management system featuring multi-city destination flow, activity scheduling, day-wise timeline generation, dynamic cost aggregation, and read-only public sharing.*

---

### 🌐 Live Public Demo & Evaluator Access

- 🌐 **LIVE PUBLIC URL FOR JUDGES:** **[https://wicked-months-worry.loca.lt](https://wicked-months-worry.loca.lt)**
- 🚀 **Local Web App Portal:** `http://localhost:5000` *(Start via `python app.py`)*
- 🔒 **Shared Public Read-Only Trip View:** [https://wicked-months-worry.loca.lt/static/public-trip.html?id=1](https://wicked-months-worry.loca.lt/static/public-trip.html?id=1)

---

## 👥 Hackathon Engineering Team

| Member | Developer Name | Primary Role | GitHub Handle |
|:---|:---|:---|:---|
| **M1** | **Aksh Patel** | Lead Backend Engineer & Data Architecture | `Akshpatel39` |
| **M2** | **Pushkar Kanzariya** | Lead Frontend Engineer & UX Design | `pushkar1001` |
| **M3** | **Rushabh Patel** | Data Integration & Itinerary Logic Engineer | `rushabhpatel917` |
| **M4** | **Yug Patel** | DevOps, Quality Assurance & Public Sharing | `yugHp-tech` |

---

## ✨ Core Key Features

1. **🗺️ Multi-City Trip Planner:** Create trips with ordered destination stops (e.g. Paris ➔ Rome ➔ Barcelona) with start and end dates.
2. **🎟️ Activity Discovery & Stop Association:** Search and filter curated activities by category, cost, and city, linking activities directly to specific destination stops.
3. **📅 Day-Wise Itinerary Engine:** Automatically generates chronological day-by-day travel timelines (Trip ➔ Date ➔ City ➔ Activity) with time chips and duration pills.
4. **💰 Automatic Budget Engine & Expense Tracker:** Calculates itemized cost categories (Transport, Stay, Activities, Meals, Other), total estimated cost, and average daily cost per day.
5. **📊 Executive Trip Summary:** Provides at-a-glance KPI cards, destination flow breadcrumbs, and comprehensive metrics for quick decision-making.
6. **🌐 Public Read-Only Sharing:** Toggle public status with one click, generating a shareable URL (`/static/public-trip.html?id=<id>`) with automated clipboard copy support.

---

## 🛠️ Technology Stack

| Component | Technology | Description |
|:---|:---|:---|
| **Backend Engine** | Python Flask 3.x | Lightweight, modular blueprint API architecture |
| **Database** | SQLite3 (`globetrotter.db`) | Relational schema with foreign keys and dynamic migrations |
| **Frontend UI** | HTML5, Modern Vanilla CSS, ES6 JavaScript | Glassmorphism styling, responsive dark mode design system |
| **State & API** | REST API + Fetch API | Asynchronous JSON responses with standardized structure |

---

## 📐 Database Schema

```
trips (id, title, description, start_date, end_date, is_public, user_id)
  │
  ├── trip_stops (id, trip_id, city, country, start_date, end_date, stop_order)
  │
  ├── trip_activities (id, trip_id, activity_id, stop_id, day_number, activity_date, activity_time, notes)
  │     └── activities (id, name, category, description, duration, cost, city, preferred_time)
  │
  └── trip_expenses (id, trip_id, category, title, cost, notes)
```

---

## 🔌 API Endpoints Summary

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/api/health` | Backend engine health status check |
| `POST` | `/api/auth/login` | User login authentication |
| `GET` | `/api/trips` | List all trips for active user |
| `POST` | `/api/trips` | Create a new trip with initial city stops |
| `GET` | `/api/trips/<id>` | Fetch detailed trip payload |
| `POST` | `/api/trips/<id>/stops` | Add a destination stop to a trip |
| `GET` | `/api/activities` | Filter & search activity catalog |
| `POST` | `/api/trips/<id>/activities` | Link activity to trip destination stop |
| `PUT` | `/api/trip-activities/<id>/schedule` | Assign date, time, and notes to activity |
| `GET` | `/api/trips/<id>/itinerary` | Fetch chronological day-wise itinerary |
| `GET` | `/api/trips/<id>/budget` | Compute trip budget totals and averages |
| `POST` | `/api/trips/<id>/expenses` | Add custom manual expense (Stay, Transport, Meals) |
| `POST` | `/api/trips/<id>/share` | Toggle public status & return share URL |
| `GET` | `/api/trips/public/<id>` | Fetch public read-only trip payload |

---

## 🎯 12-Step Judge Demonstration Walkthrough

1. **Launch App:** Navigate to `http://localhost:5000` (Main Guided Portal).
2. **Dashboard:** Click **"Trip Dashboard"** (`/static/dashboard.html`).
3. **Plan New Trip:** Click **"＋ Plan New Trip"** (`/static/create-trip.html`).
4. **Enter Details:** Input trip title, dates, and destination stops (e.g. Paris & Rome).
5. **Trip Executive View:** View the newly created trip summary card on `/static/trip-details.html`.
6. **Add Destination Stops:** Append additional stops dynamically.
7. **Discover Activities:** Click **"＋ Add Activity"** to open activity catalog filtered by destination city.
8. **Link Activities:** Select activities (e.g. *Eiffel Tower Visit*, *Louvre Museum*, *Colosseum Tour*).
9. **Build Itinerary:** Click **"📅 Day-Wise Itinerary"** (`/static/itinerary.html`) to view the chronological timeline.
10. **Budget Breakdown:** Click **"💰 Budget Breakdown"** (`/static/budget.html`) to check total trip cost and average cost per day.
11. **Share Trip:** Click **"🔗 Share Trip"** to copy the public URL to clipboard.
12. **Public View:** Open the public URL (`/static/public-trip.html?id=<id>`) to view the read-only itinerary page.

---

## 🚀 Setup & Execution Instructions

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database schema & seed initial dataset
python database.py

# 3. Start local development server
python app.py

# 4. Open in web browser
http://localhost:5000
```

---

## 🏆 Hackathon Commit History Log

- `8319bbd` **fix: validate end-to-end travel planning flow** *(M3 — Turn 6)*
- `3789c75` **fix: finalize primary user experience** *(M2 — Turn 6)*
- `263d5c8` **fix: stabilize GlobeTrotter system integration** *(M1 — Turn 6)*
- `5d239ca` **feat: implement shareable public itinerary** *(M4 — Turn 5)*
- `1e03809` **feat: add comprehensive trip summary** *(M3 — Turn 5)*
- `3caa9f9` **feat: build trip budget dashboard** *(M2 — Turn 5)*
- `15e34ba` **feat: implement automatic trip budget engine** *(M1 — Turn 5)*
- `e82311d` **style: polish day-wise itinerary experience** *(M4 — Turn 4)*
- `80aa751` **feat: build day-wise travel itinerary** *(M3 — Turn 4)*
- `65d1d6a` **feat: add itinerary editing controls** *(M2 — Turn 4)*
- `be9ac9a` **feat: implement itinerary scheduling logic** *(M1 — Turn 4)*

---
*Built with ❤️ for Odoo x LDCE Hackathon 2026.*
