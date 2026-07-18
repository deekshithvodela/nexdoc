// Core Application File for NexDoc
import { SearchFilters } from './components/SearchFilters.js';
import { AnalyticsPanel } from './components/AnalyticsPanel.js';
import { SankeyChart } from './components/SankeyChart.js';
import { ComparisonMatrix } from './components/ComparisonMatrix.js';

// Application State
const AppState = {
  activeLevel: 'ug',         // 'ug' | 'pg' | 'ss'
  selectedState: '',         // e.g. 'karnataka'
  statsMode: 'physical',     // 'physical' | 'counseling'
  
  // Data sets
  manifest: null,
  levelSummary: null,
  rawSeatsData: [],
  filteredSeatsData: [],
  comparisonList: [],        // Array of college_ids (Max 3)
  collegesDetails: {},       // Registry details for all colleges
  
  // Cache systems for instant loads
  seatsDataCache: {},        // Cache for loaded state datasets
  levelSummaryCache: {},     // Cache for loaded level summary stats
  fetchingCollegesDetails: null, // Promise reference for lazy loading registry
  
  // Filters State
  filters: {
    query: '',
    courseQuery: '',
    stateQuery: '',
    types: [],
    counselingRoute: 'all',
    quotas: [],
    courses: [],
    states: []
  },
  
  // Fullscreen state
  fullscreenActive: false,
  fullscreenDismissed: false,
  fullscreenType: 'table',
  rotatePromptTimeout: null
};

window.AppState = AppState;

// Performance Debounce Utility
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Initialize Application
async function init() {
  try {
    // 1. Fetch Manifest
    const manifestRes = await fetch('data/manifest.json');
    AppState.manifest = await manifestRes.json();
    
    // Fetch College details registry asynchronously in the background to prevent rendering block
    AppState.fetchingCollegesDetails = fetch('data/colleges_details.json')
      .then(res => res.json())
      .then(data => {
        AppState.collegesDetails = data;
        return data;
      })
      .catch(e => {
        console.warn("Failed to load college details in background:", e);
        return {};
      });
    
    // 2. Load default level summary statistics
    await loadLevelData(AppState.activeLevel);

    // 3. Attach Global Event Listeners
    setupGlobalListeners();
    
    // 4. Initialize Lucide icons
    if (window.lucide) {
      window.lucide.createIcons();
    }
  } catch (err) {
    console.error('Initialization failed:', err);
  }
}

// Load summary files and populate dropdowns for a chosen level
async function loadLevelData(level) {
  try {
    let summary;
    if (AppState.levelSummaryCache[level]) {
      summary = AppState.levelSummaryCache[level];
    } else {
      const summaryRes = await fetch(`data/${level}/summary.json`);
      summary = await summaryRes.json();
      AppState.levelSummaryCache[level] = summary;
    }
    AppState.levelSummary = summary;
    
    // Reset filters state for new level (empty arrays mean no filtering is active, i.e., all allowed)
    AppState.filters.query = '';
    AppState.filters.courseQuery = '';
    AppState.filters.stateQuery = '';
    AppState.filters.types = [];
    AppState.filters.counselingRoute = 'all';
    AppState.filters.quotas = [];
    AppState.filters.courses = [];
    AppState.filters.states = [];

    // Populate State Selector Dropdown
    const selector = document.getElementById('stateSelector');
    selector.innerHTML = '<option value="" disabled selected>Select Region / State</option>';
    
    // Add "All States" option
    const allOption = document.createElement('option');
    allOption.value = 'all';
    allOption.textContent = 'All States';
    selector.appendChild(allOption);

    summary.states.forEach(state => {
      const option = document.createElement('option');
      option.value = state.toLowerCase().replace(/ /g, '_');
      option.textContent = state;
      selector.appendChild(option);
    });

    // Preserve selected state if it exists in the new level, otherwise fallback to 'all'
    const prevSelectedState = AppState.selectedState;
    let stateExistsInNewLevel = false;
    if (prevSelectedState && prevSelectedState !== 'all') {
      stateExistsInNewLevel = summary.states.some(s => s.toLowerCase().replace(/ /g, '_') === prevSelectedState);
    }

    if (stateExistsInNewLevel) {
      selector.value = prevSelectedState;
      AppState.selectedState = prevSelectedState;
      await loadStateDetails(prevSelectedState);
    } else if (summary.states && summary.states.length > 0) {
      selector.value = 'all';
      AppState.selectedState = 'all';
      await loadStateDetails('all');
    } else {
      AppState.rawSeatsData = [];
      AppState.filteredSeatsData = [];
      renderDashboardStats();
      updateExplorerViews();
      SearchFilters.render('filterSidebar', AppState.activeLevel, AppState.levelSummary, AppState.filters, AppState.selectedState, onFilterChange);
    }
  } catch (err) {
    console.error(`Failed loading summary for ${level}:`, err);
  }
}

