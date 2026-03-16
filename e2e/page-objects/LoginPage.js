/**
 * Page Object for the Login screen.
 */

class LoginPage {
  constructor(page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto("/");
    // Wait for the login form to be visible
    await this.page.waitForSelector('input[placeholder*="sername"], input[placeholder*="ser"]', {
      timeout: 10_000,
    });
  }

  async fillUsername(username) {
    const input = this.page.locator('input[placeholder*="sername"], input[placeholder*="ser"]').first();
    await input.fill(username);
  }

  async fillPassword(password) {
    const input = this.page.locator('input[type="password"], input[placeholder*="assword"]').first();
    await input.fill(password);
  }

  async clickLoginButton() {
    // React Native Web renders Pressable as plain <div tabindex="0">, not <button>
    const btn = this.page.locator('button:has-text("Login"), [role="button"]:has-text("Login"), button:has-text("Sign In"), [role="button"]:has-text("Sign In"), div[tabindex="0"]:has-text("Sign In"), div[tabindex="0"]:has-text("Login")').first();
    await btn.click();
  }

  async login(username, password) {
    await this.fillUsername(username);
    await this.fillPassword(password);
    await this.clickLoginButton();
  }

  async isLoginFormVisible() {
    try {
      await this.page.waitForSelector(
        'input[placeholder*="sername"], input[placeholder*="ser"]',
        { timeout: 5_000 }
      );
      return true;
    } catch {
      return false;
    }
  }

  async getErrorMessage() {
    try {
      const errorEl = await this.page.waitForSelector(
        '[data-testid="error"], .error-text, :text-matches("Invalid|incorrect|failed", "i")',
        { timeout: 3_000 }
      );
      return errorEl ? await errorEl.textContent() : null;
    } catch {
      return null;
    }
  }
}

module.exports = { LoginPage };
