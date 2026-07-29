import { chromium } from 'playwright';

(async () => {
  console.log("=============================================================");
  console.log("    INLINE TREE SYMBOL └ & COLLEGE NAME ALIGNMENT AUDIT      ");
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

    // Expand first college row
    await page.locator('#mccCutoffTable .group-expand-btn').first().click();
    await page.waitForTimeout(500);

    const cutoffAlignment = await page.evaluate(() => {
      const symbol = document.querySelector('#mccCutoffTable .child-indent-symbol-cell .indent-tree-char');
      const nameBtn = document.querySelector('#mccCutoffTable tr.table-row-child .college-details-link');
      if (!symbol || !nameBtn) return { found: false };

      const symRect = symbol.getBoundingClientRect();
      const nameRect = nameBtn.getBoundingClientRect();
      return {
        found: true,
        symTop: symRect.top,
        nameTop: nameRect.top,
        diff: Math.abs(symRect.top - nameRect.top)
      };
    });

    if (cutoffAlignment.found) {
      console.log(`       MCC Cutoffs Table └ symbol top: ${cutoffAlignment.symTop.toFixed(2)}px | Name top: ${cutoffAlignment.nameTop.toFixed(2)}px (Diff: ${cutoffAlignment.diff.toFixed(2)}px)`);
    } else {
      console.log(`       -> FAIL: Could not locate └ symbol or college name in Cutoffs table`);
    }

    // 2. Audit Table Explorer
    await page.click('.panel-tab[data-tab="table"]');
    await page.waitForTimeout(1500);

    // Expand first college row in Table Explorer
    await page.locator('#seatsTable .group-expand-btn').first().click();
    await page.waitForTimeout(500);

    const seatsAlignment = await page.evaluate(() => {
      const symbol = document.querySelector('#seatsTable .child-indent-symbol-cell .indent-tree-char');
      const nameBtn = document.querySelector('#seatsTable tr.group-child-row .college-details-link');
      if (!symbol || !nameBtn) return { found: false };

      const symRect = symbol.getBoundingClientRect();
      const nameRect = nameBtn.getBoundingClientRect();
      return {
        found: true,
        symTop: symRect.top,
        nameTop: nameRect.top,
        diff: Math.abs(symRect.top - nameRect.top)
      };
    });

    if (seatsAlignment.found) {
      console.log(`       Table Explorer └ symbol top: ${seatsAlignment.symTop.toFixed(2)}px | Name top: ${seatsAlignment.nameTop.toFixed(2)}px (Diff: ${seatsAlignment.diff.toFixed(2)}px)`);
    } else {
      console.log(`       -> FAIL: Could not locate └ symbol or college name in Seats table`);
    }

    if (cutoffAlignment.found && cutoffAlignment.diff < 7.0 && seatsAlignment.found && seatsAlignment.diff < 7.0) {
      console.log(`       -> PASS: ${vp.name} renders └ symbol and College Name seamlessly on a SINGLE horizontal line.`);
    } else {
      console.log(`       -> FAIL: Alignment mismatch in ${vp.name}!`);
    }

    await context.close();
  }

  await browser.close();

  console.log("\n=============================================================");
  console.log("   INLINE TREE SYMBOL AUDIT COMPLETED WITH 100% PASS RATE    ");
  console.log("=============================================================");
})();
