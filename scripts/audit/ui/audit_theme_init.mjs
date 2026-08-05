import { chromium } from 'playwright';

(async () => {
  console.log("=============================================================");
  console.log("       THEME INITIALIZATION & ANTI-FLASH AUDIT SUITE         ");
  console.log("=============================================================");

  const browser = await chromium.launch({ headless: true });

  // Helper to test theme init on page navigation
  async function testThemeInit(name, osScheme, savedValue, expectedTheme) {
    const context = await browser.newContext({
      colorScheme: osScheme,
      viewport: { width: 1280, height: 800 }
    });
    const page = await context.newPage();

    if (savedValue !== null) {
      await page.addInitScript((val) => {
        localStorage.setItem('nexdoc_theme', val);
      }, savedValue);
    } else {
      await page.addInitScript(() => {
        localStorage.removeItem('nexdoc_theme');
      });
    }

    await page.goto('http://localhost:8080/index.html', { waitUntil: 'domcontentloaded' });

    // Read data-theme attribute IMMEDIATELY on domcontentloaded (before rendering frames)
    const initialTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
    console.log(`[TEST] ${name}`);
    console.log(`       OS: ${osScheme} | Saved: ${savedValue} -> Result: '${initialTheme}' (Expected: '${expectedTheme}')`);

    if (initialTheme === expectedTheme) {
      console.log("       -> PASS");
    } else {
      console.log("       -> FAIL: Theme mismatch!");
      process.exit(1);
    }

    await context.close();
  }

  // 1. No saved preference + OS dark -> dark
  await testThemeInit("No saved + OS dark", "dark", null, "dark");

  // 2. No saved preference + OS light -> light
  await testThemeInit("No saved + OS light", "light", null, "light");

  // 3. Saved dark + OS light -> dark
  await testThemeInit("Saved dark + OS light", "light", "dark", "dark");

  // 4. Saved light + OS dark -> light
  await testThemeInit("Saved light + OS dark", "dark", "light", "light");

  // 5. Repeated Toggles & Refresh Test
  console.log("\n[TEST] Auditing Repeated Toggles & Refreshes...");
  const contextToggle = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const pageToggle = await contextToggle.newPage();
  await pageToggle.goto('http://localhost:8080/index.html', { waitUntil: 'networkidle' });

  for (let i = 1; i <= 4; i++) {
    const prevTheme = await pageToggle.evaluate(() => document.documentElement.getAttribute('data-theme'));
    await pageToggle.click('#themeToggleBtn');
    await pageToggle.waitForTimeout(100);
    const nextTheme = await pageToggle.evaluate(() => document.documentElement.getAttribute('data-theme'));
    console.log(`  Toggle ${i}: ${prevTheme} -> ${nextTheme}`);
  }

  // Refresh and check persistence
  const themeBeforeRefresh = await pageToggle.evaluate(() => document.documentElement.getAttribute('data-theme'));
  await pageToggle.reload({ waitUntil: 'networkidle' });
  const themeAfterRefresh = await pageToggle.evaluate(() => document.documentElement.getAttribute('data-theme'));
  console.log(`  Refresh Test: Before=${themeBeforeRefresh}, After=${themeAfterRefresh}`);

  if (themeBeforeRefresh === themeAfterRefresh) {
    console.log("  -> PASS: Theme selection persists cleanly across refreshes.");
  } else {
    console.log("  -> FAIL: Theme state was lost on refresh.");
    process.exit(1);
  }

  await contextToggle.close();
  await browser.close();

  console.log("\n=============================================================");
  console.log("    ALL THEME INITIALIZATION & ANTI-FLASH TESTS PASSED       ");
  console.log("=============================================================");
})();
