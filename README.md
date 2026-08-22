# GlobeTrotter 🌍

> Smart Travel Planning — Odoo x LDCE Hackathon 2026

---

## 👥 Team

| Member | Role |
|--------|------|
| M1 | Backend Developer |
| M2 | Frontend Developer |
| M3 | Integration & Bug Fixer |
| M4 | DevOps & Demo Lead |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python Flask |
| Database | SQLite (`globetrotter.db`) |
| Frontend | HTML + CSS + Vanilla JavaScript |
| Port | 5000 |

---

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. (Optional) Seed sample data
```bash
python seed_data.py
```

### 3. Start the server
```bash
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

---

## 🔌 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login |
| GET | `/api/trips` | Get all trips for user |
| POST | `/api/trips` | Create a new trip |
| GET | `/api/trips/<id>` | Get trip details |
| PUT | `/api/trips/<id>` | Update trip |
| DELETE | `/api/trips/<id>` | Delete trip |

---

## 📐 API Response Format

```json
{ "success": true, "data": [...], "message": "..." }
```

---

## 🗂️ Folder Structure

```
globe trotter/
├── app.py              ← Flask entry point
├── database.py         ← SQLite connection & schema
├── requirements.txt
├── .gitignore
├── context.md          ← Shared team contract
├── seed_data.py        ← Sample data (M4)
├── routes/
│   ├── __init__.py
│   ├── auth.py         ← Login / Register
│   └── trips.py        ← Trip CRUD
└── static/
    ├── index.html      ← Login/Signup page
    ├── dashboard.html  ← Trip dashboard
    ├── trip.html       ← Create/View trip
    ├── style.css
    └── app.js
```
