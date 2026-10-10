# 🌌 Campus Lost & Found — Antigravity Web Application

A full-stack, college-ready web application designed for university campuses to help students, faculty, and security staff report lost items, register found items, and safely coordinate recoveries.

Crafted with the **Antigravity Design System** — featuring high-tech glassmorphism, cosmic dark gradients, cyan & purple glowing accents, and reactive micro-interactions.

---

## 🚀 Key Feature Highlights

### 1. 🤖 Smart Item Matching (AI Similarity Engine)
* Automatically cross-analyzes `LOST` and `FOUND` reports across multiple dimensions:
  * **Category Concordance:** Exact and semantic taxonomy matching.
  * **Campus Zone Proximity:** Correlates reports in identical or adjacent campus buildings.
  * **Temporal Proximity:** Awards confidence score for reports occurring within close calendar proximity.
  * **Keyword & Title Token Overlap:** Jaccard token overlap on titles and descriptions.
* Displays side-by-side **Smart Match Comparison Radar** (`/matches`) with match confidence percentage badges (e.g., 94% Match).
* Triggers automatic in-app alerts when a matching counterpart is filed.

### 2. 🛡️ Confidential Ownership Verification Shield
* **Security standard:** Prevents fraudulent claims by never disclosing all identifying features publicly.
* When reporting an item, finders input **Confidential Identifying Details** (e.g. lockscreen wallpaper, serial number, internal sticker, scratch pattern, wallet contents).
* Public visitors see a frosted **Security Vault Shield** stating the feature is encrypted.
* Claimants must answer an **Ownership Questionnaire** describing those secret details.
* The finder or campus security administrator reviews claimant answers side-by-side with the private record before approving handover.

### 3. 💬 In-App Handover Coordination Chat
* Secure direct communication between the finder and claimant.
* Eliminates the need to post personal phone numbers or private social handles publicly.
* Coordinates exact handover timings (e.g., *"Meet at Central Library Desk Room 102 at 3:30 PM"*).

### 4. 🗺️ Google Maps JavaScript API Integration
* **Live Campus Spatial Map (`/map`):**
  * Powered by the **Google Maps JavaScript API** with an **Antigravity Dark Cosmic Theme** (styled with midnight black canvas, neon cyan roads, deep cobalt waters, and glowing POI highlights).
  * **Interactive Building Nodes & Custom Glowing Pins:**
    * 🔴 Crimson Pin: Active Lost Items
    * 🟢 Emerald Pin: Active Found Belongings
    * 🟣 Purple Pin: Campus Buildings with item counts
  * **Interactive InfoWindows:** Click any pin on Google Maps to reveal the item photo thumbnail, title, category, location, and one-click access to the item detail and claim page.
  * **Jump-to Navigation:** Instant smooth panning & zoom (`map.panTo()` & `map.setZoom(17)`) when selecting campus facilities.
  * **Dual Mode Switcher:** Toggle between **Google Maps Satellite/Street View** and the **Campus Blueprint Schematic**.
* **Interactive Google Maps Pin Selector (`/report`):**
  * Allows students to click or drag a marker directly on Google Maps to pinpoint the exact discovery or loss coordinates (`latitude`, `longitude`).
* **Item Details Map Widget (`/item/<id>`):**
  * Displays precise geospatial coordinates and a direct *"Open in Google Maps"* link for route guidance.
* **API Key Flexibility:**
  * Configure via `GOOGLE_MAPS_API_KEY` environment variable in `config.py`, or use the in-app **"🔑 Maps API Key"** button to input a key directly without restarting the server. Graceful fallback mode ensures the page never breaks.

### 5. ⚠️ Real-Time Duplicate Detection
* Live AJAX duplicate scanner on the reporting form (`/report`).
* Warns users if a similar report has already been logged by another student to keep listings clean.

