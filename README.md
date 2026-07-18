# NexDoc - NEET seat explorer

NexDoc is a premium, zero-backend, high-performance database explorer and analytics dashboard for Indian medical seat matrices (MBBS, MD, MS, DM, MCh, DrNB) across all levels: Undergraduate (UG), Postgraduate (PG), and Super Specialty (SS). 

Designed to be hosted entirely on GitHub Pages, the application processes structured JSON datasets on-demand directly inside the client's browser, delivering database-like search speeds (<10ms) and beautiful interactive visualizations.

---

## 🚀 Key Features

* **Instant Search & Multi-keyword Filter**: Regex-based search with debounced state inputs (150ms) to prevent mobile typing lag.
* **Institutional Cross-Level (UG ➔ PG ➔ SS) Mapping**: Intelligent mapping of colleges across different courses via institutional registry codes and tokenized word-set intersections. 
* **Dynamic Analytics Panel**: Visualizes seat distribution by specialty and ownership type using high-performance Chart.js graphs.
* **Sankey Flow Diagrams**: Interactive D3-powered diagrams showing how seats flow from counseling quotas down to colleges and specialties.
* **Side-by-Side Comparison Matrix**: Fullscreen-capable comparison grid comparing up to 3 colleges simultaneously, showcasing Ownership, Location, Quotas, and Specialties.
* **Responsive Dark/Glassmorphic Design**: Customized CSS variable tokens, Outfit/Inter typography, and CSS-animated micro-interactions tailored for both mobile and desktop screens.

---

## 🛠️ Technology Stack

* **Core UI**: HTML5 & ES6 Javascript Modules (modular components under `public/components/`)
* **Styling**: Vanilla CSS3 Custom Variables (dark mode theme, custom animations, glassmorphism)
* **Data Visualizations**: Chart.js (Bar/Pie/Doughnut charts) & D3.js (Sankey Flow layout)
* **Icons**: Lucide Icons
* **Data Processing Ingestion**: Python (pdfplumber, pandas) for build-time official seat matrix extraction and cross-level code mapping

---

## 📂 Project Structure

```
├── architecture.md           # Detailed system architecture document
├── package.json              # Client dependencies and dev scripts
├── .gitignore                # Git ignore patterns
├── scripts/                  # Data ingestion & parsing scripts
│   └── update_ug_data.py     # Cross-level seat mapping automation
├── public/                   # Main web assets (deployed folder)
│   ├── index.html            # Core HTML entrypoint
│   ├── app.js                # Core App state management & routing
│   ├── app.css               # Main design system stylesheet
│   ├── components/           # Modular ES6 UI components
│   │   ├── SearchFilters.js
│   │   ├── AnalyticsPanel.js
│   │   ├── SankeyChart.js
│   │   └── ComparisonMatrix.js
│   └── data/                 # Segmented JSON datasets
│       ├── colleges_details.json
│       ├── ug/
│       ├── pg/
│       └── ss/
```

---

## 💻 Local Development

1. **Clone the Repository**:
   ```bash
   git clone <repo-url>
   cd nexdoc
   ```

2. **Install Node dependencies**:
   ```bash
   npm install
   ```

3. **Start the local server**:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` (or the port specified by the dev server) in your browser.

---

## 🚀 GitHub Pages Deployment

NexDoc uses relative URLs and is pre-configured with a GitHub Actions workflow to deploy the `public/` directory directly to GitHub Pages (`username.github.io/nexdoc`).

To deploy:
1. Push your repository to GitHub.
2. Go to your repository settings: **Settings ➔ Pages**.
3. Under **Build and deployment ➔ Source**, select **GitHub Actions**.
4. The workflow will automatically run, build, and host the app at your repository's pages URL.

---

## 📄 License

This database and application are licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**. You are free to share and adapt the material as long as appropriate credit is given.

