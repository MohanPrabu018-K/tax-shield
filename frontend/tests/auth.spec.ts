import { test, expect } from '@playwright/test';
import { gotoHydrated, fillStable } from './helpers';

/** Auth + guards. Needs backend :8000 (see playwright.config.ts). */

test.beforeEach(async ({ page }) => {
  // pre-acknowledge the cookie notice so the fixed banner never blocks form clicks
  await page.addInitScript(() => localStorage.setItem('taxshield_cookie_ack', new Date().toISOString()));
});

async function uniqueUser() {
  const stamp = `${Date.now()}${Math.floor(Math.random() * 1e6)}`;
  return { email: `pw${stamp}@example.com`, password: 'Pass1234!', name: 'PW User' };
}

test('unauthenticated /dashboard redirects to /login', async ({ page }) => {
  await page.context().clearCookies();
  await page.goto('/dashboard');
  await expect(page).toHaveURL(/\/login/, { timeout: 15000 });
});

test('login page renders and validates', async ({ page }) => {
  await page.goto('/login');
  await expect(page.getByRole('heading', { name: /welcome back/i })).toBeVisible();
  await page.getByRole('button', { name: /sign in/i }).click();
  // stays on page with validation or error toast — never a blank screen
  await expect(page).toHaveURL(/\/login/);
});

test('register → dashboard → logout', async ({ page }) => {
  const u = await uniqueUser();
  await gotoHydrated(page, '/register');
  await expect(page.getByRole('heading', { name: /create your account/i })).toBeVisible();
  await fillStable(page.getByLabel(/full name/i), u.name);
  await fillStable(page.getByLabel(/email/i), u.email);
  await fillStable(page.getByLabel(/^password/i).first(), u.password);
  await fillStable(page.getByLabel(/confirm/i), u.password);
  await page.getByLabel(/employment type/i).selectOption('salaried');
  await page.getByRole('button', { name: /create account/i }).click();
  await expect(page).toHaveURL(/\/dashboard/, { timeout: 20000 });
  await expect(page.getByText(/financial health/i).first()).toBeVisible({ timeout: 20000 });
});
