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
        <div class="mapping-stats-dashboard" style="margin-top: 1.5rem; padding: 1.5rem; background: rgba(255,255,255,0.01); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
          <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1.25rem;">
            <i data-lucide="git-merge" style="color: var(--accent-blue); width: 22px; height: 22px;"></i>
            <h3 style="margin: 0; font-size: 1.2rem; font-weight: 600; font-family: var(--font-header);">Institutional Cross-Level Mapping & Statistics</h3>
          </div>
          
          <div class="stats-cards-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-bottom: 1.25rem;">
            <!-- Card 1: UG Only -->
            <div class="stats-card-glass" style="padding: 1.25rem; background: rgba(255,255,255,0.02); border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; gap: 0.4rem;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: var(--text-secondary); font-size: 0.85rem; font-weight: 500;">UG Only (MBBS)</span>
                <span class="badge badge-govt" style="background: rgba(59, 130, 246, 0.1) !important; color: var(--accent-blue) !important; border-color: rgba(59, 130, 246, 0.2) !important;">Level 1</span>
              </div>
              <strong style="font-size: 1.6rem; color: var(--text-primary); font-family: var(--font-header);">${ugOnlyCount} <span style="font-size: 0.85rem; font-weight: normal; color: var(--text-secondary);">colleges</span></strong>
              <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: auto; display: flex; flex-direction: column; gap: 0.2rem; border-top: 1px solid rgba(255,255,255,0.03); padding-top: 0.5rem;">
                <div style="display: flex; justify-content: space-between;">
                  <span>MBBS Seats:</span>
                  <strong style="color: var(--accent-green);">${ugOnlySeats}</strong>
                </div>
              </div>
            </div>

            <!-- Card 2: UG + PG -->
            <div class="stats-card-glass" style="padding: 1.25rem; background: rgba(255,255,255,0.02); border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; gap: 0.4rem;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: var(--text-secondary); font-size: 0.85rem; font-weight: 500;">UG + PG (MD/MS)</span>
                <span class="badge badge-private" style="background: rgba(168, 85, 247, 0.1) !important; color: var(--accent-purple) !important; border-color: rgba(168, 85, 247, 0.2) !important;">Level 2</span>
              </div>
              <strong style="font-size: 1.6rem; color: var(--text-primary); font-family: var(--font-header);">${ugPgCount} <span style="font-size: 0.85rem; font-weight: normal; color: var(--text-secondary);">colleges</span></strong>
              <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: auto; display: flex; flex-direction: column; gap: 0.2rem; border-top: 1px solid rgba(255,255,255,0.03); padding-top: 0.5rem;">
                <div style="display: flex; justify-content: space-between;">
                  <span>MBBS Seats:</span>
                  <strong style="color: var(--text-primary);">${ugPgSeatsUg}</strong>
                </div>
                <div style="display: flex; justify-content: space-between;">
                  <span>PG MD/MS Seats:</span>
                  <strong style="color: var(--accent-blue);">${ugPgSeatsPg}</strong>
                </div>
              </div>
            </div>

            <!-- Card 3: UG + PG + SS -->
            <div class="stats-card-glass" style="padding: 1.25rem; background: rgba(255,255,255,0.02); border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; gap: 0.4rem;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: var(--text-secondary); font-size: 0.85rem; font-weight: 500;">UG + PG + SS (DM/MCh)</span>
                <span class="badge badge-deemed" style="background: rgba(236, 72, 153, 0.1) !important; color: var(--accent-pink) !important; border-color: rgba(236, 72, 153, 0.2) !important;">Level 3</span>
              </div>
              <strong style="font-size: 1.6rem; color: var(--text-primary); font-family: var(--font-header);">${ugPgSsCount} <span style="font-size: 0.85rem; font-weight: normal; color: var(--text-secondary);">colleges</span></strong>
              <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: auto; display: flex; flex-direction: column; gap: 0.2rem; border-top: 1px solid rgba(255,255,255,0.03); padding-top: 0.5rem;">
                <div style="display: flex; justify-content: space-between;">
                  <span>MBBS / MD Seats:</span>
                  <strong style="color: var(--text-primary);">${ugPgSsSeatsUg} / ${ugPgSsSeatsPg}</strong>
                </div>
                <div style="display: flex; justify-content: space-between;">
                  <span>SS DM/MCh Seats:</span>
                  <strong style="color: var(--accent-pink);">${ugPgSsSeatsSs}</strong>
                </div>
              </div>
            </div>
          </div>

          <!-- Mapped seat ratios and distribution bar -->
          <div style="margin-top: 1rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.4rem;">
              <span>Institutional Distribution</span>
              <span>Total Mapped: ${totalColleges} Colleges</span>
            </div>
            <div style="display: flex; height: 8px; border-radius: 4px; overflow: hidden; background: rgba(255,255,255,0.05);">
              <div style="width: ${(ugOnlyCount / totalColleges * 100).toFixed(1)}%; background: var(--accent-blue);" title="UG Only: ${ugOnlyCount} colleges (${(ugOnlyCount / totalColleges * 100).toFixed(1)}%)"></div>
              <div style="width: ${(ugPgCount / totalColleges * 100).toFixed(1)}%; background: var(--accent-purple);" title="UG + PG: ${ugPgCount} colleges (${(ugPgCount / totalColleges * 100).toFixed(1)}%)"></div>
              <div style="width: ${(ugPgSsCount / totalColleges * 100).toFixed(1)}%; background: var(--accent-pink);" title="UG + PG + SS: ${ugPgSsCount} colleges (${(ugPgSsCount / totalColleges * 100).toFixed(1)}%)"></div>
            </div>
            <div style="display: flex; justify-content: flex-start; gap: 1.25rem; font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">
              <span style="display: flex; align-items: center; gap: 0.3rem;"><span style="width: 7px; height: 7px; border-radius: 50%; background: var(--accent-blue);"></span> UG Only (${(ugOnlyCount / totalColleges * 100).toFixed(1)}%)</span>
              <span style="display: flex; align-items: center; gap: 0.3rem;"><span style="width: 7px; height: 7px; border-radius: 50%; background: var(--accent-purple);"></span> UG + PG (${(ugPgCount / totalColleges * 100).toFixed(1)}%)</span>
              <span style="display: flex; align-items: center; gap: 0.3rem;"><span style="width: 7px; height: 7px; border-radius: 50%; background: var(--accent-pink);"></span> UG + PG + SS (${(ugPgSsCount / totalColleges * 100).toFixed(1)}%)</span>
            </div>
          </div>
        </div>
      `;
    }

    if (comparisonList.length === 0) {
      container.innerHTML = `
        <div class="placeholder-text" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 3rem 1.5rem; gap: 1rem; text-align: center;">
          <i data-lucide="columns-3" style="width: 48px; height: 48px; color: var(--text-secondary); opacity: 0.5;"></i>
          <p style="margin: 0; max-width: 500px;">No colleges selected for comparison. Use the search explorer table and click the "Compare" buttons to add colleges here.</p>
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
        <div class="matrix-cell matrix-header-cell" style="position: relative;">
          <span class="matrix-college-header">${col.name}</span>
          <button class="matrix-remove-btn" data-remove-id="${col.id}">
            <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i> Remove
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
          <span class="badge ${badgeClass}" style="width: fit-content;">${col.type}</span>
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
      html += `<div class="matrix-cell"><strong style="font-size: 1.25rem; color: var(--accent-green);">${col.totalSeats}</strong></div>`;
    });

    // Row 5: Detailed Seat Mix / Quotas
    html += `<div class="matrix-cell matrix-cell-sticky"><span class="matrix-row-label">Quota Allocation</span></div>`;
    collegeData.forEach(col => {
      let quotaItems = '';
      Object.entries(col.quotas).forEach(([quota, seats]) => {
        quotaItems += `
          <div class="matrix-seats-item">
            <span>${quota}</span>
            <strong style="color: var(--accent-blue);">${seats}</strong>
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
          <div class="matrix-seats-item" style="border-top: 1px dashed rgba(255, 255, 255, 0.1); margin-top: 0.5rem; padding-top: 0.5rem;">
            <span style="color: var(--accent-blue);">PG Seats (MD/MS)</span>
            <strong style="color: var(--accent-blue);">${col.pgSeats || '0'}</strong>
          </div>
          <div class="matrix-seats-item">
            <span style="color: var(--accent-pink);">SS Seats (DM/MCh)</span>
            <strong style="color: var(--accent-pink);">${col.ssSeats || '0'}</strong>
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
