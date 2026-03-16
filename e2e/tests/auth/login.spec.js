// @ts-check
const { test, expect } = require("@playwright/test");
const { LoginPage } = require("../../page-objects/LoginPage");
const { USERS } = require("../../fixtures/users");

test.describe("Login Screen", () => {
  let loginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });

  // ── Happy paths ────────────────────────────────────────────────────────────
  test("admin can log in", async ({ page }) => {
    await loginPage.login(USERS.admin.username, USERS.admin.password);
    // After login, should redirect away from login page
    await page.waitForURL((url) => !url.pathname.includes("login"), { timeout: 10_000 });
    await expect(page).not.toHaveURL(/login/);
  });

  test("manager can log in", async ({ page }) => {
    await loginPage.login(USERS.manager.username, USERS.manager.password);
    await page.waitForURL((url) => !url.pathname.includes("login"), { timeout: 10_000 });
    await expect(page).not.toHaveURL(/login/);
  });

  test("cashier can log in", async ({ page }) => {
    await loginPage.login(USERS.cashier.username, USERS.cashier.password);
    await page.waitForURL((url) => !url.pathname.includes("login"), { timeout: 10_000 });
    await expect(page).not.toHaveURL(/login/);
  });

  test("store_manager can log in", async ({ page }) => {
    await loginPage.login(USERS.store_manager.username, USERS.store_manager.password);
    await page.waitForURL((url) => !url.pathname.includes("login"), { timeout: 10_000 });
    await expect(page).not.toHaveURL(/login/);
  });

  test("packer can log in", async ({ page }) => {
    await loginPage.login(USERS.packer.username, USERS.packer.password);
    await page.waitForURL((url) => !url.pathname.includes("login"), { timeout: 10_000 });
    await expect(page).not.toHaveURL(/login/);
  });

  test("driver can log in", async ({ page }) => {
    await loginPage.login(USERS.driver.username, USERS.driver.password);
    await page.waitForURL((url) => !url.pathname.includes("login"), { timeout: 10_000 });
    await expect(page).not.toHaveURL(/login/);
  });

  // ── Error paths ────────────────────────────────────────────────────────────
  test("wrong password shows error", async ({ page }) => {
    await loginPage.login(USERS.admin.username, "totally-wrong-password");
    // Should stay on login page or show error
    await page.waitForTimeout(2000);
    const isStillOnLogin = await loginPage.isLoginFormVisible();
    if (!isStillOnLogin) {
      // If redirected, that's unexpected — fail
      expect(isStillOnLogin).toBe(true);
    }
  });

  test("nonexistent user shows error", async ({ page }) => {
    await loginPage.login("ghost_user_does_not_exist", "any-password");
    await page.waitForTimeout(2000);
    const isStillOnLogin = await loginPage.isLoginFormVisible();
    expect(isStillOnLogin).toBe(true);
  });

  test("empty username shows validation", async ({ page }) => {
    await loginPage.fillPassword(USERS.admin.password);
    await loginPage.clickLoginButton();
    await page.waitForTimeout(1000);
    // Should not navigate away
    const isStillOnLogin = await loginPage.isLoginFormVisible();
    expect(isStillOnLogin).toBe(true);
  });

  test("empty password shows validation", async ({ page }) => {
    await loginPage.fillUsername(USERS.admin.username);
    await loginPage.clickLoginButton();
    await page.waitForTimeout(1000);
    const isStillOnLogin = await loginPage.isLoginFormVisible();
    expect(isStillOnLogin).toBe(true);
  });

  test("both fields empty shows validation", async ({ page }) => {
    await loginPage.clickLoginButton();
    await page.waitForTimeout(1000);
    const isStillOnLogin = await loginPage.isLoginFormVisible();
    expect(isStillOnLogin).toBe(true);
  });

  // ── UI checks ──────────────────────────────────────────────────────────────
  test("login form has username and password fields", async ({ page }) => {
    const usernameInput = page.locator(
      'input[placeholder*="sername"], input[placeholder*="ser"]'
    ).first();
    const passwordInput = page.locator(
      'input[type="password"], input[placeholder*="assword"]'
    ).first();
    await expect(usernameInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
  });

  test("page title contains SmartFarm", async ({ page }) => {
    const title = await page.title();
    // Either the page title or visible text should mention SmartFarm
    const bodyText = await page.textContent("body");
    expect(
      title.toLowerCase().includes("smartfarm") ||
      (bodyText && bodyText.toLowerCase().includes("smartfarm"))
    ).toBe(true);
  });
});

// ── Logout ─────────────────────────────────────────────────────────────────
test.describe("Logout", () => {
  test.beforeEach(async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(USERS.admin.username, USERS.admin.password);
    await page.waitForURL((url) => !url.pathname.includes("login"), { timeout: 10_000 });
  });

  test("logged-in user can log out", async ({ page }) => {
    // The app uses "Sign Out" (not "Logout") — rendered as a React Native Web div
    await page.waitForTimeout(1000);
    const signOutBtn = page.getByText("Sign Out", { exact: true });

    if (await signOutBtn.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await signOutBtn.click();
    } else {
      // Open drawer and find sign out
      const hamburger = page.locator(
        '[aria-label="menu"], [aria-label="open drawer"]'
      ).first();
      if (await hamburger.isVisible({ timeout: 2_000 }).catch(() => false)) {
        await hamburger.click();
        await page.waitForTimeout(500);
        await page.getByText("Sign Out", { exact: true }).click();
      }
    }

    await page.waitForTimeout(2000);
    // Should be back on login page or login should be visible
    const loginPage = new LoginPage(page);
    const isOnLogin = await loginPage.isLoginFormVisible();
    // Either redirected to login OR the page title indicates logged out
    expect(isOnLogin || page.url().includes("login")).toBeTruthy();
  });

  test("after logout, protected pages redirect to login", async ({ page }) => {
    // Perform logout
    const logoutBtn = page.getByText("Sign Out", { exact: true });
    if (await logoutBtn.isVisible({ timeout: 3_000 }).catch(() => false)) {
      await logoutBtn.click();
      await page.waitForTimeout(2000);
    }
    // Try navigating to a protected route
    await page.goto("/");
    await page.waitForTimeout(2000);
    const loginPage = new LoginPage(page);
    const isOnLogin = await loginPage.isLoginFormVisible();
    expect(isOnLogin).toBe(true);
  });
});
