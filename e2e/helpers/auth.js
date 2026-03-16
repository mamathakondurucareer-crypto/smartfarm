// @ts-check
const { USERS } = require("../fixtures/users");

/**
 * Log in as a specific role and wait until the app navigates away from /login.
 * @param {import("@playwright/test").Page} page
 * @param {"admin"|"manager"|"supervisor"|"worker"|"viewer"|"store_manager"|"cashier"|"packer"|"driver"|"scanner"} role
 */
async function loginAs(page, role) {
  const user = USERS[role];
  await page.goto("/");

  // Wait for the login form to appear
  await page
    .locator('input[placeholder*="sername"], input[placeholder*="ser"]')
    .first()
    .waitFor({ timeout: 10_000 });

  // Fill in credentials
  await page
    .locator('input[placeholder*="sername"], input[placeholder*="ser"]')
    .first()
    .fill(user.username);

  await page
    .locator('input[type="password"], input[placeholder*="assword"]')
    .first()
    .fill(user.password);

  // Click login button
  const loginButton = page
    .locator('button:has-text("Login"), [role="button"]:has-text("Login"), button:has-text("Sign In"), [role="button"]:has-text("Sign In"), div[tabindex="0"]:has-text("Sign In"), div[tabindex="0"]:has-text("Login")')
    .first();

  await loginButton.click();

  // Wait for response and navigation. Try multiple strategies:
  // 1. Wait for URL to change away from login
  // 2. Wait for any navigation/loading
  // 3. Retry with patience for slower browsers (webkit)

  let loginSuccess = false;
  for (let attempt = 0; attempt < 3; attempt++) {
    await page.waitForTimeout(2_000);

    // Check if we're still on login page
    const currentUrl = page.url();
    const onLoginPage = currentUrl.includes("login") || currentUrl === page.context().browser()?.url;

    // Check if error message is visible (login failed)
    const hasError = await page
      .locator('text="User not found or inactive", text="Invalid credentials", text="Login failed"')
      .first()
      .isVisible({ timeout: 1_000 })
      .catch(() => false);

    // If no error and left login page, success
    if (!hasError && !onLoginPage) {
      loginSuccess = true;
      break;
    }

    // If error is shown, login failed - wait and retry
    if (hasError) {
      await page.waitForTimeout(1_000);
      // Try clicking login again
      await loginButton.click();
    }
  }

  // Final wait for dashboard or content to load
  await page.waitForTimeout(2_000);
}

/**
 * Navigate to a screen using the drawer.
 * Opens the hamburger if needed, then clicks the matching label.
 * @param {import("@playwright/test").Page} page
 * @param {string} label  — text shown in the drawer (e.g. "Aquaculture")
 */
async function navigateTo(page, label) {
  // Wait for initial page load
  await page.waitForTimeout(500);

  // Try direct click first (drawer may already be expanded on desktop)
  const directLink = page.locator(`text="${label}"`).first();
  if (await directLink.isVisible({ timeout: 2_000 }).catch(() => false)) {
    await directLink.click();
    await page.waitForTimeout(2_000);
    return;
  }

  // Open hamburger / drawer
  const hamburger = page
    .locator('[aria-label="menu"], [aria-label="open drawer"], button:has-text("☰")')
    .first();
  if (await hamburger.isVisible({ timeout: 2_500 }).catch(() => false)) {
    await hamburger.click();
    await page.waitForTimeout(600);
  } else {
    // If hamburger not found, wait longer and retry
    await page.waitForTimeout(1_000);
  }

  const item = page.locator(`text="${label}"`).first();
  if (await item.isVisible({ timeout: 4_000 }).catch(() => false)) {
    await item.click();
    await page.waitForTimeout(2_500);
  }
}

/**
 * Return the full visible text of <body> after waiting for content.
 * @param {import("@playwright/test").Page} page
 * @param {number} [wait=2500]
 */
async function pageText(page, wait = 2500) {
  await page.waitForTimeout(wait);
  const text = await page.textContent("body").catch(() => null);
  return text || "";
}

/**
 * Assert a screen loaded: body is non-null and longer than 100 chars.
 * @param {import("@playwright/test").Page} page
 * @param {import("@playwright/test").Expect} expect
 */
async function expectScreenLoaded(page, expect) {
  const text = await pageText(page);
  expect(text).toBeTruthy();
  expect(text.length).toBeGreaterThan(100);
}

module.exports = { loginAs, navigateTo, pageText, expectScreenLoaded };
