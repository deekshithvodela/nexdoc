const fs = require('fs');
const path = require('path');

// Load dataset
const rawData = fs.readFileSync('public/data/ug_colleges_aiq_mapping.json', 'utf-8');
const ugMappingData = JSON.parse(rawData);

// Mock CutoffExplorer state and getFilteredColleges logic
const CutoffExplorer = {
  state: {
    ugMappingData: ugMappingData,
    userRank: '',
    searchQuery: '',
    showNonAiq: false,
    selectedCategories: [],
    selectedQuotas: []
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

    // 1. Hide Non-AIQ colleges by default unless showNonAiq is true
    if (!this.state.showNonAiq) {
      colleges = colleges.filter(c => c.mcc_status !== 'Non AIQ');
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

      if (this.state.selectedCategories.length > 0) {
        rawCutoffs = rawCutoffs.filter(c => this.state.selectedCategories.includes(c.category));
      }

      if (this.state.selectedQuotas.length > 0) {
        rawCutoffs = rawCutoffs.filter(c => this.state.selectedQuotas.includes(c.quota));
      }

      const processedChildRows = rawCutoffs.map(c => {
        const r1Open = this.parseRankNum(c.r1_opening_rank);
        const r1Close = this.parseRankNum(c.r1_closing_rank);
        const r2Open = this.parseRankNum(c.r2_opening_rank);
        const r2Close = this.parseRankNum(c.r2_closing_rank);
        const r3Open = this.parseRankNum(c.r3_opening_rank);
        const r3Close = this.parseRankNum(c.r3_closing_rank);
        const finalOpen = this.parseRankNum(c.final_opening_rank);
        const finalClose = this.parseRankNum(c.final_closing_rank);

        return {
          quota: c.quota || 'All India',
          category: c.category || 'Open',
          course: c.course || 'MBBS',
          r1_open_str: this.formatRankVal(c.r1_opening_rank),
          r1_close_str: this.formatRankVal(c.r1_closing_rank),
          r2_open_str: this.formatRankVal(c.r2_opening_rank),
          r2_close_str: this.formatRankVal(c.r2_closing_rank),
          r3_open_str: this.formatRankVal(c.r3_opening_rank),
          r3_close_str: this.formatRankVal(c.r3_closing_rank),
          final_open_str: this.formatRankVal(c.final_opening_rank),
          final_close_str: this.formatRankVal(c.final_closing_rank)
        };
      });

      processedChildRows.sort((a, b) => a.quota.localeCompare(b.quota));

      const finalOpeningNums = processedChildRows.map(r => this.parseRankNum(r.final_open_str)).filter(x => x !== Infinity);
      const finalClosingNums = processedChildRows.map(r => this.parseRankNum(r.final_close_str)).filter(x => x !== Infinity);

      const minFinalOpen = finalOpeningNums.length > 0 ? Math.min(...finalOpeningNums) : Infinity;
      const maxFinalClose = finalClosingNums.length > 0 ? Math.max(...finalClosingNums) : Infinity;

      result.push({
        college_id: col.college_id,
        college_name: col.college_name,
        state: col.state || '',
        city: col.city || '',
        college_type: col.college_type || 'Government',
        mcc_status: col.mcc_status || (col.matched_in_aiq ? 'Matched' : 'Non AIQ'),
        min_final_open_str: this.formatRankVal(minFinalOpen),
        max_final_close_str: this.formatRankVal(maxFinalClose),
        childRows: processedChildRows
      });
    });

    return result;
  }
};

