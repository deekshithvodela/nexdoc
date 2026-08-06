// Declarative Table Schemas for NexDoc Table Engine (TableSchemas.js)

export const CutoffExplorerSchema = {
  tableName: 'mcc_ug_cutoffs',
  defaultSortColumn: 'college_name',
  defaultSortDirection: 'asc',

  // Nested child rows processor
  processChildRows(rawCutoffs, state) {
    const result = [];
    const hasRank = state.userRank !== null && state.userRank !== '' && !isNaN(state.userRank) && Number(state.userRank) > 0;
    const rankVal = hasRank ? Number(state.userRank) : null;

    rawCutoffs.forEach(c => {
      // Allied course exclusion
      const course = String(c.course || '').toLowerCase();
      if (course.includes('nursing') || course.includes('bds') || course.includes('ayush')) return;

      // Category filter
      if (state.selectedCategory !== 'ALL' && c.category !== state.selectedCategory) return;
      if (state.selectedCategories && state.selectedCategories.length > 0 && !state.selectedCategories.includes(c.category)) return;

      // Quota filter
      if (state.selectedQuota !== 'ALL' && c.quota !== state.selectedQuota) return;
      if (state.selectedQuotas && state.selectedQuotas.length > 0 && !state.selectedQuotas.includes(c.quota)) return;

      // Predictor chance filter logic
      let chanceCategory = 'N/A';
      if (hasRank) {
        const finalClose = c.final_closing_rank || c.r3_closing_rank || c.r2_closing_rank || c.r1_closing_rank;
        if (finalClose) {
          const closeNum = Number(finalClose);
          if (rankVal <= closeNum * 0.9) chanceCategory = 'HIGH';
          else if (rankVal <= closeNum * 1.1) chanceCategory = 'BORDERLINE';
          else chanceCategory = 'LOW';
        }
      }

      if (state.selectedChance !== 'ALL' && chanceCategory !== state.selectedChance) return;

      result.push({
        ...c,
        chanceCategory
      });
    });

    return result;
  },

  columns: [
    { field: 'toggle', label: '', className: 'col-expand-toggle' },
    { field: 'college_name', label: 'College Name', className: 'col-name-th', sortable: true },
    { field: 'state', label: 'State & City', sortable: true },
    { field: 'college_type', label: 'Type', sortable: true },
    { field: 'course', label: 'Course' },
    { field: 'quota', label: 'Quota' },
    { field: 'category', label: 'Category' },
    { field: 'chanceCategory', label: 'Predicted Chance' },
    { field: 'r1_opening_rank', label: 'R1 Op', className: 'text-right' },
    { field: 'r1_closing_rank', label: 'R1 Cl', className: 'text-right' },
    { field: 'r2_opening_rank', label: 'R2 Op', className: 'text-right' },
    { field: 'r2_closing_rank', label: 'R2 Cl', className: 'text-right' },
    { field: 'r3_opening_rank', label: 'R3 Op', className: 'text-right' },
    { field: 'r3_closing_rank', label: 'R3 Cl', className: 'text-right' },
    { field: 'final_opening_rank', label: 'Final Op', className: 'text-right' },
    { field: 'final_closing_rank', label: 'Final Cl', className: 'text-right' }
  ]
};

export const SeatMatrixSchema = {
  tableName: 'seat_matrix',
  defaultSortColumn: 'college_name',
  defaultSortDirection: 'asc',

  columns: [
    { field: 'college_name', label: 'College Name', className: 'col-name-th', sortable: true },
    { field: 'state', label: 'State', sortable: true },
    { field: 'city', label: 'City' },
    { field: 'college_type', label: 'Management', sortable: true },
    { field: 'course', label: 'Course' },
    { field: 'seats', label: 'Total Seats', className: 'text-right', sortable: true },
    { field: 'recognized_seats', label: 'Recognized Seats', className: 'text-right' },
    { field: 'permitted_seats', label: 'Permitted Seats', className: 'text-right' }
  ]
};
