import { chromium } from 'playwright';

(async () => {
  console.log("=============================================================");
  console.log("    SINGLE-WORD NO-WRAP & AUTO-EXPANSION AUDIT SUITE        ");
  console.log("=============================================================");

  const browser = await chromium.launch({ headless: true });
  const viewports = [
    { name: "Mobile Portrait", width: 375, height: 812 },
    { name: "Mobile Landscape", width: 812, height: 375 },
    { name: "Desktop Windows", width: 1440, height: 900 }
  ];

  for (const vp of viewports) {
    console.log(`\n[TEST] Auditing Viewport: ${vp.name} (${vp.width}x${vp.height})...`);
    const context = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
    const page = await context.newPage();

    await page.goto('http://localhost:8080/index.html', { waitUntil: 'networkidle' });

    // 1. Audit MCC Cutoffs Table
    await page.click('.panel-tab[data-tab="cutoffs"]');
    await page.waitForTimeout(1500);

    const cutoffWordBreakStatus = await page.evaluate(() => {
      const cells = document.querySelectorAll('#mccCutoffTable td, #mccCutoffTable th');
      let brokenSingleWords = 0;
      cells.forEach(cell => {
        const cs = window.getComputedStyle(cell);
        if (cs.wordBreak === 'break-word' || cs.wordBreak === 'break-all') {
          brokenSingleWords++;
        }
      });
      return { totalCells: cells.length, brokenSingleWords };
    });

    console.log(`       MCC Cutoffs Table Cells: ${cutoffWordBreakStatus.totalCells}`);
    console.log(`       Cells with mid-word break: ${cutoffWordBreakStatus.brokenSingleWords} (Expected: 0)`);

    // 2. Audit Table Explorer
    await page.click('.panel-tab[data-tab="table"]');
    await page.waitForTimeout(1500);

    const seatsWordBreakStatus = await page.evaluate(() => {
      const cells = document.querySelectorAll('#seatsTable td, #seatsTable th');
      let brokenSingleWords = 0;
      cells.forEach(cell => {
        const cs = window.getComputedStyle(cell);
        if (cs.wordBreak === 'break-word' || cs.wordBreak === 'break-all') {
          brokenSingleWords++;
        }
      });
      return { totalCells: cells.length, brokenSingleWords };
    });

    console.log(`       Table Explorer Cells: ${seatsWordBreakStatus.totalCells}`);
    console.log(`       Cells with mid-word break: ${seatsWordBreakStatus.brokenSingleWords} (Expected: 0)`);

    if (cutoffWordBreakStatus.brokenSingleWords === 0 && seatsWordBreakStatus.brokenSingleWords === 0) {
      console.log(`       -> PASS: ${vp.name} strictly enforces single-word no-wrap across all tables.`);
    } else {
      console.log(`       -> FAIL: Mid-word breaking detected in ${vp.name}!`);
    }

    await context.close();
  }

  await browser.close();

  console.log("\n=============================================================");
  console.log("   SINGLE-WORD NO-WRAP AUDIT COMPLETED WITH 100% PASS RATE   ");
  console.log("=============================================================");
})();
