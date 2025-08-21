# Playwright Automation Scripts Guide

## Overview

This guide covers various automation script generation tools and libraries available for Playwright, including built-in tools, Python libraries, and custom generators.

## 1. Built-in Playwright Codegen

Playwright comes with a powerful code generator that records your browser interactions and generates scripts.

### How to Use Codegen:

```bash
# Generate JavaScript/TypeScript code
npx playwright codegen https://example.com

# Generate Python code
playwright codegen --target python https://example.com

# Generate C# code
playwright codegen --target csharp https://example.com

# Save to file
npx playwright codegen https://example.com -o test.spec.ts

# Use specific browser
npx playwright codegen --browser firefox https://example.com

# Use device emulation
npx playwright codegen --device="iPhone 12" https://example.com
```

### Codegen Features:
- Records clicks, typing, and navigation
- Generates assertions automatically
- Supports multiple languages
- Preserves selectors and waits
- Mobile device emulation

## 2. Custom Automation Generator

We've created a comprehensive automation script generator that creates different types of scripts:

### Usage:

```bash
# Generate basic automation
./scripts/automation-generator.py basic --url https://example.com -o basic_test.py

# Generate form filler
./scripts/automation-generator.py form_filler --url https://example.com/form

# Generate web scraper
./scripts/automation-generator.py scraper --url https://example.com

# Generate website monitor
./scripts/automation-generator.py monitor --url https://example.com

# Generate E2E test
./scripts/automation-generator.py e2e_test --url https://example.com

# Generate API test
./scripts/automation-generator.py api_test --url https://api.example.com

# Generate visual regression test
./scripts/automation-generator.py visual_test --url https://example.com

# Generate performance test
./scripts/automation-generator.py performance --url https://example.com

# Generate accessibility test
./scripts/automation-generator.py accessibility --url https://example.com

# Generate workflow automation
./scripts/automation-generator.py workflow --config workflow.json
```

### Available Templates:

1. **Basic Automation** - Simple navigation and interaction
2. **Form Filler** - Automated form submission
3. **Web Scraper** - Data extraction from websites
4. **Website Monitor** - Continuous monitoring and alerting
5. **E2E Test** - Complete user journey testing
6. **API Test** - API endpoint testing
7. **Visual Test** - Visual regression testing
8. **Performance Test** - Page load and Core Web Vitals
9. **Accessibility Test** - WCAG compliance testing
10. **Workflow Automation** - Custom multi-step workflows

## 3. Python Libraries for Test Generation

### 3.1 pytest-playwright

Integrates Playwright with pytest for better test organization:

```python
# Install
pip install pytest-playwright

# Generate test from recording
playwright codegen --target python-pytest https://example.com
```

### 3.2 Robot Framework Browser Library

Uses Robot Framework's keyword-driven approach:

```bash
pip install robotframework-browser
rfbrowser init

# Example robot file
*** Settings ***
Library    Browser

*** Test Cases ***
Example Test
    New Browser    chromium    headless=False
    New Page    https://example.com
    Click    text=Login
    Fill Text    id=username    testuser
```

### 3.3 Behave with Playwright

BDD-style testing with Gherkin syntax:

```bash
pip install behave playwright-behave

# Feature file
Feature: Login functionality
  Scenario: Successful login
    Given I navigate to "https://example.com"
    When I click on "Login"
    And I enter "testuser" in username field
    Then I should see "Welcome"
```

## 4. AI-Powered Test Generation

### 4.1 Using GPT for Test Generation

```python
import openai

def generate_test_from_description(description):
    prompt = f"""
    Generate a Playwright Python test for the following scenario:
    {description}
    
    Include proper assertions and error handling.
    """
    
    response = openai.Completion.create(
        engine="gpt-4",
        prompt=prompt,
        max_tokens=500
    )
    
    return response.choices[0].text
```

### 4.2 ML-based Selector Generation