// Lazy load actual row-level details for a state
async function loadStateDetails(stateValue) {
  try {
    const level = AppState.activeLevel;
    const cacheKey = `${level}_${stateValue}`;
    
    if (AppState.seatsDataCache[cacheKey]) {
      AppState.rawSeatsData = AppState.seatsDataCache[cacheKey];
    } else {
      let res;
      if (stateValue === 'all') {
        res = await fetch(`data/${level}/all.json`);
      } else {
        res = await fetch(`data/${level}/states/${stateValue}.json`);
      }
      const data = await res.json();
      AppState.seatsDataCache[cacheKey] = data;
      AppState.rawSeatsData = data;
    }
    
    // Refresh filters with empty selection (meaning all are allowed)
    AppState.filters.types = [];
    AppState.filters.quotas = [];
    AppState.filters.courses = [];
    AppState.filters.states = [];
    AppState.filters.stateQuery = '';
    
    SearchFilters.render('filterSidebar', AppState.activeLevel, AppState.levelSummary, AppState.filters, AppState.selectedState, onFilterChange);
    
    // Apply initial filters & render
    applyFiltering();
  } catch (err) {
    console.error(`Failed loading state details for ${stateValue}:`, err);
  }
}

// Multi-faceted search and filter engine
function applyFiltering() {
  const f = AppState.filters;
  let data = AppState.rawSeatsData;

  // 0. State selection filter (only applied when browsing All States)
  if (AppState.selectedState === 'all' && f.states && f.states.length > 0) {
    data = data.filter(row => f.states.includes(row.state));
  }

  // 1. Sidebar Keyword text search (matches college name)
  if (f.query.trim()) {
    const keywords = f.query.toLowerCase().split(' ').filter(Boolean);
    data = data.filter(row => {
      const name = row.college_name.toLowerCase();
      return keywords.every(kw => name.includes(kw));
    });
  }

  // 2. Table quick search input (matches college name or course name)
  const quickQuery = document.getElementById('tableSearchInput').value.toLowerCase().trim();
  if (quickQuery) {
    data = data.filter(row => 
      row.college_name.toLowerCase().includes(quickQuery) || 
      row.course.toLowerCase().includes(quickQuery)
    );
  }

  // 3. College Type check
  if (f.types && f.types.length > 0) {
    data = data.filter(row => f.types.includes(row.college_type));
  }

  // 4. Counseling Route check
  if (f.counselingRoute !== 'all') {
    data = data.filter(row => row.counseling_route === f.counselingRoute);
  }

  // 5. Quotas check
  if (f.quotas && f.quotas.length > 0) {
    data = data.filter(row => f.quotas.includes(row.quota_type));
  }

  // 6. Courses / Branches check
  if (f.courses && f.courses.length > 0) {
    data = data.filter(row => f.courses.includes(row.course));
  }

  AppState.filteredSeatsData = data;
  
  // Re-calculate statistics and update display
  renderDashboardStats();
  updateExplorerViews();
}

// Handle filter modifications inside SearchFilters component
function onFilterChange(updatedFilters) {
  AppState.filters = updatedFilters;
  applyFiltering();
}

// Render counters in the main Dashboard Section
function renderDashboardStats() {
  const collegesSpan = document.getElementById('statColleges');
  const seatsSpan = document.getElementById('statSeats');
  const govtSpan = document.getElementById('statGovt');
  const privateSpan = document.getElementById('statPrivate');
  const govtLabel = document.getElementById('statGovtLabel');
  const privateLabel = document.getElementById('statPrivateLabel');

  if (AppState.rawSeatsData.length === 0) {
    collegesSpan.textContent = '-';
    seatsSpan.textContent = '-';
    govtSpan.textContent = '-';
    privateSpan.textContent = '-';
    return;
  }

  // Compute stats on filtered dataset
  const uniqueColleges = new Set(AppState.filteredSeatsData.map(r => r.college_id));
  const totalSeats = AppState.filteredSeatsData.reduce((sum, r) => sum + r.seats, 0);

  collegesSpan.textContent = uniqueColleges.size.toLocaleString();
  seatsSpan.textContent = totalSeats.toLocaleString();

  if (AppState.statsMode === 'physical') {
    // Mode: Geographical Capacity
    govtLabel.textContent = "Govt. Institution Seats";
    privateLabel.textContent = "Private & Deemed Seats";

    const govtSeats = AppState.filteredSeatsData
      .filter(r => r.college_type === 'Government')
      .reduce((sum, r) => sum + r.seats, 0);
    const pvtSeats = totalSeats - govtSeats;

    govtSpan.textContent = govtSeats.toLocaleString();
    privateSpan.textContent = pvtSeats.toLocaleString();
  } else {
    // Mode: Counseling Access splits
    govtLabel.textContent = "MCC (Central) Seats";
    privateLabel.textContent = "State Portal Seats";

    const mccSeats = AppState.filteredSeatsData
      .filter(r => r.counseling_route === 'MCC')
      .reduce((sum, r) => sum + r.seats, 0);
    const stateSeats = totalSeats - mccSeats;

    govtSpan.textContent = mccSeats.toLocaleString();
    privateSpan.textContent = stateSeats.toLocaleString();
  }
}

