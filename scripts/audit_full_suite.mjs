import { chromium } from 'playwright';

(async () => {
  console.log("=============================================================");
  console.log("    PLAYWRIGHT FULL SUITE REGRESSION & SYSTEM AUDIT        ");
  console.log("=============================================================");

  const browser = await chromium.launch({ headless: true });

  // -------------------------------------------------------------------
  // TEST 1: CUTOFF & PREDICTOR FUNCTIONALITY (Desktop Viewport)
  // -------------------------------------------------------------------
  console.log("\n[TEST 1] Auditing Cutoff Explorer & Predictor (Desktop 1440x900)...");
  const contextDesktop = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await contextDesktop.newPage();

  await page.goto('http://localhost:8080/index.html', { waitUntil: 'networkidle' });
  
  // Switch to Cutoffs Tab
  await page.click('.panel-tab[data-tab="cutoffs"]');
  await page.waitForTimeout(2500);

  // 1. All Colleges Rendered (No 20 limit)
  const groupRowsCount = await page.evaluate(() => document.querySelectorAll('.table-row-group-header').length);
  console.log(`  1.1 Group rows rendered (default hide Non AIQ): ${groupRowsCount}`);
  if (groupRowsCount === 522) {
    console.log("      -> PASS: Default renders 522 colleges (not limited to 20).");
  } else {
    console.log(`      -> FAIL: Unexpected default row count: ${groupRowsCount}`);
  }

  // 2. Hide Non AIQ toggle
  await page.evaluate(() => document.getElementById('topShowNonAiqCb').click());
  await page.waitForTimeout(500);
  const showAllCount = await page.evaluate(() => document.querySelectorAll('.table-row-group-header').length);
  console.log(`  1.2 Group rows rendered with Show Non AIQ=true: ${showAllCount}`);
  if (showAllCount === 845) {
    console.log("      -> PASS: Renders all 845 colleges when Show Non AIQ is checked.");
  } else {
    console.log(`      -> FAIL: Unexpected total row count: ${showAllCount}`);
  }
  // Re-enable default
  await page.evaluate(() => document.getElementById('topShowNonAiqCb').click());
  await page.waitForTimeout(300);

  // 3. College Search
  await page.fill('#cutoffTopSearchInput', 'Burdwan');
  await page.dispatchEvent('#cutoffTopSearchInput', 'blur');
  await page.waitForTimeout(300);
  const searchMatchCount = await page.evaluate(() => document.querySelectorAll('.table-row-group-header').length);
  console.log(`  1.3 Search 'Burdwan' matches: ${searchMatchCount}`);
  if (searchMatchCount === 1) {
    console.log("      -> PASS: College search filters accurately.");
  } else {
    console.log(`      -> FAIL: Expected 1 match for Burdwan, got ${searchMatchCount}`);
  }
  await page.fill('#cutoffTopSearchInput', '');
  await page.dispatchEvent('#cutoffTopSearchInput', 'blur');
  await page.waitForTimeout(300);

  // 4. Rank input (Arbitrary length rank & Blur submit)
  await page.fill('#cutoffTopRankInput', '1450');
  await page.dispatchEvent('#cutoffTopRankInput', 'blur');
  await page.waitForTimeout(400);

  const predictorBadge = await page.evaluate(() => {
    const el = document.querySelector('.table-row-group-header .badge');
    return el ? el.textContent.trim() : 'N/A';
  });
  console.log(`  1.4 Rank '1450' blur submit result badge: ${predictorBadge}`);

  // 5. Expand row via Expand Arrow ONLY
  const firstCollegeId = await page.evaluate(() => {
    const btn = document.querySelector('#viewCutoffs .group-expand-btn');
    return btn ? btn.getAttribute('data-toggle-college') : null;
  });

  await page.evaluate(() => {
    const btn = document.querySelector('#viewCutoffs .group-expand-btn');
    if (btn) btn.click();
  });
  await page.waitForTimeout(300);

  const childRowsVisible = await page.evaluate((colId) => {
    return document.querySelectorAll(`#viewCutoffs .child-row-${colId}:not(.is-hidden)`).length;
  }, firstCollegeId);

  console.log(`  1.5 Visible child rows after clicking expand arrow: ${childRowsVisible}`);
  if (childRowsVisible > 0) {
    console.log("      -> PASS: Chevron arrow expands child rows without refreshing table.");
  } else {
    console.log("      -> FAIL: Expand arrow failed to show child rows.");
  }

  // 6. Collapse All button
  await page.evaluate(() => document.getElementById('collapseAllRowsBtn').click());
  await page.waitForTimeout(300);
  const remainingChildVisible = await page.evaluate((colId) => {
    return document.querySelectorAll(`#viewCutoffs .child-row-${colId}:not(.is-hidden)`).length;
  }, firstCollegeId);

  if (remainingChildVisible === 0) {
    console.log("  1.6 -> PASS: Collapse All hides all child rows.");
  } else {
    console.log("  1.6 -> FAIL: Collapse All failed to hide child rows.");
  }

  await contextDesktop.close();

  // -------------------------------------------------------------------
  // TEST 2: MOBILE VIEWPORT & MIDPOINT FULLSCREEN TRIGGER
  // -------------------------------------------------------------------
  console.log("\n[TEST 2] Auditing Mobile Responsive Viewport & Midpoint Fullscreen Trigger (375x812)...");
  const contextMobile = await browser.newContext({ viewport: { width: 375, height: 812 } });
  const pageMobile = await contextMobile.newPage();

  await pageMobile.goto('http://localhost:8080/index.html', { waitUntil: 'networkidle' });
  await pageMobile.click('.panel-tab[data-tab="cutoffs"]');
  await pageMobile.waitForTimeout(2000);

  // Scroll down so predictor control card midpoint reaches top of viewport
  const cardMidpointScrollY = await pageMobile.evaluate(() => {
    const card = document.querySelector('.cutoff-controls-card');
    if (!card) return 0;
    const rect = card.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    return scrollTop + rect.top + (rect.height / 2) + 10;
  });

  console.log(`  2.1 Calculated predictor control card midpoint scroll Y: ${cardMidpointScrollY}`);
  await pageMobile.evaluate((targetY) => window.scrollTo(0, targetY), cardMidpointScrollY);
  await pageMobile.waitForTimeout(500);

  const isFullscreenActive = await pageMobile.evaluate(() => document.body.classList.contains('table-fullscreen-active'));
  console.log(`  2.2 Fullscreen active after card midpoint reaches viewport top: ${isFullscreenActive}`);
  if (isFullscreenActive) {
    console.log("      -> PASS: Automatic mobile fullscreen triggered correctly at midpoint scroll.");
  } else {
    console.log("      -> FAIL: Mobile midpoint scroll trigger did not activate fullscreen.");
  }

  // Exit fullscreen via exit button
  await pageMobile.evaluate(() => document.getElementById('exitFullscreenBtn').click());
  await pageMobile.waitForTimeout(300);
  const isFullscreenAfterExit = await pageMobile.evaluate(() => document.body.classList.contains('table-fullscreen-active'));
  if (!isFullscreenAfterExit) {
    console.log("  2.3 -> PASS: Exit Fullscreen button dismisses mobile table fullscreen.");
  }

  await contextMobile.close();

  // -------------------------------------------------------------------
  // TEST 3: THEME INITIALIZATION & TOGGLE AUDIT
  // -------------------------------------------------------------------
  console.log("\n[TEST 3] Auditing Theme System & Dark/Light Toggle...");
  const contextTheme = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const pageTheme = await contextTheme.newPage();

  await pageTheme.goto('http://localhost:8080/index.html', { waitUntil: 'networkidle' });

  // Initial theme (default dark)
  const theme1 = await pageTheme.evaluate(() => document.documentElement.getAttribute('data-theme'));
  console.log(`  3.1 Initial Theme: ${theme1}`);

  // Click Theme Toggle -> Light
  await pageTheme.click('#themeToggleBtn');
  await pageTheme.waitForTimeout(300);
  const theme2 = await pageTheme.evaluate(() => document.documentElement.getAttribute('data-theme'));
  console.log(`  3.2 Theme after toggle click: ${theme2}`);

  // Reload page -> verify persisted light mode
  await pageTheme.reload({ waitUntil: 'networkidle' });
  const themePersisted = await pageTheme.evaluate(() => document.documentElement.getAttribute('data-theme'));
  console.log(`  3.3 Persisted Theme after reload: ${themePersisted}`);
  if (themePersisted === 'light') {
    console.log("      -> PASS: Theme state is correctly persisted across page refreshes.");
  }

  await contextTheme.close();
  await browser.close();

  console.log("\n=============================================================");
  console.log("      FULL PLAYWRIGHT AUTOMATED AUDIT COMPLETED CLEANLY      ");
  console.log("=============================================================");
})();
