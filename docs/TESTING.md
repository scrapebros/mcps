# Testing Guide

Comprehensive guide for testing and validating the MCP Playwright server and its integrations.

## Testing Overview

The MCP Playwright project includes multiple testing layers:

1. **MCP Server Testing** - Validate server functionality
2. **Tool Testing** - Test individual MCP tools
3. **Integration Testing** - Test Claude integration
4. **End-to-End Testing** - Complete workflow validation
5. **Performance Testing** - Benchmark and optimization

## Quick Test Commands

```bash
# Test MCP server
node build/index.js

# Run JavaScript tests
npm test

# Run Python tests
pytest

# Run all tests
./scripts/run-tests.sh

# Quick website test
./scripts/quick-test.py https://example.com

# Test with MCP Inspector
npx @modelcontextprotocol/inspector node build/index.js
```

## MCP Server Testing

### 1. Direct Server Test

```bash
# Start server and check output
node build/index.js
# Expected: "MCP Playwright server started"
```

### 2. MCP Inspector Testing

```bash
# Install inspector
npm install -g @modelcontextprotocol/inspector

# Run inspector
npx @modelcontextprotocol/inspector node build/index.js
```

In the inspector:
1. Click "Connect"
2. View available tools
3. Test each tool with sample inputs

### 3. Tool Validation Tests

Test each tool individually:

```javascript
// Test navigate_to_page
{
  "tool": "navigate_to_page",
  "arguments": {
    "url": "https://example.com"
  }
}

// Test take_screenshot
{
  "tool": "take_screenshot",
  "arguments": {
    "url": "https://example.com",
    "fullPage": true
  }
}

// Test extract_data
{
  "tool": "extract_data",
  "arguments": {
    "url": "https://example.com",
    "selectors": {
      "title": "h1",
      "content": "p"
    }
  }
}
```

## Claude Integration Testing

### 1. Basic Connection Test

Ask Claude:
```
"Can you see the playwright MCP server?"
```

Expected: Claude should confirm the server is available.

### 2. Simple Tool Test

```
"Use the playwright server to get the title of example.com"
```

### 3. Complex Workflow Test

```
"Test example.com by:
1. Taking a screenshot
2. Checking performance
3. Extracting the main heading
4. Generating a test script"
```

## Automated Test Suites

### JavaScript/TypeScript Tests

```bash
# Run all tests
npm test

# Run specific test file
npx playwright test tests/e2e/js/example.spec.ts

# Run with UI mode
npm run test:ui

# Run in headed mode
npm run test:headed

# Run specific browser
npm run test:chrome
npm run test:firefox
npm run test:webkit

# Debug mode
npm run test:debug
```

### Python Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all Python tests
pytest

# Run specific test file
pytest tests/e2e/python/test_example.py

# Run with specific markers
pytest -m smoke
pytest -m "not slow"

# Parallel execution
pytest -n auto

# Generate HTML report
pytest --html=reports/pytest-report.html
```

## Tool-Specific Testing

### 1. Navigation Tool

```python
# test_navigation.py
def test_navigate_to_page():
    result = mcp_call("navigate_to_page", {
        "url": "https://example.com"
    })
    assert result["status"] == 200
    assert "Example" in result["title"]
```

### 2. Screenshot Tool

```python
def test_screenshot():
    result = mcp_call("take_screenshot", {
        "url": "https://example.com",
        "fullPage": True
    })
    assert "Screenshot saved" in result["content"][0]["text"]
    assert result["content"][1]["type"] == "image"
```

### 3. Data Extraction Tool

```python
def test_extract_data():
    result = mcp_call("extract_data", {
        "url": "https://example.com",
        "selectors": {
            "title": "h1",
            "links": "a"
        }
    })
    assert "title" in result
    assert isinstance(result["links"], list)
```

### 4. Form Filling Tool

```python
def test_fill_form():
    result = mcp_call("fill_form", {
        "url": "https://example.com/form",
        "formData": {
            "name": "Test User",
            "email": "test@example.com"
        }
    })
    assert result["success"] == True
```

### 5. Website Testing Tool

```python
def test_website_testing():
    result = mcp_call("test_website", {
        "url": "https://example.com",
        "tests": ["performance", "accessibility"]
    })
    assert "performance" in result["tests"]
    assert result["tests"]["performance"]["loadTime"] < 5000
```

## Performance Testing

### 1. Load Time Benchmarks

```bash
# Test page load times
./scripts/quick-test.py https://example.com
```

### 2. Concurrent Testing

```javascript
// Test parallel execution
test.describe.parallel('Parallel tests', () => {
  test('test 1', async ({ page }) => {
    await page.goto('https://example.com');
  });
  
  test('test 2', async ({ page }) => {
    await page.goto('https://example.org');
  });
});
```

### 3. Resource Usage

```bash
# Monitor memory usage
node --inspect build/index.js

