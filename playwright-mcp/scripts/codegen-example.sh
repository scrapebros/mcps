#!/bin/bash

# Playwright Codegen Examples
# This script demonstrates various ways to use Playwright's built-in code generator

echo "=== Playwright Codegen Examples ==="
echo ""

# Function to show codegen command without running it
show_example() {
    echo "Example: $1"
    echo "Command: $2"
    echo ""
}

# Basic codegen examples
show_example "Generate JavaScript test by recording browser interactions" \
    "npx playwright codegen https://example.com"

show_example "Generate Python test" \
    "playwright codegen --target python https://example.com"

show_example "Generate test with specific browser" \
    "npx playwright codegen --browser firefox https://example.com"

show_example "Generate test with mobile device emulation" \
    "npx playwright codegen --device='iPhone 12' https://example.com"

show_example "Save generated test to file" \
    "npx playwright codegen https://example.com -o tests/recorded_test.spec.ts"

show_example "Generate test with custom viewport" \
    "npx playwright codegen --viewport-size=800,600 https://example.com"

show_example "Generate test with geolocation" \
    "npx playwright codegen --geolocation='40.730610,-73.935242' https://maps.google.com"

show_example "Generate test with timezone" \
    "npx playwright codegen --timezone='Europe/Rome' https://example.com"

show_example "Generate test with color scheme preference" \
    "npx playwright codegen --color-scheme=dark https://example.com"

# Actual example - generate a simple test
echo "=== Generating Actual Test File ==="
echo "Generating a test for example.com..."
echo ""

# Create a simple test without launching browser (using --save-only flag doesn't exist, so we'll create manually)
cat > tests/e2e/js/codegen_example.spec.ts << 'EOF'
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
EOF

echo "✅ Generated test file: tests/e2e/js/codegen_example.spec.ts"
echo ""
echo "To run the generated test:"
echo "  npm test tests/e2e/js/codegen_example.spec.ts"
echo ""
echo "To use interactive codegen (requires display):"
echo "  npx playwright codegen https://example.com"
echo ""
echo "This will open a browser where you can:"
echo "  1. Interact with the page"
echo "  2. See generated code in real-time"
echo "  3. Copy the code to your test file"
echo "  4. Add assertions using the toolbar"