// Redraw active views depending on selected panel tab
function updateExplorerViews() {
  const activeTabBtn = document.querySelector('.panel-tab.active');
  if (!activeTabBtn) return;
  const activeTab = activeTabBtn.getAttribute('data-tab');

  // Update Showing count label
  const level = AppState.activeLevel;
  if (AppState.filteredSeatsData.length > 0) {
    const uniqueColleges = new Set(AppState.filteredSeatsData.map(r => r.college_id)).size;
    document.getElementById('showingCount').textContent = `Showing ${uniqueColleges} colleges · ${AppState.filteredSeatsData.length} records`;
  } else {
    document.getElementById('showingCount').textContent = `Showing 0 records`;
  }

  if (activeTab === 'table') {
    renderTableExplorer();
  } else if (activeTab === 'analytics') {
    AnalyticsPanel.render(AppState.filteredSeatsData);
  } else if (activeTab === 'sankey') {
    SankeyChart.render(AppState.filteredSeatsData);
  } else if (activeTab === 'compare') {
    renderComparisonMatrix();
  }
}

// Render dynamic rows inside the main table
function renderTableExplorer() {
  const tbody = document.getElementById('seatsTableBody');
  tbody.innerHTML = '';

  if (AppState.rawSeatsData.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="placeholder-text">Please select a region/state to load the database.</td></tr>`;
    return;
  }

  if (AppState.filteredSeatsData.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="placeholder-text">No seat records match the active filter criteria.</td></tr>`;
    return;
  }

  const level = AppState.activeLevel;

  // Group rows by college_id for collapsible view (all levels)
  renderGroupedTable(tbody);

  // Attach button events
  tbody.querySelectorAll('.btn-compare-action').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const colId = e.currentTarget.getAttribute('data-college-id');
      toggleCollegeCompare(colId);
    });
  });

  tbody.querySelectorAll('.college-details-link').forEach(link => {
    link.addEventListener('click', (e) => {
      const colId = e.currentTarget.getAttribute('data-college-id');
      showCollegeDetailsModal(colId);
    });
  });

  if (window.lucide) window.lucide.createIcons();
}

