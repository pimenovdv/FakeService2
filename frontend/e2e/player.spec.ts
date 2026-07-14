import { test, expect } from '@playwright/test';

test('completes service_1 flow', async ({ page }) => {
  await page.goto('/service_1/1');

  // Wait for loading options to disappear
  await expect(page.locator('.options-loading')).toHaveCount(0);

  // Fill first screen
  await page.locator('#name_input').fill('John Doe');

  // Use page.selectOption by value
  await page.locator('#country_input').selectOption({ label: 'United States' });
  await page.locator('body').click(); // blur to trigger validation

  await page.locator('button', { hasText: 'Next' }).click();

  // Wait for screen 2
  await expect(page.locator('h1')).toContainText('Confirm Details');

  // Ensure our new Checkbox Component works!
  await page.locator('#confirmation_checkbox').check();

  await page.locator('button', { hasText: 'Submit' }).click();
});
