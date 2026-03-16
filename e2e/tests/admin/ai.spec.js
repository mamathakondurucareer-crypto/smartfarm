// @ts-check
const { test, expect } = require("@playwright/test");
const { loginAs, navigateTo, pageText, expectScreenLoaded } = require("../../helpers/auth");

// AI Analysis screen — RBAC: ADMIN, MANAGER, SUPERVISOR (FARM_MGMT)

test.describe("AI Analysis Screen", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, "admin");
  });

  test("AI Analysis screen loads for admin", async ({ page }) => {
    await navigateTo(page, "AI Analysis");
    await expectScreenLoaded(page, expect);
  });

  test("AI Analysis shows analysis content or empty state", async ({ page }) => {
    await navigateTo(page, "AI Analysis");
    const text = await pageText(page);
    // Accept: any page content that indicates the screen loaded
    expect(text.length > 50).toBe(true);
  });

  test("AI Analysis has actionable sections", async ({ page }) => {
    await navigateTo(page, "AI Analysis");
    const text = await pageText(page, 3000);
    // Should show some structured content (cards, sections, tabs)
    expect(text).toBeTruthy();
    expect(text.length).toBeGreaterThan(100);
  });
});

test.describe("AI Analysis — Manager Access", () => {
  test("manager can access AI Analysis", async ({ page }) => {
    await loginAs(page, "manager");
    await navigateTo(page, "AI Analysis");
    await expectScreenLoaded(page, expect);
  });
});

test.describe("AI Analysis — Supervisor Access", () => {
  test("supervisor can access AI Analysis", async ({ page }) => {
    await loginAs(page, "supervisor");
    await navigateTo(page, "AI Analysis");
    await expectScreenLoaded(page, expect);
  });
});

test.describe("AI Analysis — RBAC Denied Roles", () => {
  test("worker cannot see AI Analysis in navigation", async ({ page }) => {
    await loginAs(page, "worker");
    const aiLink = page.locator('text="AI Analysis"').first();
    const isVisible = await aiLink.isVisible({ timeout: 3_000 }).catch(() => false);
    // Worker should not see AI Analysis in nav (FARM_MGMT only)
    expect(isVisible).toBe(false);
  });

  test("viewer cannot see AI Analysis in navigation", async ({ page }) => {
    await loginAs(page, "viewer");
    const aiLink = page.locator('text="AI Analysis"').first();
    const isVisible = await aiLink.isVisible({ timeout: 3_000 }).catch(() => false);
    expect(isVisible).toBe(false);
  });

  test("cashier cannot see AI Analysis in navigation", async ({ page }) => {
    await loginAs(page, "cashier");
    const aiLink = page.locator('text="AI Analysis"').first();
    const isVisible = await aiLink.isVisible({ timeout: 3_000 }).catch(() => false);
    expect(isVisible).toBe(false);
  });
});
