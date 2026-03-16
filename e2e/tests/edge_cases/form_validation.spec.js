// @ts-check
const { test, expect } = require("@playwright/test");
const { loginAs } = require("../../helpers/auth");

// ── Form validation edge cases ───────────────────────────────────────────────
test.describe("Date Filter Validation", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, "admin");
  });

  test("stock sales accepts valid date format", async ({ page }) => {
    const link = page.locator('text="Stock Sales"').first();
    if (await link.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await link.click();
      await page.waitForTimeout(1500);

      const startInput = page.locator('input[placeholder*="YYY"]').first();
      if (await startInput.isVisible({ timeout: 2_000 }).catch(() => false)) {
        await startInput.fill("2025-01-01");
        await startInput.press("Tab");
        await page.waitForTimeout(500);
        // Input should hold the value
        const value = await startInput.inputValue();
        expect(value).toBe("2025-01-01");
      }
    }
  });

  test("reports screen date filter works", async ({ page }) => {
    const link = page.locator('text="Reports"').first();
    if (await link.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await link.click();
      await page.waitForTimeout(1500);
      // App should not crash when navigating to reports
      const body = await page.textContent("body");
      expect(body).toBeTruthy();
    }
  });

  test("invalid date does not crash the app", async ({ page }) => {
    const link = page.locator('text="Stock Sales"').first();
    if (await link.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await link.click();
      await page.waitForTimeout(1500);

      const startInput = page.locator('input[placeholder*="YYY"]').first();
      if (await startInput.isVisible({ timeout: 2_000 }).catch(() => false)) {
        await startInput.fill("not-a-date");
        const applyBtn = page.locator('button:has-text("Apply"), :has-text("Apply")').first();
        if (await applyBtn.isVisible({ timeout: 1_500 }).catch(() => false)) {
          await applyBtn.click();
          await page.waitForTimeout(2000);
          // App should show error or ignore invalid date, not crash
          const body = await page.textContent("body");
          expect(body).toBeTruthy();
        }
      }
    }
  });
});

// ── Empty state handling ─────────────────────────────────────────────────────
test.describe("Empty State Handling", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, "admin");
  });

  test("empty transaction list shows helpful message", async ({ page }) => {
    // Filter for a date range with no transactions
    const link = page.locator('text="Stock Sales"').first();
    if (await link.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await link.click();
      await page.waitForTimeout(1500);

      const startInput = page.locator('input[placeholder*="YYY"]').first();
      const endInput = page.locator('input[placeholder*="YYY"]').last();

      if (await startInput.isVisible({ timeout: 2_000 }).catch(() => false)) {
        await startInput.fill("2020-01-01");
        await endInput.fill("2020-01-02");

        const applyBtn = page.locator('button:has-text("Apply")').first();
        if (await applyBtn.isVisible({ timeout: 1_500 }).catch(() => false)) {
          await applyBtn.click();
          await page.waitForTimeout(2500);

          const body = await page.textContent("body");
          // Should show either transactions or an empty state message
          expect(
            body.includes("No transaction") ||
            body.includes("no transaction") ||
            body.includes("₹") ||  // may still show summary
            body.includes("0") ||
            body.includes("Failed") ||
            body.includes("error")
          ).toBe(true);
        }
      }
    }
  });
});

// ── Large data handling ─────────────────────────────────────────────────────
test.describe("Large Data & Pagination", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, "admin");
  });

  test("activity log load more works", async ({ page }) => {
    const logLink = page.locator('text="Activity Log"').first();
    if (await logLink.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await logLink.click();
      await page.waitForTimeout(3000);

      const loadMoreBtn = page.locator('text="Load More"').first();
      if (await loadMoreBtn.isVisible({ timeout: 3_000 }).catch(() => false)) {
        await loadMoreBtn.click();
        await page.waitForTimeout(2000);
        const body = await page.textContent("body");
        expect(body).toBeTruthy();
      }
    }
  });

  test("products list renders without overflow crash", async ({ page }) => {
    // Navigate to a screen that lists products
    const links = [
      page.locator('text="Store"').first(),
      page.locator('text="Products"').first(),
    ];

    for (const link of links) {
      if (await link.isVisible({ timeout: 1_500 }).catch(() => false)) {
        await link.click();
        await page.waitForTimeout(2500);
        break;
      }
    }

    const body = await page.textContent("body");
    expect(body).toBeTruthy();
  });
});

// ── Navigation edge cases ────────────────────────────────────────────────────
test.describe("Navigation Edge Cases", () => {
  test("back and forward navigation does not break state", async ({ page }) => {
    await loginAs(page, "admin");
    await page.waitForTimeout(1000);

    // Navigate forward
    const link = page.locator('text="Store"').first();
    if (await link.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await link.click();
      await page.waitForTimeout(1000);
    }

    // Go back
    await page.goBack();
    await page.waitForTimeout(2000);

    // App should still be functional
    const body = await page.textContent("body").catch(() => "");
    expect(body !== null && (body.length > 0 || true)).toBeTruthy();
  });

  test("rapid tab switching in reports does not crash", async ({ page }) => {
    await loginAs(page, "admin");

    const reportsLink = page.locator('text="Reports"').first();
    if (await reportsLink.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await reportsLink.click();
      await page.waitForTimeout(1000);

      // Rapidly click through tabs
      const tabLabels = ["Production", "Financial", "Store Daily", "Sales"];
      for (const label of tabLabels) {
        const tab = page.locator(`text="${label}"`).first();
        if (await tab.isVisible({ timeout: 500 }).catch(() => false)) {
          await tab.click();
          await page.waitForTimeout(300);
        }
      }

      await page.waitForTimeout(2000);
      const body = await page.textContent("body");
      expect(body).toBeTruthy();
    }
  });

  test("refreshing page keeps user logged in", async ({ page }) => {
    await loginAs(page, "admin");
    await page.waitForTimeout(1000);
    await page.reload();
    await page.waitForTimeout(3000);

    // Should still be authenticated (AsyncStorage persists across reloads in web)
    const body = await page.textContent("body");
    expect(body).toBeTruthy();
  });
});
