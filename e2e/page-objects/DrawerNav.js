/**
 * Page Object for the Drawer Navigation.
 */

class DrawerNav {
  constructor(page) {
    this.page = page;
  }

  async open() {
    // Try hamburger menu or swipe right
    const hamburger = this.page.locator(
      '[aria-label="menu"], [aria-label="open drawer"], button:has-text("☰")'
    ).first();
    if (await hamburger.isVisible({ timeout: 2_000 }).catch(() => false)) {
      await hamburger.click();
    } else {
      // Try clicking on the far left to open drawer on mobile/web
      await this.page.mouse.move(10, 300);
      await this.page.mouse.down();
      await this.page.mouse.move(200, 300, { steps: 20 });
      await this.page.mouse.up();
    }
  }

  async navigateTo(screenLabel) {
    await this.open();
    const item = this.page.locator(`text="${screenLabel}"`).first();
    await item.click();
  }

  async isVisible() {
    try {
      await this.page.waitForSelector(
        '[data-testid="drawer"], .drawer, nav',
        { timeout: 3_000 }
      );
      return true;
    } catch {
      return false;
    }
  }
}

module.exports = { DrawerNav };
