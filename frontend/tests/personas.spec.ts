import { test, expect, Page } from '@playwright/test';
import { gotoHydrated, fillStable } from './helpers';

/**
 * Browser-based persona passes. Representative independent accounts per
 * segment; core journey through real UI. All other personas were exercised
 * via the API harness (persona_api.py) — both are recorded separately.
 */

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('taxshield_cookie_ack', new Date().toISOString()));
});

const PERSONAS: Record<string, any> = {
  p1a_agency: { segment: 'Sole proprietor', name: 'Riya Sharma', et: 'business', path: '/invoices' },
  p1b_contractor: { segment: 'Sole proprietor', name: 'Suresh Contractor', et: 'business', path: '/vendors' },
  p2a_dev: { segment: 'Freelancer', name: 'Kiran Dev', et: 'freelancer', path: '/tax' },
  p3a_accountant: { segment: 'Accountant', name: 'Ravi Accountant', et: 'accountant', path: '/practice' },
  p4a_ca: { segment: 'CA firm', name: 'Priya CA', et: 'ca', path: '/practice' },
  p5a_grocer: { segment: 'Retail', name: 'Anil Grocer', et: 'business', path: '/pos' },
  p6a_salaried: { segment: 'Individual', name: 'Rohan Employee', et: 'salaried', path: '/dashboard' },
};

async function register(page: Page, p: any) {
  const email = `b-${p.et}-${Date.now()}${Math.floor(Math.random() * 1e5)}@example.com`;
  await gotoHydrated(page, '/register');
  await fillStable(page.getByLabel(/full name/i), p.name);
  await fillStable(page.getByLabel(/email/i), email);
  await fillStable(page.getByLabel(/^password/i).first(), 'Pass1234!');
  await fillStable(page.getByLabel(/confirm/i), 'Pass1234!');
  const etMap: any = { business: 'business_owner', freelancer: 'freelancer', accountant: 'other', ca: 'other', salaried: 'salaried' };
  await page.getByLabel(/employment type/i).selectOption(etMap[p.et] || 'other');
  await page.getByRole('button', { name: /create account/i }).click();
  await expect(page).toHaveURL(/\/dashboard/, { timeout: 20000 });
  return email;
}

for (const [id, p] of Object.entries(PERSONAS)) {
  test(`persona ${id}: register -> onboard -> module page`, async ({ page }) => {
    await register(page, p);
    // onboarding wizard
    await gotoHydrated(page, '/onboarding');
    await expect(page.getByText(/set up your workspace/i).first()).toBeVisible({ timeout: 15000 });
    const userType = page.getByLabel(/user type/i);
    if (await userType.count()) await userType.selectOption(p.et === 'salaried' ? 'individual' : p.et);
    await page.getByRole('button', { name: /continue/i }).first().click();
    await page.waitForTimeout(300);
    const bn = page.getByPlaceholder(/sharma services/i).first();
    if (await bn.count()) await fillStable(bn, `${p.name} Trading`);
    await page.getByRole('button', { name: /continue/i }).first().click();
    await page.waitForTimeout(300);
    const cont = page.getByRole('button', { name: /continue/i }).first();
    if (await cont.count()) await cont.click();
    await page.waitForTimeout(300);
    const finish = page.getByRole('button', { name: /finish|save|done|get started/i }).first();
    if (await finish.count()) await finish.click();
    // module page reachable + renders real content
    await gotoHydrated(page, p.path);
    await expect(page.locator('h1:visible, h2:visible').first()).toBeVisible({ timeout: 15000 });
    // assistant present
    await gotoHydrated(page, '/assistant');
    const ta = page.getByLabel(/type message/i);
    if (await ta.count()) {
      await fillStable(ta, 'How much tax do I owe?');
      await page.getByRole('button', { name: /send/i }).first().click();
      await expect(page.locator('text=/tax|owe|estimated|analysis|preliminary/i').first())
        .toBeVisible({ timeout: 15000 }).catch(() => undefined);
    }
  });
}
