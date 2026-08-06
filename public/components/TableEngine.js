// Unified NexDoc Data Table Engine (TableEngine.js)
// Serves layout, DOM rendering, live filtering, WCAG 2.1 accessibility, sticky headers, and CSV exports.

export class TableEngine {
  constructor(options = {}) {
    this.schema = options.schema || {};
    this.containerId = options.containerId || null;
    this.dataUrl = options.dataUrl || null;
    this.rawData = options.rawData || [];
    this.onStateChange = options.onStateChange || null;

    this.state = {
      data: [],
      isLoading: true,
      searchQuery: '',
      selectedCategory: 'ALL',
      selectedQuota: 'ALL',
      selectedChance: 'ALL',
      selectedCategories: [],
      selectedQuotas: [],
      selectedState: 'ALL',
      selectedManagement: 'ALL',
      selectedCourse: 'ALL',
      userRank: null,
      expandedRowIds: new Set(),
      sortColumn: this.schema.defaultSortColumn || 'college_name',
      sortDirection: this.schema.defaultSortDirection || 'asc',
      categoriesList: [],
      quotasList: [],
      statesList: [],
      coursesList: []
    };
  }

  async init() {
    if (this.dataUrl) {
      try {
        const response = await fetch(this.dataUrl);
        const json = await response.json();
        this.state.data = Array.isArray(json) ? json : (json.data || []);
      } catch (err) {
        console.error(`[TableEngine] Failed to load data from ${this.dataUrl}:`, err);
        this.state.data = this.rawData || [];
      }
    } else {
      this.state.data = Array.isArray(this.rawData) ? this.rawData : [];
    }

    this.state.isLoading = false;
    this.extractFilterLists();
    this.render();
  }

  setData(data) {
    this.state.data = Array.isArray(data) ? data : [];
    this.extractFilterLists();
    this.render();
  }

  extractFilterLists() {
    const categories = new Set();
    const quotas = new Set();
    const states = new Set();
    const courses = new Set();

    this.state.data.forEach(item => {
      if (item.state) states.add(item.state);
      if (item.course) courses.add(item.course);

      // Support nested cutoffs raw lists
      const rawCutoffs = item.aiq_cutoffs_raw || item.childRows || [];
      rawCutoffs.forEach(c => {
        if (c.category) categories.add(c.category);
        if (c.quota) quotas.add(c.quota);
        if (c.quota_type) quotas.add(c.quota_type);
        if (c.course) courses.add(c.course);
      });
    });

    this.state.categoriesList = Array.from(categories).sort();
    this.state.quotasList = Array.from(quotas).sort();
    this.state.statesList = Array.from(states).sort();
    this.state.coursesList = Array.from(courses).sort();
  }

  // Presentation-layer Allied Course Exclusion Rule
  isAlliedCourse(courseName = '') {
    const c = String(courseName).toLowerCase();
    return c.includes('nursing') || c.includes('bds') || c.includes('dental') || c.includes('ayush') || c.includes('bams') || c.includes('bhms');
  }

  // Active filter evaluation
  isFilterActive() {
    return (this.state.selectedCategory !== 'ALL') ||
           (this.state.selectedQuota !== 'ALL') ||
           (this.state.selectedChance !== 'ALL') ||
           (this.state.selectedState !== 'ALL') ||
           (this.state.selectedManagement !== 'ALL') ||
           (this.state.selectedCourse !== 'ALL') ||
           (this.state.selectedCategories && this.state.selectedCategories.length > 0) ||
           (this.state.selectedQuotas && this.state.selectedQuotas.length > 0);
  }

  getFilteredData() {
    if (this.state.isLoading || !this.state.data) return [];

    let filtered = [];

    this.state.data.forEach(item => {
      // 1. Presentation-layer Allied Course Filter
      if (this.isAlliedCourse(item.course)) return;

      // 2. Search Query Matching
      if (this.state.searchQuery) {
        const query = this.state.searchQuery.toLowerCase().trim();
        const nameMatch = (item.college_name || item.name || '').toLowerCase().includes(query);
        const cityMatch = (item.city || '').toLowerCase().includes(query);
        const stateMatch = (item.state || '').toLowerCase().includes(query);
        const codeMatch = (item.college_code || '').toLowerCase().includes(query);
        
        if (!nameMatch && !cityMatch && !stateMatch && !codeMatch) {
          return;
        }
      }

      // 3. High-level Item Attributes
      if (this.state.selectedState !== 'ALL' && item.state !== this.state.selectedState) return;
      if (this.state.selectedManagement !== 'ALL' && item.college_type !== this.state.selectedManagement && item.management !== this.state.selectedManagement) return;
      if (this.state.selectedCourse !== 'ALL' && item.course !== this.state.selectedCourse) return;

      // 4. Nested Cutoff Child Rows Filtering (if applicable)
      let processedChildRows = [];
      const rawCutoffs = item.aiq_cutoffs_raw || item.childRows || [];

      if (rawCutoffs.length > 0 && this.schema.processChildRows) {
        processedChildRows = this.schema.processChildRows(rawCutoffs, this.state, this);
        if (this.isFilterActive() && processedChildRows.length === 0) {
          return; // Skip parent item if active filters leave 0 matching child rows
        }
      }

      const itemCopy = { ...item };
      if (processedChildRows.length > 0) {
        itemCopy.childRows = processedChildRows;
      }
      filtered.push(itemCopy);
    });

    // 5. Enforce Strict A-to-Z Alphabetical Sorting by default
    const sortKey = this.state.sortColumn || 'college_name';
    const isAsc = this.state.sortDirection === 'asc';

    filtered.sort((a, b) => {
      const valA = a[sortKey] || '';
      const valB = b[sortKey] || '';
      if (typeof valA === 'string' && typeof valB === 'string') {
        return isAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }
      return isAsc ? (valA - valB) : (valB - valA);
    });

    return filtered;
  }

