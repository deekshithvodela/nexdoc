// MCC UG Cutoff Explorer & NEET Rank Predictor Component
import { TableEngine } from './TableEngine.js';
import { CutoffExplorerSchema } from './TableSchemas.js';

export const CutoffExplorer = {
  tableEngine: null,
  state: {
    ugMappingData: [],       // All 823 Master UG colleges with MCC status
    loaded: false,
    loading: false,
    
    // Filters & Inputs
    userRank: '',            // Entered NEET Rank
    searchQuery: '',         // Top college search query
    selectedCategory: 'ALL', // Category dropdown filter
    selectedQuota: 'ALL',    // Quota dropdown filter
    selectedChance: 'ALL',   // Chance predictor selection
    selectedCategories: [],  // Legacy sidebar compatibility
    selectedQuotas: [],      // Legacy sidebar compatibility
    
    // Collapsed/Expanded state tracking
    expandedCollegeIds: new Set(),
    
    // Available Dropdown Options
    categoriesList: ['Open', 'Open PwD', 'OBC', 'OBC PwD', 'EWS', 'EWS PwD', 'SC', 'SC PwD', 'ST', 'ST PwD', 'NRI'],
    quotasList: [],
    selectedStateVal: 'all',
    statesList: [],
    selectedStates: [],
    stateSearchQuery: ''
  },

  setSelectedState(stateVal) {
    this.state.selectedStateVal = stateVal || 'all';
    this.state.selectedStates = [];
    this.state.stateSearchQuery = '';
    if (this.tableEngine) {
      this.tableEngine.state.selectedState = stateVal === 'all' ? 'ALL' : stateVal;
    }
    const sidebar = document.getElementById('filterSidebar');
    if (sidebar) this.renderSidebarFilters('filterSidebar');
    const container = document.getElementById('viewCutoffs');
    if (container && this.state.loaded) this.render(container);
  },

  async init(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!this.state.loaded && !this.state.loading) {
      this.state.loading = true;
      this.renderLoading(container);

      try {
        const res = await fetch('data/ug_colleges_aiq_mapping.json');
        this.state.ugMappingData = await res.json();
        
        // Extract quotas and states list
        const qSet = new Set();
        const sSet = new Set();
        this.state.ugMappingData.forEach(c => {
          if (c.state) sSet.add(c.state);
          (c.aiq_cutoffs_raw || []).forEach(cutoff => {
            const courseName = (cutoff.course || '').toLowerCase();
            const quotaName = (cutoff.quota || '').toLowerCase();
            if (courseName.includes('nursing') || courseName.includes('bds') || quotaName.includes('nursing') || quotaName.includes('bsc')) {
              return;
            }
            if (cutoff.quota) qSet.add(cutoff.quota);
          });
        });
        this.state.quotasList = Array.from(qSet).sort();
        this.state.statesList = Array.from(sSet).sort();

        // Initialize TableEngine instance
        this.tableEngine = new TableEngine({
          schema: CutoffExplorerSchema,
          containerId: containerId,
          rawData: this.state.ugMappingData
        });

        this.state.loaded = true;
        this.state.loading = false;
        this.render(container);
        this.renderSidebarFilters('filterSidebar');
      } catch (err) {
        console.error("Failed to load MCC Cutoff mapping data:", err);
        container.innerHTML = `
          <div class="placeholder-text pad-2 text-red">
            Failed to load MCC Cutoff Data. Please try refreshing.
          </div>
        `;
        this.state.loading = false;
        return;
      }
    } else if (this.state.loaded) {
      this.render(container);
    }
  },

  renderLoading(container) {
    container.innerHTML = `
      <div class="cutoff-loading-container">
        <div class="loader loader-lg"></div>
        <p class="font-medium">Loading MCC UG Cutoff Explorer & College Predictor...</p>
      </div>
    `;
  },

  parseRankNum(val) {
    if (typeof val === 'number') return val;
    if (val !== '-' && val !== undefined && val !== null && val !== '') {
      const cleanStr = val.toString().replace(/,/g, '');
      const p = parseInt(cleanStr, 10);
      return isNaN(p) ? Infinity : p;
    }
    return Infinity;
  },

  formatRankVal(val) {
    if (val === '-' || val === undefined || val === null || val === '' || val === Infinity) return '-';
    if (typeof val === 'number') return val.toLocaleString();
    const p = parseInt(val, 10);
    return isNaN(p) ? '-' : p.toLocaleString();
  },

  getFilteredColleges() {
    const searchQueryLow = this.state.searchQuery.toLowerCase().trim();
    const userRankNum = parseInt(this.state.userRank, 10);
    const hasRank = !isNaN(userRankNum) && userRankNum > 0;

    let colleges = [...this.state.ugMappingData];

    // Region Filter (from global top-of-page state selector or checkboxes)
    if (this.state.selectedStateVal && this.state.selectedStateVal !== 'all') {
      colleges = colleges.filter(c => (c.state || '').toLowerCase() === this.state.selectedStateVal.toLowerCase());
    } else if (this.state.selectedStates && this.state.selectedStates.length > 0) {
      colleges = colleges.filter(c => this.state.selectedStates.includes(c.state));
    }

    // Top Search Query Filter
    if (searchQueryLow) {
      colleges = colleges.filter(c => {
        const nameMatch = (c.college_name || '').toLowerCase().includes(searchQueryLow);
        const cityMatch = (c.city || '').toLowerCase().includes(searchQueryLow);
        const stateMatch = (c.state || '').toLowerCase().includes(searchQueryLow);
        const codeMatch = (c.college_code || '').toLowerCase().includes(searchQueryLow);
        return nameMatch || cityMatch || stateMatch || codeMatch;
      });
    }

    const result = [];

    colleges.forEach(col => {
      let rawCutoffs = col.aiq_cutoffs_raw || [];
      if (!rawCutoffs || rawCutoffs.length === 0) return;

      const processedChildRows = [];

      rawCutoffs.forEach(c => {
        // Presentation-layer Allied Course Exclusion Rule
        const courseName = (c.course || '').toLowerCase();
        const quotaName = (c.quota || '').toLowerCase();
        if (courseName.includes('nursing') || courseName.includes('bds') || quotaName.includes('nursing') || quotaName.includes('bsc')) {
          return;
        }

        // Category Filter
        if (this.state.selectedCategory !== 'ALL' && c.category !== this.state.selectedCategory) {
          return;
        }
        if (this.state.selectedCategories && this.state.selectedCategories.length > 0 && !this.state.selectedCategories.includes(c.category)) {
          return;
        }

        // Quota Filter
        if (this.state.selectedQuota !== 'ALL' && c.quota !== this.state.selectedQuota) {
          return;
        }
        if (this.state.selectedQuotas && this.state.selectedQuotas.length > 0 && !this.state.selectedQuotas.includes(c.quota)) {
          return;
        }

        // Chance Predictor Calculation
        let chanceCategory = 'N/A';
        let chanceBadgeClass = '';
        let chanceLabel = 'N/A';

        const r1Open = this.parseRankNum(c.r1_opening_rank);
        const r1Close = this.parseRankNum(c.r1_closing_rank);
        const r2Open = this.parseRankNum(c.r2_opening_rank);
        const r2Close = this.parseRankNum(c.r2_closing_rank);
        const r3Open = this.parseRankNum(c.r3_opening_rank);
        const r3Close = this.parseRankNum(c.r3_closing_rank);
        const finalOpen = this.parseRankNum(c.final_opening_rank);
        const finalClose = this.parseRankNum(c.final_closing_rank);

        if (hasRank) {
          const validCloses = [finalClose, r3Close, r2Close, r1Close].filter(x => x !== Infinity);
          if (validCloses.length > 0) {
            const bestClose = Math.max(...validCloses);
            if (userRankNum <= bestClose) {
              chanceCategory = 'HIGH';
              chanceBadgeClass = 'badge-chance-high';
              chanceLabel = 'High Chance';
            } else if (userRankNum <= bestClose * 1.15) {
              chanceCategory = 'BORDERLINE';
              chanceBadgeClass = 'badge-chance-medium';
              chanceLabel = 'Borderline';
            } else {
              chanceCategory = 'LOW';
              chanceBadgeClass = 'badge-chance-low';
              chanceLabel = 'Low Chance';
            }
          }
        }

        if (this.state.selectedChance !== 'ALL' && chanceCategory !== this.state.selectedChance) {
          return;
        }

        processedChildRows.push({
          quota: c.quota,
          category: c.category,
          course: c.course || 'MBBS',
          chanceCategory,
          chanceBadgeClass,
          chanceLabel,
          r1_open_num: r1Open,
          r1_close_num: r1Close,
          r2_open_num: r2Open,
          r2_close_num: r2Close,
          r3_open_num: r3Open,
          r3_close_num: r3Close,
          final_open_num: finalOpen,
          final_close_num: finalClose,
          r1_open_str: this.formatRankVal(c.r1_opening_rank),
          r1_close_str: this.formatRankVal(c.r1_closing_rank),
          r2_open_str: this.formatRankVal(c.r2_opening_rank),
          r2_close_str: this.formatRankVal(c.r2_closing_rank),
          r3_open_str: this.formatRankVal(c.r3_opening_rank),
          r3_close_str: this.formatRankVal(c.r3_closing_rank),
          final_open_str: this.formatRankVal(c.final_opening_rank),
          final_close_str: this.formatRankVal(c.final_closing_rank)
        });
      });

      // If active dropdown or sidebar checkbox filter leaves 0 child rows, skip college
      const isFilterActive = (this.state.selectedCategory !== 'ALL') || (this.state.selectedQuota !== 'ALL') || (this.state.selectedChance !== 'ALL') || (this.state.selectedCategories && this.state.selectedCategories.length > 0) || (this.state.selectedQuotas && this.state.selectedQuotas.length > 0);
      if (isFilterActive && processedChildRows.length === 0) {
        return;
      }

      // Sort expanded cutoff information: Quota first, then ascending rank order within quota
      processedChildRows.sort((a, b) => {
        const quotaCmp = a.quota.localeCompare(b.quota);
        if (quotaCmp !== 0) return quotaCmp;

        const getMinRank = (r) => {
          const ranks = [r.r1_close_num, r.r2_close_num, r.r3_close_num, r.final_close_num, r.r1_open_num, r.final_open_num].filter(x => x !== Infinity);
          return ranks.length > 0 ? Math.min(...ranks) : Infinity;
        };
        return getMinRank(a) - getMinRank(b);
      });

      const finalOpeningNums = processedChildRows.map(r => r.final_open_num).filter(x => x !== Infinity);
      const finalClosingNums = processedChildRows.map(r => r.final_close_num).filter(x => x !== Infinity);

      const minFinalOpen = finalOpeningNums.length > 0 ? Math.min(...finalOpeningNums) : Infinity;
      const maxFinalClose = finalClosingNums.length > 0 ? Math.max(...finalClosingNums) : Infinity;

      result.push({
        college_id: col.college_id,
        college_name: col.college_name,
        state: col.state || '',
        city: col.city || '',
        college_type: col.college_type || 'Government',
        college_code: col.college_code || '',
        pincode: col.pincode || '',
        mcc_status: col.mcc_status || (col.matched_in_aiq ? 'Matched' : 'Non AIQ'),
        aiq_college_name: col.aiq_college_name,
        min_final_open_str: this.formatRankVal(minFinalOpen),
        max_final_close_str: this.formatRankVal(maxFinalClose),
        childRows: processedChildRows
      });
    });

    // Ensure all filtered cutoff table records are strictly sorted alphabetically by college_name
    result.sort((a, b) => (a.college_name || '').localeCompare(b.college_name || ''));

    return result;
  },

  // Dedicated Sidebar Filter Panel Renderer
  renderSidebarFilters(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const html = `
      <div class="sidebar-mobile-header">
        <h3>MCC Predictor Filters</h3>
        <button class="btn-close-sidebar" id="closeSidebarBtn">
          <i data-lucide="x"></i>
        </button>
      </div>

      <!-- State Filter Section -->
      <div class="sidebar-section">
        <h4 class="sidebar-section-title">
          <i data-lucide="map-pin"></i>
          <span>Filter by State</span>
        </h4>
        <div class="sidebar-search-box">
          <i data-lucide="search" class="icon-xs"></i>
          <input type="text" id="sidebarStateSearchInput" placeholder="Search states..." value="${this.state.stateSearchQuery}">
        </div>
        <div class="sidebar-checkbox-group sidebar-scrollable-list">
          <label class="sidebar-checkbox-label ${this.state.selectedStates.length === 0 ? 'active' : ''}">
            <input type="checkbox" name="sidebarStateRadio" value="ALL" ${this.state.selectedStates.length === 0 ? 'checked' : ''}>
            <span>All States</span>
          </label>
          ${this.state.statesList
            .filter(s => s.toLowerCase().includes(this.state.stateSearchQuery.toLowerCase()))
            .map(s => `
              <label class="sidebar-checkbox-label ${this.state.selectedStates.includes(s) ? 'active' : ''}">
                <input type="checkbox" name="sidebarStateCheckbox" value="${s}" ${this.state.selectedStates.includes(s) ? 'checked' : ''}>
                <span>${s}</span>
              </label>
            `).join('')}
        </div>
      </div>

      <!-- Quota Filter Section -->
      <div class="sidebar-section">
        <h4 class="sidebar-section-title">
          <i data-lucide="layers"></i>
          <span>Filter by Quota</span>
        </h4>
        <div class="sidebar-checkbox-group">
          <label class="sidebar-checkbox-label ${this.state.selectedQuotas.length === 0 ? 'active' : ''}">
            <input type="checkbox" name="sidebarQuotaRadio" value="ALL" ${this.state.selectedQuotas.length === 0 ? 'checked' : ''}>
            <span>All Quotas</span>
          </label>
          ${this.state.quotasList.map(q => `
            <label class="sidebar-checkbox-label ${this.state.selectedQuotas.includes(q) ? 'active' : ''}">
              <input type="checkbox" name="sidebarQuotaCheckbox" value="${q}" ${this.state.selectedQuotas.includes(q) ? 'checked' : ''}>
              <span>${q}</span>
            </label>
          `).join('')}
        </div>
      </div>

      <!-- Category Filter Section -->
      <div class="sidebar-section">
        <h4 class="sidebar-section-title">
          <i data-lucide="users"></i>
          <span>Filter by Category</span>
        </h4>
        <div class="sidebar-checkbox-group">
          <label class="sidebar-checkbox-label ${this.state.selectedCategories.length === 0 ? 'active' : ''}">
            <input type="checkbox" name="sidebarCategoryRadio" value="ALL" ${this.state.selectedCategories.length === 0 ? 'checked' : ''}>
            <span>All Categories</span>
          </label>
          ${this.state.categoriesList.map(cat => `
            <label class="sidebar-checkbox-label ${this.state.selectedCategories.includes(cat) ? 'active' : ''}">
              <input type="checkbox" name="sidebarCategoryCheckbox" value="${cat}" ${this.state.selectedCategories.includes(cat) ? 'checked' : ''}>
              <span>${cat}</span>
            </label>
          `).join('')}
        </div>
      </div>
    `;

    container.innerHTML = html;
    if (window.lucide) window.lucide.createIcons();
    this.bindSidebarEvents(container);
  },

  bindSidebarEvents(container) {
    const closeBtn = container.querySelector('#closeSidebarBtn');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        document.body.classList.remove('sidebar-open');
      });
    }

    const stateSearchInput = container.querySelector('#sidebarStateSearchInput');
    if (stateSearchInput) {
      stateSearchInput.addEventListener('input', (e) => {
        this.state.stateSearchQuery = e.target.value;
        this.renderSidebarFilters('filterSidebar');
      });
    }

    container.querySelectorAll('input[name="sidebarStateCheckbox"]').forEach(cb => {
      cb.addEventListener('change', (e) => {
        const val = e.target.value;
        if (e.target.checked) {
          if (!this.state.selectedStates.includes(val)) this.state.selectedStates.push(val);
        } else {
          this.state.selectedStates = this.state.selectedStates.filter(s => s !== val);
        }
        this.renderSidebarFilters('filterSidebar');
        const viewContainer = document.getElementById('viewCutoffs');
        if (viewContainer) this.render(viewContainer);
      });
    });

    const allStateRadio = container.querySelector('input[name="sidebarStateRadio"]');
    if (allStateRadio) {
      allStateRadio.addEventListener('change', () => {
        this.state.selectedStates = [];
        this.renderSidebarFilters('filterSidebar');
        const viewContainer = document.getElementById('viewCutoffs');
        if (viewContainer) this.render(viewContainer);
      });
    }

    container.querySelectorAll('input[name="sidebarQuotaCheckbox"]').forEach(cb => {
      cb.addEventListener('change', (e) => {
        const val = e.target.value;
        if (e.target.checked) {
          if (!this.state.selectedQuotas.includes(val)) this.state.selectedQuotas.push(val);
        } else {
          this.state.selectedQuotas = this.state.selectedQuotas.filter(q => q !== val);
        }
        this.renderSidebarFilters('filterSidebar');
        const viewContainer = document.getElementById('viewCutoffs');
        if (viewContainer) this.render(viewContainer);
      });
    });

    const allQuotaRadio = container.querySelector('input[name="sidebarQuotaRadio"]');
    if (allQuotaRadio) {
      allQuotaRadio.addEventListener('change', () => {
        this.state.selectedQuotas = [];
        this.renderSidebarFilters('filterSidebar');
        const viewContainer = document.getElementById('viewCutoffs');
        if (viewContainer) this.render(viewContainer);
      });
    }

    container.querySelectorAll('input[name="sidebarCategoryCheckbox"]').forEach(cb => {
      cb.addEventListener('change', (e) => {
        const val = e.target.value;
        if (e.target.checked) {
          if (!this.state.selectedCategories.includes(val)) this.state.selectedCategories.push(val);
        } else {
          this.state.selectedCategories = this.state.selectedCategories.filter(c => c !== val);
        }
        this.renderSidebarFilters('filterSidebar');
        const viewContainer = document.getElementById('viewCutoffs');
        if (viewContainer) this.render(viewContainer);
      });
    });

    const allCatRadio = container.querySelector('input[name="sidebarCategoryRadio"]');
    if (allCatRadio) {
      allCatRadio.addEventListener('change', () => {
        this.state.selectedCategories = [];
        this.renderSidebarFilters('filterSidebar');
        const viewContainer = document.getElementById('viewCutoffs');
        if (viewContainer) this.render(viewContainer);
      });
    }
  },

  render(container) {
    if (!container) return;
    const filteredColleges = this.getFilteredColleges();
    const userRankNum = parseInt(this.state.userRank, 10);
    const hasRank = !isNaN(userRankNum) && userRankNum > 0;

    const html = `
      <div class="cutoff-explorer-layout card-glass pad-1-5">
        
        <!-- Controls Header Card -->
        <div class="cutoff-controls-card">
          <div class="cutoff-filters-grid">
            
            <div class="filter-group">
              <label for="rankPredictorInput"><i data-lucide="award"></i> Predict by Rank:</label>
              <input type="number" id="rankPredictorInput" class="input-dark input-rank" placeholder="Enter NEET Rank (e.g. 10000)" value="${this.state.userRank}" aria-label="Enter NEET AIR Rank for Prediction" />
            </div>

            <div class="filter-group col-span-2">
              <label for="collegeSearchInput"><i data-lucide="search"></i> Search College:</label>
              <input type="text" id="collegeSearchInput" class="input-dark" placeholder="Search college, city, state..." value="${this.state.searchQuery}" aria-label="Search college by name, city, or state" />
            </div>

            <div class="filter-group">
              <label for="categoryFilterSelect"><i data-lucide="users"></i> Category:</label>
              <select id="categoryFilterSelect" class="select-dark" aria-label="Filter cutoffs by candidate category">
                <option value="ALL" ${this.state.selectedCategory === 'ALL' ? 'selected' : ''}>All Categories</option>
                ${this.state.categoriesList.map(cat => `<option value="${cat}" ${this.state.selectedCategory === cat ? 'selected' : ''}>${cat}</option>`).join('')}
              </select>
            </div>

            <div class="filter-group">
              <label for="quotaFilterSelect"><i data-lucide="layers"></i> Quota:</label>
              <select id="quotaFilterSelect" class="select-dark" aria-label="Filter cutoffs by seat allotment quota">
                <option value="ALL" ${this.state.selectedQuota === 'ALL' ? 'selected' : ''}>All Quotas</option>
                ${this.state.quotasList.map(q => `<option value="${q}" ${this.state.selectedQuota === q ? 'selected' : ''}>${q}</option>`).join('')}
              </select>
            </div>

            <div class="filter-group">
              <label for="chanceFilterSelect"><i data-lucide="sparkles"></i> Chance Predictor:</label>
              <select id="chanceFilterSelect" class="select-dark" ${!hasRank ? 'disabled' : ''} aria-label="Filter predicted admission chance">
                <option value="ALL" ${this.state.selectedChance === 'ALL' ? 'selected' : ''}>All Chances</option>
                <option value="HIGH" ${this.state.selectedChance === 'HIGH' ? 'selected' : ''}>High Chance</option>
                <option value="BORDERLINE" ${this.state.selectedChance === 'BORDERLINE' ? 'selected' : ''}>Borderline</option>
                <option value="LOW" ${this.state.selectedChance === 'LOW' ? 'selected' : ''}>Low Chance</option>
              </select>
            </div>

          </div>

          <!-- Quick Action Bar -->
          <div class="cutoff-action-bar">
            <div class="action-buttons-left">
              <button id="btnExpandAllCutoffs" class="btn btn-secondary btn-sm">
                <i data-lucide="maximize-2"></i> Expand All
              </button>
              <button id="btnCollapseAllCutoffs" class="btn btn-secondary btn-sm">
                <i data-lucide="minimize-2"></i> Collapse All
              </button>
            </div>
            <div class="action-info-right">
              <span class="count-badge">Showing ${filteredColleges.length} Colleges</span>
            </div>
          </div>
        </div>

        <!-- Main Cutoff Table -->
        <div class="cutoff-table-scroll">
          <table class="cutoff-table">
            <thead>
              <tr>
                <th class="col-expand-toggle"></th>
                <th class="col-name-th">College Name</th>
                <th>State & City</th>
                <th>Type</th>
                <th>Course</th>
                <th>Quota</th>
                <th>Category</th>
                ${hasRank ? '<th>Predicted Chance</th>' : ''}
                <th class="text-right">R1 Op</th>
                <th class="text-right">R1 Cl</th>
                <th class="text-right">R2 Op</th>
                <th class="text-right">R2 Cl</th>
                <th class="text-right">R3 Op</th>
                <th class="text-right">R3 Cl</th>
                <th class="text-right">Final Op</th>
                <th class="text-right">Final Cl</th>
              </tr>
            </thead>
            <tbody>
              ${filteredColleges.length === 0 ? `
                <tr>
                  <td colspan="${hasRank ? 16 : 15}" class="text-center py-8 text-muted">
                    No matching cutoff records found matching your filters.
                  </td>
                </tr>
              ` : filteredColleges.map(group => {
                const isExpanded = this.state.expandedCollegeIds.has(group.college_id);
                const typeBadgeClass = group.college_type === 'INI' ? 'badge-ini' : (group.college_type === 'Government' ? 'badge-govt' : (group.college_type === 'Deemed' ? 'badge-deemed' : 'badge-private'));
                
                const categoriesCount = group.childRows.length;

                return `
                  <tr class="group-header-row table-row-group-header" data-college-group-id="${group.college_id}">
                    <td class="text-center th-expand-col">
                      <button class="group-expand-btn ${isExpanded ? 'expanded' : ''}" data-toggle-college="${group.college_id}" aria-label="Toggle ${group.college_name} details">
                        <i data-lucide="${isExpanded ? 'chevron-down' : 'chevron-right'}" class="icon-sm"></i>
                      </button>
                    </td>
                    <td class="col-name-td font-semibold text-main">
                      <a href="#" class="college-link text-primary hover:underline" data-college-id="${group.college_id}">
                        ${group.college_name}
                      </a>
                    </td>
                    <td class="text-muted text-sm">${group.city ? `${group.city}, ` : ''}${group.state}</td>
                    <td><span class="badge ${typeBadgeClass}">${group.college_type}</span></td>
                    <td class="text-muted text-sm">MBBS</td>
                    <td class="text-muted text-sm">${group.childRows.length > 0 ? (new Set(group.childRows.map(r=>r.quota))).size + ' Quotas' : '-'}</td>
                    <td>
                      <span class="badge badge-subtle">
                        ${categoriesCount} ${categoriesCount === 1 ? 'Category' : 'Categories'}
                      </span>
                    </td>
                    ${hasRank ? `
                      <td>
                        ${(() => {
                          const chances = group.childRows.map(r => r.chanceCategory);
                          if (chances.includes('HIGH')) return '<span class="badge badge-chance-high">High Chance</span>';
                          if (chances.includes('BORDERLINE')) return '<span class="badge badge-chance-medium">Borderline</span>';
                          if (chances.includes('LOW')) return '<span class="badge badge-chance-low">Low Chance</span>';
                          return '<span class="text-muted text-xs">N/A</span>';
                        })()}
                      </td>
                    ` : ''}
                    <td class="text-right font-mono text-sm">${group.childRows[0]?.r1_open_str || '-'}</td>
                    <td class="text-right font-mono text-sm">${group.childRows[0]?.r1_close_str || '-'}</td>
                    <td class="text-right font-mono text-sm">${group.childRows[0]?.r2_open_str || '-'}</td>
                    <td class="text-right font-mono text-sm">${group.childRows[0]?.r2_close_str || '-'}</td>
                    <td class="text-right font-mono text-sm">${group.childRows[0]?.r3_open_str || '-'}</td>
                    <td class="text-right font-mono text-sm">${group.childRows[0]?.r3_close_str || '-'}</td>
                    <td class="text-right font-mono text-sm text-primary font-semibold">${group.min_final_open_str || '-'}</td>
                    <td class="text-right font-mono text-sm text-primary font-semibold">${group.max_final_close_str || '-'}</td>
                  </tr>

                  ${isExpanded ? group.childRows.map(c => `
                    <tr class="child-cutoff-row child-row-${group.college_id}">
                      <td></td>
                      <td colspan="3" class="pl-8 text-sm">
                        <div class="flex items-center gap-2">
                          <span class="tree-branch-icon text-muted">└</span>
                          <span class="font-medium text-main">${c.quota}</span>
                        </div>
                      </td>
                      <td class="text-sm text-muted">MBBS</td>
                      <td class="text-sm font-medium">${c.quota}</td>
                      <td><span class="badge badge-subtle">${c.category}</span></td>
                      ${hasRank ? `<td><span class="badge ${c.chanceBadgeClass}">${c.chanceLabel}</span></td>` : ''}
                      <td class="text-right font-mono text-xs">${c.r1_open_str}</td>
                      <td class="text-right font-mono text-xs">${c.r1_close_str}</td>
                      <td class="text-right font-mono text-xs">${c.r2_open_str}</td>
                      <td class="text-right font-mono text-xs">${c.r2_close_str}</td>
                      <td class="text-right font-mono text-xs">${c.r3_open_str}</td>
                      <td class="text-right font-mono text-xs">${c.r3_close_str}</td>
                      <td class="text-right font-mono text-xs font-semibold text-primary">${c.final_open_str}</td>
                      <td class="text-right font-mono text-xs font-semibold text-primary">${c.final_close_str}</td>
                    </tr>
                  `).join('') : ''}
                `;
              }).join('')}
            </tbody>
          </table>
        </div>

      </div>
    `;

    container.innerHTML = html;
    if (window.lucide) window.lucide.createIcons();
    this.bindEvents(container);
  },

  bindEvents(container) {
    const rankInput = container.querySelector('#rankPredictorInput');
    if (rankInput) {
      rankInput.addEventListener('input', (e) => {
        this.state.userRank = e.target.value;
        this.render(container);
      });
    }

    const searchInput = container.querySelector('#collegeSearchInput');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.state.searchQuery = e.target.value;
        this.render(container);
      });
    }

    const catSelect = container.querySelector('#categoryFilterSelect');
    if (catSelect) {
      catSelect.addEventListener('change', (e) => {
        this.state.selectedCategory = e.target.value;
        this.render(container);
      });
    }

    const quotaSelect = container.querySelector('#quotaFilterSelect');
    if (quotaSelect) {
      quotaSelect.addEventListener('change', (e) => {
        this.state.selectedQuota = e.target.value;
        this.render(container);
      });
    }

    const chanceSelect = container.querySelector('#chanceFilterSelect');
    if (chanceSelect) {
      chanceSelect.addEventListener('change', (e) => {
        this.state.selectedChance = e.target.value;
        this.render(container);
      });
    }

    const btnExpandAll = container.querySelector('#btnExpandAllCutoffs');
    if (btnExpandAll) {
      btnExpandAll.addEventListener('click', () => {
        const filtered = this.getFilteredColleges();
        filtered.forEach(c => this.state.expandedCollegeIds.add(c.college_id));
        this.render(container);
      });
    }

    const btnCollapseAll = container.querySelector('#btnCollapseAllCutoffs');
    if (btnCollapseAll) {
      btnCollapseAll.addEventListener('click', () => {
        this.state.expandedCollegeIds.clear();
        this.render(container);
      });
    }

    container.querySelectorAll('[data-toggle-college]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const collegeId = e.currentTarget.getAttribute('data-toggle-college');
        if (this.state.expandedCollegeIds.has(collegeId)) {
          this.state.expandedCollegeIds.delete(collegeId);
        } else {
          this.state.expandedCollegeIds.add(collegeId);
        }
        this.render(container);
      });
    });

    container.querySelectorAll('.college-link').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const cid = e.currentTarget.getAttribute('data-college-id');
        if (window.showCollegeDetailsModal) {
          window.showCollegeDetailsModal(cid);
        }
      });
    });
  }
};
