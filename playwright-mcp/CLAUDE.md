# MCP Playwright - Claude Integration Guide

## Overview

MCP Playwright is a Model Context Protocol (MCP) server that provides Claude with autonomous web testing and automation capabilities through Playwright. This enables Claude to interact with websites, capture screenshots, extract data, run tests, and generate test scripts without manual intervention.

## Quick Start for Claude

### Available Tools

You have access to 7 Playwright tools through the MCP server:

1. **navigate_to_page** - Navigate to URLs and get page information
2. **take_screenshot** - Capture webpage screenshots
3. **extract_data** - Extract data using CSS selectors
4. **fill_form** - Fill and submit forms automatically
5. **test_website** - Run comprehensive website tests
6. **run_script** - Execute JavaScript on pages
7. **generate_test** - Generate test scripts in multiple languages

### Basic Usage Examples

```
"Take a screenshot of github.com"
"Test the performance of example.com"
"Extract all headlines from news.ycombinator.com"
"Fill the contact form on mysite.com with test data"
"Generate an E2E test for the login page"
```

## Tool Reference

### 1. Navigate to Page
```json
{
  "tool": "navigate_to_page",
  "arguments": {
    "url": "https://example.com",
    "browser": "chromium",  // Optional: chromium, firefox, webkit
    "headless": true,       // Optional: run without UI
    "waitUntil": "networkidle"  // Optional: load, domcontentloaded, networkidle
  }
}
```

### 2. Take Screenshot
```json
{
  "tool": "take_screenshot",
  "arguments": {
    "url": "https://example.com",
    "fullPage": true,       // Capture entire page
    "path": "screenshot.png"  // Optional: save path
  }
}
```

### 3. Extract Data
```json
{
  "tool": "extract_data",
  "arguments": {
    "url": "https://example.com",
    "selectors": {
      "title": "h1",
      "price": ".price",
      "description": ".description"
    }
  }
}
```

### 4. Fill Form
```json
{
  "tool": "fill_form",
  "arguments": {
    "url": "https://example.com/form",
    "formData": {
      "name": "Test User",
      "email": "test@example.com",
      "message": "Test message"
    },
    "submitSelector": "button[type='submit']"  // Optional
  }
}
```

### 5. Test Website
```json
{
  "tool": "test_website",
  "arguments": {
    "url": "https://example.com",
    "tests": ["performance", "accessibility", "seo", "responsiveness", "console-errors"]
  }
}
```

### 6. Run Script
```json
{
  "tool": "run_script",
  "arguments": {
    "url": "https://example.com",
    "script": "return document.querySelectorAll('img').length"
  }
}
```

### 7. Generate Test
```json
{
  "tool": "generate_test",
  "arguments": {
    "url": "https://example.com",
    "type": "e2e",  // e2e, form, navigation, api, visual, performance, accessibility
    "language": "typescript"  // javascript, typescript, python
  }
}
```

## Common Workflows

### Website Testing Workflow
1. Navigate to the website
2. Check for console errors
3. Test performance metrics
4. Check accessibility
5. Take screenshots for documentation
6. Generate test report

### Data Extraction Workflow
1. Navigate to target page
2. Extract structured data
3. Navigate to next page if pagination exists
4. Compile results
5. Format and present data

### Form Testing Workflow
1. Navigate to form page
2. Fill form with test data
3. Submit form
4. Verify success message or redirect
5. Check for validation errors

## Best Practices

### 1. Error Handling
- Always check if tools execute successfully
- Provide fallback options if a tool fails
- Report detailed error messages to help debugging

### 2. Performance
- Use `headless: true` for faster execution
- Specify only needed test types to reduce runtime
- Use specific selectors rather than generic ones

### 3. Data Extraction
- Verify selectors exist before extracting
- Handle cases where elements might not be present
- Use array extraction for multiple elements

### 4. Testing
- Start with basic tests before complex ones
- Chain operations logically
- Capture screenshots for visual verification

## Project Structure

```
/opt/mcp-playwright/
├── src/index.ts           # MCP server implementation
├── build/index.js         # Compiled server
├── scripts/               # Utility scripts
│   ├── quick-test.py     # Quick website testing
│   ├── capture-website.py # Screenshot & data extraction
│   └── automation-generator.py # Generate test scripts
├── tests/                # Test files
├── docs/                 # Documentation
└── reports/             # Test reports & screenshots
```

## Troubleshooting

### Common Issues

1. **Tool not responding**: Check if MCP server is running
2. **Browser launch fails**: Ensure browsers are installed (`npx playwright install`)
3. **Timeout errors**: Increase timeout or check network connectivity
4. **Selector not found**: Verify the CSS selector is correct

### Debug Mode

Enable debug logging:
```bash
export DEBUG=mcp:*
```

## Advanced Usage

### Custom Browser Configuration
```json
{
  "browser": "firefox",
  "headless": false,  // Show browser window
  "waitUntil": "domcontentloaded"  // Faster for static sites
}
```

### Chaining Operations
```
"First navigate to example.com, then take a screenshot, extract all links, and test the performance"
```

### Conditional Testing
```
"Test the login form, and if it fails, try with different credentials"
```

## Performance Metrics

When running performance tests, you'll receive:
- **Load Time**: Total page load time
- **DOM Content Loaded**: Time until DOM is ready
- **First Paint**: Time to first visual change
- **First Contentful Paint**: Time to first content render
- **Largest Contentful Paint**: Time to largest element render

## Accessibility Checks

Accessibility tests check for:
- Missing alt text on images
- Form inputs without labels
- Improper heading hierarchy
- Missing ARIA attributes
- Keyboard navigation issues

## Generated Test Examples

### TypeScript E2E Test
```typescript
import { test, expect } from '@playwright/test';

test('complete user journey', async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page).toHaveTitle(/Example/);
  // ... more test steps
});
```

### Python Test
```python
def test_homepage(page):
    page.goto("https://example.com")
    expect(page).to_have_title(re.compile("Example"))
    # ... more test steps
```

## Quick Commands Reference

| Task | Command |
|------|---------|
| Screenshot | "Take a screenshot of [URL]" |
| Test | "Test [URL] for [performance/accessibility/etc]" |
| Extract | "Extract [data] from [URL]" |
| Fill Form | "Fill the form at [URL] with test data" |
| Generate | "Generate a [type] test for [URL]" |
| Navigate | "Go to [URL] and tell me what you see" |
| Execute | "Run this JavaScript on [URL]: [code]" |

## Environment Variables

- `BASE_URL`: Default URL for testing
- `HEADLESS`: Run browsers in headless mode
- `DEBUG`: Enable debug logging
- `TIMEOUT`: Default timeout in milliseconds

## Additional Resources

- [Installation Guide](docs/INSTALLATION.md)
- [MCP Tools Reference](docs/MCP_TOOLS.md)
- [Usage Examples](docs/CLAUDE_USAGE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Testing Guide](docs/TESTING.md)
- [Advanced Configuration](docs/ADVANCED_CONFIGURATION.md)

## Notes for Claude

1. **Always verify tool availability** before attempting to use them
2. **Check for errors** in tool responses and handle gracefully
3. **Use appropriate timeouts** for long-running operations
4. **Prefer specific selectors** over generic ones for reliability
5. **Chain operations logically** for complex workflows
6. **Capture screenshots** when visual verification is needed
7. **Generate tests** to help users automate repetitive tasks

---

This MCP server enables you to perform comprehensive web testing and automation tasks autonomously. Use these tools to help users test their websites, extract data, automate workflows, and generate test scripts.