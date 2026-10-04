import { Page } from '@playwright/test';

/**
 * Navigate and wait until React hydration is done.
 * WebKit hydrates slower than Chromium: filling a controlled input before
 * hydration causes React to reset it to its server value on mount, which
 * silently breaks form flows. networkidle is the reliable gate here.
 */
export async function gotoHydrated(page: Page, path: string) {
  await page.goto(path);
  await page.waitForLoadState('networkidle').catch(() => undefined);
}

/** fill() + verify: retry once if hydration reset the controlled value. */
export async function fillStable(locator: ReturnType<Page['getByLabel']>, value: string) {
  await locator.fill(value);
  if ((await locator.inputValue()) !== value) {
    await locator.fill(value);
  }
}
