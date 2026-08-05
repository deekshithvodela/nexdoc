# NexDoc | NEET Medical Seat Explorer & MCC UG Cutoff Predictor

**NexDoc** is a high-performance, client-side, zero-backend interactive web application and data analytics dashboard for Indian medical seat matrices (MBBS, MD, MS, DM, MCh) across Undergraduate (UG), Postgraduate (PG), and Super Specialty (SS) levels.

It features a deterministic, unpaginated MCC UG Cutoff Explorer and NEET Rank Predictor powered by validated allotment data from **MCC NEET UG Counselling Rounds 1–3**.

---

## Key Features

- **Master Medical College Dataset**:
  - Contains **926 unique medical colleges** mapped across India (`colleges_details.json`).
  - **UG (Undergraduate - MBBS)**: **845 colleges** (2,052 seat matrix rows).
  - **PG (Postgraduate - MD/MS/DNB)**: **644 colleges** (22,053 seat matrix rows).
  - **SS (Super Speciality - DM/MCh)**: **220 colleges** (1,360 seat matrix rows).
  - **Multi-Level Institutions**: **650 colleges** offering 2 or 3 course levels.
  - **366 AIQ Matched Colleges**: Participating in MCC AIQ counselling with historical cutoff records.

- **MCC UG Cutoff Explorer & NEET Rank Predictor**:
  - **Unpaginated Table**: Renders colleges on a single, continuous view without arbitrary page limits.
  - **Rank Predictor**: Calculates category-specific admission probabilities based on user-entered NEET All India Rank (AIR).
  - **Blur & Icon Submit**: Supports typing arbitrary rank lengths, submitting via icon button or on input `blur`.
  - **Checklist Filter Windows**: Filter by specific quotas (AIQ, Deemed, Central Universities, etc.) and categories (OPEN, OBC, SC, ST, EWS, PwD).
  - **Chevron Arrow Expansion**: Expand rows to inspect round-by-round opening and closing ranks without page refreshes.

- **Multi-Level Seat Matrix Explorer**:
  - Explore seat matrices across **UG (MBBS)**, **PG (MD/MS)**, and **SS (DM/MCh)** levels.
  - Filter by State, Management Type (Government, Private, Deemed), Quota, and Course.
  - Styled with bright neon green Total Seats visualization in Dark Mode (`#00f5a0` / `#00e676`) and high-contrast emerald green in Light Mode (`#047857`).

- **Visual Seat Analytics & Sankey Flowchart**:
  - Interactive distribution charts powered by Chart.js.
  - D3.js Sankey diagrams visualizing seat flows from States $\rightarrow$ Management Types $\rightarrow$ Courses.

- **College Comparison Drawer**:
  - Select medical colleges to compare side-by-side across seats, fees, courses, and cutoff metrics.

- **Local Admin Registry Panel & Build Exclusion**:
  - Dedicated administrative dashboard at `public/admin.html` for local data management (`npm start`).
  - Automatically stripped from production build artifacts via `.github/workflows/static.yml` to prevent public deployment of administrative tools.

- **Progressive Web App (PWA) & Dark/Light Themes**:
  - Installable PWA with offline caching via Service Worker (`sw.js`).
  - Dual glassmorphic dark and sky-tinted light themes with zero-flash initial loading.
  - Geometry-based automatic mobile table fullscreen mode.

- **SEO & Clean URL Routing**:
  - Client-side clean URL transformations (`replaceState`) stripping `.html` extensions.
  - `WebApplication` JSON-LD schema, OpenGraph, and Twitter Card rich media metadata.

- **Web Content Accessibility Guidelines (WCAG 2.1 Level AA/AAA) & Academic Scope**:
  - Built-in screen-reader skip link (`Skip to main content`).
  - Native HTML5 landmarks (`header`, `main`, `nav`, `aside`) and ARIA roles (`role="tablist"`, `role="tab"`, `aria-selected`, `aria-label`).
  - High-visibility focus rings (`:focus-visible`) and WCAG AAA color contrast ratios across dark/light modes.
  - **Core Medical Focus & Allied Course Exclusion**: Non-MBBS allotments (B.Sc Nursing, BDS, AYUSH) are excluded at the presentation layer, and institution badges present concise medical levels (`UG`, `PG`, `SS`).
  - Public accessibility and data disclosure statement available at `public/disclosure.html`.

---

## Data Sources & Methodology

- **MCC UG Allotment Data**: Parsed from official **MCC NEET UG Counselling Allotment lists (Rounds 1, 2, and 3)**.
- **Master Seat Matrices**: Compiled from official Medical Counselling Committee (MCC) seat matrices and State Health Department publications.
- **Matching Methodology**: Conservative, deterministic college identity matching based on official state codes, college names, and locations. 100% of raw variations in `alias-to-canonical.json` (531/531) are mapped to canonical master college names.

---

## Local Development & Setup

NexDoc is built using pure vanilla JavaScript (ES modules), HTML5, and CSS3 with zero build dependencies.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/deekshithvodela/nexdoc.git
   cd nexdoc
   ```

2. **Serve locally**:
   Launch the dev server:
   ```bash
   npm start
   ```
   *Or using Python:*
   ```bash
   python3 -m http.server 8080 --directory public
   ```

3. **Open in browser**:
   - Main App: `http://localhost:8080/index.html`
   - Local Admin Panel: `http://localhost:8080/admin.html`

---

## License

Open Access / Educational Use. Data sourced from public counselling records.
