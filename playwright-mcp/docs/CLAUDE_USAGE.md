# Claude Usage Examples

This guide provides practical examples of how to use the MCP Playwright tools with Claude for various web testing and automation tasks.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Web Testing](#web-testing)
3. [Data Extraction](#data-extraction)
4. [Form Automation](#form-automation)
5. [Screenshot Capture](#screenshot-capture)
6. [Test Generation](#test-generation)
7. [Advanced Scenarios](#advanced-scenarios)
8. [Workflow Examples](#workflow-examples)

---

## Basic Usage

### Simple Commands

Ask Claude directly using natural language:

```
"Take a screenshot of example.com"
"Test the performance of github.com"
"Extract all headlines from news.ycombinator.com"
"Fill out the contact form on mysite.com with test data"
```

### Specifying Options

You can be more specific with your requests:

```
"Take a full-page screenshot of github.com using Firefox"
"Test example.com for accessibility issues only"
"Extract product prices from shop.com using the .price-tag selector"
"Generate a Python test for the login page at myapp.com/login"
```

---

## Web Testing

### 1. Comprehensive Website Testing

**Request:**
```
"Run a complete test suite on example.com including performance, accessibility, SEO, and responsive design checks"
```

**Claude will execute:**
```json
{
  "tool": "test_website",
  "arguments": {
    "url": "https://example.com",
    "tests": ["performance", "accessibility", "seo", "responsiveness", "console-errors"]
  }
}
```

**Expected Response:**
- Performance metrics (load time, FCP, LCP)
- Accessibility violations
- SEO issues
- Responsive design problems
- Console errors

### 2. Performance Testing

**Request:**
```
"Check if my website at localhost:3000 loads within 3 seconds"
```

**Claude's Analysis:**
- Page load time
- Time to first byte (TTFB)
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Recommendations for improvements

### 3. Accessibility Audit

**Request:**
```
"Check example.com for accessibility issues and WCAG compliance"
```

**Claude will identify:**
- Missing alt text on images
- Form inputs without labels
- Insufficient color contrast
- Missing ARIA attributes
- Heading hierarchy issues

### 4. Cross-Browser Testing

**Request:**
```
"Test my website in Chrome, Firefox, and Safari browsers"
```

**Claude will:**
1. Run tests in Chromium
2. Run tests in Firefox
3. Run tests in WebKit (Safari)
4. Compare results across browsers
5. Identify browser-specific issues

---

## Data Extraction

### 1. News Aggregation

**Request:**
```
"Extract the top 10 stories from Hacker News with their titles, points, and comment counts"
```

**Claude executes:**
```json
{
  "tool": "extract_data",
  "arguments": {
    "url": "https://news.ycombinator.com",
    "selectors": {
      "titles": ".titleline",
      "points": ".score",
      "comments": ".subtext a:last-child"
    }
  }
}
```

### 2. E-commerce Price Monitoring

**Request:**
```
"Extract product names and prices from the first page of results on shop.example.com"
```

**Claude will:**
- Navigate to the shop page
- Extract product information
- Format data in a readable table
- Identify any pricing patterns

### 3. Content Scraping

**Request:**
```
"Get all blog post titles and dates from blog.example.com"
```

**Response includes:**
- List of blog titles
- Publication dates
- Links to full articles
- Summary statistics

### 4. Social Media Metrics

**Request:**
```
"Extract follower counts and engagement metrics from our company's social media pages"
```

---

## Form Automation

### 1. Contact Form Testing

**Request:**
```
"Fill and submit the contact form on example.com with test data to verify it works"
```

**Test Data Used:**
```json
{
  "name": "Test User",
  "email": "test@example.com",
  "subject": "Test Message",
  "message": "This is an automated test"
}
```

### 2. Registration Flow

**Request:**
```
"Test the user registration process on myapp.com/signup"
```

**Claude will:**
1. Navigate to signup page
2. Fill in registration details
3. Submit the form
4. Verify success message or redirect
5. Report any errors encountered

### 3. Multi-Step Forms

**Request:**
```
"Complete the multi-step checkout process on shop.com with test credit card details"
```

**Process:**
1. Add items to cart
2. Fill shipping information
3. Enter payment details (test data)
4. Confirm order
5. Verify confirmation page

### 4. Form Validation Testing

**Request:**
```
"Test form validation by submitting invalid data to see error messages"
```

---

## Screenshot Capture

### 1. Full Page Documentation

**Request:**
```
"Take a full-page screenshot of our documentation site for archival"
```

**Result:**
- High-resolution full-page capture
- Saved with timestamp
- Includes all scrollable content

### 2. Visual Comparison

**Request:**
```
"Take screenshots of example.com on desktop, tablet, and mobile viewports"
```

**Claude captures:**
- Desktop (1920x1080)
- Tablet (768x1024)
- Mobile (375x667)

### 3. Before/After Testing

**Request:**
```
"Take a screenshot before and after clicking the 'Show More' button"
```

### 4. Error Documentation

**Request:**
```
"Capture a screenshot of any error messages that appear during testing"
```

---

## Test Generation

### 1. E2E Test Creation

**Request:**
```
"Generate an end-to-end test for the user journey from homepage to checkout on shop.com"
```

**Generated Test Includes:**
- Navigation steps
- Product selection
- Cart management
- Checkout process
- Assertions for each step

### 2. Form Test Generation

**Request:**
```
"Create a Playwright test in TypeScript for testing the login form"
```

**Output:**
```typescript
test('login form submission', async ({ page }) => {
  await page.goto('https://example.com/login');
  await page.fill('#username', 'testuser');
  await page.fill('#password', 'testpass');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/dashboard/);
});
```

### 3. API Test Generation

**Request:**
```
"Generate Python tests for the REST API endpoints at api.example.com"
```

### 4. Accessibility Test Suite

**Request:**
```
"Create a comprehensive accessibility test suite for my website"
```

---

## Advanced Scenarios

### 1. Performance Monitoring

**Request:**
```
"Monitor the performance of example.com every hour for the next 24 hours"
```

**Claude sets up:**
- Scheduled performance checks
- Metrics tracking
- Trend analysis
- Alert on degradation

### 2. Competitive Analysis

**Request:**
```
"Compare the load times and features of our site with three competitors"
```

**Analysis includes:**
- Performance comparison
- Feature matrix
- SEO comparison
- User experience evaluation

### 3. Security Testing

**Request:**
```
"Check for common security issues like mixed content, exposed API keys, or console errors"
```

### 4. Internationalization Testing

**Request:**
```
"Test the website with different language settings and locales"
```

---

## Workflow Examples

### 1. Daily Test Suite

**Morning Routine Request:**
```
"Run our daily test suite: check homepage loads, test login, verify main features work, and capture screenshots"
```

**Claude executes:**
1. Performance check on homepage
2. Login functionality test
3. Core feature validation
4. Screenshot documentation
5. Summary report generation

### 2. Release Validation

**Pre-Release Request:**
```
"Validate the staging environment at staging.example.com before we deploy to production"
```

**Validation includes:**
- Smoke tests
- Regression tests
- Performance baseline
- Visual regression
- Accessibility check

### 3. Bug Reproduction

**Debug Request:**
```
"Try to reproduce the bug where clicking 'Submit' on the form doesn't work on mobile devices"
```

**Claude will:**
1. Switch to mobile viewport
2. Navigate to form
3. Attempt submission
4. Capture console errors
5. Take screenshots
6. Provide detailed report

### 4. Content Validation

**Content Check Request:**
```
"Verify all links on our website are working and images are loading properly"
```

---

## Tips for Effective Usage

### 1. Be Specific
Instead of: "Test my website"
Better: "Test example.com for performance and accessibility issues"

### 2. Provide Context
Instead of: "Extract data"
Better: "Extract product names and prices from the search results page"

### 3. Chain Operations
```
"First take a screenshot of the homepage, then click the login button, fill in test credentials, and take another screenshot of the dashboard"
```

### 4. Request Analysis
```
"Test example.com and tell me the three most critical issues to fix"
```

### 5. Iterative Testing
```
"Test the form, and if it fails, try with different test data"
```

## Common Patterns

### Testing Workflow
```
1. "Navigate to the website"
2. "Check for console errors"
3. "Test the main user flow"
4. "Take screenshots of key pages"
5. "Generate a test report"
```

### Data Collection Pattern
```
1. "Extract initial data"
2. "Navigate to next page"
3. "Extract additional data"
4. "Compile and format results"
```

### Validation Pattern
```
1. "Fill and submit form"
2. "Check for success message"
3. "Verify data was saved"
4. "Test edge cases"
```

## Integration with Development Workflow

### 1. Pre-Commit Testing
```
"Before I commit, test that the login page still works correctly"
```

### 2. Post-Deployment Verification
```
"The deployment is complete. Verify the production site is working"
```

### 3. Continuous Monitoring
```
"Check the website health every 30 minutes and alert if issues"
```

### 4. Feature Testing
```
"Test the new shopping cart feature I just implemented"
```

## Error Handling

When Claude encounters errors, it will:
1. Provide detailed error messages
2. Suggest potential fixes
3. Offer alternative approaches
4. Take screenshots of error states

Example error handling:
```
"The form submission failed. Try again with different data or check if the form structure has changed"
```

## Best Practices

1. **Start Simple**: Begin with basic requests and add complexity
2. **Verify First**: Ask Claude to navigate to the page first to ensure it's accessible
3. **Use Iterations**: If something fails, ask Claude to try alternative approaches
4. **Request Explanations**: Ask Claude to explain what it's doing and why
5. **Save Results**: Request screenshots and data exports for documentation

---

## Quick Reference Card

### Essential Commands

| Task | Command |
|------|---------|
| Screenshot | "Take a screenshot of [URL]" |
| Test | "Test [URL] for [performance/accessibility/etc]" |
| Extract | "Extract [data] from [URL]" |
| Fill Form | "Fill the form at [URL] with test data" |
| Generate | "Generate a test for [URL]" |
| Navigate | "Go to [URL] and tell me what you see" |
| Execute | "Run this JavaScript on [URL]: [code]" |

### Modifiers

| Modifier | Example |
|----------|---------|
| Browser | "...using Firefox" |
| Full page | "...full-page screenshot" |
| Headless | "...in headless mode" |
| Wait | "...wait for the page to fully load" |
| Specific | "...only test performance" |

---

For more technical details, see the [MCP Tools Reference](./MCP_TOOLS.md).