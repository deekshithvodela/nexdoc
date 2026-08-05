# NexDoc Developer Architecture & Symbol Reference

This document maps the core CSS classes, element IDs, JavaScript state architecture, table components, and responsive geometry triggers for developers working on the NexDoc codebase.

---

## 📌 Core Data Scope & Display Filtering Principle

1. **Primary Website Scope**: `NexDoc` is strictly designed for **MBBS** (Undergraduate) and further medical study pathways (**MD / MS / DNB** Postgraduate & **DM / MCh** Super Speciality).
2. **Backend Data Processing**: All raw data files and counselling datasets (including non-MBBS courses like BDS, B.Sc Nursing, AYUSH) **MUST be fully ingested and processed** by backend python scripts. Truncating data at the processing level is strictly prohibited as it leads to index shifts, rank gaps, and dataset corruption.
3. **Frontend View Layer Filtering**: Non-MBBS courses (e.g. BDS, B.Sc Nursing) are **filtered out exclusively at the UI / presentation layer** (in `public/app.js` and frontend display components) so end users only view MBBS and medical post-grad pathways.

---

## 📌 Cutoff Mapping & Allotment Calculation Engine Logic

* **Anchor Points**:
  * In **Consolidated Allotment Lists**: `all_india_rank` is the anchor data point (1 candidate per row).
  * In **Cutoff Mapping Lists**: **Individual `college_name`** is the anchor data point (grouped by raw `college_name`, `quota`, `category`, `course`).
* **College Name Normalization Constraint**: Do **NOT** normalize college names during initial raw cutoff mapping generation. Preserve exact raw strings. Normalization is performed in downstream reference matching steps.
* **Opening & Closing Ranks Computation**:
  * Mapped **round-wise** (`r1`, `r2`, `r3`).
  * In each round, any candidate allotted/opted for upgradation in that college is tracked.
  * `rX_opening_rank` = **lowest (minimum) All India Rank** allotted in that round.
  * `rX_closing_rank` = **highest (maximum) All India Rank** allotted in that round.
* **Confirmed Seats Allotted Computation**:
  * Round ranks are tracked for all allotments/upgradations.
  * **BUT Seat Count is NOT counted if the candidate opted for upgradation out of that college!**
  * A candidate is counted towards `confirmed_seats_allotted` **ONLY IF** the college is their final allotted college and no further upgradation out was performed.

---

## 📌 Strict Alias Registration & Human-in-the-Loop Verification Rule

1. **Zero Auto-Commit on Ambiguity**: Newly discovered raw institute strings from allotment PDFs or datasets must **NEVER** be automatically committed to `reference/alias-to-canonical.json` if there is the slightest ambiguity, doubt, or fuzzy match threshold uncertainty.
2. **Human-in-the-Loop Confirmation**: When pipeline scripts encounter an unmatched raw institute string that does not have an exact or high-confidence Tier 1–3 alias match:
   * The pipeline must log/flag the unmapped raw string along with the proposed canonical candidate.
   * **The developer / AI must ask the USER for explicit confirmation** before adding any new alias to `reference/alias-to-canonical.json`.
3. **Alias Registry Integrity**: `reference/alias-to-canonical.json` serves as the project's single source of truth phonebook. Erroneous alias mappings corrupt downstream cutoff data, college cards, and analytics across the platform.

---

## 📌 Data Integrity Audit & Automated Categorization Pipeline Logic

To prevent dataset corruption, unmapped MBBS strings, or improper data leakage in future counseling updates, all incoming raw cutoff datasets must adhere to the **5-Category Automated Data Integrity Audit Standard** (`scripts/audit/audit_data_integrity.py`):

1. **5-Category Raw Name Classification Standard**:
   * **Category A (Matched MBBS Colleges)**: Raw strings cleanly mapped to master MBBS institutions in `reference/master-lists-of-colleges.json`.
   * **Category B (Matched BDS/Dental Colleges)**: Raw strings cleanly mapped to master Dental institutions.
   * **Category C (Unmatched BDS/Dental Colleges)**: Legitimate non-MBBS raw strings (Dental cutoffs). Must be preserved in backend cutoff datasets and filtered at frontend UI layer.
   * **Category D (Unmatched Nursing Colleges)**: Legitimate non-MBBS raw strings (B.Sc Nursing cutoffs). Must be preserved in backend cutoff datasets and filtered at frontend UI layer.
   * **Category E (Unmatched MBBS Colleges)**: Raw MBBS strings requiring manual alias registration or master list reconciliation. **Target: Must be 0 before release!**

