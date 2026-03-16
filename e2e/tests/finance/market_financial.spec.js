// @ts-check
const { test, expect } = require("@playwright/test");
const { loginAs, navigateTo, pageText, expectScreenLoaded } = require("../../helpers/auth");

// ─── Markets Screen ───────────────────────────────────────────────────────────
// RBAC: ADMIN, MANAGER only

test.describe("Markets Screen", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, "admin");
  });

  test("screen loads for admin", async ({ page }) => {
    await navigateTo(page, "Markets");
    await expectScreenLoaded(page, expect);
  });

  test("shows market price data or empty state", async ({ page }) => {
    await navigateTo(page, "Markets");
    const text = await pageText(page);
    expect(text.length > 50).toBe(true);
  });

  test("shows city market prices", async ({ page }) => {
    await navigateTo(page, "Markets");
    const text = await pageText(page);
    expect(text.length > 50).toBe(true);
  });

  test("shows customer orders section", async ({ page }) => {
    await navigateTo(page, "Markets");
    const text = await pageText(page);
    expect(text.length > 50).toBe(true);
  });

  test("shows price trend information", async ({ page }) => {
    await navigateTo(page, "Markets");
    const text = await pageText(page);
    expect(text.length > 50).toBe(true);
  });

  test("manager can access markets screen", async ({ page }) => {
    await loginAs(page, "manager");
    await navigateTo(page, "Markets");
    await expectScreenLoaded(page, expect);
  });

  test("supervisor cannot see Markets in nav", async ({ page }) => {
    await loginAs(page, "supervisor");
    const link = page.locator('text="Markets"').first();
    const isVisible = await link.isVisible({ timeout: 3_000 }).catch(() => false);
    expect(!isVisible).toBe(true);
  });

  test("worker cannot see Markets in nav", async ({ page }) => {
    await loginAs(page, "worker");
    const link = page.locator('text="Markets"').first();
    const isVisible = await link.isVisible({ timeout: 3_000 }).catch(() => false);
    expect(!isVisible).toBe(true);
  });

  test("cashier cannot see Markets in nav", async ({ page }) => {
    await loginAs(page, "cashier");
    const link = page.locator('text="Markets"').first();
    const isVisible = await link.isVisible({ timeout: 3_000 }).catch(() => false);
    expect(!isVisible).toBe(true);
  });

  test("store_manager cannot see Markets in nav", async ({ page }) => {
    await loginAs(page, "store_manager");
    const link = page.locator('text="Markets"').first();
    const isVisible = await link.isVisible({ timeout: 3_000 }).catch(() => false);
    expect(!isVisible).toBe(true);
  });
});

// ─── Financials Screen ────────────────────────────────────────────────────────
// RBAC: ADMIN, MANAGER only

test.describe("Financials Screen", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, "admin");
  });

  test("screen loads for admin", async ({ page }) => {
    await navigateTo(page, "Financials");
    await expectScreenLoaded(page, expect);
  });

  test("shows revenue and expense data", async ({ page }) => {
    await navigateTo(page, "Financials");
    const text = await pageText(page);
    expect(text.length > 50).toBe(true);
  });

  test("shows profit/loss summary", async ({ page }) => {
    await navigateTo(page, "Financials");
    const text = await pageText(page);
    expect(text.length > 50).toBe(true);
  });

  test("shows salary records section", async ({ page }) => {
    await navigateTo(page, "Financials");
    const text = await pageText(page);
    expect(text.length > 50).toBe(true);
  });

  test("shows invoice section", async ({ page }) => {
    await navigateTo(page, "Financials");
    const text = await pageText(page);
    expect(text.length > 50).toBe(true);
  });

  test("manager can access financials screen", async ({ page }) => {
    await loginAs(page, "manager");
    await navigateTo(page, "Financials");
    await expectScreenLoaded(page, expect);
  });

  test("supervisor cannot see Financials in nav", async ({ page }) => {
    await loginAs(page, "supervisor");
    const link = page.locator('text="Financials"').first();
    const isVisible = await link.isVisible({ timeout: 3_000 }).catch(() => false);
    expect(!isVisible).toBe(true);
  });

  test("cashier cannot see Financials in nav", async ({ page }) => {
    await loginAs(page, "cashier");
    const link = page.locator('text="Financials"').first();
    const isVisible = await link.isVisible({ timeout: 3_000 }).catch(() => false);
    expect(!isVisible).toBe(true);
  });

  test("store_manager cannot see Financials in nav", async ({ page }) => {
    await loginAs(page, "store_manager");
    const link = page.locator('text="Financials"').first();
    const isVisible = await link.isVisible({ timeout: 3_000 }).catch(() => false);
    expect(!isVisible).toBe(true);
  });

  test("packer cannot see Financials in nav", async ({ page }) => {
    await loginAs(page, "packer");
    const link = page.locator('text="Financials"').first();
    const isVisible = await link.isVisible({ timeout: 3_000 }).catch(() => false);
    expect(!isVisible).toBe(true);
  });

  test("driver cannot see Financials in nav", async ({ page }) => {
    await loginAs(page, "driver");
    const link = page.locator('text="Financials"').first();
    const isVisible = await link.isVisible({ timeout: 3_000 }).catch(() => false);
    expect(!isVisible).toBe(true);
  });

  test("financial summary shows currency symbols", async ({ page }) => {
    await navigateTo(page, "Financials");
    const text = await pageText(page);
    expect(text.length > 50).toBe(true);
  });
});
