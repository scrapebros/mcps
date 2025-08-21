import { test, expect } from '@playwright/test';

test('example codegen test', async ({ page }) => {
  // This is an example of what codegen would generate
  
  // Go to https://example.com
  await page.goto('https://example.com');
  
  // Click on "More information..." link
  await page.getByRole('link', { name: 'More information...' }).click();
  
  // Expect page to have title
  await expect(page).toHaveTitle(/IANA/);
  
  // Go back
  await page.goBack();
  
  // Verify we're back on example.com
  await expect(page).toHaveTitle(/Example Domain/);
  
  // Take a screenshot
  await page.screenshot({ path: 'example-screenshot.png' });
});

test('form interaction example', async ({ page }) => {
  // Example of form interaction that codegen would generate
  await page.goto('https://example.com/form');
  
  // Fill in form fields
  await page.getByLabel('Name').fill('John Doe');
  await page.getByLabel('Email').fill('john@example.com');
  await page.getByLabel('Message').fill('This is a test message');
  
  // Select dropdown option
  await page.getByLabel('Country').selectOption('USA');
  
  // Check checkbox
  await page.getByLabel('I agree to terms').check();
  
  // Click submit button
  await page.getByRole('button', { name: 'Submit' }).click();
  
  // Wait for success message
  await expect(page.getByText('Form submitted successfully')).toBeVisible();
});

test('navigation example', async ({ page }) => {
  // Example of navigation that codegen would generate
  await page.goto('https://example.com');
  
  // Click through navigation menu
  await page.getByRole('navigation').getByText('About').click();
  await expect(page).toHaveURL(/.*about/);
  
  await page.getByRole('navigation').getByText('Services').click();
  await expect(page).toHaveURL(/.*services/);
  
  await page.getByRole('navigation').getByText('Contact').click();
  await expect(page).toHaveURL(/.*contact/);
});
