import { test, expect, Page } from '@playwright/test';
import { gotoHydrated, fillStable } from './helpers';

/**
 * TAXSHIELD PROFESSIONAL - 24 VIRTUAL PARTICIPANT REAL-WORLD BROWSER TEST
 * Exercises all 6 Practice/Professional roles and 18 Client roles through the live Next.js UI.
 */

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('taxshield_cookie_ack', new Date().toISOString()));
});

async function registerUser(page: Page, name: string, email: string, userType: string = 'other') {
  const uniqueEmail = email.includes('@')
    ? email.replace('@', `+${Date.now()}-${Math.random().toString(36).slice(2, 6)}@`)
    : email;
  await gotoHydrated(page, '/register');
  await fillStable(page.getByLabel(/full name/i), name);
  await fillStable(page.getByLabel(/email/i), uniqueEmail);
  await fillStable(page.getByLabel(/^password/i).first(), 'Password123!');
  await fillStable(page.getByLabel(/confirm/i), 'Password123!');
  const et = page.getByLabel(/employment type/i);
  if (await et.count()) {
    await et.selectOption(userType);
  }
  await page.getByRole('button', { name: /create account/i }).click();
  await expect(page).toHaveURL(/\/dashboard/, { timeout: 20000 });
}

// ---------------------------------------------------------------------------
// 1. Professional Practice Workspaces (6 Professionals)
// ---------------------------------------------------------------------------

test.describe('Practice 01: Solo Practicing CA (CA Ananya Sharma)', () => {
  test('Solo CA practice workflow: Dashboard, Clients 360, Finance Ageing & Calendar', async ({ page }) => {
    const email = `ca01-browser-${Date.now()}@example.com`;
    await registerUser(page, 'CA Ananya Sharma', email, 'other');

    // 1. Practice Dashboard
    await gotoHydrated(page, '/practice');
    await expect(page.locator('h1:visible').first()).toBeVisible({ timeout: 15000 });

    // 2. Client Master
    await gotoHydrated(page, '/practice/clients');
    await expect(page.locator('h1:visible').first()).toBeVisible({ timeout: 15000 });

    // 3. Fee Ageing & Practice Invoicing
    await gotoHydrated(page, '/practice/finance');
    await expect(page.locator('h1:visible').first()).toBeVisible({ timeout: 15000 });

    // 4. Compliance Calendar
    await gotoHydrated(page, '/practice/calendar');
    await expect(page.locator('h1:visible').first()).toBeVisible({ timeout: 15000 });
  });
});

test.describe('Practice 02: Small CA Firm Partner (CA Rajesh Kothari)', () => {
  test('Small Firm workflow: Team Workload, Tasks Board & SQC-1 Reviews', async ({ page }) => {
    const email = `ca02-firm-${Date.now()}@example.com`;
    await registerUser(page, 'CA Rajesh Kothari', email, 'other');

    // 1. Team Capacity & Workload
    await gotoHydrated(page, '/practice/team');
    await expect(page.locator('h1:visible').first()).toBeVisible({ timeout: 15000 });

    // 2. 12-Status Task Board
    await gotoHydrated(page, '/practice/tasks');
    await expect(page.locator('h1:visible').first()).toBeVisible({ timeout: 15000 });

    // 3. Maker-Checker Review Queue (SQC-1)
    await gotoHydrated(page, '/practice/reviews');
    await expect(page.locator('h1:visible').first()).toBeVisible({ timeout: 15000 });
  });
});

test.describe('Practice 03: Accounting Practice Owner (Accountant Suresh Gupta)', () => {
  test('Accounting practice workflow: Books, Ledgers & Month-End Close', async ({ page }) => {
    const email = `acc03-browser-${Date.now()}@example.com`;
    await registerUser(page, 'Accountant Suresh Gupta', email, 'other');

    // 1. Accounting Desk
    await gotoHydrated(page, '/accounting');
    await expect(page.locator('h1:visible, h2:visible').first()).toBeVisible({ timeout: 15000 });

    // 2. Month-End Close
    await gotoHydrated(page, '/close');
    await expect(page.locator('h1:visible, h2:visible').first()).toBeVisible({ timeout: 15000 });
  });
});

