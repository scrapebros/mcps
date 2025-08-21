# MCP Tools Reference

## Overview

This document provides a comprehensive reference for all Playwright tools exposed through the Model Context Protocol (MCP) server. These tools enable Claude to interact with web browsers programmatically for testing, automation, and data extraction.

## Table of Contents

1. [navigate_to_page](#1-navigate_to_page)
2. [take_screenshot](#2-take_screenshot)
3. [extract_data](#3-extract_data)
4. [fill_form](#4-fill_form)
5. [test_website](#5-test_website)
6. [run_script](#6-run_script)
7. [generate_test](#7-generate_test)

---

## 1. navigate_to_page

Navigate to a URL and retrieve comprehensive page information.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | ✅ | - | The URL to navigate to |
| `browser` | enum | ❌ | `chromium` | Browser type: `chromium`, `firefox`, `webkit` |
| `headless` | boolean | ❌ | `true` | Run browser in headless mode |
| `waitUntil` | enum | ❌ | `networkidle` | Wait condition: `load`, `domcontentloaded`, `networkidle` |

### Returns

```json
{
  "url": "https://example.com",
  "title": "Example Domain",
  "status": 200,
  "headers": {...},
  "content": "<!DOCTYPE html>..."
}
```

### Examples

#### Basic Navigation
```json
{
  "tool": "navigate_to_page",
  "arguments": {
    "url": "https://example.com"
  }
}
```

#### With Specific Browser
```json
{
  "tool": "navigate_to_page",
  "arguments": {
    "url": "https://example.com",
    "browser": "firefox",
    "headless": false,
    "waitUntil": "domcontentloaded"
  }
}
```

### Claude Usage
> "Navigate to example.com and tell me the page title"

---

## 2. take_screenshot

Capture a screenshot of a webpage with various options.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | ✅ | - | The URL to capture |
| `path` | string | ❌ | auto-generated | Path to save the screenshot |
| `fullPage` | boolean | ❌ | `true` | Capture entire scrollable page |
| `browser` | enum | ❌ | `chromium` | Browser type |
| `headless` | boolean | ❌ | `true` | Run browser in headless mode |

### Returns

```json
{
  "content": [
    {
      "type": "text",
      "text": "Screenshot saved to: screenshot-1234567890.png"
    },
    {
      "type": "image",
      "data": "base64_encoded_image_data",
      "mimeType": "image/png"
    }
  ]
}
```

### Examples

#### Full Page Screenshot
```json
{
  "tool": "take_screenshot",
  "arguments": {
    "url": "https://github.com",
    "fullPage": true
  }
}
```

#### Viewport Screenshot with Custom Path
```json
{
  "tool": "take_screenshot",
  "arguments": {
    "url": "https://example.com",
    "path": "homepage.png",
    "fullPage": false
  }
}
```

### Claude Usage
> "Take a full-page screenshot of the GitHub homepage"

---

## 3. extract_data

Extract structured data from a webpage using CSS selectors.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | ✅ | - | The URL to extract data from |
| `selectors` | object | ✅ | - | Object mapping field names to CSS selectors |
| `browser` | enum | ❌ | `chromium` | Browser type |
| `headless` | boolean | ❌ | `true` | Run browser in headless mode |

### Returns

```json
{
  "fieldName1": "extracted text",
  "fieldName2": ["array", "of", "texts"],
  "fieldName3": null
}
```

### Examples

#### Extract News Headlines
```json
{
  "tool": "extract_data",
  "arguments": {
    "url": "https://news.ycombinator.com",
    "selectors": {
      "titles": ".titleline",
      "points": ".score",
      "comments": ".subtext a:last-child",
      "links": ".titleline a"
    }
  }
}
```

#### Extract Product Information
```json
{
  "tool": "extract_data",
  "arguments": {
    "url": "https://example-shop.com/product",
    "selectors": {
      "name": "h1.product-title",
      "price": ".price-now",
      "description": ".product-description",
      "images": "img.product-image",
      "reviews": ".review-count"
    }
  }
}
```

### Claude Usage
> "Extract all article titles and links from Hacker News"

---

## 4. fill_form

Automatically fill and submit forms on webpages.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | ✅ | - | The URL containing the form |
| `formData` | object | ✅ | - | Object with field names/values to fill |
| `submitSelector` | string | ❌ | `button[type="submit"]` | CSS selector for submit button |
| `browser` | enum | ❌ | `chromium` | Browser type |
| `headless` | boolean | ❌ | `true` | Run browser in headless mode |

### Returns

```json
{
  "url": "https://example.com/success",
  "title": "Form Submitted Successfully",
  "success": true
}
```

### Examples

#### Contact Form Submission
```json
{
  "tool": "fill_form",
  "arguments": {
    "url": "https://example.com/contact",
    "formData": {
      "name": "John Doe",
      "email": "john@example.com",
      "subject": "Test Message",
      "message": "This is a test submission",
      "newsletter": true
    }
  }
}
```

#### Login Form
```json
{
  "tool": "fill_form",
  "arguments": {
    "url": "https://example.com/login",
    "formData": {
      "username": "testuser",
      "password": "testpass123",
      "remember_me": true
    },
    "submitSelector": "#login-button"
  }
}
```

### Claude Usage
> "Fill out the contact form on example.com with test data"

---

## 5. test_website

Run comprehensive automated tests on a website.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | ✅ | - | The URL to test |
| `tests` | array | ❌ | `["performance", "accessibility", "console-errors"]` | Test types to run |
| `browser` | enum | ❌ | `chromium` | Browser type |
| `headless` | boolean | ❌ | `true` | Run browser in headless mode |

### Available Test Types

- `performance` - Page load metrics, Core Web Vitals
- `accessibility` - Basic WCAG compliance checks
- `seo` - SEO meta tags and structure
- `responsiveness` - Mobile/tablet/desktop viewport testing
- `links` - Extract and validate all links
- `console-errors` - Capture JavaScript console errors

### Returns

```json
{
  "url": "https://example.com",
  "tests": {
    "performance": {
      "loadTime": 1234,
      "domContentLoaded": 567,
      "firstPaint": 234
    },
    "accessibility": [
      "Image 1 missing alt text",
      "Input 3 missing label"
    ],
    "seo": {
      "title": "Page Title",
      "description": "Meta description",
      "h1Count": 1
    },
    "responsiveness": [
      {"viewport": "desktop", "isResponsive": true},
      {"viewport": "mobile", "isResponsive": true}
    ],
    "consoleErrors": []
  }
}
```

### Examples

#### Comprehensive Testing
```json
{
  "tool": "test_website",
  "arguments": {
    "url": "https://example.com",
    "tests": ["performance", "accessibility", "seo", "responsiveness", "console-errors"]
  }
}
```

#### Performance Testing Only
```json
{
  "tool": "test_website",
  "arguments": {
    "url": "https://example.com",
    "tests": ["performance"]
  }
}
```

### Claude Usage
> "Test example.com for performance, accessibility, and SEO issues"

---

## 6. run_script

Execute custom JavaScript code on a webpage.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | ✅ | - | The URL to run the script on |
| `script` | string | ✅ | - | JavaScript code to execute |
| `browser` | enum | ❌ | `chromium` | Browser type |
| `headless` | boolean | ❌ | `true` | Run browser in headless mode |

### Returns

The return value of the executed JavaScript code (JSON serialized).

### Examples

#### Count Page Elements
```json
{
  "tool": "run_script",
  "arguments": {
    "url": "https://example.com",
    "script": "return { images: document.querySelectorAll('img').length, links: document.querySelectorAll('a').length, forms: document.querySelectorAll('form').length }"
  }
}
```

#### Extract Custom Data
```json
{
  "tool": "run_script",
  "arguments": {
    "url": "https://example.com",
    "script": "return Array.from(document.querySelectorAll('h2')).map(h => h.textContent)"
  }
}
```

#### Interact with Page
```json
{
  "tool": "run_script",
  "arguments": {
    "url": "https://example.com",
    "script": "document.querySelector('#menu-toggle').click(); return document.querySelector('.menu').classList.contains('open')"
  }
}
```

### Claude Usage
> "Count how many images and links are on the homepage"

---

## 7. generate_test

Generate test code for a webpage in various languages and frameworks.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | ✅ | - | The URL to generate tests for |
| `type` | enum | ✅ | - | Test type to generate |
| `language` | enum | ❌ | `typescript` | Output language |

### Test Types

- `e2e` - End-to-end user journey test
- `form` - Form interaction and validation test
- `navigation` - Site navigation test
- `api` - API endpoint testing
- `visual` - Visual regression test
- `performance` - Performance metrics test
- `accessibility` - Accessibility compliance test

### Languages

- `javascript` - Plain JavaScript with Playwright
- `typescript` - TypeScript with Playwright Test
- `python` - Python with pytest-playwright

### Returns

Generated test code as a string.

### Examples

#### Generate E2E Test
```json
{
  "tool": "generate_test",
  "arguments": {
    "url": "https://example.com",
    "type": "e2e",
    "language": "typescript"
  }
}
```

#### Generate Python Form Test
```json
{
  "tool": "generate_test",
  "arguments": {
    "url": "https://example.com/signup",
    "type": "form",
    "language": "python"
  }
}
```

### Example Output (TypeScript)
```typescript
import { test, expect } from '@playwright/test';

test.describe('e2e tests for https://example.com', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://example.com');
  });

  test('complete user journey', async ({ page }) => {
    // Navigate through the site
    await expect(page).toHaveTitle(/.*/);
    
    // Click first navigation link
    const navLink = page.locator('nav a').first();
    if (await navLink.isVisible()) {
      await navLink.click();
      await page.waitForLoadState('networkidle');
    }
    
    // Verify page loaded
    await expect(page.locator('body')).toBeVisible();
  });
});
```

### Claude Usage
> "Generate an end-to-end test for my website in TypeScript"

---

## Best Practices

### 1. Browser Selection
- Use `chromium` for most testing (fastest, most compatible)
- Use `firefox` for Firefox-specific testing
- Use `webkit` for Safari compatibility testing

### 2. Wait Strategies
- `networkidle` - Best for SPAs and dynamic content
- `domcontentloaded` - Faster for static sites
- `load` - Traditional page load event

### 3. Selector Strategies
- Prefer semantic selectors: `role`, `text`, `label`
- Use `data-testid` attributes for reliable testing
- Avoid fragile selectors like complex CSS paths

### 4. Error Handling
- Tools will return error messages if operations fail
- Check returned status codes and success flags
- Use appropriate wait conditions to avoid timing issues

### 5. Performance Considerations
- Use `headless: true` for faster execution
- Reuse browser contexts when possible
- Limit full-page screenshots to necessary cases

## Integration Examples

### Testing Workflow
```javascript
// 1. Navigate to page
await claude.use('navigate_to_page', { url: 'https://example.com' });

// 2. Run tests
await claude.use('test_website', { 
  url: 'https://example.com',
  tests: ['performance', 'accessibility']
});

// 3. Take screenshot for documentation
await claude.use('take_screenshot', { 
  url: 'https://example.com',
  fullPage: true
});
```

### Data Extraction Pipeline
```javascript
// 1. Extract structured data
const data = await claude.use('extract_data', {
  url: 'https://shop.example.com',
  selectors: {
    products: '.product-card',
    prices: '.price',
    availability: '.stock-status'
  }
});

// 2. Process and analyze data
// ... your analysis logic ...
```

### Form Testing Automation
```javascript
// 1. Fill and submit form
await claude.use('fill_form', {
  url: 'https://example.com/register',
  formData: {
    username: 'testuser',
    email: 'test@example.com',
    password: 'Test123!'
  }
});

// 2. Verify success
await claude.use('run_script', {
  url: 'https://example.com/dashboard',
  script: 'return document.querySelector(".welcome-message").textContent'
});
```

## Troubleshooting

### Common Issues

1. **Timeout Errors**
   - Increase wait conditions
   - Check network connectivity
   - Verify URL accessibility

2. **Selector Not Found**
   - Verify selector accuracy
   - Check if element is dynamically loaded
   - Use more specific selectors

3. **Form Submission Failures**
   - Ensure field names match
   - Check for required fields
   - Verify submit button selector

4. **Screenshot Issues**
   - Check disk space
   - Verify write permissions
   - Ensure valid file path

## Support

For issues or questions:
- Check [Troubleshooting Guide](./TROUBLESHOOTING.md)
- Review [Claude Usage Examples](./CLAUDE_USAGE.md)
- Submit issues on GitHub