### 6. 👑 Campus Security & Admin Control Center (`/admin`)
* Moderation dashboard to archive, restore, or delete spam/inappropriate reports.
* Dispute resolution and claim auditing.
* Campus user management directory with student IDs/USNs.
* Recovery analytics (total reports, active open items, recovery success rate %).
* Student reviews and recovery experience feedback log.

---

## 🛠️ Technology Stack

| Component | Technology | Rationale |
|---|---|---|
| **Frontend** | HTML5, Antigravity CSS3, Vanilla JavaScript | Zero-dependency, ultra-fast rendering, glowing glassmorphism |
| **Backend** | Python Flask (3.1+) | Clean MVC structure, flexible routing & sessions |
| **Database** | SQLite3 (Row Factory) | Zero-setup, portable, ACID compliant relational database |
| **Authentication**| Werkzeug Password Hashing | Secure SHA-256 salted password encryption, student/admin roles |
| **Styling** | `antigravity.css` | Futuristic Google Antigravity dark cosmic UI & micro-interactions |

---

## 📂 Project Directory Structure

```
campus_lost_and_found/
├── app.py                 # Core Flask application & API routes
├── config.py              # Application settings, categories & campus locations
├── database.py            # SQLite schema initialization & database helpers
├── smart_matcher.py       # Multi-dimensional matching & duplicate detection engine
├── seed_data.py           # Pre-seeds realistic campus demo items, claims & users
├── test_app.py            # Automated test suite (all endpoints)
├── run.py                 # Server startup launcher
├── static/
│   ├── css/
│   │   └── antigravity.css  # Antigravity Design System stylesheet
│   ├── js/
│   │   ├── app.js           # Client-side reactivity, duplicate checker, bookmarks
│   │   └── map.js           # Interactive campus map interactions
│   └── uploads/             # Item photo uploads & SVG illustrations
└── templates/
    ├── base.html            # Antigravity HUD navbar, demo account picker, footer
    ├── index.html           # Home dashboard with live KPIs & recent reports
    ├── browse.html          # Advanced keyword & category search directory
    ├── item_detail.html     # Detail view with private verification shield & claim modal
    ├── report.html          # Filing form with duplicate alert & photo upload
    ├── claims.html          # Verification review center with side-by-side comparison
    ├── matches.html         # AI Smart Matching radar screen
    ├── map.html             # Interactive vector campus hotspot map
    ├── messages.html        # In-app handover coordination chat thread
    ├── notifications.html   # System & match notifications feed
    ├── admin.html           # Administration command center & user directory
    ├── profile.html         # User profile, my reports & bookmarks
    ├── login.html           # Authentication sign-in screen
    └── register.html        # Verified campus registration screen
```

---

## ⚡ How to Run the Application

### 1. Open Terminal in the project directory:
```powershell
cd C:\Users\hp\.gemini\antigravity\scratch\campus_lost_and_found
```

### 2. Launch the Application:
```powershell
python run.py
```

### 3. Open in Browser:
Navigate to: **`http://127.0.0.1:5000`**

---

## 🔑 Pre-Seeded Demo Accounts for Project Demonstration

The top navigation bar contains a **"⚡ Demo Accounts"** button that lets you instantly switch between demo roles with one click! Or you can sign in manually using:

| Name | Role | Email / Login ID | Password | USN / ID |
|---|---|---|---|---|
| **Campus Security Desk** | Administrator | `admin@campus.edu` | `Admin@123` | `ADMIN-001` |
| **Alex Chen** | Student (CS) | `alex.chen@campus.edu` | `Student@123` | `1MS21CS042` |
| **Priya Sharma** | Student (ECE) | `priya.sharma@campus.edu` | `Student@123` | `1MS21EC088` |
| **Marcus Vance** | Student (Mech) | `marcus.vance@campus.edu` | `Student@123` | `1MS22ME015` |
| **Sara Connor** | Student (IS) | `sara.connor@campus.edu` | `Student@123` | `1MS22IS073` |

> *Note: To register a new Admin account via the registration form, enter the Campus Admin Security Passcode: `CAMPUS-ADMIN-2026`.*
