import { chromium } from 'playwright';

(async () => {
  console.log("=============================================================");
  console.log("    ROW EXPANSION COLUMN STABILITY & ZERO-SHIFT AUDIT        ");
  console.log("=============================================================");

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto('http://localhost:8080/index.html', { waitUntil: 'networkidle' });
  await page.click('.panel-tab[data-tab="cutoffs"]');
  await page.waitForTimeout(1500);

  // 1. Measure column widths BEFORE expansion
  const initialWidths = await page.evaluate(() => {
    const ths = Array.from(document.querySelectorAll('#mccCutoffTable thead th'));
    return ths.map(th => ({ title: th.textContent.trim(), width: th.getBoundingClientRect().width }));
  });

  console.log("\n1. Measure initial header column widths (Collapsed state):");
  initialWidths.forEach((col, i) => console.log(`   Col ${i+1} [${col.title || 'Chevron'}]: ${col.width.toFixed(2)}px`));

  // 2. Click expand button on first college in MCC Cutoff Table
  await page.locator('#mccCutoffTable .group-expand-btn').first().click();
  await page.waitForTimeout(1000);

  // 3. Measure column widths AFTER expansion
  const expandedWidths = await page.evaluate(() => {
    const ths = Array.from(document.querySelectorAll('#mccCutoffTable thead th'));
    return ths.map(th => ({ title: th.textContent.trim(), width: th.getBoundingClientRect().width }));
  });

  console.log("\n2. Measure header column widths AFTER expanding child rows:");
  let maxShift = 0;
  expandedWidths.forEach((col, i) => {
    const diff = Math.abs(col.width - initialWidths[i].width);
    if (diff > maxShift) maxShift = diff;
    console.log(`   Col ${i+1} [${col.title || 'Chevron'}]: ${col.width.toFixed(2)}px (Delta: ${diff.toFixed(2)}px)`);
  });

  await browser.close();

  console.log("\n=============================================================");
  if (maxShift < 1.0) {
    console.log(`   -> PASS: Max column width shift upon row expansion is ${maxShift.toFixed(2)}px — 100% STABLE & ZERO JITTER!`);
  } else {
    console.log(`   -> FAIL: Column width shift detected: ${maxShift.toFixed(2)}px!`);
  }
  console.log("=============================================================");
})();
