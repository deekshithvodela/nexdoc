# NexDoc Developer Architecture & Symbol Reference

This document maps the core CSS classes, element IDs, JavaScript state architecture, table components, and responsive geometry triggers for developers working on the NexDoc codebase.

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
| `#topShowNonAiqCb` | Checkbox toggle to include Non-AIQ colleges | Cutoff toolbar |
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
