# GlobeTrotter 🌍 — Smart Multi-City Travel Planner & Budget Engine

> **Odoo x LDCE Hackathon 2026 Official Submission**  
> *A high-performance, web-based travel management system featuring multi-city destination flow, activity scheduling, day-wise timeline generation, dynamic cost aggregation, and read-only public sharing.*

---

## ✨ Features

- **🗺️ Multi-City Destinations:** Create trips with ordered destination stops (e.g. Paris ➔ Rome ➔ Barcelona).
- **🎟️ Activity Discovery:** Search and link curated activities by category, duration, cost, and city.
- **📅 Day-Wise Itinerary:** Automatically generates chronological day-by-day travel timelines (Trip ➔ Date ➔ City ➔ Activity).
- **💰 Dynamic Budget Engine:** Calculates itemized cost categories (Transport, Stay, Activities, Meals, Other), total estimated cost, and average daily cost per day.
- **📊 Executive Trip Summary:** At-a-glance KPI cards, destination flow breadcrumbs, and trip metrics.
- **🌐 Public Read-Only Sharing:** One-click public status toggle with shareable URL generation and clipboard copy integration.

---

## 👥 Hackathon Engineering Team

| Member | Developer Name | Primary Role | GitHub Handle |
|:---|:---|:---|:---|
| **M1** | **Aksh Patel** | Lead Backend Engineer & Data Architecture | `Akshpatel39` |
| **M2** | **Pushkar Kanzariya** | Lead Frontend Engineer & UX Design | `pushkar1001` |
| **M3** | **Rushabh Patel** | Data Integration & Itinerary Logic Engineer | `rushabhpatel917` |
| **M4** | **Yug Patel** | DevOps, Quality Assurance & Deployment Engineer | `yugHp-tech` |

---

## 🛠️ Technology Stack

| Component | Technology | Description |
|:---|:---|:---|
| **Backend Framework** | Python Flask 3.x | Lightweight, modular blueprint API architecture |
| **Production Server** | Gunicorn (WSGI) | Production-ready HTTP server interface |
| **Database** | SQLite3 (`globetrotter.db`) | Relational schema with foreign keys and migrations |
| **Frontend UI** | HTML5, Vanilla CSS, Vanilla ES6 JavaScript | Glassmorphic dark-mode design system |

---

## 💻 Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Copy `.env.example` to create your local environment configuration:
```bash
cp .env.example .env
```

### 3. Run Development Server
```bash
python app.py
```
Open your browser at `http://localhost:5000`.

### 4. Production Build & Execution
To start using production Gunicorn WSGI server:
```bash
gunicorn app:app --bind 0.0.0.0:5000
```

---

## 🚀 Deployment Configuration

The application is fully prepared for zero-downtime deployment on cloud hosting platforms (e.g. Render, Railway, Heroku, or Localtunnel/Ngrok):

- **WSGI Entry Point:** `gunicorn app:app` configured in `Procfile`.
- **Environment Variables:** Reads `PORT`, `HOST`, `DATABASE_URL`, `SECRET_KEY`, and `CORS_ORIGINS` from environment.
- **CORS Config:** Dynamically configured for secure cross-origin requests.
- **Database:** Auto-initializes tables and pre-seeds initial demo data on server startup.

---

## 🏆 Hackathon Git Commit History

- `f2a5c8a` **docs: add active live public URL to README.md** *(M4)*
- `fb11ce7` **fix: remove emoji from app.py print for Windows compatibility** *(M4)*
- `220020a` **build: add Procfile and gunicorn dependency for cloud deployment** *(M4)*
- `8319bbd` **fix: validate end-to-end travel planning flow** *(M3)*
- `3789c75` **fix: finalize primary user experience** *(M2)*
- `263d5c8` **fix: stabilize GlobeTrotter system integration** *(M1)*

---
*Built with ❤️ for Odoo x LDCE Hackathon 2026.*