2. **Standard Operating Procedure for Future Data Releases**:
   * **Step 1: Audit Run**: Execute `python3 scripts/audit/audit_data_integrity.py` on the raw input allotment dataset (`reference/raw_college_cutoffs_mapping.json`).
   * **Step 2: Category E Zeroing**: Inspect any remaining Category E (unmatched MBBS) raw strings:
     * *Existing Master College Match*: If the raw string is an abbreviated, misspelled, or address-heavy version of a master college, add an explicit entry to `MCC_MANUAL_OVERRIDES` in `scripts/pipeline/generate_mcc_aliases.py`.
     * *New College Registry Expansion*: If the raw string is a newly established GMC (e.g. 2023–2025 batch) missing from `reference/master-lists-of-colleges.json`, append it to `reference/master-lists-of-colleges.json` in standard `"College Name, City"` format.
   * **Step 3: Verification & Execution**: Re-run `./scripts/pipeline/run.sh` and re-run the audit script to confirm **Category E = 0**.

3. **Dynamic City Compatibility Enforcement**:
   * Pipeline resolution logic MUST use `extract_master_cities()` and `is_city_compatible()` to prevent cross-campus collapsing (e.g., preventing AIIMS Rishikesh from collapsing into AIIMS Jammu, or GMC Jammu into GMC Kathua).

---

## 📌 Comprehensive Developer Release Audit Checklist

Before tagging or pushing any production release, developers must execute and verify the following 5-point audit checklist:

1. **Strict Allied & Non-Medical Course Exclusion Rule**:
   - **Cutoff Explorer Filtering**: Ensure `CutoffExplorer.js` filters out all non-MBBS allotments (`B.Sc. Nursing`, `BDS`, `AYUSH`, `Paramedical`) at the UI presentation layer.
   - **Modal Allied Course Filtering**: Verify `showCollegeDetailsModal()` in `public/app.js` filters `aiq_cutoffs_raw` to omit non-MBBS entries.
   - **Offered Academic Level Badges**: Confirm the College Details modal renders concise academic level badges (`UG`, `PG`, `SS`) corresponding strictly to core medical programs (`MBBS`, `MD/MS/DNB`, `DM/MCh`), without parenthetical or allied course labels.

2. **Master Institution Type Classification (`INI`, `Government`, `Deemed`, `Private`) Audit**:
   - **INI Programmatic Mapping**: Verify `scripts/pipeline/6_build_normalized_cutoffs.py` matches colleges against `colleges_details.json` so all Institutes of National Importance (AIIMS institutes and JIPMER) are assigned `college_type = "INI"`.
   - **INI Badge Styling**: Confirm `CutoffExplorer.js` assigns `typeBadgeClass = 'badge-ini'` and `app.css` applies the purple `.badge-ini` styling.

3. **Quota Mapping & Foreign Country Quota Accuracy Audit**:
   - **Foreign Quota Verification**: Verify that `FOREIGN` quota cutoffs (e.g. AIIMS New Delhi foreign national seats) map exclusively to eligible master institutions and do not collapse onto regional campuses (e.g. AIIMS Jammu).
   - **Filter Active Check**: Ensure `CutoffExplorer.js` `isFilterActive` logic incorporates both top dropdown states and sidebar multi-select checkboxes (`selectedQuotas`, `selectedCategories`) so colleges with zero matching child rows are cleanly hidden when filters are active.

4. **WCAG 2.1 Level AA/AAA Accessibility Audit**:
   - **Keyboard Navigation & Skip Link**: Verify `:focus-visible` outline rings on interactive components and functional `#main-content` skip link.
   - **ARIA Landmarks & Screen Reader Support**: Confirm `role="tablist"`, `role="tab"`, `aria-selected`, `aria-label`, and `aria-hidden` attributes across all components.
   - **Compliance Statement**: Ensure `public/disclosure.html` includes updated WCAG accessibility and data scope statements.

5. **Automated Audit Suite Pass Rate**:
   - Run `python3 scripts/audit/audit_data_integrity.py` (confirm Category E = 0).
   - Run `python3 scripts/audit/check_ini_leakage.py`.
   - Run Playwright UI suite `node scripts/audit/ui/audit_full_suite.mjs`.

---


## 📌 Dataset Generation & Reference Boundary Rule

1. **Strict Source File Constrained Generation**: Pipeline generation scripts (such as `scripts/pipeline/6_build_normalized_cutoffs.py` creating `public/data/ug_colleges_aiq_mapping.json`) must **NEVER** inflate the output dataset by generating entries for every item in `reference/master-lists-of-colleges.json`.
2. **Input Source Data Boundary**: Generation of domain-specific datasets (e.g. UG cutoffs & college mapping) must be **strictly constrained** to the unique colleges present in the provided input source files.
3. **Master Institution Directory Exception**: `public/data/colleges_details.json` serves as the platform-wide master institution directory. As an explicit exception to the input-constrained boundary rule, `colleges_details.json` **MUST contain 100% of all institutions from `reference/master-lists-of-colleges.json`** (`926` master colleges).

