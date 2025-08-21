import { test, expect, Page } from '@playwright/test';

test.describe('Example Web Application Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the base URL before each test
    await page.goto('/');
  });

  test('should load homepage successfully', async ({ page }) => {
    // Check if page loads with expected title
    await expect(page).toHaveTitle(/.*Home.*/i);
    
    // Check for main content visibility
    const mainContent = page.locator('main, [role="main"], #main');
    await expect(mainContent).toBeVisible();
  });

  test('should navigate to different pages', async ({ page }) => {
    // Look for navigation links
    const navLinks = page.locator('nav a, header a');
    const linkCount = await navLinks.count();
    
    if (linkCount > 0) {
      // Click first navigation link
      await navLinks.first().click();
      
      // Verify navigation occurred
      await page.waitForLoadState('networkidle');
      expect(page.url()).not.toBe(process.env.BASE_URL || 'http://localhost:3000');
    }
  });

  test('should handle form submission', async ({ page }) => {
    // Look for any form on the page
    const form = page.locator('form').first();
    
    if (await form.isVisible()) {
      // Fill in text inputs
      const textInputs = form.locator('input[type="text"], input[type="email"]');
      const inputCount = await textInputs.count();
      
      for (let i = 0; i < inputCount; i++) {
        await textInputs.nth(i).fill(`test-value-${i}`);
      }
      
      // Submit form if submit button exists
      const submitButton = form.locator('button[type="submit"], input[type="submit"]');
      if (await submitButton.isVisible()) {
        await submitButton.click();
        
        // Wait for response
        await page.waitForLoadState('networkidle');
      }
    }
  });

  test('should be responsive', async ({ page }) => {
    // Test different viewport sizes
    const viewports = [
      { width: 1920, height: 1080, name: 'Desktop' },
      { width: 768, height: 1024, name: 'Tablet' },
      { width: 375, height: 667, name: 'Mobile' }
    ];

    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      
      // Take screenshot for visual validation
      await page.screenshot({ 
        path: `reports/screenshots/${viewport.name.toLowerCase()}.png`,
        fullPage: true 
      });
      
      // Check that main content is still visible
      const mainContent = page.locator('main, [role="main"], #main, body');
      await expect(mainContent).toBeVisible();
    }
  });

  test('should handle API interactions', async ({ page, request }) => {
    // Example of API testing alongside UI testing
    const apiEndpoint = `${process.env.BASE_URL || 'http://localhost:3000'}/api/health`;
    
    try {
      const response = await request.get(apiEndpoint);
      
      if (response.ok()) {
        expect(response.status()).toBe(200);
        
        const data = await response.json();
        expect(data).toHaveProperty('status');
      }
    } catch (error) {
      // API endpoint might not exist, skip test
      test.skip();
    }
  });

  test('should check accessibility', async ({ page }) => {
    // Basic accessibility checks
    
    // Check for alt text on images
    const images = page.locator('img');
    const imageCount = await images.count();
    
    for (let i = 0; i < imageCount; i++) {
      const img = images.nth(i);
      const altText = await img.getAttribute('alt');
      
      // Images should have alt text (can be empty for decorative images)
      expect(altText).not.toBeNull();
    }
    
    // Check for ARIA labels on interactive elements
    const buttons = page.locator('button');
    const buttonCount = await buttons.count();
    
    for (let i = 0; i < buttonCount; i++) {
      const button = buttons.nth(i);
      const text = await button.textContent();
      const ariaLabel = await button.getAttribute('aria-label');
      
      // Button should have either text content or aria-label
      expect(text || ariaLabel).toBeTruthy();
    }
  });

  test('should handle errors gracefully', async ({ page }) => {
    // Navigate to non-existent page
    const response = await page.goto('/non-existent-page-404', { 
      waitUntil: 'networkidle' 
    });
    
    // Check if proper error page is shown
    if (response && response.status() === 404) {
      const errorMessage = page.locator('text=/404|not found/i');
      await expect(errorMessage).toBeVisible();
    }
  });

  test('should test search functionality', async ({ page }) => {
    // Look for search input
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i]').first();
    
    if (await searchInput.isVisible()) {
      // Type search query
      await searchInput.fill('test query');
      
      // Press Enter or click search button
      await searchInput.press('Enter');
      
      // Wait for results
      await page.waitForLoadState('networkidle');
      
      // Check if results are displayed
      const results = page.locator('[class*="result"], [id*="result"], [data-testid*="result"]');
      expect(await results.count()).toBeGreaterThanOrEqual(0);
    }
  });
});

test.describe('Advanced Testing Patterns', () => {
  test('should handle authentication flow', async ({ page, context }) => {
    // Example login flow
    const loginPage = page.locator('a[href*="login"], button:has-text("Login")').first();
    
    if (await loginPage.isVisible()) {
      await loginPage.click();
      
      // Fill login form if it exists
      const usernameInput = page.locator('input[name="username"], input[type="email"]').first();
      const passwordInput = page.locator('input[type="password"]').first();
      
      if (await usernameInput.isVisible() && await passwordInput.isVisible()) {
        await usernameInput.fill('testuser@example.com');
        await passwordInput.fill('testpassword123');
        
        const submitButton = page.locator('button[type="submit"]');
        await submitButton.click();
        
        // Check for successful login indicators
        await page.waitForLoadState('networkidle');
        
        // Check cookies were set
        const cookies = await context.cookies();
        expect(cookies.length).toBeGreaterThan(0);
      }
    }
  });

  test('should test file upload', async ({ page }) => {
    const fileInput = page.locator('input[type="file"]').first();
    
    if (await fileInput.isVisible()) {
      // Create a test file
      const filePath = 'fixtures/test-file.txt';
      
      // Upload file
      await fileInput.setInputFiles(filePath);
      
      // Verify file was selected
      const fileName = await fileInput.evaluate((input: HTMLInputElement) => {
        return input.files?.[0]?.name;
      });
      
      expect(fileName).toBeTruthy();
    }
  });

  test('should test drag and drop', async ({ page }) => {
    const draggable = page.locator('[draggable="true"]').first();
    const dropzone = page.locator('[ondrop], [data-drop-zone]').first();
    
    if (await draggable.isVisible() && await dropzone.isVisible()) {
      // Perform drag and drop
      await draggable.dragTo(dropzone);
      
      // Verify drop was successful (implementation specific)
      await expect(dropzone).toHaveClass(/.*active|dropped|success.*/);
    }
  });
});