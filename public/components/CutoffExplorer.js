// MCC UG Cutoff Explorer & NEET Rank Predictor Component
export const CutoffExplorer = {
  state: {
    ugMappingData: [],       // All 823 Master UG colleges with MCC status
    loaded: false,
    loading: false,
    
    // Filters & Inputs
    userRank: '',            // Entered NEET Rank (digits strictly restricted)
    searchQuery: '',         // Top college search query (words strictly restricted)
    selectedCategory: 'ALL', // Category dropdown filter ('ALL' or specific category)
    selectedQuota: 'ALL',    // Quota dropdown filter ('ALL' or specific quota)
    selectedChance: 'ALL',   // Chance predictor selection ('ALL', 'HIGH', 'BORDERLINE', 'LOW')
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
            if (cutoff.quota) qSet.add(cutoff.quota);
          });
        });
        this.state.quotasList = Array.from(qSet).sort();
        this.state.statesList = Array.from(sSet).sort();

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
      const cleanVal = this.state.selectedStateVal.toLowerCase().replace(/_/g, ' ');
      colleges = colleges.filter(c => c.state && c.state.toLowerCase() === cleanVal);
    } else if (this.state.selectedStates && this.state.selectedStates.length > 0) {
      colleges = colleges.filter(c => c.state && this.state.selectedStates.includes(c.state));
    }

    // 2. College Search Filter
    if (searchQueryLow) {
      const words = searchQueryLow.split(' ').filter(Boolean);
      colleges = colleges.filter(c => {
        const str = `${c.college_name} ${c.state} ${c.city || ''} ${c.college_code || ''} ${c.pincode || ''} ${c.mcc_status}`.toLowerCase();
        return words.every(w => str.includes(w));
      });
    }

    const result = [];

    colleges.forEach(col => {
      let rawCutoffs = col.aiq_cutoffs_raw || [];

      // Sidebar multi-select filter compatibility
      if (this.state.selectedCategories.length > 0) {
        rawCutoffs = rawCutoffs.filter(c => this.state.selectedCategories.includes(c.category));
      }
      // Category dropdown filter
      if (this.state.selectedCategory && this.state.selectedCategory !== 'ALL') {
        rawCutoffs = rawCutoffs.filter(c => c.category === this.state.selectedCategory);
      }

      // Sidebar multi-select quota compatibility
      if (this.state.selectedQuotas.length > 0) {
        rawCutoffs = rawCutoffs.filter(c => this.state.selectedQuotas.includes(c.quota));
      }
      // Quota dropdown filter
      if (this.state.selectedQuota && this.state.selectedQuota !== 'ALL') {
        rawCutoffs = rawCutoffs.filter(c => c.quota === this.state.selectedQuota);
      }

      const processedChildRows = [];

      rawCutoffs.forEach(c => {
        const r1Open = this.parseRankNum(c.r1_opening_rank);
        const r1Close = this.parseRankNum(c.r1_closing_rank);
        const r2Open = this.parseRankNum(c.r2_opening_rank);
        const r2Close = this.parseRankNum(c.r2_closing_rank);
        const r3Open = this.parseRankNum(c.r3_opening_rank);
        const r3Close = this.parseRankNum(c.r3_closing_rank);
        const finalOpen = this.parseRankNum(c.final_opening_rank);
        const finalClose = this.parseRankNum(c.final_closing_rank);

        let predictorBadge = '';
        let chanceLevel = 'NONE';

        if (hasRank && finalClose !== Infinity) {
          const diff = finalClose - userRankNum;
          if (diff >= 3000) {
            predictorBadge = `<span class="badge badge-govt badge-chance-high">High Chance</span>`;
            chanceLevel = 'HIGH';
          } else if (diff >= 0) {
            predictorBadge = `<span class="badge badge-deemed badge-chance-borderline">Borderline</span>`;
            chanceLevel = 'BORDERLINE';
          } else {
            predictorBadge = `<span class="badge badge-private badge-chance-low">Low Chance</span>`;
            chanceLevel = 'LOW';
          }
        }

        // Apply Chance Predictor Dropdown filter if set
        if (this.state.selectedChance && this.state.selectedChance !== 'ALL') {
          if (hasRank && chanceLevel !== this.state.selectedChance) {
            return; // Skip non-matching chance cutoff row
          }
        }

        processedChildRows.push({
          quota: c.quota || 'All India',
          category: c.category || 'Open',
          course: c.course || 'MBBS',
          predictor_badge: predictorBadge,
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

      // If active dropdown filter leaves 0 child rows, skip college
      const isFilterActive = (this.state.selectedCategory !== 'ALL') || (this.state.selectedQuota !== 'ALL') || (this.state.selectedChance !== 'ALL');
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

      <!-- NEET Rank Predictor Input -->
      <div class="filter-group cutoff-filter-box">
        <h4 class="cutoff-filter-title">
          <i data-lucide="award"></i> Enter NEET AIR Rank:
        </h4>
        <div class="input-action-row">
          <input type="text" id="sidebarCutoffUserRank" placeholder="e.g. 10000" value="${this.state.userRank}" inputmode="numeric" class="rank-input-field">
          <button id="submitRankBtn" title="Apply Rank Filter" class="btn-rank-submit">
            <i data-lucide="search" class="icon-sm"></i>
          </button>
        </div>
      </div>

      <!-- Checklist-Style State Filter (Only if selectedStateVal is 'all') -->
      ${this.state.selectedStateVal === 'all' ? `
      <div class="filter-group">
        <h4 class="cutoff-filter-header">
          <span>State / Region Filter</span>
          <button id="clearSidebarStateFilterBtn" class="btn-link-action">Clear</button>
        </h4>
        <div class="search-box-container margin-bottom-sm">
          <i data-lucide="filter"></i>
          <input type="text" id="sidebarStateSearch" placeholder="Filter states..." value="${this.state.stateSearchQuery || ''}">
        </div>
        <div class="filter-options scrollable-checklist-list">
          ${(() => {
            const stateQueryLow = (this.state.stateSearchQuery || '').toLowerCase().trim();
            const filteredStates = this.state.statesList.filter(s =>
              !stateQueryLow || s.toLowerCase().includes(stateQueryLow)
            );
            if (filteredStates.length === 0) {
              return `<span class="placeholder-text text-sm-pad">No states match</span>`;
            }
            return filteredStates.map(state => `
              <label class="checkbox-label checkbox-item-row">
                <input type="checkbox" class="sidebar-state-cb" value="${state}" ${this.state.selectedStates.includes(state) ? 'checked' : ''}>
                <div class="checkbox-custom"><i data-lucide="check"></i></div>
                <span class="checkbox-item-text">${state}</span>
              </label>
            `).join('');
          })()}
        </div>
      </div>
      ` : ''}

      <!-- Checklist-Style Category Filter Window -->
      <div class="filter-group">
        <h4 class="cutoff-filter-header">
          <span>Category Filter</span>
          <button id="clearCategoryFilterBtn" class="btn-link-action">Clear</button>
        </h4>
        <div class="filter-options scrollable-checklist-list">
          ${this.state.categoriesList.map(cat => `
            <label class="checkbox-label checkbox-item-row">
              <input type="checkbox" class="sidebar-category-cb" value="${cat}" ${this.state.selectedCategories.includes(cat) ? 'checked' : ''}>
              <div class="checkbox-custom"><i data-lucide="check"></i></div>
              <span class="checkbox-item-text">${cat}</span>
            </label>
          `).join('')}
        </div>
      </div>

      <!-- Checklist-Style Quota Filter Window -->
      <div class="filter-group">
        <h4 class="cutoff-filter-header">
          <span>Quota Filter</span>
          <button id="clearQuotaFilterBtn" class="btn-link-action">Clear</button>
        </h4>
        <div class="filter-options scrollable-checklist-list">
          ${this.state.quotasList.map(q => `
            <label class="checkbox-label checkbox-item-row">
              <input type="checkbox" class="sidebar-quota-cb" value="${q}" ${this.state.selectedQuotas.includes(q) ? 'checked' : ''}>
              <div class="checkbox-custom"><i data-lucide="check"></i></div>
              <span class="checkbox-item-text">${q}</span>
            </label>
          `).join('')}
        </div>
      </div>

      <button class="btn-reset-filters margin-top-sm" id="sidebarResetCutoffFiltersBtn">
        <i data-lucide="refresh-cw"></i> Reset All Predictor Filters
      </button>
    `;

    container.innerHTML = html;

    if (window.lucide) window.lucide.createIcons();

    // Attach Event Listeners
    const rankInput = container.querySelector('#sidebarCutoffUserRank');
    const submitRankBtn = container.querySelector('#submitRankBtn');

    const applyRankFilter = () => {
      if (!rankInput) return;
      const val = rankInput.value.trim();
      if (this.state.userRank !== val) {
        this.state.userRank = val;
        const targetView = document.getElementById('viewCutoffs');
        if (targetView) this.render(targetView);
      }
    };

    if (rankInput) {
      // Restrict input strictly to numbers (0-9)
      rankInput.addEventListener('input', (e) => {
        const clean = e.target.value.replace(/[^0-9]/g, '');
        if (e.target.value !== clean) {
          e.target.value = clean;
        }
      });
      rankInput.addEventListener('blur', applyRankFilter);
      rankInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') applyRankFilter();
      });
    }

    if (submitRankBtn) {
      submitRankBtn.addEventListener('click', applyRankFilter);
    }

    if (this.state.selectedStateVal === 'all') {
      const stateSearchInput = container.querySelector('#sidebarStateSearch');
      if (stateSearchInput) {
        stateSearchInput.addEventListener('input', (e) => {
          if (this.state.stateSearchTimeout) clearTimeout(this.state.stateSearchTimeout);
          this.state.stateSearchTimeout = setTimeout(() => {
            this.state.stateSearchQuery = e.target.value;
            this.renderSidebarFilters(containerId);
            const input = document.getElementById('sidebarStateSearch');
            if (input) {
              input.focus();
              input.setSelectionRange(input.value.length, input.value.length);
            }
          }, 150);
        });
      }

      container.querySelectorAll('.sidebar-state-cb').forEach(cb => {
        cb.addEventListener('change', () => {
          const checked = Array.from(container.querySelectorAll('.sidebar-state-cb:checked')).map(el => el.value);
          this.state.selectedStates = checked;
          const targetView = document.getElementById('viewCutoffs');
          if (targetView) this.render(targetView);
        });
      });

      const clearStateBtn = container.querySelector('#clearSidebarStateFilterBtn');
      if (clearStateBtn) {
        clearStateBtn.addEventListener('click', () => {
          this.state.selectedStates = [];
          this.state.stateSearchQuery = '';
          this.renderSidebarFilters(containerId);
          const targetView = document.getElementById('viewCutoffs');
          if (targetView) this.render(targetView);
        });
      }
    }

    container.querySelectorAll('.sidebar-category-cb').forEach(cb => {
      cb.addEventListener('change', () => {
        const checked = Array.from(container.querySelectorAll('.sidebar-category-cb:checked')).map(el => el.value);
        this.state.selectedCategories = checked;
        const targetView = document.getElementById('viewCutoffs');
        if (targetView) this.render(targetView);
      });
    });

    const clearCatBtn = container.querySelector('#clearCategoryFilterBtn');
    if (clearCatBtn) {
      clearCatBtn.addEventListener('click', () => {
        this.state.selectedCategories = [];
        this.renderSidebarFilters(containerId);
        const targetView = document.getElementById('viewCutoffs');
        if (targetView) this.render(targetView);
      });
    }

    container.querySelectorAll('.sidebar-quota-cb').forEach(cb => {
      cb.addEventListener('change', () => {
        const checked = Array.from(container.querySelectorAll('.sidebar-quota-cb:checked')).map(el => el.value);
        this.state.selectedQuotas = checked;
        const targetView = document.getElementById('viewCutoffs');
        if (targetView) this.render(targetView);
      });
    });

    const clearQuotaBtn = container.querySelector('#clearQuotaFilterBtn');
    if (clearQuotaBtn) {
      clearQuotaBtn.addEventListener('click', () => {
        this.state.selectedQuotas = [];
        this.renderSidebarFilters(containerId);
        const targetView = document.getElementById('viewCutoffs');
        if (targetView) this.render(targetView);
      });
    }

    const resetBtn = container.querySelector('#sidebarResetCutoffFiltersBtn');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        this.state.userRank = '';
        this.state.searchQuery = '';
        this.state.selectedCategories = [];
        this.state.selectedQuotas = [];
        this.state.selectedStates = [];
        this.state.stateSearchQuery = '';
        this.state.selectedCategory = 'ALL';
        this.state.selectedQuota = 'ALL';
        this.state.selectedChance = 'ALL';
        this.renderSidebarFilters(containerId);
        const targetView = document.getElementById('viewCutoffs');
        if (targetView) this.render(targetView);
      });
    }

    const closeBtn = container.querySelector('#closeSidebarBtn');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        document.getElementById('filterSidebar').classList.remove('active');
        document.getElementById('sidebarBackdrop').classList.remove('active');
      });
    }
  },

  render(container) {
    const filteredColleges = this.getFilteredColleges();
    const totalColleges = filteredColleges.length;
    const userRankNum = parseInt(this.state.userRank, 10);
    const hasRank = !isNaN(userRankNum) && userRankNum > 0;

    container.innerHTML = `
      <div class="cutoff-explorer-wrapper">
        
        <!-- Compact Mobile-Optimized Control Card (No manual fullscreen button per spec) -->
        <div class="cutoff-controls-card card-glass">
          
          <!-- Line 1: Header Title & Data Source Badge -->
          <div class="cutoff-controls-top-row">
            <h3 class="cutoff-title-heading">
              <i data-lucide="target" class="icon-accent-blue"></i>
              <span>MCC UG Cutoff Explorer & Predictor</span>
            </h3>
            <div class="cutoff-source-badge">
              <i data-lucide="calendar-check" class="icon-xs"></i>
              <span>MCC MBBS Allotment (Rounds 1–3)</span>
            </div>
          </div>

          <!-- Line 2: Responsive Inputs Grid (Rank Input & Top Search Input) -->
          <div class="top-inputs-grid">
            <!-- Rank Input (Digits restricted) -->
            <div class="top-input-relative">
              <i data-lucide="award" class="top-rank-icon" aria-hidden="true"></i>
              <input type="text" id="cutoffTopRankInput" placeholder="Enter NEET Rank (e.g. 10000)" value="${this.state.userRank}" inputmode="numeric" class="top-input-field" aria-label="Enter NEET All India Rank">
            </div>

            <!-- College Search Bar (Words restricted) -->
            <div class="top-input-relative">
              <i data-lucide="search" class="top-search-icon" aria-hidden="true"></i>
              <input type="text" id="cutoffTopSearchInput" placeholder="Search college, city, state..." value="${this.state.searchQuery}" class="top-input-field top-search-field" aria-label="Search college, city, or state cutoffs">
            </div>
          </div>

          <!-- Line 3: Filter Dropdowns Grid (Category, Quota, Chance Predictor) -->
          <div class="top-dropdowns-grid">
            
            <!-- Category Dropdown -->
            <div class="dropdown-filter-group">
              <label class="dropdown-label" for="cutoffCategorySelect">
                <i data-lucide="users" class="icon-xs"></i>
                <span>Category:</span>
              </label>
              <select id="cutoffCategorySelect" class="cutoff-filter-select">
                <option value="ALL" ${this.state.selectedCategory === 'ALL' ? 'selected' : ''}>All Categories</option>
                ${this.state.categoriesList.map(cat => `
                  <option value="${cat}" ${this.state.selectedCategory === cat ? 'selected' : ''}>${cat}</option>
                `).join('')}
              </select>
            </div>

            <!-- Quota Dropdown -->
            <div class="dropdown-filter-group">
              <label class="dropdown-label" for="cutoffQuotaSelect">
                <i data-lucide="layers" class="icon-xs"></i>
                <span>Quota:</span>
              </label>
              <select id="cutoffQuotaSelect" class="cutoff-filter-select">
                <option value="ALL" ${this.state.selectedQuota === 'ALL' ? 'selected' : ''}>All Quotas</option>
                ${this.state.quotasList.map(q => `
                  <option value="${q}" ${this.state.selectedQuota === q ? 'selected' : ''}>${q}</option>
                `).join('')}
              </select>
            </div>

            <!-- Chance Predictor Dropdown -->
            <div class="dropdown-filter-group">
              <label class="dropdown-label" for="cutoffChanceSelect">
                <i data-lucide="sparkles" class="icon-xs"></i>
                <span>Chance Predictor:</span>
              </label>
              <select id="cutoffChanceSelect" class="cutoff-filter-select">
                <option value="ALL" ${this.state.selectedChance === 'ALL' ? 'selected' : ''}>All Chances</option>
                <option value="HIGH" ${this.state.selectedChance === 'HIGH' ? 'selected' : ''}>High Chance</option>
                <option value="BORDERLINE" ${this.state.selectedChance === 'BORDERLINE' ? 'selected' : ''}>Borderline</option>
                <option value="LOW" ${this.state.selectedChance === 'LOW' ? 'selected' : ''}>Low Chance</option>
              </select>
            </div>

          </div>

          <!-- Line 4: Toolbar (Collapse All & Master College Count) -->
          <div class="top-toolbar-row">
            <div class="top-toolbar-actions">
              <!-- Collapse All Button -->
              <button id="collapseAllRowsBtn" class="btn-action-standard">
                <i data-lucide="fold-vertical" class="icon-xs"></i>
                <span>Collapse All</span>
              </button>
            </div>

            <!-- Master College Count Badge -->
            <span class="badge badge-govt badge-master-count">
              Showing ${totalColleges.toLocaleString()} Colleges
            </span>
          </div>

        </div>

        <!-- Full Unpaginated Cutoff Table View -->
        <div class="table-container card-glass cutoff-table-wrapper">
          <table id="mccCutoffTable" class="cutoff-table">
            <thead>
              <tr>
                <th class="th-expand-col"></th>
                <th>College Name</th>
                <th class="col-location">State & City</th>
                <th class="col-type">Type</th>
                <th class="col-course">Course</th>
                ${hasRank ? '<th class="text-center col-predictor">Predictor</th>' : ''}
                <th class="col-quota">Quota</th>
                <th class="col-category">Category</th>
                <th class="rank-col" title="Round 1 Opening Rank">R1 Op</th>
                <th class="rank-col" title="Round 1 Closing Rank">R1 Cl</th>
                <th class="rank-col" title="Round 2 Opening Rank">R2 Op</th>
                <th class="rank-col" title="Round 2 Closing Rank">R2 Cl</th>
                <th class="rank-col" title="Round 3 Opening Rank">R3 Op</th>
                <th class="rank-col" title="Round 3 Closing Rank">R3 Cl</th>
                <th class="rank-col" title="Final Opening Rank">Fin Op</th>
                <th class="rank-col th-fin-cl" title="Final Closing Rank">Fin Cl</th>
              </tr>
            </thead>
            <tbody>
              ${filteredColleges.length === 0 ? `
                <tr>
                  <td colspan="${hasRank ? 16 : 15}" class="placeholder-text placeholder-empty-table">
                    No UG colleges found matching your active search/predictor filters.
                  </td>
                </tr>
              ` : filteredColleges.map(group => {
                const isExpanded = this.state.expandedCollegeIds.has(group.college_id);
                const typeBadgeClass = group.college_type === 'Government' ? 'badge-govt' : (group.college_type === 'Deemed' ? 'badge-deemed' : 'badge-private');
                
                const categoriesCount = group.childRows.length;

                return `
                  <!-- Group Header Row -->
                  <tr class="group-header-row table-row-group-header" data-college-group-id="${group.college_id}">
                    <!-- Column 1: Dedicated Expand/Collapse Arrow ONLY -->
                    <td class="text-center th-expand-col">
                      <button class="group-expand-btn" data-toggle-college="${group.college_id}" aria-label="Toggle college dropdown">
                        <i data-lucide="chevron-right" class="group-chevron group-chevron-${group.college_id} ${isExpanded ? 'is-rotated' : ''}"></i>
                      </button>
                    </td>
                    
                    <!-- Column 2: College Name & Left-Aligned Chips (Code Removed) -->
                    <td>
                      <div>
                        <button class="college-details-link" data-college-id="${group.college_id}">
                          ${group.college_name}
                        </button>
                      </div>
                      <div class="group-summary-chips">
                        ${group.mcc_status === 'Matched' ? `<span class="group-chip chip-text-xs">${categoriesCount} cutoff${categoriesCount > 1 ? 's' : ''}</span>` : ''}
                        ${group.mcc_status === 'New' ? `<span class="group-chip chip-new-colleges">New</span>` : ''}
                        ${group.mcc_status === 'Non AIQ' ? `<span class="group-chip chip-non-aiq">State Quota Only</span>` : ''}
                      </div>
                    </td>

                    <!-- Column 3: State & City -->
                    <td>
                      <span class="font-medium">${group.state}</span>
                      ${group.city ? `<br><small class="cell-subtle-sm">${group.city}</small>` : ''}
                    </td>

                    <!-- Column 4: Type -->
                    <td><span class="badge ${typeBadgeClass}">${group.college_type}</span></td>

                    <!-- Column 5: Course -->
                    <td><span class="badge badge-govt cell-course-badge">MBBS</span></td>

                    <!-- Column 6: Predictor (if active) -->
                    ${hasRank ? '<td class="text-center opacity-50">—</td>' : ''}

                    <!-- Column 7: Quota Summary -->
                    <td><small class="opacity-70">Summary</small></td>

                    <!-- Column 8: Category Summary -->
                    <td><small class="opacity-70">Summary</small></td>

                    <!-- Columns 9..14: Intermediate Round Summary Ranks (Intentionally Dash) -->
                    <td class="text-right cell-dash-disabled">-</td>
                    <td class="text-right cell-dash-disabled">-</td>
                    <td class="text-right cell-dash-disabled">-</td>
                    <td class="text-right cell-dash-disabled">-</td>
                    <td class="text-right cell-dash-disabled">-</td>
                    <td class="text-right cell-dash-disabled">-</td>

                    <!-- Column 15: Final OP Summary -->
                    <td class="text-right">
                      <strong class="cell-final-op">
                        ${group.min_final_open_str}
                      </strong>
                    </td>

                    <!-- Column 16: Final CL Summary with End Padding -->
                    <td class="text-right cell-final-cl">
                      <strong class="cell-final-cl-val">
                        ${group.max_final_close_str}
                      </strong>
                    </td>
                  </tr>

                  <!-- Child Rows Container (Mapped precisely to columns 1 to 16) -->
                  ${group.childRows.length > 0 ? group.childRows.map(row => `
                    <tr class="child-row-${group.college_id} table-row-child ${isExpanded ? '' : 'is-hidden'}">
                      <!-- Col 1: Indent Tree Symbol under Expand Button -->
                      <td class="th-expand-col child-indent-symbol-cell"><span class="indent-tree-char">└</span></td>

                      <!-- Col 2: College Name Column -->
                      <td>
                        <button class="college-details-link" data-college-id="${group.college_id}">
                          ${group.college_name}
                        </button>
                      </td>

                      <!-- Col 3: State & City -->
                      <td class="opacity-75 text-sm">${group.state}</td>

                      <!-- Col 4: Type -->
                      <td><small class="opacity-75 text-xs">${group.college_type}</small></td>

                      <!-- Col 5: Course -->
                      <td><strong class="text-blue text-sm">${row.course}</strong></td>

                      <!-- Col 6: Predictor Badge (if active) -->
                      ${hasRank ? `<td class="text-center">${row.predictor_badge || '—'}</td>` : ''}

                      <!-- Col 7: Quota -->
                      <td><small class="opacity-85 text-xs">${row.quota}</small></td>

                      <!-- Col 8: Category Column -->
                      <td><span class="badge badge-code badge-cat-sm">${row.category}</span></td>

                      <!-- Col 9..16: R1 Op, R1 Cl, R2 Op, R2 Cl, R3 Op, R3 Cl, Fin Op, Fin Cl -->
                      <td class="text-right opacity-85 text-sm">${row.r1_open_str}</td>
                      <td class="text-right opacity-85 text-sm">${row.r1_close_str}</td>
                      <td class="text-right opacity-85 text-sm">${row.r2_open_str}</td>
                      <td class="text-right opacity-85 text-sm">${row.r2_close_str}</td>
                      <td class="text-right opacity-85 text-sm">${row.r3_open_str}</td>
                      <td class="text-right opacity-85 text-sm">${row.r3_close_str}</td>
                      <td class="text-right text-green text-sm">${row.final_open_str}</td>
                      <td class="text-right cell-final-cl"><strong class="text-blue text-sm-md">${row.final_close_str}</strong></td>
                    </tr>
                  `).join('') : `
                    <tr class="child-row-${group.college_id} table-row-child table-row-child-warning ${isExpanded ? '' : 'is-hidden'}">
                      <td class="th-expand-col"></td>
                      <td colspan="${hasRank ? 15 : 14}" class="pad-3-4">
                        ${group.mcc_status === 'New' ? `
                          <div class="info-box-row text-warning">
                            <i data-lucide="info" class="icon-md"></i>
                            <span><strong>New MCC College:</strong> Participates in MCC counselling but lacks historical 2025 cutoff data.</span>
                          </div>
                        ` : `
                          <div class="info-box-row text-muted">
                            <i data-lucide="shield-off" class="icon-md"></i>
                            <span><strong>Non AIQ College:</strong> Admissions conducted strictly through State Quota Counselling.</span>
                          </div>
                        `}
                      </td>
                    </tr>
                  `}
                `;
              }).join('')}
            </tbody>
          </table>
        </div>

        <!-- Back-to-Top Control Footer (Horizontally and Vertically Centered using Table Explorer implementation) -->
        <div class="table-footer-actions">
          <button class="btn-go-to-top" id="goToTopCutoffsBtn" title="Back to Top">
            <i data-lucide="arrow-up"></i> Back to Top
          </button>
        </div>

      </div>
    `;

    this.attachEvents(container);
    if (window.lucide) window.lucide.createIcons();
  },

  attachEvents(container) {
    // 1. Top Search Input with Character Restriction
    const topSearch = container.querySelector('#cutoffTopSearchInput');

    const applySearchFilter = () => {
      if (!topSearch) return;
      const val = topSearch.value.trim();
      if (this.state.searchQuery !== val) {
        this.state.searchQuery = val;
        this.render(container);
      }
    };

    if (topSearch) {
      // Restrict input to valid words/letters/numbers/spaces/hyphens/ampersands
      topSearch.addEventListener('input', (e) => {
        const clean = e.target.value.replace(/[^a-zA-Z0-9\s,\-&]/g, '');
        if (e.target.value !== clean) {
          e.target.value = clean;
        }
      });
      // Execute search ONLY on blur or Enter key press
      topSearch.addEventListener('blur', applySearchFilter);
      topSearch.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') applySearchFilter();
      });
    }

    // 2. Top Rank Input with Digits-Only Restriction
    const topRankInput = container.querySelector('#cutoffTopRankInput');

    const applyTopRankFilter = () => {
      if (!topRankInput) return;
      const val = topRankInput.value.trim();
      if (this.state.userRank !== val) {
        this.state.userRank = val;
        this.render(container);
      }
    };

    if (topRankInput) {
      // Restrict input strictly to numbers (0-9)
      topRankInput.addEventListener('input', (e) => {
        const clean = e.target.value.replace(/[^0-9]/g, '');
        if (e.target.value !== clean) {
          e.target.value = clean;
        }
      });
      // Execute search ONLY on blur or Enter key press
      topRankInput.addEventListener('blur', applyTopRankFilter);
      topRankInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') applyTopRankFilter();
      });
    }

    // 3. Dropdowns: Category, Quota, Chance Predictor
    const categorySelect = container.querySelector('#cutoffCategorySelect');
    if (categorySelect) {
      categorySelect.addEventListener('change', (e) => {
        this.state.selectedCategory = e.target.value;
        this.render(container);
      });
    }

    const quotaSelect = container.querySelector('#cutoffQuotaSelect');
    if (quotaSelect) {
      quotaSelect.addEventListener('change', (e) => {
        this.state.selectedQuota = e.target.value;
        this.render(container);
      });
    }

    const chanceSelect = container.querySelector('#cutoffChanceSelect');
    if (chanceSelect) {
      chanceSelect.addEventListener('change', (e) => {
        this.state.selectedChance = e.target.value;
        this.render(container);
      });
    }

    // 4. Dedicated Chevron Expand/Collapse Arrow ONLY toggles child rows
    container.querySelectorAll('.group-expand-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const colId = btn.getAttribute('data-toggle-college');
        if (!colId) return;

        const isCurrentlyExpanded = this.state.expandedCollegeIds.has(colId);
        const childRows = container.querySelectorAll(`.child-row-${colId}`);
        const chevronIcon = container.querySelector(`.group-chevron-${colId}`);

        if (isCurrentlyExpanded) {
          this.state.expandedCollegeIds.delete(colId);
          childRows.forEach(r => r.classList.add('is-hidden'));
          if (chevronIcon) chevronIcon.classList.remove('is-rotated');
        } else {
          this.state.expandedCollegeIds.add(colId);
          childRows.forEach(r => r.classList.remove('is-hidden'));
          if (chevronIcon) chevronIcon.classList.add('is-rotated');
        }
      });
    });

    // 5. Clickable College Name (.college-details-link) triggers details modal
    container.querySelectorAll('.college-details-link').forEach(el => {
      el.addEventListener('click', (e) => {
        e.stopPropagation();
        const cid = el.getAttribute('data-college-id');
        if (cid && window.showCollegeDetailsModal) {
          window.showCollegeDetailsModal(cid);
        }
      });
    });

    // 6. Collapse All Rows Button
    const collapseAllBtn = container.querySelector('#collapseAllRowsBtn');
    if (collapseAllBtn) {
      collapseAllBtn.addEventListener('click', () => {
        this.state.expandedCollegeIds.clear();
        this.render(container);
      });
    }

    // 7. Back to Top Button
    const goToTopCutoffsBtn = container.querySelector('#goToTopCutoffsBtn');
    if (goToTopCutoffsBtn) {
      goToTopCutoffsBtn.addEventListener('click', () => {
        window.scrollTo({
          top: 0,
          behavior: 'smooth'
        });
      });
    }

    // 9. Scroll Indicator Affordance Check
    const cutoffTableWrapper = container.querySelector('.cutoff-table-wrapper');
    if (cutoffTableWrapper && window.initScrollAffordance) {
      window.initScrollAffordance(cutoffTableWrapper);
    }
  },

  exportToCsv() {
    const colleges = this.getFilteredColleges();
    if (!colleges || colleges.length === 0) {
      alert("No cutoff records to export.");
      return;
    }

    const headers = [
      "College Name", "Course", "State", "City", "College Type", "College Code",
      "Quota", "Category", 
      "R1 Opening Rank", "R1 Closing Rank", 
      "R2 Opening Rank", "R2 Closing Rank", 
      "R3 Opening Rank", "R3 Closing Rank", 
      "Final Opening Rank", "Final Closing Rank"
    ];

    const rows = [];
    colleges.forEach(col => {
      if (col.childRows.length > 0) {
        col.childRows.forEach(r => {
          rows.push([
            `"${(col.college_name || '').replace(/"/g, '""')}"`,
            `"${(r.course || 'MBBS').replace(/"/g, '""')}"`,
            `"${(col.state || '').replace(/"/g, '""')}"`,
            `"${(col.city || '').replace(/"/g, '""')}"`,
            `"${(col.college_type || '').replace(/"/g, '""')}"`,
            `"${(col.college_code || '').replace(/"/g, '""')}"`,
            `"${(r.quota || '').replace(/"/g, '""')}"`,
            `"${(r.category || '').replace(/"/g, '""')}"`,
            r.r1_open_str,
            r.r1_close_str,
            r.r2_open_str,
            r.r2_close_str,
            r.r3_open_str,
            r.r3_close_str,
            r.final_open_str,
            r.final_close_str
          ]);
        });
      } else {
        rows.push([
          `"${(col.college_name || '').replace(/"/g, '""')}"`,
          `"MBBS"`,
          `"${(col.state || '').replace(/"/g, '""')}"`,
          `"${(col.city || '').replace(/"/g, '""')}"`,
          `"${(col.college_type || '').replace(/"/g, '""')}"`,
          `"${(col.college_code || '').replace(/"/g, '""')}"`,
          `"${(col.mcc_status || '').replace(/"/g, '""')}"`,
          `"-"`, `"-"`, `"-"`, `"-"`, `"-"`, `"-"`, `"-"`, `"-"`, `"-"`, `"-"`
        ]);
      }
    });

    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `mcc_ug_cutoffs_predictor_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};