---

## 📌 Master College Code Articulation (`STATE/SEQ/TYPE/TIER`)

1. **Standard Code Format**: `STATE/SEQ/TYPE/TIER` (e.g., `KA/001/P/3`, `PB/001/G/1`, `IN/001/I/1`).
   * **`STATE`**: 2-letter uppercase state abbreviation (`KA`, `MH`, `DL`, `PB`, `IN` for INI/AIIMS).
   * **`SEQ`**: 3-digit index per state & sector (`001`, `002`, `003`...).
   * **`TYPE`**: `G` = Government, `P` = Private / Deemed / Trust, `I` = INI (Institute of National Importance).
   * **`TIER`**: `1` = Government/INI UG (MBBS), `2` = Government PG, `3` = Private/Deemed UG (MBBS), `4` = Private/Deemed PG.
2. **Synchronized `college_id` Key**: Object keys and `college_id` properties are formatted as lowercase versions without slashes (e.g., `ug_ka001p3`, `ug_pb001g1`, `ug_in001i1`).
3. **Property Standard**: Every record must include: `college_id`, `college_code`, `college_name`, `college_type`, `management`, `state`, `city`, `pincode`, `address`, `website`, `email`, `telephone`, `fax`, `year_of_inc`, `university`, `status`, `status_text`, `dean_name`, `dean_designation`, `contacts`, and `aliases`.

---

## 1. Core Element IDs

### Header & System Controls
| Element ID | Purpose / Component | Location |
| :--- | :--- | :--- |
| `#pwaInstallBtn` | PWA installation trigger button | Header top right |
| `#themeToggleBtn` | Dark / Light mode toggle button | Header top right |
| `#stateSelector` | Dropdown for state filtering | Header controls |
| `#mainTabContainer` | Parent container for panel tab buttons | Main workspace |
| `#globalDisclaimer` | Global INI data scope banner | Sub-header |

### Cutoff Explorer & Predictor Controls
| Element ID | Purpose / Component | Location |
| :--- | :--- | :--- |
| `#cutoffTopRankInput` | NEET All India Rank numeric input | Cutoff top control card |
| `#cutoffTopRankSubmitBtn` | Compact icon-only rank submit button | Cutoff top control card |
| `#cutoffTopSearchInput` | Live search input for cutoff table | Cutoff top control card |
| `#collapseAllRowsBtn` | Button to collapse all expanded table rows | Cutoff toolbar |
| `#exportCutoffCsvBtn` | CSV export button for cutoff data | Cutoff toolbar |
| `#viewCutoffs` | Target container view for CutoffExplorer.js | Main panel |

### Mobile & Fullscreen Controls
| Element ID | Purpose / Component | Location |
| :--- | :--- | :--- |
| `#exitFullscreenBtn` | Sticky button to dismiss mobile fullscreen | Top floating banner |
| `#goToTopBtn` | Scroll to top button | Bottom right floating |
| `#openSidebarBtn` | Mobile filter drawer opener | Bottom mobile bar |

---

## 2. Important CSS Classes & Design Tokens

### Layout & Glassmorphism
- `.card-glass`: Base translucent container style with backdrop blur.
- `.app-workspace`: Main two-column grid layout (sidebar + main panel).
- `.panel-tab`: Tab button style; active tab marked with `.active`.

### Table & Column Classes
- `.table-row-group-header`: Parent summary row in unpaginated cutoff table.
- `.th-expand-col`: Dedicated 40px blank header column for expand/collapse chevron arrow.
- `.group-expand-btn`: Chevron button inside `.th-expand-col` (`data-toggle-college="..."`).
- `.col-predictor`: Table column cell displaying rank prediction chance badge.
- `.child-row-${collegeId}`: Round-by-round detailed cutoff rows under parent college.

### Status & Classification Badges
- `.badge-status-matched`: Cyan badge for MCC AIQ participating colleges with cutoffs.
- `.badge-status-new`: Blue/Purple badge for MCC colleges without historical cutoffs (`New`).
- `.badge-status-non-aiq`: Dark slate badge for State Quota only colleges (`Non AIQ`).
- `.badge-chance-high`: Green chance badge (High probability of allotment).
- `.badge-chance-medium`: Yellow/Orange chance badge (Moderate probability).
- `.badge-chance-low`: Red/Coral chance badge (Low probability).

---

## 3. Theme Architecture & State System