```python
from sklearn.ensemble import RandomForestClassifier

class SmartSelectorGenerator:
    def __init__(self):
        self.model = RandomForestClassifier()
    
    def train_on_page_elements(self, page):
        # Extract features from page elements
        # Train model to predict best selectors
        pass
    
    def generate_selector(self, element_description):
        # Use ML model to generate robust selector
        pass
```

## 5. Page Object Model (POM) Generator

### Example POM Generator:

```python
class POMGenerator:
    def analyze_page(self, url):
        """Analyze page and generate POM class."""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)
            
            # Extract page elements
            buttons = page.locator('button').all()
            inputs = page.locator('input').all()
            links = page.locator('a').all()
            
            # Generate POM class
            pom_code = self.generate_pom_class(buttons, inputs, links)
            
            browser.close()
            return pom_code
```

## 6. Test Data Generation

### Libraries for Test Data:

1. **Faker** - Generate realistic test data
```python
from faker import Faker
fake = Faker()

test_data = {
    'name': fake.name(),
    'email': fake.email(),
    'address': fake.address(),
    'phone': fake.phone_number()
}
```

2. **Hypothesis** - Property-based testing
```python
from hypothesis import given, strategies as st

@given(st.text())
def test_with_generated_text(text):
    # Test with automatically generated text
    pass
```

## 7. Automation Workflow Examples

### 7.1 CI/CD Integration

```yaml
# GitHub Actions example
name: Playwright Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm install
      - run: npx playwright install
      - run: npm test
```

### 7.2 Parallel Test Execution

```python
# Using pytest-xdist for parallel execution
pytest -n auto tests/

# Using Playwright Test
npx playwright test --workers=4
```

### 7.3 Cross-Browser Testing

```python
browsers = ['chromium', 'firefox', 'webkit']
for browser_name in browsers:
    browser = getattr(playwright, browser_name).launch()
    # Run tests
```

## 8. Advanced Automation Patterns

### 8.1 Retry Logic

```python
def retry_on_failure(func, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep(2 ** attempt)
```

### 8.2 Custom Wait Conditions

```python
def wait_for_custom_condition(page, condition_func, timeout=30000):
    page.wait_for_function(condition_func, timeout=timeout)
```

### 8.3 Network Mocking

```python
def mock_api_response(page, url_pattern, response_data):
    page.route(url_pattern, lambda route: route.fulfill(
        status=200,
        content_type='application/json',
        body=json.dumps(response_data)
    ))
```

## 9. Best Practices

### Script Organization:
- Use Page Object Model for maintainability
- Separate test data from test logic
- Implement proper error handling
- Use meaningful test names

### Selector Strategies:
1. **Priority Order:**
   - User-facing attributes (role, text)
   - Test IDs (data-testid)
   - IDs and names
   - CSS selectors
   - XPath (last resort)

### Performance Tips:
- Run tests in parallel
- Use headless mode in CI
- Minimize waits
- Reuse browser contexts

## 10. Quick Reference

### Common Automation Tasks:

```python
# Click element
page.click('button')

# Type text
page.fill('input', 'text')

# Select dropdown
page.select_option('select', 'value')

# Upload file
page.set_input_files('input[type="file"]', 'path/to/file')

# Drag and drop
page.drag_and_drop('#source', '#target')

# Take screenshot
page.screenshot(path='screenshot.png')

# PDF generation
page.pdf(path='page.pdf')

# Get element text
text = page.text_content('.element')

# Wait for element
page.wait_for_selector('.element')

# Execute JavaScript
result = page.evaluate('() => document.title')
```

## 11. Troubleshooting

### Common Issues:

1. **Timeout errors**: Increase timeout or add explicit waits
2. **Element not found**: Check selector specificity
3. **Flaky tests**: Add retry logic or better wait conditions
4. **Performance issues**: Use parallel execution

## 12. Resources

- [Playwright Documentation](https://playwright.dev)
- [Playwright Python](https://playwright.dev/python/)
- [Test Automation University](https://testautomationu.applitools.com/)
- [Playwright Community](https://github.com/microsoft/playwright)

---

This environment provides everything needed for comprehensive web automation with Playwright!