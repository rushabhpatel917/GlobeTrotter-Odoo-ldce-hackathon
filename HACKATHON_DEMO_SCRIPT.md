# 🎬 GlobeTrotter — 4-Minute Hackathon Pitch & Demo Video Script
**Target Duration:** Exactly 4 Minutes (240 Seconds)  
**Target Audience:** Odoo x LDCE Hackathon Judges & Technical Evaluators  
**Project:** GlobeTrotter — Smart AI Travel Planner & Odoo-Grade Expense Tracker  

---

## ⏰ Video Timeline & Scene Breakdown

| Timestamp | Section | Key Feature / Focus | Speaker / Persona |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:45** | **1. Problem & Hook** | Travel Fragmented Pain Points & High-Level Solution | **Member 1 (Presenter/Lead)** |
| **0:45 - 1:45** | **2. AI Engine & Routes** | Natural Prompt AI, Multi-City Sequencing (Ahmedabad ➔ Mumbai ➔ Goa) | **Member 2 (AI & Backend)** |
| **1:45 - 2:45** | **3. Expense & INR Budget** | Odoo-Grade Expense Breakdown, Category Gauges & INR (₹) Conversion | **Member 3 (Full-Stack Engineer)** |
| **2:45 - 3:30** | **4. Public Sharing & UX** | Read-Only Public Link Sharing, Desktop/Mobile Slide Polish & Photos | **Member 4 (UI/UX Engineer)** |
| **3:30 - 4:00** | **5. Tech Stack & Closing** | Flask + SQLite3 Architecture, Reliability & Closing Pitch | **All Members / Team Lead** |

---

## 📜 Full Word-for-Word Script

### 🎬 Scene 1: Problem Statement & Vision (0:00 – 0:45)
**[Visual On-Screen]:** Screen opens on the glowing **GlobeTrotter Landing Page** (`http://127.0.0.1:5000`), showing the dark glassmorphic UI, hero text *"Smart Travel Planning, Engineered for Perfection"*, and the prompt bar.

> **Speaker (Member 1):**  
> *"Hello judges! Planning a multi-city travel itinerary today is broken. Travelers switch between dozens of tabs—calculating daily routes, estimating hidden activity costs, and struggling to stay within budget.*  
>  
> *Meet **GlobeTrotter**—the intelligent, all-in-one travel planner engineered to transform raw travel ideas into complete, day-by-day chronologically slotted itineraries with real-time budget tracking in seconds."*

---

### 🎬 Scene 2: AI Prompt & Multi-City Route Engine (0:45 – 1:45)
**[Visual On-Screen]:** Cursor types into the AI Prompt bar: `"5 days in Goa with beaches and water sports under ₹20,000"`. Clicks **Generate with AI ➔**. Transitions smoothly to **Create Trip Page** (`create-trip.html`) displaying pre-filled multi-city destination rows: `Paris (France)` and `Rome (Italy)`.

> **Speaker (Member 2):**  
> *"With GlobeTrotter’s **AI Itinerary Generator**, users simply type natural language travel prompts like '5 days in Goa with beaches under 20,000 Rupees'.*  
>  
> *Our backend route sequencing engine dynamically structures multi-destination waypoints—such as **Ahmedabad to Mumbai to Goa**. It automatically calculates day-wise stop sequencing, assigns optimal morning, afternoon, and evening time slots, and pulls pre-vetted destination activities."*  

**[Visual On-Screen]:** Click into **Trip Details Page** (`trip-details.html`). Show the day-by-day timeline with high-res destination photos (Kashmir, Goa, Jaipur, Paris, Rome) and category badges (`Sightseeing`, `Adventure`, `Culture`).

---

### 🎬 Scene 3: Odoo-Grade Expense Tracker & INR Localization (1:45 – 2:45)
**[Visual On-Screen]:** Navigate to **Budget Dashboard** (`budget.html`). Highlight the hero KPI cards displaying **Total Trip Cost**, **Average Cost / Day**, and the **Interactive Category Cost Breakdown Bars** in **Indian Rupees (₹)**.

> **Speaker (Member 3):**  
> *"Financial clarity is at the core of GlobeTrotter. Our **Odoo-Grade Expense Tracker** breaks down every rupee spent across five core travel categories: **Transport, Stay, Activities, Meals, and Other**.*  
>  
> *Notice how all financial calculations are localized 100% in **Indian Rupee (₹)**. As users select activities or log custom expenses—like flights, hotel bookings, or local cab fares—our backend automatically computes real-time daily averages and category percentages with absolute precision."*

---

### 🎬 Scene 4: Instant Public Share & Master UI/UX (2:45 – 3:30)
**[Visual On-Screen]:** Click **"📋 Copy Share Link"** on the Public Itinerary page (`public-trip.html`). Open an Incognito window / new browser tab pasting the URL (`/static/public-trip.html?id=1`). Show the read-only shared view loading seamlessly.

> **Speaker (Member 4):**  
> *"Collaboration should be effortless. With **Instant Share & Export**, trip creators can publish a read-only public URL with a single click. Friends, family, or fellow travelers can view the entire itinerary and budget summary on any mobile or desktop device without needing an account.*  
>  
> *Our UI/UX features a glassmorphic dark theme built with modern CSS tokens, responsive destination cover cards, micro-animations, and instant city filtering tabs."*

---

### 🎬 Scene 5: Technical Stack & Closing Pitch (3:30 – 4:00)
**[Visual On-Screen]:** Return to the main GlobeTrotter dashboard showing the stats overview (26 Trips Planned, 20 Activities Available, 7 Cities to Explore). Show team credits on screen.

> **Speaker (Member 1 / Team Lead):**  
> *"Under the hood, GlobeTrotter is built with a lightweight, high-performance **Python Flask 3.x** backend, **SQLite3** database with automated schema migration, and modern responsive **Vanilla HTML5/CSS3**.  
>  
> *GlobeTrotter bridges AI intelligence with practical travel execution. Thank you for your time, and we welcome your questions!"*

---

## 🛠️ Pre-Recording Checklist for the Team

1. **Local Server:** Ensure Flask is running on `http://127.0.0.1:5000` (`python app.py`).
2. **Public Link:** Have local tunnel link ready if showing remote access (`https://wicked-months-worry.loca.lt`).
3. **Hard Refresh:** Press `Ctrl + Shift + R` before recording to load fresh CSS & images.
4. **Resolution:** Record in 1080p full screen with clean audio.
