// SearchFilters Component for NexDoc

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

export const SearchFilters = {
  render(containerId, activeLevel, summary, activeFilters, selectedState, onChange) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Reset list of items
    const quotas = summary.quotas || [];
    const courses = summary.courses || [];
    const types = summary.types || [];
    const states = summary.states || [];

    let html = `
      <div class="sidebar-mobile-header">
        <h3>Filters</h3>
        <button class="btn-close-sidebar" id="closeSidebarBtn">
          <i data-lucide="x"></i>
        </button>
      </div>
      <div class="filter-group">
        <h4>Search Database</h4>
        <div class="search-box-container">
          <i data-lucide="search"></i>
          <input type="text" id="sidebarSearch" placeholder="Search college name..." value="${activeFilters.query || ''}">
        </div>
      </div>
    `;

    // 1. Filter by State (Only rendered if browsing 'All States' at once)
    if (selectedState === 'all') {
      html += `
        <div class="filter-group">
          <h4>Filter by State</h4>
          <div class="search-box-container">
            <i data-lucide="filter"></i>
            <input type="text" id="stateFilterSearch" placeholder="Filter states..." value="${activeFilters.stateQuery || ''}">
          </div>
          <div class="filter-options" style="max-height: 150px; overflow-y: auto; margin-top: 0.5rem; padding-right: 0.25rem;">
      `;

      const filteredStates = states.filter(s =>
        !activeFilters.stateQuery || s.toLowerCase().includes(activeFilters.stateQuery.toLowerCase())
      );

      if (filteredStates.length === 0) {
        html += `<span class="placeholder-text" style="font-size: 0.8rem; padding: 0.5rem 0;">No states match</span>`;
      } else {
        filteredStates.forEach(state => {
          const isChecked = activeFilters.states.includes(state) ? 'checked' : '';
          html += `
            <label class="checkbox-label">
              <input type="checkbox" class="filter-state-checkbox" value="${state}" ${isChecked}>
              <div class="checkbox-custom"><i data-lucide="check"></i></div>
              <span style="font-size: 0.85rem;">${state}</span>
            </label>
          `;
        });
      }

      html += `
          </div>
        </div>
      `;
    }

    html += `
      <div class="filter-group">
        <h4>College Type</h4>
        <div class="filter-options">
    `;

    types.forEach(type => {
      const isChecked = activeFilters.types.includes(type) ? 'checked' : '';
      html += `
        <label class="checkbox-label">
          <input type="checkbox" class="filter-type-checkbox" value="${type}" ${isChecked}>
          <div class="checkbox-custom"><i data-lucide="check"></i></div>
          <span>${type}</span>
        </label>
      `;
    });

    html += `
        </div>
      </div>

      <div class="filter-group">
        <h4>Counseling Route</h4>
        <div class="radio-options">
          <label class="radio-label">
            <input type="radio" name="counselingRoute" value="all" ${activeFilters.counselingRoute === 'all' ? 'checked' : ''}>
            <div class="radio-custom"></div>
            <span>All Routes</span>
          </label>
          <label class="radio-label">
            <input type="radio" name="counselingRoute" value="MCC" ${activeFilters.counselingRoute === 'MCC' ? 'checked' : ''}>
            <div class="radio-custom"></div>
            <span>MCC (Central)</span>
          </label>
          <label class="radio-label">
            <input type="radio" name="counselingRoute" value="STATE" ${activeFilters.counselingRoute === 'STATE' ? 'checked' : ''}>
            <div class="radio-custom"></div>
            <span>State Authority</span>
          </label>
        </div>
      </div>

      <div class="filter-group">
        <h4>Quota Categories</h4>
        <div class="filter-options">
    `;

    quotas.forEach(quota => {
      const isChecked = activeFilters.quotas.includes(quota) ? 'checked' : '';
      html += `
        <label class="checkbox-label">
          <input type="checkbox" class="filter-quota-checkbox" value="${quota}" ${isChecked}>
          <div class="checkbox-custom"><i data-lucide="check"></i></div>
          <span>${quota}</span>
        </label>
      `;
    });

    html += `
        </div>
      </div>

      <div class="filter-group">
        <h4>Specialization / Course</h4>
        <div class="search-box-container">
          <i data-lucide="filter"></i>
          <input type="text" id="courseSearch" placeholder="Filter courses..." value="${activeFilters.courseQuery || ''}">
        </div>
        <div class="filter-options" style="max-height: 150px; overflow-y: auto; margin-top: 0.5rem; padding-right: 0.25rem;">
    `;

    const filteredCourses = courses.filter(c => 
      !activeFilters.courseQuery || c.toLowerCase().includes(activeFilters.courseQuery.toLowerCase())
    );

    if (filteredCourses.length === 0) {
      html += `<span class="placeholder-text" style="font-size: 0.8rem; padding: 0.5rem 0;">No courses match</span>`;
    } else {
      filteredCourses.forEach(course => {
        const isChecked = activeFilters.courses.includes(course) ? 'checked' : '';
        html += `
          <label class="checkbox-label">
            <input type="checkbox" class="filter-course-checkbox" value="${course}" ${isChecked}>
            <div class="checkbox-custom"><i data-lucide="check"></i></div>
            <span style="font-size: 0.85rem;">${course}</span>
          </label>
        `;
      });
    }

    html += `
        </div>
      </div>

      <button class="btn-reset-filters" id="resetFiltersBtn">
        <i data-lucide="refresh-cw"></i> Reset All Filters
      </button>
    `;

    container.innerHTML = html;
    
    // Initialize lucide icons inside sidebar
    if (window.lucide) {
      window.lucide.createIcons();
    }

    // Attach Event Listeners (with debounce for smooth typing performance)
    const sidebarSearch = document.getElementById('sidebarSearch');
    const debouncedSidebarSearch = debounce((val) => {
      activeFilters.query = val;
      onChange(activeFilters);
    }, 150);
    sidebarSearch.addEventListener('input', (e) => {
      debouncedSidebarSearch(e.target.value);
    });

    // State filter search event
    if (selectedState === 'all') {
      const stateFilterSearch = document.getElementById('stateFilterSearch');
      const debouncedStateSearch = debounce((val) => {
        activeFilters.stateQuery = val;
        SearchFilters.render(containerId, activeLevel, summary, activeFilters, selectedState, onChange);
        const input = document.getElementById('stateFilterSearch');
        if (input) {
          input.focus();
          input.setSelectionRange(input.value.length, input.value.length);
        }
      }, 150);
      
      stateFilterSearch.addEventListener('input', (e) => {
        debouncedStateSearch(e.target.value);
      });

      // State checkboxes events
      container.querySelectorAll('.filter-state-checkbox').forEach(cb => {
        cb.addEventListener('change', () => {
          const checked = Array.from(container.querySelectorAll('.filter-state-checkbox:checked')).map(el => el.value);
          activeFilters.states = checked;
          onChange(activeFilters);
        });
      });
    }

    const courseSearch = document.getElementById('courseSearch');
    const debouncedCourseSearch = debounce((val) => {
      activeFilters.courseQuery = val;
      SearchFilters.render(containerId, activeLevel, summary, activeFilters, selectedState, onChange);
      const input = document.getElementById('courseSearch');
      if (input) {
        input.focus();
        input.setSelectionRange(input.value.length, input.value.length);
      }
    }, 150);
    
    courseSearch.addEventListener('input', (e) => {
      debouncedCourseSearch(e.target.value);
    });

    // College type checkbox events
    container.querySelectorAll('.filter-type-checkbox').forEach(cb => {
      cb.addEventListener('change', () => {
        const checked = Array.from(container.querySelectorAll('.filter-type-checkbox:checked')).map(el => el.value);
        activeFilters.types = checked;
        onChange(activeFilters);
      });
    });

    // Counseling Route radio events
    container.querySelectorAll('input[name="counselingRoute"]').forEach(radio => {
      radio.addEventListener('change', (e) => {
        activeFilters.counselingRoute = e.target.value;
        onChange(activeFilters);
      });
    });

    // Quota checkbox events
    container.querySelectorAll('.filter-quota-checkbox').forEach(cb => {
      cb.addEventListener('change', () => {
        const checked = Array.from(container.querySelectorAll('.filter-quota-checkbox:checked')).map(el => el.value);
        activeFilters.quotas = checked;
        onChange(activeFilters);
      });
    });

    // Course selection checkbox events
    container.querySelectorAll('.filter-course-checkbox').forEach(cb => {
      cb.addEventListener('change', () => {
        const checked = Array.from(container.querySelectorAll('.filter-course-checkbox:checked')).map(el => el.value);
        activeFilters.courses = checked;
        onChange(activeFilters);
      });
    });

    // Reset button events
    document.getElementById('resetFiltersBtn').addEventListener('click', () => {
      activeFilters.query = '';
      activeFilters.courseQuery = '';
      activeFilters.stateQuery = '';
      activeFilters.types = [];
      activeFilters.counselingRoute = 'all';
      activeFilters.quotas = [];
      activeFilters.courses = [];
      activeFilters.states = [];
      
      SearchFilters.render(containerId, activeLevel, summary, activeFilters, selectedState, onChange);
      onChange(activeFilters);
    });

    // Close button events (mobile only)
    const closeBtn = document.getElementById('closeSidebarBtn');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        document.getElementById('filterSidebar').classList.remove('active');
        document.getElementById('sidebarBackdrop').classList.remove('active');
      });
    }
  }
};
