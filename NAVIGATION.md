# NexDoc Website Navigation & Structure Guide

This document maps the user interface structure, navigation controls, and panel tabs of the NexDoc web application.

---

## 1. Header Navigation & Global Controls

Top persistent header bar containing core application controls:

- **NexDoc Branding & Logo**:
  - Displays transparent logo SVG, brand title, and level tagline (`NEET Seat Matrix Explorer`).
- **PWA Installation Control (`#pwaInstallBtn`)**:
  - Sleek downward-arrow icon button.
  - Automatically visible when PWA installation is supported by the browser. Directly triggers native browser installation prompt without intermediate popups.
- **Theme Toggle (`#themeToggleBtn`)**:
  - Toggles between base **Dark Glass Theme** and **Sky-Tinted Light Theme**.
  - Synchronously resolves theme in `<head>` before rendering to eliminate opposite-theme flash (FOUC).
- **Academic Level Selector (`.level-tabs`)**:
  - **UG (MBBS)**: Undergraduate medical seat matrix and MCC cutoff explorer.
  - **PG (MD/MS)**: Postgraduate medical seat matrix explorer.
  - **SS (DM/MCh)**: Super Specialty medical seat matrix explorer.
- **State Selector Dropdown (`#stateSelector`)**:
  - Filters all active views by specific Indian State / Union Territory or `All States`.

---

## 2. Global Disclaimer Banner

Located directly beneath the header section:
> **Note & Disclaimer:** This portal does not contain Institutes of National Importance (INI) data (such as AIIMS, JIPMER, PGIMER, NIMHANS, etc.).

---

## 3. Main Workspace Panel Tabs (Exact Runtime Order)

The application workspace contains **5 main panel tabs**, arranged in the following exact order:

### Tab 1: Table Explorer (`data-tab="table"`)
- **Purpose**: Primary interactive seat matrix data table.
- **Features**:
  - Unpaginated, searchable list of medical colleges and seat counts.
  - Management classification badges (`Govt.`, `Private`, `Deemed`).
  - Interactive *Compare* button on each row to add colleges to the comparison drawer.
  - Detail modal link to inspect complete college profiles.

### Tab 2: MCC UG Cutoffs & Predictor (`data-tab="cutoffs"`)
- **Purpose**: Comprehensive MCC NEET UG Counselling Allotment Explorer and NEET Rank Predictor.
- **Features**:
  - **Top Control Card**: Contains rank input field (`#cutoffTopRankInput`), rank submit button (`#cutoffTopRankSubmitBtn`), search input (`#cutoffTopSearchInput`), *Include Non-AIQ* toggle (`#topShowNonAiqCb`), *Collapse All* button (`#collapseAllRowsBtn`), and CSV export.
  - **Unpaginated College Table**: Renders all 823 colleges (360 Matched, 142 New, 321 Non AIQ).
  - **Chevron Arrow Column**: Dedicated expand/collapse arrow column to toggle round-by-round opening/closing ranks.
  - **Sidebar Checklist Filters**: Separate floating sidebar for quota and category selection.

### Tab 3: Seat Analytics (`data-tab="analytics"`)
- **Purpose**: Graphical analytical overview of seat distribution.
- **Features**:
  - State-wise seat count bar charts.
  - Management type breakdown pie charts.
  - Course-wise allocation distributions.

### Tab 4: Sankey Flowchart (`data-tab="sankey"`)
- **Purpose**: D3.js interactive flow visualization.
- **Features**:
  - Multi-stage diagram visualizing the flow of seats from **State $\rightarrow$ College Type $\rightarrow$ Quota $\rightarrow$ Course**.
  - Interactive node highlighting and flow tooltips.

### Tab 5: Compare Colleges (`data-tab="compare"`)
- **Purpose**: Side-by-side comparison matrix for selected colleges.
- **Features**:
  - Displays up to 4 selected colleges in a comparative grid.
  - Compares total seats, management types, courses offered, and MCC cutoff history.
  - Contains dynamic count badge (`#compareCount`) showing active selection count.

---

## 4. Responsive & Mobile Fullscreen Controls

- **Floating Filter Drawer Button (`#openSidebarBtn`)**:
  - Accessible on mobile screens to open the filter drawer.
- **Automatic Mobile Table Fullscreen**:
  - Triggers automatically when the midpoint of `.cutoff-controls-card` scrolls past the top of the mobile viewport.
  - Includes sticky exit control (`#exitFullscreenBtn`) to dismiss fullscreen mode.
