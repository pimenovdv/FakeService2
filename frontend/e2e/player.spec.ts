import { test, expect } from '@playwright/test';

test('Player component user flow - service_1', async ({ page }) => {
  // Navigate to service_1 screen 1
  await page.goto('/service_1/1');

  // Wait for the main container to be visible (screen loaded)
  const appPlayer = page.locator('app-player');
  await expect(appPlayer).toBeVisible();

  // Wait for header text to verify screen 1 loaded
  await expect(page.locator('h1')).toContainText('Welcome to Service 1');

  // Fill out the Full Name input
  const nameInput = page.locator('input[id="name_input"]');
  await nameInput.fill('John Test');

  // Select a value in the Country combobox
  // Wait for at least one option (other than the disabled placeholder) to appear
  const countryCombobox = page.locator('select[id="country_input"]');
  await expect(countryCombobox.locator('option').nth(1)).toBeAttached({ timeout: 5000 });
  await countryCombobox.selectOption({ label: 'United States' });

  // Click outside to trigger blur/validation
  await page.locator('body').click();

  // Click the Next button
  const nextButton = page.locator('button', { hasText: 'Next' });
  await nextButton.click();

  // Assert the next screen is rendered by checking the header text
  await expect(page.locator('h1')).toContainText('Confirm Details');
});