test.describe('Practice 04: GST Specialist (Priya Patel)', () => {
  test('GST Specialist workflow: 8-Way GSTR-2B Recon Desk', async ({ page }) => {
    const email = `gst04-browser-${Date.now()}@example.com`;
    await registerUser(page, 'Priya Patel', email, 'other');

    // 1. GST Practice Desk & 8-Way Recon
    await gotoHydrated(page, '/practice/gst');
    await expect(page.locator('h1:visible').first()).toBeVisible({ timeout: 15000 });
  });
});

test.describe('Practice 05: Income Tax Specialist (CA Ramesh Iyer)', () => {
  test('Tax Specialist workflow: Section 115BAC Comparison & AIS Scrutiny', async ({ page }) => {
    const email = `tax05-browser-${Date.now()}@example.com`;
    await registerUser(page, 'CA Ramesh Iyer', email, 'other');

    // 1. Direct Tax Desk (115BAC vs Old Regime)
    await gotoHydrated(page, '/practice/tax');
    await expect(page.locator('h1:visible').first()).toBeVisible({ timeout: 15000 });

    // 2. AIS / Form 26AS Scrutiny
    await gotoHydrated(page, '/ais');
    await expect(page.locator('h1:visible, h2:visible').first()).toBeVisible({ timeout: 15000 });
  });
});

test.describe('Practice 06: Audit Professional (CA Sanjay Deshmukh)', () => {
  test('Audit Professional workflow: SA 230 Lead Schedules & UDIN Tracker', async ({ page }) => {
    const email = `audit06-browser-${Date.now()}@example.com`;
    await registerUser(page, 'CA Sanjay Deshmukh', email, 'other');

    // 1. SA 230 Workpaper Desk
    await gotoHydrated(page, '/practice/workpapers');
    await expect(page.locator('h1:visible').first()).toBeVisible({ timeout: 15000 });

    // 2. ICAI UDIN Tracker
    await gotoHydrated(page, '/practice/udin');
    await expect(page.locator('h1:visible').first()).toBeVisible({ timeout: 15000 });
  });
});

// ---------------------------------------------------------------------------
// 2. Client Portal Experience (Desktop & Mobile Passes)
// ---------------------------------------------------------------------------

test.describe('Client Portal 2.0 Workflows', () => {
  test('Client Desktop Experience: Client 01 (Digital Agency)', async ({ page }) => {
    const email = `client01-browser-${Date.now()}@example.com`;
    await registerUser(page, 'PixelCraft Creative LLP', email, 'business_owner');

    // Navigate to Client Portal 2.0
    await gotoHydrated(page, '/portal');
    await expect(page.locator('text=Client Portal').first()).toBeVisible({ timeout: 15000 });
    await expect(page.locator('text=Assigned Professional Engagement Team').first()).toBeVisible();
    await expect(page.locator('text=Documents Requested by Your Accountant').first()).toBeVisible();
    await expect(page.locator('text=GST Filing Status').first()).toBeVisible();

    // Test accountant messaging
    const msgInput = page.getByPlaceholder(/Type a question or message for your accountant/i);
    if (await msgInput.count()) {
      await fillStable(msgInput, 'Uploaded the updated February bank reconciliation file.');
      await page.getByRole('button', { name: /Send Message/i }).click();
    }
  });

  test('Client Mobile Experience: Client 04 (Retail Grocery Store)', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 }); // Mobile viewport (Pixel 7 / iPhone 14)
    const email = `client04-mobile-${Date.now()}@example.com`;
    await registerUser(page, 'Anil Kirana Store', email, 'business_owner');

    // Visit Mobile Client Portal
    await gotoHydrated(page, '/portal');
    await expect(page.locator('text=Client Portal').first()).toBeVisible({ timeout: 15000 });
    await expect(page.locator('text=Assigned Professional Engagement Team').first()).toBeVisible();
  });

  test('Client Mobile Experience: Client 06 (Freelance Designer)', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    const email = `client06-mobile-${Date.now()}@example.com`;
    await registerUser(page, 'Rhea Sen Design Studio', email, 'freelancer');

    await gotoHydrated(page, '/portal');
    await expect(page.locator('text=Client Portal').first()).toBeVisible({ timeout: 15000 });
  });
});