# Check browser processes
ps aux | grep chromium
```

## Visual Testing

### 1. Screenshot Comparison

```javascript
test('visual regression', async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page).toHaveScreenshot('homepage.png');
});
```

### 2. Responsive Testing

```javascript
const viewports = [
  { width: 1920, height: 1080 },
  { width: 768, height: 1024 },
  { width: 375, height: 667 }
];

for (const viewport of viewports) {
  test(`responsive at ${viewport.width}x${viewport.height}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto('https://example.com');
    await page.screenshot({ path: `responsive-${viewport.width}.png` });
  });
}
```

## Test Data Management

### Using Fixtures

```javascript
// fixtures/test-data.json
{
  "users": [
    {
      "name": "Test User 1",
      "email": "test1@example.com"
    },
    {
      "name": "Test User 2",
      "email": "test2@example.com"
    }
  ]
}

// Using in tests
const testData = require('./fixtures/test-data.json');

test('data-driven test', async ({ page }) => {
  for (const user of testData.users) {
    await page.fill('#name', user.name);
    await page.fill('#email', user.email);
  }
});
```

## Debugging Tests

### 1. Playwright Debug Mode

```bash
# Launch with inspector
PWDEBUG=1 npm test

# Or use debug flag
npx playwright test --debug
```

### 2. Console Logging

```javascript
test('debug test', async ({ page }) => {
  page.on('console', msg => console.log('PAGE:', msg.text()));
  page.on('pageerror', err => console.error('ERROR:', err));
  
  await page.goto('https://example.com');
});
```

### 3. Trace Viewer

```bash
# Run with trace
npx playwright test --trace on

# View trace
npx playwright show-trace trace.zip
```

### 4. Video Recording

```javascript
// playwright.config.ts
use: {
  video: 'on-first-retry',
  trace: 'on-first-retry',
}
```

## Test Reports

### 1. Playwright HTML Report

```bash
# Generate report
npm test -- --reporter=html

# View report
npx playwright show-report
```

### 2. JSON Report

```bash
# Generate JSON report
npm test -- --reporter=json > test-results.json
```

### 3. Custom Reporting

```javascript
// Custom reporter
class CustomReporter {
  onTestEnd(test, result) {
    console.log(`${test.title}: ${result.status}`);
  }
}

module.exports = CustomReporter;
```

## Continuous Testing

### 1. Watch Mode

```bash
# Run tests on file change
npx playwright test --watch
```

### 2. Scheduled Testing

```bash
# Cron job for hourly tests
0 * * * * cd /opt/mcp-playwright && npm test
```

### 3. Git Hooks

```bash
# .git/hooks/pre-commit
#!/bin/sh
npm test
```

## Test Validation Checklist

### Pre-Release Testing

- [ ] All MCP tools respond correctly
- [ ] Claude can access all tools
- [ ] Screenshots are captured properly
- [ ] Data extraction works
- [ ] Form filling succeeds
- [ ] Performance metrics are accurate
- [ ] Error handling works
- [ ] Multiple browsers tested
- [ ] Parallel execution works
- [ ] Reports generate correctly

### Integration Testing

- [ ] Claude Desktop configuration valid
- [ ] Server starts without errors
- [ ] Tools execute in sequence
- [ ] Memory usage acceptable
- [ ] Response times adequate
- [ ] Error messages helpful
- [ ] Documentation accurate

## Common Test Patterns

### 1. Page Object Model

```javascript
class HomePage {
  constructor(page) {
    this.page = page;
    this.searchInput = page.locator('#search');
    this.submitButton = page.locator('button[type="submit"]');
  }
  
  async search(query) {
    await this.searchInput.fill(query);
    await this.submitButton.click();
  }
}
```

### 2. API Testing

```javascript
test('API test', async ({ request }) => {
  const response = await request.get('https://api.example.com/data');
  expect(response.ok()).toBeTruthy();
  
  const data = await response.json();
  expect(data).toHaveProperty('status');
});
```

### 3. Database Validation

```python
def test_database_state():
    # Run UI action
    mcp_call("fill_form", {...})
    
    # Verify database
    conn = connect_to_db()
    result = conn.query("SELECT * FROM users WHERE email = 'test@example.com'")
    assert len(result) == 1
```

## Test Metrics

### Coverage Goals

- **Code Coverage**: > 80%
- **Tool Coverage**: 100%
- **Browser Coverage**: All 3 browsers
- **Viewport Coverage**: Desktop, tablet, mobile

### Performance Targets

- **Tool Response**: < 2 seconds
- **Screenshot Capture**: < 5 seconds
- **Data Extraction**: < 3 seconds
- **Test Execution**: < 10 minutes total

## Troubleshooting Tests

### Common Issues

1. **Timeout Errors**
   - Increase timeout in config
   - Check network connectivity
   - Verify selectors

2. **Flaky Tests**
   - Add explicit waits
   - Use retry logic
   - Check for race conditions

3. **Browser Issues**
   - Reinstall browsers
   - Check system dependencies
   - Update Playwright

4. **Memory Leaks**
   - Close browser contexts
   - Clear cache periodically
   - Monitor process usage

---

For specific issues, see [Troubleshooting Guide](./TROUBLESHOOTING.md).