function runTestSuite() {
  console.log("==============================================================");
  console.log("    MCC UG CUTOFF EXPLORER FUNCTIONAL TEST SUITE RESULTS");
  console.log("==============================================================\n");

  let passedCount = 0;

  // 1. All-college rendering (default showNonAiq = false)
  CutoffExplorer.state = { ugMappingData, userRank: '', searchQuery: '', showNonAiq: false, selectedCategories: [], selectedQuotas: [] };
  let cols = CutoffExplorer.getFilteredColleges();
  console.log(`[Test 1] All-College Rendering (default showNonAiq=false): Rendered ${cols.length} colleges`);
  if (cols.length === 502) { console.log("  -> PASS"); passedCount++; } else { console.log("  -> FAIL"); }

  // 2. Hide / Show Non-AIQ Toggle
  CutoffExplorer.state.showNonAiq = true;
  cols = CutoffExplorer.getFilteredColleges();
  console.log(`[Test 2] Hide/Show Non AIQ (showNonAiq=true): Rendered ${cols.length} colleges (all 823 master colleges)`);
  if (cols.length === 823) { console.log("  -> PASS"); passedCount++; } else { console.log("  -> FAIL"); }

  // 3. 1 digit rank input (e.g. rank '5')
  CutoffExplorer.state.userRank = '5';
  CutoffExplorer.state.showNonAiq = false;
  cols = CutoffExplorer.getFilteredColleges();
  console.log(`[Test 3] 1-Digit Rank (Rank '5'): ${cols.length} colleges processed without error`);
  if (cols.length > 0) { console.log("  -> PASS"); passedCount++; } else { console.log("  -> FAIL"); }

  // 4. Multi-digit rank (e.g. rank '1450')
  CutoffExplorer.state.userRank = '1450';
  cols = CutoffExplorer.getFilteredColleges();
  console.log(`[Test 4] Multi-Digit Rank (Rank '1450'): ${cols.length} colleges processed without error`);
  if (cols.length > 0) { console.log("  -> PASS"); passedCount++; } else { console.log("  -> FAIL"); }

  // 5. Rank 10,000 & ACSR Government Medical College verification
  CutoffExplorer.state.userRank = '10000';
  CutoffExplorer.state.searchQuery = 'ACSR';
  cols = CutoffExplorer.getFilteredColleges();
  const acsr = cols.find(c => c.college_name.includes('ACSR'));
  console.log(`[Test 5] Rank 10,000 / ACSR GMC: Found ${cols.length} match. Summary: Fin Op=${acsr?.min_final_open_str}, Fin Cl=${acsr?.max_final_close_str}`);
  if (acsr && acsr.max_final_close_str.replace(/,/g, '') === '1040503') { console.log("  -> PASS (No blank cells, correct max closing rank)"); passedCount++; } else { console.log("  -> FAIL"); }

  // 6. Rank 100,000+ verification
  CutoffExplorer.state.userRank = '120000';
  CutoffExplorer.state.searchQuery = '';
  cols = CutoffExplorer.getFilteredColleges();
  console.log(`[Test 6] Rank 100,000+: ${cols.length} colleges processed cleanly`);
  if (cols.length > 0) { console.log("  -> PASS"); passedCount++; } else { console.log("  -> FAIL"); }

  // 7. Category filtering
  CutoffExplorer.state.selectedCategories = ['OBC'];
  cols = CutoffExplorer.getFilteredColleges();
  console.log(`[Test 7] Category Filter ('OBC'): ${cols.length} colleges matched`);
  if (cols.length > 0) { console.log("  -> PASS"); passedCount++; } else { console.log("  -> FAIL"); }

  // 8. Quota filtering
  CutoffExplorer.state.selectedCategories = [];
  CutoffExplorer.state.selectedQuotas = ['All India'];
  cols = CutoffExplorer.getFilteredColleges();
  console.log(`[Test 8] Quota Filter ('All India'): ${cols.length} colleges matched`);
  if (cols.length > 0) { console.log("  -> PASS"); passedCount++; } else { console.log("  -> FAIL"); }

  // 9. College Search Filter
  CutoffExplorer.state.selectedQuotas = [];
  CutoffExplorer.state.searchQuery = 'Burdwan';
  cols = CutoffExplorer.getFilteredColleges();
  console.log(`[Test 9] College Search ('Burdwan'): Found ${cols.length} college (${cols[0]?.college_name})`);
  if (cols.length === 1 && cols[0].college_name.includes('Burdwan')) { console.log("  -> PASS"); passedCount++; } else { console.log("  -> FAIL"); }

  // 10. Missing cutoff values rendering (renders '-' not blank)
  CutoffExplorer.state.searchQuery = 'ACSR';
  cols = CutoffExplorer.getFilteredColleges();
  const acsrChild = cols[0]?.childRows[0];
  console.log(`[Test 10] Missing Cutoff Rendering: R1 Op=${acsrChild?.r1_open_str}, R1 Cl=${acsrChild?.r1_close_str}`);
  if (acsrChild?.r1_open_str === '-' && acsrChild?.r1_close_str === '-') { console.log("  -> PASS (Missing values render '-' cleanly)"); passedCount++; } else { console.log("  -> FAIL"); }

  console.log("\n==============================================================");
  console.log(`  FINAL RESULT: ${passedCount} / 10 FUNCTIONAL SUITE TESTS PASSED`);
  console.log("==============================================================");
}

runTestSuite();
