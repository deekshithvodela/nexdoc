# 📘 NexDoc Platform User Manual

Welcome to the official **NexDoc Platform User Manual**. This document provides comprehensive guidance for navigating the platform, analyzing NEET All India Quota (AIQ) counseling cutoffs, utilizing rank prediction tools, and managing institutional registry data.

---

## 📑 Table of Contents

1. [📖 Introduction & Platform Mission](#1-introduction--platform-mission)
2. [🖥️ Main Application Interface](#2-main-application-interface)
3. [📊 Cutoff Explorer & Rank Predictor](#3-cutoff-explorer--rank-predictor)
4. [🔍 State & Quota Filter System](#4-state--quota-filter-system)
5. [🏛️ Institution Master Directory & Cards](#5-institution-master-directory--cards)
6. [🌙 Dark / Light Theme Customization](#6-dark--light-theme-customization)
7. [📱 Mobile & Fullscreen Experience](#7-mobile--fullscreen-experience)
8. [⚙️ Admin & College Registry Management](#8-admin--college-registry-management)
9. [❓ Frequently Asked Questions (FAQ)](#9-frequently-asked-questions-faq)

---

## 1. 📖 Introduction & Platform Mission

**NexDoc** is an advanced medical counseling intelligence platform engineered to provide medical aspirants (Undergraduate **MBBS** and Postgraduate **MD / MS / DNB / DM / M.Ch**) with accurate, zero-loss, and transparent All India Quota (AIQ) allotment insights.

### Key Highlights
- **100% Record Parity**: Ingests full MCC allotment datasets without artificial data truncation.
- **Precision Normalization**: Maps complex raw counselling strings across 531 variations to standardized master medical colleges.
- **Real-Time Chance Predictor**: Evaluates student NEET All India Ranks against multi-round closing ranks to calculate statistical allotment probability.

---

## 2. 🖥️ Main Application Interface

The NexDoc web application features a responsive workspace designed for rapid navigation:

- **Header Bar**:
  - **PWA Installer**: Download NexDoc for offline mobile/desktop usage.
  - **Theme Toggle**: Instantly switch between **Dark Mode** and **Sky-Tinted Light Mode**.
  - **State Filter Dropdown**: Quickly isolate medical institutions by state.
- **Main Navigation Tabs**:
  - **Cutoff Explorer**: Interactive multi-round allotment tables.
  - **Analytics Panel**: Visual breakdowns of rank trends and seat distributions.
  - **College Directory**: Comprehensive profiles of all 926 recognized medical colleges.

---

## 3. 📊 Cutoff Explorer & Rank Predictor

The **Cutoff Explorer** is the primary engine for analyzing historical NEET counseling trends.

### How to Predict Your Allotment Chance

1. **Enter Your Rank**: Type your NEET All India Rank (AIR) into the `#cutoffTopRankInput` box at the top of the Cutoff Explorer card.
2. **Submit / Search**: Click the submit button or press `Enter`.
3. **Probability Badges**: NexDoc dynamically evaluates historical closing ranks across Round 1, Round 2, and Round 3:
   - 🟢 **High Chance**: Your rank is significantly safer than the historical closing rank.
   - 🟡 **Medium Chance**: Your rank is within 5% of the closing rank boundary.
   - 🔴 **Low Chance**: Your rank exceeds historical closing ranks.

### Expandable Multi-Round Breakdown
- Click the chevron arrow (`▶`) next to any medical college row to expand detailed round-by-round allotments:
  - **Round 1 Opening / Closing Ranks**
  - **Round 2 Upgradation Ranks**
  - **Round 3 Mop-Up Ranks**
  - **Confirmed Seats Allotted** (excluding candidates who opted for upgradation out).

---

## 4. 🔍 State & Quota Filter System

Refine allotment data instantly using multi-dimensional filters:

- **State Filter**: Filter colleges by state (e.g. Maharashtra, Tamil Nadu, Delhi, Karnataka, Uttar Pradesh).
- **Quota Types**:
  - `AIQ`: All India Quota
  - `MNG`: Management / Deemed Quota
  - `NRI`: Non-Resident Indian Quota
  - `MM`: Muslim Minority Quota / `JM`: Jain Minority Quota
- **Live Keyword Search**: Type any college name, city, or shorthand (e.g., `"AIIMS"`, `"Sassoon"`, `"MMC Chennai"`) into the search bar.

---

## 5. 🏛️ Institution Master Directory & Cards

Access detailed institutional profiles for all **926 master medical institutions**:

- **College Code**: Standardized `STATE/SEQ/TYPE/TIER` classification (e.g., `MH/001/G/1` for BJ Medical College, Pune).
- **Institutional Metadata**: State, City, Management Sector (Government vs Deemed/Private), Year of Establishment, University Affiliation, Dean/Principal Contacts.
- **Historical Allotment Status**:
  - `Participating AIQ`: Colleges active in MCC central counseling with mapped cutoff data.
  - `New`: Newly established colleges added to latest counseling cycles.
  - `State Quota`: Institutions operating strictly under state authority counseling.

---

## 6. 🌙 Dark / Light Theme Customization

NexDoc provides tailored visual themes optimized for extended counseling research:

- **Dark Mode (Default)**: Deep obsidian theme with high-contrast glowing indicators and reduced eye fatigue.
- **Light Theme**: Bright, sky-tinted canvas (`#f0f7ff`) with crisp translucent cards.
- **Theme Persistence**: Theme preferences are automatically saved in browser `localStorage` and applied synchronously on page load.

---

## 7. 📱 Mobile & Fullscreen Experience

- **Sticky Mobile Controls**: Floating bottom bar provides 1-tap access to search, state selection, and filters.
- **Smart Mobile Fullscreen**: Swiping or scrolling down on mobile automatically expands the Cutoff Table to immersive full-screen mode to maximize data visibility.
- **Top Bar Dismiss**: Tap the floating `Exit Fullscreen` button at any time to return to normal browsing mode.

---

## 8. ⚙️ Admin & College Registry Management

Developers can access the local **Registry Admin Tool** at `http://localhost:8080/admin.html` during local development:

- **Strict Alphabetical Sorting**: All master medical institutions are presented in deterministic alphabetical order by institution name.
- **Automated GitHub Pages Exclusion**: The GitHub Actions deployment workflow (`.github/workflows/static.yml`) automatically strips `public/admin.html` right before uploading the web artifact, ensuring the Admin Panel is **never published to public GitHub Pages**.
- **Full 926 Master College Inspection**: Scroll, page, or search through 100% of all master medical colleges without artificial limits.
- **Pagination Controls**: Adjust items per page (**50**, **100**, **250**, or **All 926**).
- **Alias Management Modal**: Click `⚙️ Manage Aliases` on any college card to inspect raw variations, add newly discovered name aliases, or remove outdated variations.
- **Pipeline Exporter**: Export updated registry definitions to `colleges_details_export.json` for backend pipeline sync.

---

## 9. ❓ Frequently Asked Questions (FAQ)

#### Q1: Why do some raw allotment PDF names differ from the display name?
**A**: Counseling authorities frequently use shorthand names, typos, or full address blocks in allotment PDFs. NexDoc normalizes these raw strings to single authoritative canonical names using our 531 alias dictionary.

#### Q2: Are BDS (Dental) and B.Sc Nursing ranks included?
**A**: Backend datasets process 100% of raw data records without rank shifts. Non-MBBS courses like BDS and B.Sc Nursing are selectively filtered at the UI layer so medical aspirants view clean MBBS & post-grad data.

#### Q3: How frequently are cutoffs updated?
**A**: Cutoff data is updated immediately following the release of official MCC seat allotment results after every counseling round.
