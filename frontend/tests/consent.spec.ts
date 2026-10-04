import { test, expect } from '@playwright/test';

/** Cookie notice: shows once, acknowledges, remembered (no pre-ack here). */

test('cookie notice shows once, acknowledges, and is remembered', async ({ page }) => {
  await page.goto('/login');
  const banner = page.getByRole('dialog', { name: 'Cookie notice' });
  await expect(banner).toBeVisible({ timeout: 10000 });
  await page.getByRole('button', { name: 'Understood' }).click();
  await expect(banner).toBeHidden();
  await page.reload();
  await expect(page.getByRole('dialog', { name: 'Cookie notice' })).toBeHidden();
  const ack = await page.evaluate(() => localStorage.getItem('taxshield_cookie_ack'));
  expect(ack).toBeTruthy();
});
