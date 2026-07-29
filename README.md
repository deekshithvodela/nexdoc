# NexDoc | NEET Medical Seat Explorer & MCC UG Cutoff Predictor

**NexDoc** is a high-performance, client-side, zero-backend interactive web application and data analytics dashboard for Indian medical seat matrices (MBBS, MD, MS, DM, MCh) across Undergraduate (UG), Postgraduate (PG), and Super Specialty (SS) levels.

It features a deterministic, unpaginated MCC UG Cutoff Explorer and NEET Rank Predictor powered by validated allotment data from **MCC NEET UG Counselling Rounds 1–3**.

---

## Key Features

- **Master Medical College Dataset**:
  - Contains **823 unique UG medical colleges** mapped across India.
  - **360 Matched Colleges**: Participating in MCC AIQ counselling with historical cutoff records.
  - **142 New Colleges**: Participating in MCC counselling without historical allotment data (marked `New`).
  - **321 Non-AIQ Colleges**: State quota only institutions not participating in MCC AIQ (marked `Non AIQ`).

- **MCC UG Cutoff Explorer & NEET Rank Predictor**:
  - **Unpaginated Table**: Renders all 823 colleges on a single, continuous view without arbitrary page limits.
  - **Rank Predictor**: Calculates category-specific admission probabilities based on user-entered NEET All India Rank (AIR).
  - **Blur & Icon Submit**: Supports typing arbitrary rank lengths, submitting via icon button or on input `blur`.
  - **Checklist Filter Windows**: Filter by specific quotas (AIQ, Deemed, Central Universities, etc.) and categories (OPEN, OBC, SC, ST, EWS, PwD).
  - **Chevron Arrow Expansion**: Expand rows to inspect round-by-round opening and closing ranks without page refreshes.

- **Multi-Level Seat Matrix Explorer**:
  - Explore seat matrices across **UG (MBBS)**, **PG (MD/MS)**, and **SS (DM/MCh)** levels.
  - Filter by State, Management Type (Government, Private, Deemed), Quota, and Course.

- **Visual Seat Analytics & Sankey Flowchart**:
  - Interactive distribution charts powered by Chart.js.
  - D3.js Sankey diagrams visualizing seat flows from States $\rightarrow$ Management Types $\rightarrow$ Courses.

- **College Comparison Drawer**:
  - Select up to 4 medical colleges to compare side-by-side across seats, fees, courses, and cutoff metrics.

- **Progressive Web App (PWA) & Dark/Light Themes**:
  - Installable PWA with offline caching via Service Worker (`sw.js`).
  - Dual glassmorphic dark and sky-tinted light themes with zero-flash initial loading.
  - Geometry-based automatic mobile table fullscreen mode.

---

## Note & Disclaimer

> [!NOTE]
> **Data Scope Disclaimer:**
> This portal does not contain Institutes of National Importance (INI) data (such as AIIMS, JIPMER, PGIMER, NIMHANS, etc.).
> Admissions for INI institutions are conducted separately through INI-CET / INI counselling portals.

---

## Data Sources & Methodology

- **MCC UG Allotment Data**: Parsed from official **MCC NEET UG 2024 Counselling Allotment lists (Rounds 1, 2, and 3)**.
- **Master Seat Matrices**: Compiled from official Medical Counselling Committee (MCC) seat matrices and State Health Department publications.
- **Matching Methodology**: Conservative, deterministic college identity matching based on official state codes, college names, and locations. Fuzzy matching is strictly disabled to prevent false mappings.

---

## Local Development & Setup

NexDoc is built using pure vanilla JavaScript (ES modules), HTML5, and CSS3 with zero build dependencies.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/deekshithvodela/nexdoc.git
   cd nexdoc
   ```

2. **Serve locally**:
   Launch any static HTTP server from the `public` directory:
   ```bash
   python3 -m http.server 8080 --directory public
   ```

3. **Open in browser**:
   Navigate to `http://localhost:8080/index.html`.

---

## License

Open Access / Educational Use. Data sourced from public counselling records.