Theme state is governed by a **single attribute** on `document.documentElement`:
```html
<html data-theme="dark"> <!-- Default Base Theme -->
<html data-theme="light"> <!-- Sky-Tinted Light Theme -->
```

### Theme Ownership
1. **[app.css](file:///home/drover/Projects/nexdoc/public/app.css)**: Owns base `:root` design tokens, global layout structures, and all light mode custom token remappings under `[data-theme="light"]` selectors (canvas `#f0f7ff`, cards `rgba(255, 255, 255, 0.88)`). No separate light-mode.css file is used, ensuring clean maintenance of visual surfaces.

### Synchronous Head Resolution Script
Location: `<head>` of [index.html](file:///home/drover/Projects/nexdoc/public/index.html):
```javascript
(function() {
  try {
    var saved = localStorage.getItem('nexdoc_theme');
    var theme = saved || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    document.documentElement.setAttribute('data-theme', theme);
  } catch (e) {}
})();
```

---

## 4. Responsive Geometry & Mobile Fullscreen Logic

- **Mobile Viewport Threshold**: `window.innerWidth <= 768px`.
- **Fullscreen Scroll Trigger Logic** ([app.js](file:///home/drover/Projects/nexdoc/public/app.js)):
  ```javascript
  const card = document.querySelector('.cutoff-controls-card');
  if (card) {
    const rect = card.getBoundingClientRect();
    const cardMidpoint = rect.top + (rect.height / 2);
    // Auto-trigger fullscreen when midpoint reaches viewport top (<= 0)
    if (cardMidpoint <= 0) {
      toggleFullscreen(true, 'table');
    }
  }
  ```
- **Fullscreen State Class**: `document.body.classList.contains('table-fullscreen-active')`.

---

## 5. Alphabetical Dataset Sorting Standard

All public dataset JSON files in `public/data/` (`ug/all.json`, `pg/all.json`, `ss/all.json`, `ug_colleges_aiq_mapping.json`, state JSON files, and summary files) **MUST be sorted alphabetically** by institution name (`college_name`), state, course, and quota.

* **Automated Utility Script**: `python3 scripts/sort_data_files.py`
* Run this script whenever new raw allotment PDFs or counselling records are processed to ensure deterministic, alphabetical data presentation across the platform.

---

## 6. Clean URL Routing & SEO Meta Tag Standard

1. **Clean URL Routing**:
   * All static HTML pages (`index.html`, `admin.html`, `privacy.html`, `license.html`, `disclosure.html`) execute inline `<head>` scripts utilizing `window.history.replaceState` to strip `.html` extensions cleanly without triggers or reloads.
   * `sw.js` offline caching logic normalizes incoming request URLs to handle both slash-terminated (`/privacy`) and `.html`-extension requests seamlessly.
2. **SEO Metadata Standard**:
   * **Structured Data**: `index.html` embeds a `WebApplication` JSON-LD schema block targeting search engine rich snippets (`applicationCategory: EducationalApplication`).
   * **OpenGraph & Twitter Cards**: Configured with `og:site_name`, `og:image` (512x512 app icon), `og:url`, and `twitter:card` set to `summary_large_image`.
   * **Canonical Links**: Defined via `<link rel="canonical" href="...">`.
   * **Admin Panel Security**: `public/admin.html` includes `<meta name="robots" content="noindex, nofollow">` to prevent public search engine indexing.

---

## 7. Web Content Accessibility Guidelines (WCAG 2.1 Level AA/AAA) Standard

All frontend components, layout templates, and interactive views **MUST comply with WCAG 2.1 Level AA/AAA standards**:

1. **Keyboard Accessibility & Skip Link**:
   * Embedded `<a href="#main-content" class="skip-link">Skip to main content</a>` at the top of `<body>`.
   * All interactive elements (buttons, inputs, select dropdowns, filter cards) enforce high-visibility focus indicators via `:focus-visible` styling (`outline: 2px solid var(--accent-blue)`).
2. **HTML5 Landmarks & ARIA Roles**:
   * Structural elements use native HTML5 tags (`<header role="banner">`, `<main id="main-content" role="main">`, `<nav>`, `<aside>`).
   * Dynamic view tabs implement `role="tablist"` and `role="tab"`, with real-time state synchronization (`aria-selected="true/false"` and `aria-pressed="true/false"`).
3. **Screen Reader Optimization**:
   * Non-text decorative icons (`lucide` SVGs) include `aria-hidden="true"`.
   * All form inputs, rank fields, state selectors, and action buttons feature explicit `aria-label` definitions.
4. **Disclosure Statement**:
   * `public/disclosure.html` includes an explicit compliance section documenting platform-wide WCAG standards.