// Flat table rendering (UG mode — one row per entry)
function renderFlatTable(tbody) {
  AppState.filteredSeatsData.forEach(row => {
    const tr = document.createElement('tr');
    
    let badgeClass = 'badge-govt';
    if (row.college_type === 'Deemed') badgeClass = 'badge-deemed';
    if (row.college_type === 'Private') badgeClass = 'badge-private';

    const isInCompare = AppState.comparisonList.includes(row.college_id);
    const compareBtnClass = isInCompare ? 'btn-compare-action active' : 'btn-compare-action';
    const compareBtnText = isInCompare ? 'Comparing' : 'Compare';

    const seatsPrev = row.seats_prev !== undefined ? row.seats_prev : row.seats;
    const seatsInc = row.seats_inc !== undefined ? row.seats_inc : 0;

    tr.innerHTML = `
      <td><button class="college-details-link" data-college-id="${row.college_id}">${row.college_name}</button></td>
      <td><span class="badge ${badgeClass}">${row.college_type}</span></td>
      <td>${row.course}</td>
      <td><span style="font-weight: 600;">${row.counseling_route === 'MCC' ? 'MCC' : 'State'}</span></td>
      <td><small style="opacity: 0.85;">${row.quota_type}</small></td>
      <td class="text-right" style="opacity: 0.85; font-size: 0.95rem;">${seatsPrev}</td>
      <td class="text-right" style="color: ${seatsInc > 0 ? 'var(--accent-green)' : 'inherit'}; font-weight: ${seatsInc > 0 ? '600' : 'normal'}; font-size: 0.95rem;">
        ${seatsInc > 0 ? `+${seatsInc}` : '0'}
      </td>
      <td class="text-right"><strong style="font-size: 1rem; color: var(--accent-green);">${row.seats}</strong></td>
      <td class="text-center">
        <button class="${compareBtnClass}" data-college-id="${row.college_id}" title="${compareBtnText}">
          <i data-lucide="${isInCompare ? 'check' : 'plus'}"></i>
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// Grouped collapsible table rendering (PG/SS mode)
function renderGroupedTable(tbody) {
  // Group filtered data by college_id preserving order of first appearance
  const groupOrder = [];
  const groups = {};
  AppState.filteredSeatsData.forEach(row => {
    if (!groups[row.college_id]) {
      groups[row.college_id] = [];
      groupOrder.push(row.college_id);
    }
    groups[row.college_id].push(row);
  });

  groupOrder.forEach(collegeId => {
    const rows = groups[collegeId];
    const sample = rows[0];

    // Compute summary stats
    const uniqueCourses = new Set(rows.map(r => r.course));
    const uniqueQuotas = new Set(rows.map(r => r.quota_type));
    const totalSeats = rows.reduce((s, r) => s + r.seats, 0);
    const totalPrev = rows.reduce((s, r) => s + (r.seats_prev !== undefined ? r.seats_prev : r.seats), 0);
    const totalInc = rows.reduce((s, r) => s + (r.seats_inc !== undefined ? r.seats_inc : 0), 0);

    let badgeClass = 'badge-govt';
    if (sample.college_type === 'Deemed') badgeClass = 'badge-deemed';
    if (sample.college_type === 'Private') badgeClass = 'badge-private';

    const isInCompare = AppState.comparisonList.includes(collegeId);
    const compareBtnClass = isInCompare ? 'btn-compare-action active' : 'btn-compare-action';
    const compareBtnText = isInCompare ? 'Comparing' : 'Compare';

    // Level-aware chip and course column
    const isUG = AppState.activeLevel === 'ug';
    const chipText = isUG
      ? `${uniqueQuotas.size} quota${uniqueQuotas.size > 1 ? 's' : ''}`
      : `${uniqueCourses.size} course${uniqueCourses.size > 1 ? 's' : ''}`;
    const courseSummary = isUG
      ? `<span style="opacity: 0.7;">${sample.course}</span>`
      : `<span style="opacity: 0.7; font-style: italic;">${uniqueCourses.size} specialties</span>`;

    // Group header row (collapsed summary)
    const headerTr = document.createElement('tr');
    headerTr.classList.add('group-header-row');
    headerTr.setAttribute('data-group-id', collegeId);
    headerTr.innerHTML = `
      <td>
        <div class="group-toggle">
          <button class="group-expand-btn" data-group-id="${collegeId}" aria-label="Expand college">
            <i data-lucide="chevron-right" class="group-chevron"></i>
          </button>
          <button class="college-details-link" data-college-id="${collegeId}">${sample.college_name}</button>
        </div>
        <div class="group-summary-chips">
          <span class="group-chip">${chipText}</span>
        </div>
      </td>
      <td><span class="badge ${badgeClass}">${sample.college_type}</span></td>
      <td class="group-summary-courses">${courseSummary}</td>
      <td><span style="font-weight: 600;">${rows.some(r => r.counseling_route === 'MCC') ? 'MCC' : ''}${rows.some(r => r.counseling_route === 'MCC') && rows.some(r => r.counseling_route !== 'MCC') ? ' / ' : ''}${rows.some(r => r.counseling_route !== 'MCC') ? 'State' : ''}</span></td>
      <td>—</td>
      <td class="text-right" style="opacity: 0.85;">${totalPrev}</td>
      <td class="text-right" style="color: ${totalInc > 0 ? 'var(--accent-green)' : 'inherit'}; font-weight: ${totalInc > 0 ? '600' : 'normal'};">
        ${totalInc > 0 ? `+${totalInc}` : '0'}
      </td>
      <td class="text-right"><strong style="font-size: 1rem; color: var(--accent-green);">${totalSeats}</strong></td>
      <td class="text-center">
        <button class="${compareBtnClass}" data-college-id="${collegeId}" title="${compareBtnText}">
          <i data-lucide="${isInCompare ? 'check' : 'plus'}"></i>
        </button>
      </td>
    `;
    tbody.appendChild(headerTr);

    // Individual course rows (hidden by default)
    rows.forEach(row => {
      const childTr = document.createElement('tr');
      childTr.classList.add('group-child-row');
      childTr.setAttribute('data-parent-group', collegeId);
      childTr.style.display = 'none'; // Collapsed by default

      const seatsPrev = row.seats_prev !== undefined ? row.seats_prev : row.seats;
      const seatsInc = row.seats_inc !== undefined ? row.seats_inc : 0;

      childTr.innerHTML = `
        <td style="padding-left: 2.5rem;"><span style="opacity: 0.5;">└</span> ${row.college_name}</td>
        <td></td>
        <td>${row.course}</td>
        <td><span style="font-weight: 600;">${row.counseling_route === 'MCC' ? 'MCC' : 'State'}</span></td>
        <td><small style="opacity: 0.85;">${row.quota_type}</small></td>
        <td class="text-right" style="opacity: 0.85; font-size: 0.95rem;">${seatsPrev}</td>
        <td class="text-right" style="color: ${seatsInc > 0 ? 'var(--accent-green)' : 'inherit'}; font-weight: ${seatsInc > 0 ? '600' : 'normal'}; font-size: 0.95rem;">
          ${seatsInc > 0 ? `+${seatsInc}` : '0'}
        </td>
        <td class="text-right"><strong style="color: var(--accent-green);">${row.seats}</strong></td>
        <td></td>
      `;
      tbody.appendChild(childTr);
    });

    // Expand/collapse only via chevron button (prevents mistouch)
    const expandBtn = headerTr.querySelector('.group-expand-btn');
    expandBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isExpanded = headerTr.classList.toggle('expanded');
      const children = tbody.querySelectorAll(`tr[data-parent-group="${collegeId}"]`);
      children.forEach(child => {
        child.style.display = isExpanded ? '' : 'none';
      });
    });
  });
}

// Toggle college comparison drawer and status
function toggleCollegeCompare(collegeId) {
  const index = AppState.comparisonList.indexOf(collegeId);
  if (index > -1) {
    AppState.comparisonList.splice(index, 1);
  } else {
    if (AppState.comparisonList.length >= 3) {
      alert("You can select a maximum of 3 colleges to compare side-by-side.");
      return;
    }
    AppState.comparisonList.push(collegeId);
  }

  // Update table Compare indicators
  updateCompareDrawer();
  
  // High performance: update compare button states in table directly instead of full re-rendering
  const buttons = document.querySelectorAll(`.btn-compare-action[data-college-id="${collegeId}"]`);
  const isInCompare = AppState.comparisonList.includes(collegeId);
  buttons.forEach(btn => {
    if (isInCompare) {
      btn.classList.add('active');
      btn.title = 'Comparing';
      const icon = btn.querySelector('i');
      if (icon) {
        icon.setAttribute('data-lucide', 'check');
      }
    } else {
      btn.classList.remove('active');
      btn.title = 'Compare';
      const icon = btn.querySelector('i');
      if (icon) {
        icon.setAttribute('data-lucide', 'plus');
      }
    }
  });
  if (window.lucide) window.lucide.createIcons();

  // Re-render comparison matrix if user is currently looking at the compare tab
  const activeTabBtn = document.querySelector('.panel-tab.active');
  const activeTab = activeTabBtn ? activeTabBtn.getAttribute('data-tab') : 'table';
  if (activeTab === 'compare') {
    renderComparisonMatrix();
  }
}

// Update sticky footer compare drawer UI
function updateCompareDrawer() {
  const drawer = document.getElementById('compareDrawer');
  const countSpan = document.getElementById('compareCount');
  const drawerCount = document.getElementById('drawerCollegesCount');
  const drawerCountMini = document.getElementById('drawerCollegesCountMini');
  
  const count = AppState.comparisonList.length;
  countSpan.textContent = count;
  drawerCount.textContent = count;
  if (drawerCountMini) drawerCountMini.textContent = count;

  if (count > 0) {
    drawer.classList.add('active');
  } else {
    drawer.classList.remove('active');
    drawer.classList.remove('expanded'); // Reset expanded state when cleared
  }

  // Reposition filter button after drawer state settles
  requestAnimationFrame(() => repositionFilterButton());
}

// Keep the floating filter button just above the compare drawer
function repositionFilterButton() {
  const filterBtn = document.getElementById('mobileFilterOpenBtn');
  const drawer = document.getElementById('compareDrawer');
  if (!filterBtn || !drawer) return;

  if (drawer.classList.contains('active') && window.innerWidth <= 1024) {
    const drawerHeight = drawer.getBoundingClientRect().height;
    filterBtn.style.bottom = (drawerHeight + 16) + 'px';
  } else {
    filterBtn.style.bottom = '';
  }
}

// Render Comparison Grid panel
function renderComparisonMatrix() {
  ComparisonMatrix.render('comparisonMatrixWrapper', AppState.comparisonList, AppState.rawSeatsData, (removeId) => {
    toggleCollegeCompare(removeId);
    renderComparisonMatrix();
  });
}

// Set up UI Event listeners
function setupGlobalListeners() {
  // Level Tabs click
  document.querySelectorAll('.level-tab').forEach(tab => {
    tab.addEventListener('click', async (e) => {
      const button = e.currentTarget;
      document.querySelectorAll('.level-tab').forEach(b => b.classList.remove('active'));
      button.classList.add('active');
      
      AppState.activeLevel = button.getAttribute('data-level');
      AppState.comparisonList = [];
      updateCompareDrawer();
      
      await loadLevelData(AppState.activeLevel);
    });
  });

  // State Selector change
  document.getElementById('stateSelector').addEventListener('change', async (e) => {
    AppState.selectedState = e.target.value;
    await loadStateDetails(AppState.selectedState);
  });

  // Statistics Toggle Buttons click
  document.querySelectorAll('.toggle-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
      e.currentTarget.classList.add('active');
      
      AppState.statsMode = e.currentTarget.getAttribute('data-mode');
      renderDashboardStats();
    });
  });

  // Main Workspace panel Tabs click
  document.querySelectorAll('.panel-tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
      document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
      e.currentTarget.classList.add('active');
      
      // Hide all panels
      document.querySelectorAll('.panel-view').forEach(view => view.classList.remove('active'));
      
      // Show active panel
      const targetView = e.currentTarget.getAttribute('data-tab');
      if (targetView === 'table') document.getElementById('viewTable').classList.add('active');
      if (targetView === 'analytics') document.getElementById('viewAnalytics').classList.add('active');
      if (targetView === 'sankey') document.getElementById('viewSankey').classList.add('active');
      if (targetView === 'compare') document.getElementById('viewCompare').classList.add('active');

      updateExplorerViews();
    });
  });

  // Table Quick Search input (debounced by 150ms for performance)
  document.getElementById('tableSearchInput').addEventListener('input', debounce(() => {
    applyFiltering();
  }, 150));

  // Drawer Action Buttons
  document.getElementById('clearCompareBtn').addEventListener('click', () => {
    AppState.comparisonList = [];
    updateCompareDrawer();
    renderTableExplorer();
    renderComparisonMatrix();
  });

  document.getElementById('openCompareTabBtn').addEventListener('click', () => {
    // Exit fullscreen if active
    if (AppState.fullscreenActive) {
      toggleFullscreen(false);
    }
    
    // Activate the Compare Tab
    document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
    const compareTabBtn = document.querySelector('.panel-tab[data-tab="compare"]');
    if (compareTabBtn) compareTabBtn.classList.add('active');
    
    document.querySelectorAll('.panel-view').forEach(view => view.classList.remove('active'));
    const viewCompare = document.getElementById('viewCompare');
    if (viewCompare) viewCompare.classList.add('active');

    updateExplorerViews();

    // On mobile, auto-enter fullscreen for the compare view
    if (window.innerWidth <= 1024) {
      toggleFullscreen(true, 'compare');
    }
  });

  // Close details modal event listeners
  document.getElementById('closeDetailsModalBtn').addEventListener('click', closeCollegeDetailsModal);
  
  document.getElementById('detailsModal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
      closeCollegeDetailsModal();
    }
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeCollegeDetailsModal();
    }
  });

  // Mobile filters toggle listeners
  const filterOpenBtn = document.getElementById('mobileFilterOpenBtn');
  if (filterOpenBtn) {
    filterOpenBtn.addEventListener('click', () => {
      document.getElementById('filterSidebar').classList.add('active');
      document.getElementById('sidebarBackdrop').classList.add('active');
    });
  }

  const sidebarBackdrop = document.getElementById('sidebarBackdrop');
  if (sidebarBackdrop) {
    sidebarBackdrop.addEventListener('click', () => {
      document.getElementById('filterSidebar').classList.remove('active');
      sidebarBackdrop.classList.remove('active');
    });
  }

  // Compare drawer toggle (mobile collapsible)
  const drawerToggleBtn = document.getElementById('drawerToggleBtn');
  if (drawerToggleBtn) {
    drawerToggleBtn.addEventListener('click', () => {
      const drawer = document.getElementById('compareDrawer');
      drawer.classList.toggle('expanded');
      // Wait for CSS transition to settle, then reposition filter button
      setTimeout(() => repositionFilterButton(), 400);
    });
  }

  // Handle window resize dynamically to adjust charts
  let resizeTimeout;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      updateExplorerViews();
      repositionFilterButton();
    }, 250);
  });

  // Mobile Table Fullscreen controls
  const toggleFullscreen = (forceShow, type) => {
    if (!type) {
      type = AppState.fullscreenType || 'table';
    }
    const active = forceShow !== undefined ? forceShow : (!document.body.classList.contains('table-fullscreen-active') && !document.body.classList.contains('compare-fullscreen-active'));
    const exitBtn = document.getElementById('exitFullscreenBtn');
    const rotatePrompt = document.getElementById('rotatePrompt');
    
    if (active) {
      AppState.fullscreenType = type;
      if (type === 'table') {
        document.body.classList.add('table-fullscreen-active');
      } else {
        document.body.classList.add('compare-fullscreen-active');
      }
      AppState.fullscreenActive = true;
      if (exitBtn) exitBtn.style.display = 'flex';
      
      // Only show rotate prompt if device is in portrait mode on mobile
      if (rotatePrompt && window.innerHeight > window.innerWidth) {
        rotatePrompt.style.display = 'flex';
        // Auto hide rotate prompt after 5 seconds
        clearTimeout(AppState.rotatePromptTimeout);
        AppState.rotatePromptTimeout = setTimeout(() => {
          rotatePrompt.style.display = 'none';
        }, 5000);
      }
    } else {
      document.body.classList.remove('table-fullscreen-active');
      document.body.classList.remove('compare-fullscreen-active');
      AppState.fullscreenActive = false;
      AppState.fullscreenDismissed = true;
      if (exitBtn) exitBtn.style.display = 'none';
      if (rotatePrompt) rotatePrompt.style.display = 'none';
      clearTimeout(AppState.rotatePromptTimeout);
      
      // Scroll to the end of the table/page on exit
      setTimeout(() => {
        window.scrollTo({
          top: document.body.scrollHeight,
          behavior: 'smooth'
        });
      }, 100);
    }
  };

  const manualToggleBtn = document.getElementById('tableFullscreenToggleBtn');
  if (manualToggleBtn) {
    manualToggleBtn.addEventListener('click', () => {
      toggleFullscreen(true, 'table');
    });
  }

  const compareToggleBtn = document.getElementById('compareFullscreenToggleBtn');
  if (compareToggleBtn) {
    compareToggleBtn.addEventListener('click', () => {
      toggleFullscreen(true, 'compare');
    });
  }

  const exitBtn = document.getElementById('exitFullscreenBtn');
  if (exitBtn) {
    exitBtn.addEventListener('click', () => {
      toggleFullscreen(false);
    });
  }

  // Go to top button
  const goToTopBtn = document.getElementById('goToTopBtn');
  if (goToTopBtn) {
    goToTopBtn.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }

  const goToTopCompareBtn = document.getElementById('goToTopCompareBtn');
  if (goToTopCompareBtn) {
    goToTopCompareBtn.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }

  // Reset dismissal state if scrolled back to top
  window.addEventListener('scroll', () => {
    if (window.scrollY === 0) {
      AppState.fullscreenDismissed = false;
    }

    if (window.innerWidth > 768) return; // Only mobile

    const activeTabBtn = document.querySelector('.panel-tab.active');
    if (!activeTabBtn) return;
    
    const activeTab = activeTabBtn.getAttribute('data-tab');
    if (activeTab !== 'table' && activeTab !== 'compare') return;

    if (AppState.fullscreenDismissed || AppState.fullscreenActive) return;

    if (activeTab === 'table') {
      if (AppState.rawSeatsData.length === 0) return;
      const selectors = document.querySelector('.panel-tabs');
      if (selectors) {
        const selRect = selectors.getBoundingClientRect();
        // Auto trigger fullscreen when scrolling past category selectors (panel tabs)
        if (selRect.bottom < 10) {
          toggleFullscreen(true, 'table');
        }
      }
    } else if (activeTab === 'compare') {
      if (AppState.comparisonList.length === 0) return;
      const selectors = document.querySelector('.panel-tabs');
      if (selectors) {
        const selRect = selectors.getBoundingClientRect();
        // Auto trigger fullscreen when scrolling past category selectors (panel tabs)
        if (selRect.bottom < 10) {
          toggleFullscreen(true, 'compare');
        }
      }
    }
  });

  // Hide rotate prompt dynamically if screen orientation is changed to landscape
  window.addEventListener('resize', () => {
    const rotatePrompt = document.getElementById('rotatePrompt');
    if (rotatePrompt) {
      if (AppState.fullscreenActive && window.innerWidth > window.innerHeight) {
        rotatePrompt.style.display = 'none';
      } else if (AppState.fullscreenActive && window.innerHeight > window.innerWidth) {
        rotatePrompt.style.display = 'flex';
      }
    }
  });

  // Isolate touch input inside the fullscreen views to prevent browser overscroll/pull-to-refresh
  const setupTouchIsolation = (container) => {
    if (!container) return;
    let touchStartYSelf = 0;
    let touchStartXSelf = 0;
    
    container.addEventListener('touchstart', (e) => {
      if (AppState.fullscreenActive && e.touches.length === 1) {
        touchStartYSelf = e.touches[0].clientY;
        touchStartXSelf = e.touches[0].clientX;
      }
    }, { passive: true });

    container.addEventListener('touchmove', (e) => {
      if (!AppState.fullscreenActive) return;
      if (e.touches.length !== 1) return;

      const currentY = e.touches[0].clientY;
      const currentX = e.touches[0].clientX;
      
      const deltaY = currentY - touchStartYSelf;
      const deltaX = currentX - touchStartXSelf;

      // If primarily horizontal swiping, bypass prevention to allow horizontal scrolling
      if (Math.abs(deltaX) > Math.abs(deltaY)) {
        return;
      }

      const scrollTop = container.scrollTop;
      const isSwipingDown = deltaY > 0; // user drags finger down (scroll up)
      const isSwipingUp = deltaY < 0;   // user drags finger up (scroll down)

      // Prevent scroll from propagating when at top
      if (scrollTop <= 0 && isSwipingDown) {
        if (e.cancelable) e.preventDefault();
      }

      // Prevent scroll from propagating when at bottom
      const maxScroll = container.scrollHeight - container.clientHeight;
      if (scrollTop >= maxScroll - 1 && isSwipingUp) {
        if (e.cancelable) e.preventDefault();
      }
    }, { passive: false });
  };

  setupTouchIsolation(document.querySelector('.table-container'));
  setupTouchIsolation(document.querySelector('.comparison-container'));
}

// Display College Details Modal Popover
async function showCollegeDetailsModal(collegeId) {
  const modal = document.getElementById('detailsModal');
  if (!modal) return;

  // Set modal to loading state for instant visual feedback
  document.getElementById('modalCollegeName').textContent = "Loading College Details...";
  const codeBadge = document.getElementById('modalCollegeCode');
  codeBadge.style.display = 'none';

  const container = document.getElementById('modalBodyContent');
  container.innerHTML = `
    <div style="display: flex; justify-content: center; align-items: center; min-height: 200px; color: var(--text-secondary);">
      <div class="loader" style="width: 32px; height: 32px; border: 3px solid rgba(255,255,255,0.1); border-radius: 50%; border-top-color: var(--accent-blue); animation: spin 1s ease-in-out infinite;"></div>
    </div>
  `;

  modal.classList.add('active');

  // Await the details fetch if it's not completed yet
  let details = null;
  try {
    if (AppState.collegesDetails && Object.keys(AppState.collegesDetails).length > 0) {
      details = AppState.collegesDetails[collegeId];
    } else if (AppState.fetchingCollegesDetails) {
      const data = await AppState.fetchingCollegesDetails;
      details = data[collegeId];
    }
  } catch (err) {
    console.error("Error retrieving college details:", err);
  }

  if (!details) {
    document.getElementById('modalCollegeName').textContent = "Details Not Available";
    container.innerHTML = `
      <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 200px; color: var(--text-secondary); gap: 1rem;">
        <i data-lucide="alert-circle" style="width: 48px; height: 48px; color: var(--accent-red);"></i>
        <span>College details could not be retrieved from the server.</span>
      </div>
    `;
    if (window.lucide) {
      window.lucide.createIcons({
        attrs: { 'stroke-width': 2 },
        nameAttr: 'data-lucide',
        node: container
      });
    }
    return;
  }

  document.getElementById('modalCollegeName').textContent = details.college_name;
  
  if (details.college_code) {
    codeBadge.textContent = `Code: ${details.college_code}`;
    codeBadge.style.display = 'inline-block';
  } else {
    codeBadge.style.display = 'none';
  }

  // Format Contacts
  let contactsHtml = '';
  if (details.contacts && details.contacts.length > 0) {
    details.contacts.forEach(c => {
      let contactItems = '';
      if (c.email) {
        contactItems += `<div class="contact-info-item"><i data-lucide="mail"></i> <a href="mailto:${c.email}">${c.email}</a></div>`;
      }
      if (c.mobile) {
        contactItems += `<div class="contact-info-item"><i data-lucide="phone"></i> <span>${c.mobile}</span></div>`;
      }
      if (c.office) {
        contactItems += `<div class="contact-info-item"><i data-lucide="phone-call"></i> <span>${c.office} (Office)</span></div>`;
      }
      
      contactsHtml += `
        <div class="contact-card">
          <span class="contact-name">${c.name}</span>
          ${c.designation ? `<span class="contact-desg">${c.designation}</span>` : ''}
          ${contactItems}
        </div>
      `;
    });
  } else {
    contactsHtml = '<p class="placeholder-text" style="padding: 1rem !important;">No administrative contact details available.</p>';
  }

  // Format Status details
  let statusHtml = '';
  if (details.status_text) {
    statusHtml = `
      <div class="details-section" style="grid-column: span 2;">
        <h4><i data-lucide="shield-check"></i> NMC Recognition & Approval Status</h4>
        <div class="status-text-box">${details.status_text}</div>
      </div>
    `;
  }

  container.innerHTML = `
    <div class="modal-details-grid">
      <!-- Section 1: General Info -->
      <div class="details-section">
        <h4><i data-lucide="school"></i> Institutional Overview</h4>
        <div class="details-list">
          <div class="details-item">
            <span class="details-label">Management Type</span>
            <span class="details-value">${details.management || 'N/A'}</span>
          </div>
          <div class="details-item">
            <span class="details-label">Affiliated University</span>
            <span class="details-value">${details.university || 'N/A'}</span>
          </div>
          <div class="details-item">
            <span class="details-label">Year of Incorporation</span>
            <span class="details-value">${details.year_of_inc || 'N/A'}</span>
          </div>
          <div class="details-item">
            <span class="details-label">NMC Registry Status</span>
            <span class="details-value" style="font-weight: 700; color: var(--accent-green);">${details.status || 'Active'}</span>
          </div>
        </div>
      </div>

      <!-- Section 2: Campus & Location -->
      <div class="details-section">
        <h4><i data-lucide="map-pin"></i> Campus Registry & Location</h4>
        <div class="details-list">
          <div class="details-item">
            <span class="details-label">Postal Address</span>
            <span class="details-value" style="white-space: pre-line;">${details.address || 'N/A'}</span>
          </div>
          ${details.website ? `
          <div class="details-item">
            <span class="details-label">Official Website</span>
            <span class="details-value">
              <a href="${details.website.startsWith('http') ? details.website : 'http://' + details.website}" target="_blank" rel="noopener noreferrer">${details.website}</a>
            </span>
          </div>` : ''}
          ${details.email ? `
          <div class="details-item">
            <span class="details-label">Registry Email</span>
            <span class="details-value"><a href="mailto:${details.email}">${details.email}</a></span>
          </div>` : ''}
          ${details.telephone ? `
          <div class="details-item">
            <span class="details-label">Telephone Contacts</span>
            <span class="details-value">${details.telephone}</span>
          </div>` : ''}
        </div>
      </div>

      <!-- Section 3: Administrative Contacts -->
      <div class="details-section" style="grid-column: span 2;">
        <h4><i data-lucide="users"></i> Administrative & Key Officials</h4>
        <div class="contacts-grid">
          ${contactsHtml}
        </div>
      </div>

      <!-- Section 4: NMC status text -->
      ${statusHtml}
    </div>
  `;

  if (window.lucide) {
    window.lucide.createIcons({
      attrs: {
        'stroke-width': 2
      },
      nameAttr: 'data-lucide',
      node: container
    });
  }
}

// Close College Details Modal
function closeCollegeDetailsModal() {
  document.getElementById('detailsModal').classList.remove('active');
}

// Launch Application
if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