  toggleExpandRow(rowId) {
    if (this.state.expandedRowIds.has(rowId)) {
      this.state.expandedRowIds.delete(rowId);
    } else {
      this.state.expandedRowIds.add(rowId);
    }
    this.render();
  }

  expandAllRows(filteredData) {
    filteredData.forEach(item => {
      const id = item.college_id || item.id;
      if (id) this.state.expandedRowIds.add(id);
    });
    this.render();
  }

  collapseAllRows() {
    this.state.expandedRowIds.clear();
    this.render();
  }

  exportCSV() {
    const filteredData = this.getFilteredData();
    if (filteredData.length === 0) return;

    const columns = this.schema.columns || [];
    const headers = columns.map(c => c.label).filter(Boolean);

    let csvContent = "data:text/csv;charset=utf-8," + headers.join(",") + "\n";

    filteredData.forEach(row => {
      const rowVals = columns.map(col => {
        let val = col.getValue ? col.getValue(row, this.state) : row[col.field];
        val = String(val !== undefined && val !== null ? val : '').replace(/"/g, '""');
        return `"${val}"`;
      });
      csvContent += rowVals.join(",") + "\n";
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `${this.schema.tableName || 'nexdoc_export'}_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  render() {
    const container = document.getElementById(this.containerId);
    if (!container) return;

    if (this.state.isLoading) {
      container.innerHTML = `
        <div class="card-glass p-8 text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-4"></div>
          <p class="text-muted">Loading table data...</p>
        </div>
      `;
      return;
    }

    const filteredData = this.getFilteredData();

    // Render HTML template via schema or default table renderer
    if (this.schema.renderTemplate) {
      container.innerHTML = this.schema.renderTemplate(filteredData, this.state, this);
    } else {
      container.innerHTML = this.renderDefaultTable(filteredData);
    }

    if (window.lucide) window.lucide.createIcons();
    this.bindEvents(container, filteredData);

    if (this.onStateChange) {
      this.onStateChange(this.state, filteredData);
    }
  }

  renderDefaultTable(filteredData) {
    const columns = this.schema.columns || [];

    return `
      <div class="cutoff-table-scroll">
        <table class="cutoff-table">
          <thead>
            <tr>
              ${columns.map(col => `
                <th class="${col.className || ''}" ${col.sortable ? `data-sort-col="${col.field}" style="cursor:pointer;"` : ''}>
                  ${col.label}
                  ${this.state.sortColumn === col.field ? (this.state.sortDirection === 'asc' ? ' ↑' : ' ↓') : ''}
                </th>
              `).join('')}
            </tr>
          </thead>
          <tbody>
            ${filteredData.length === 0 ? `
              <tr>
                <td colspan="${columns.length}" class="text-center py-8 text-muted">
                  No matching records found.
                </td>
              </tr>
            ` : filteredData.map(row => {
              const isExpanded = this.state.expandedRowIds.has(row.college_id || row.id);
              const rowId = row.college_id || row.id;

              let rowHtml = `
                <tr class="table-row-group-header" data-row-id="${rowId}">
                  ${columns.map(col => `
                    <td class="${col.className || ''}">
                      ${col.render ? col.render(row, isExpanded, this.state, this) : (row[col.field] || '')}
                    </td>
                  `).join('')}
                </tr>
              `;

              if (isExpanded && this.schema.renderExpandedRow) {
                rowHtml += this.schema.renderExpandedRow(row, this.state, this);
              }
              return rowHtml;
            }).join('')}
          </tbody>
        </table>
      </div>
    `;
  }

  bindEvents(container, filteredData) {
    // Bind search input
    const searchInput = container.querySelector('#collegeSearchInput') || container.querySelector('.input-search-table');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.state.searchQuery = e.target.value;
        this.render();
      });
    }

    // Bind Expand/Collapse All
    const btnExpand = container.querySelector('#btnExpandAllCutoffs') || container.querySelector('#expandAllRowsBtn');
    if (btnExpand) {
      btnExpand.addEventListener('click', () => this.expandAllRows(filteredData));
    }

    const btnCollapse = container.querySelector('#btnCollapseAllCutoffs') || container.querySelector('#collapseAllRowsBtn');
    if (btnCollapse) {
      btnCollapse.addEventListener('click', () => this.collapseAllRows());
    }

    // Bind Export CSV
    const btnExport = container.querySelector('#exportCutoffCsvBtn') || container.querySelector('#exportCsvBtn');
    if (btnExport) {
      btnExport.addEventListener('click', () => this.exportCSV());
    }

    // Bind row chevron toggles
    container.querySelectorAll('[data-toggle-college]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.currentTarget.getAttribute('data-toggle-college');
        this.toggleExpandRow(id);
      });
    });

    // Custom schema bindings
    if (this.schema.bindCustomEvents) {
      this.schema.bindCustomEvents(container, this, filteredData);
    }
  }
}
