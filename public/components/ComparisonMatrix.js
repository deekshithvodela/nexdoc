// ComparisonMatrix Component for NexDoc

export const ComparisonMatrix = {
  render(containerId, comparisonList, rawData, onRemove) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Compute cross-level statistics for UG level
    let statsHtml = '';
    const hasPgSeatsField = rawData && rawData.length > 0 && (rawData[0].pg_seats !== undefined);
    if (hasPgSeatsField) {
      const colleges = {};
      rawData.forEach(row => {
        const cid = row.college_id;
        if (!colleges[cid]) {
          colleges[cid] = {
            name: row.college_name,
            ug: 0,
            pg: row.pg_seats || 0,
            ss: row.ss_seats || 0
          };
        }
        colleges[cid].ug += row.seats;
      });

      let ugOnlyCount = 0;
      let ugPgCount = 0;
      let ugPgSsCount = 0;
      let totalUg = 0;
      let totalPg = 0;
      let totalSs = 0;

      Object.values(colleges).forEach(col => {
        totalUg += col.ug;
        totalPg += col.pg;
        totalSs += col.ss;

        if (col.pg > 0 && col.ss > 0) {
          ugPgSsCount++;
        } else if (col.pg > 0) {
          ugPgCount++;
        } else {
          ugOnlyCount++;
        }
      });

      const totalColleges = Object.keys(colleges).length;

      // Calculate seats in each tier
      const ugOnlySeats = Object.values(colleges).filter(c => c.pg === 0 && c.ss === 0).reduce((acc, c) => acc + c.ug, 0);
      const ugPgSeatsUg = Object.values(colleges).filter(c => c.pg > 0 && c.ss === 0).reduce((acc, c) => acc + c.ug, 0);
      const ugPgSeatsPg = Object.values(colleges).filter(c => c.pg > 0 && c.ss === 0).reduce((acc, c) => acc + c.pg, 0);
      const ugPgSsSeatsUg = Object.values(colleges).filter(c => c.pg > 0 && c.ss > 0).reduce((acc, c) => acc + c.ug, 0);
      const ugPgSsSeatsPg = Object.values(colleges).filter(c => c.pg > 0 && c.ss > 0).reduce((acc, c) => acc + c.pg, 0);
      const ugPgSsSeatsSs = Object.values(colleges).filter(c => c.pg > 0 && c.ss > 0).reduce((acc, c) => acc + c.ss, 0);

      statsHtml = `
        <div class="mapping-stats-dashboard">
          <div class="matrix-header-group">
            <i data-lucide="git-merge" class="matrix-icon-blue"></i>
            <h3 class="matrix-title">Institutional Cross-Level Mapping & Statistics</h3>
          </div>
          
          <div class="stats-cards-grid">
            <!-- Card 1: UG Only -->
            <div class="stats-card-glass">
              <div class="matrix-card-header">
                <span class="matrix-card-title">UG Only (MBBS)</span>
                <span class="badge badge-govt badge-level-1">Level 1</span>
              </div>
              <strong class="matrix-stat-val">${ugOnlyCount} <span class="matrix-stat-unit">colleges</span></strong>
              <div class="matrix-stat-footer">
                <div class="matrix-stat-row">
                  <span>MBBS Seats:</span>
                  <strong class="text-green">${ugOnlySeats}</strong>
                </div>
              </div>
            </div>

            <!-- Card 2: UG + PG -->
            <div class="stats-card-glass">
              <div class="matrix-card-header">
                <span class="matrix-card-title">UG + PG (MD/MS)</span>
                <span class="badge badge-private badge-level-2">Level 2</span>
              </div>
              <strong class="matrix-stat-val">${ugPgCount} <span class="matrix-stat-unit">colleges</span></strong>
              <div class="matrix-stat-footer">
                <div class="matrix-stat-row">
                  <span>MBBS Seats:</span>
                  <strong class="text-primary">${ugPgSeatsUg}</strong>
                </div>
                <div class="matrix-stat-row">
                  <span>PG MD/MS Seats:</span>
                  <strong class="text-blue">${ugPgSeatsPg}</strong>
                </div>
              </div>
            </div>

            <!-- Card 3: UG + PG + SS -->
            <div class="stats-card-glass">
              <div class="matrix-card-header">
                <span class="matrix-card-title">UG + PG + SS (DM/MCh)</span>
                <span class="badge badge-deemed badge-level-3">Level 3</span>
              </div>
              <strong class="matrix-stat-val">${ugPgSsCount} <span class="matrix-stat-unit">colleges</span></strong>
              <div class="matrix-stat-footer">
                <div class="matrix-stat-row">
                  <span>MBBS / MD Seats:</span>
                  <strong class="text-primary">${ugPgSsSeatsUg} / ${ugPgSsSeatsPg}</strong>
                </div>
                <div class="matrix-stat-row">
                  <span>SS DM/MCh Seats:</span>
                  <strong class="text-pink">${ugPgSsSeatsSs}</strong>
                </div>
              </div>
            </div>
          </div>

          <!-- Mapped seat ratios and distribution bar -->
          <div class="matrix-distribution-container">
            <div class="matrix-distribution-meta">
              <span>Institutional Distribution</span>
              <span>Total Mapped: ${totalColleges} Colleges</span>
            </div>
            <div class="matrix-distribution-bar">
              <div class="bar-seg bar-seg-blue" style="width: ${(ugOnlyCount / totalColleges * 100).toFixed(1)}%;" title="UG Only: ${ugOnlyCount} colleges (${(ugOnlyCount / totalColleges * 100).toFixed(1)}%)"></div>
              <div class="bar-seg bar-seg-purple" style="width: ${(ugPgCount / totalColleges * 100).toFixed(1)}%;" title="UG + PG: ${ugPgCount} colleges (${(ugPgCount / totalColleges * 100).toFixed(1)}%)"></div>
              <div class="bar-seg bar-seg-pink" style="width: ${(ugPgSsCount / totalColleges * 100).toFixed(1)}%;" title="UG + PG + SS: ${ugPgSsCount} colleges (${(ugPgSsCount / totalColleges * 100).toFixed(1)}%)"></div>
            </div>
            <div class="matrix-legend-list">
              <span class="matrix-legend-item"><span class="matrix-legend-dot bg-blue"></span> UG Only (${(ugOnlyCount / totalColleges * 100).toFixed(1)}%)</span>
              <span class="matrix-legend-item"><span class="matrix-legend-dot bg-purple"></span> UG + PG (${(ugPgCount / totalColleges * 100).toFixed(1)}%)</span>
              <span class="matrix-legend-item"><span class="matrix-legend-dot bg-pink"></span> UG + PG + SS (${(ugPgSsCount / totalColleges * 100).toFixed(1)}%)</span>
            </div>
          </div>
        </div>
      `;
    }

    if (comparisonList.length === 0) {
      container.innerHTML = `
        <div class="placeholder-text matrix-placeholder">
          <i data-lucide="columns-3" class="matrix-placeholder-icon"></i>
          <p class="matrix-placeholder-text">No colleges selected for comparison. Use the search explorer table and click the "Compare" buttons to add colleges here.</p>
        </div>
        ${statsHtml}
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    // 1. Process data for each college in comparison list
    const collegeData = comparisonList.map(collegeId => {
      const collegeRows = rawData.filter(r => r.college_id === collegeId);
      if (collegeRows.length === 0) return null;

      const sample = collegeRows[0];
      const name = sample.college_name;
      const type = sample.college_type;
      const state = sample.state;
      const pgSeats = sample.pg_seats !== undefined ? sample.pg_seats : 0;
      const ssSeats = sample.ss_seats !== undefined ? sample.ss_seats : 0;
      const isUG = (sample.course === 'MBBS' || 'pg_seats' in sample);

      // Group courses and seats
      const courses = {};
      let totalSeats = 0;
      const quotas = {};

      collegeRows.forEach(row => {
        courses[row.course] = (courses[row.course] || 0) + row.seats;
        quotas[row.quota_type] = (quotas[row.quota_type] || 0) + row.seats;
        totalSeats += row.seats;
      });

      return {
        id: collegeId,
        name: name,
        type: type,
        state: state,
        totalSeats: totalSeats,
        courses: courses,
        quotas: quotas,
        pgSeats: pgSeats,
        ssSeats: ssSeats,
        isUG: isUG
      };
    }).filter(Boolean);

    // 2. Render Grid layout
    let html = `<div class="compare-matrix-grid" style="grid-template-columns: 130px repeat(${collegeData.length}, minmax(250px, 1fr));">`;

    // Row 1: Header Row (College Names)
    html += `<div class="matrix-cell matrix-header-cell matrix-cell-sticky">Attribute / Metric</div>`;
    collegeData.forEach(col => {
      html += `
        <div class="matrix-cell matrix-header-cell pos-relative">
          <span class="matrix-college-header">${col.name}</span>
          <button class="matrix-remove-btn" data-remove-id="${col.id}">
            <i data-lucide="trash-2" class="icon-sm"></i> Remove
          </button>
        </div>
      `;
    });

    // Row 2: Institution Type
    html += `<div class="matrix-cell matrix-cell-sticky"><span class="matrix-row-label">Ownership Type</span></div>`;
    collegeData.forEach(col => {
      let badgeClass = 'badge-govt';
      if (col.type === 'Deemed') badgeClass = 'badge-deemed';
      if (col.type === 'Private') badgeClass = 'badge-private';
      html += `
        <div class="matrix-cell">
          <span class="badge ${badgeClass} fit-content">${col.type}</span>
        </div>
      `;
    });

    // Row 3: Region / State
    html += `<div class="matrix-cell matrix-cell-sticky"><span class="matrix-row-label">Location / State</span></div>`;
    collegeData.forEach(col => {
      html += `<div class="matrix-cell"><strong>${col.state}</strong></div>`;
    });

    // Row 4: Total Seats
    html += `<div class="matrix-cell matrix-cell-sticky"><span class="matrix-row-label">Aggregate Seats</span></div>`;
    collegeData.forEach(col => {
      html += `<div class="matrix-cell"><strong class="matrix-total-seats">${col.totalSeats}</strong></div>`;
    });

    // Row 5: Detailed Seat Mix / Quotas
    html += `<div class="matrix-cell matrix-cell-sticky"><span class="matrix-row-label">Quota Allocation</span></div>`;
    collegeData.forEach(col => {
      let quotaItems = '';
      Object.entries(col.quotas).forEach(([quota, seats]) => {
        quotaItems += `
          <div class="matrix-seats-item">
            <span>${quota}</span>
            <strong class="text-blue">${seats}</strong>
          </div>
        `;
      });
      html += `
        <div class="matrix-cell">
          <div class="matrix-seats-list">${quotaItems}</div>
        </div>
      `;
    });

    // Row 6: Courses / Branches Available
    html += `<div class="matrix-cell matrix-cell-sticky"><span class="matrix-row-label">Specialties & Seats</span></div>`;
    collegeData.forEach(col => {
      let courseItems = '';
      Object.entries(col.courses).forEach(([course, seats]) => {
        courseItems += `
          <div class="matrix-seats-item">
            <span>${course}</span>
            <strong>${seats}</strong>
          </div>
        `;
      });
      if (col.isUG) {
        courseItems += `
          <div class="matrix-seats-item matrix-seat-divider">
            <span class="text-blue">PG Seats (MD/MS)</span>
            <strong class="text-blue">${col.pgSeats || '0'}</strong>
          </div>
          <div class="matrix-seats-item">
            <span class="text-pink">SS Seats (DM/MCh)</span>
            <strong class="text-pink">${col.ssSeats || '0'}</strong>
          </div>
        `;
      }
      html += `
        <div class="matrix-cell">
          <div class="matrix-seats-list">${courseItems}</div>
        </div>
      `;
    });

    html += `</div>`; // Close grid container
    container.innerHTML = html;

    if (window.lucide) window.lucide.createIcons();

    // Attach Remove Button Events
    container.querySelectorAll('.matrix-remove-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.currentTarget.getAttribute('data-remove-id');
        onRemove(id);
      });
    });
  }
};
