#!/usr/bin/env python3
"""
Automation Script Generator for Playwright
Generates various types of automation scripts based on different patterns and use cases.
"""

import json
import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path


class AutomationScriptGenerator:
    """Generate different types of Playwright automation scripts."""
    
    def __init__(self):
        self.templates = {
            'basic': self.generate_basic_automation,
            'form_filler': self.generate_form_filler,
            'scraper': self.generate_web_scraper,
            'monitor': self.generate_website_monitor,
            'e2e_test': self.generate_e2e_test,
            'api_test': self.generate_api_test,
            'visual_test': self.generate_visual_test,
            'performance': self.generate_performance_test,
            'accessibility': self.generate_accessibility_test,
            'workflow': self.generate_workflow_automation
        }
    
    def generate_basic_automation(self, config: Dict) -> str:
        """Generate a basic automation script."""
        url = config.get('url', 'https://example.com')
        actions = config.get('actions', [])
        
        script = f'''#!/usr/bin/env python3
"""
Basic Automation Script
Generated: {datetime.now().isoformat()}
"""

from playwright.sync_api import sync_playwright
import time

def run_automation():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless={config.get('headless', True)})
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to URL
        page.goto("{url}")
        page.wait_for_load_state("networkidle")
        
'''
        
        # Add custom actions
        for action in actions:
            if action['type'] == 'click':
                script += f"        # Click {action.get('description', 'element')}\n"
                script += f"        page.click('{action['selector']}')\n"
                script += f"        page.wait_for_load_state('networkidle')\n\n"
            
            elif action['type'] == 'fill':
                script += f"        # Fill {action.get('description', 'input')}\n"
                script += f"        page.fill('{action['selector']}', '{action['value']}')\n\n"
            
            elif action['type'] == 'select':
                script += f"        # Select {action.get('description', 'option')}\n"
                script += f"        page.select_option('{action['selector']}', '{action['value']}')\n\n"
            
            elif action['type'] == 'wait':
                script += f"        # Wait for {action.get('description', 'element')}\n"
                script += f"        page.wait_for_selector('{action['selector']}')\n\n"
            
            elif action['type'] == 'screenshot':
                script += f"        # Take screenshot\n"
                script += f"        page.screenshot(path='{action.get('path', 'screenshot.png')}')\n\n"
        
        script += '''        # Close browser
        browser.close()
        print("Automation completed successfully!")

if __name__ == "__main__":
    run_automation()
'''
        return script
    
    def generate_form_filler(self, config: Dict) -> str:
        """Generate a form filling automation script."""
        return f'''#!/usr/bin/env python3
"""
Form Filling Automation Script
Generated: {datetime.now().isoformat()}
"""

from playwright.sync_api import sync_playwright
import json
from typing import Dict

def fill_form(page, form_data: Dict):
    """Fill form with provided data."""
    for field_name, value in form_data.items():
        # Try different selector strategies
        selectors = [
            f"input[name='{{field_name}}']",
            f"input[id='{{field_name}}']",
            f"textarea[name='{{field_name}}']",
            f"select[name='{{field_name}}']",
            f"[data-testid='{{field_name}}']"
        ]
        
        for selector in selectors:
            if page.locator(selector).count() > 0:
                element = page.locator(selector).first
                
                # Determine element type and fill accordingly
                tag_name = element.evaluate("el => el.tagName.toLowerCase()")
                
                if tag_name == 'select':
                    element.select_option(value)
                elif tag_name in ['input', 'textarea']:
                    input_type = element.get_attribute('type')
                    if input_type == 'checkbox':
                        if value:
                            element.check()
                    elif input_type == 'radio':
                        element.click()
                    else:
                        element.fill(str(value))
                break

def run_form_automation():
    # Form data configuration
    form_data = {json.dumps(config.get('form_data', {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'phone': '555-0123',
        'message': 'Test message'
    }), indent=8)}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless={config.get('headless', True)})
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to form page
        page.goto("{config.get('url', 'https://example.com/form')}")
        page.wait_for_load_state("networkidle")
        
        # Fill the form
        fill_form(page, form_data)
        
        # Submit form
        submit_button = page.locator('button[type="submit"], input[type="submit"]').first
        if submit_button:
            submit_button.click()
            page.wait_for_load_state("networkidle")
            
            # Check for success message
            success_indicators = ['.success', '.alert-success', '[data-testid="success"]']
            for indicator in success_indicators:
                if page.locator(indicator).count() > 0:
                    print(f"Form submitted successfully!")
                    print(f"Success message: {{page.locator(indicator).first.text_content()}}")
                    break
        
        # Take screenshot of result
        page.screenshot(path="form_submission_result.png")
        
        browser.close()

if __name__ == "__main__":
    run_form_automation()
'''
    
    def generate_web_scraper(self, config: Dict) -> str:
        """Generate a web scraping automation script."""
        return f'''#!/usr/bin/env python3
"""
Web Scraping Automation Script
Generated: {datetime.now().isoformat()}
"""

from playwright.sync_api import sync_playwright
import json
import csv
from datetime import datetime

def scrape_website(url: str, selectors: dict):
    """Scrape data from website using provided selectors."""
    
    scraped_data = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"Scraping {{url}}...")
        page.goto(url, wait_until="networkidle")
        
        # Handle pagination if needed
        max_pages = {config.get('max_pages', 1)}
        current_page = 1
        
        while current_page <= max_pages:
            print(f"Processing page {{current_page}}...")
            
            # Extract items based on container selector
            container_selector = selectors.get('container', '{config.get('container_selector', '.item')}')
            items = page.locator(container_selector).all()
            
            for item in items:
                data = {{'url': url, 'page': current_page}}
                
                # Extract data for each field
                for field_name, selector in selectors.items():
                    if field_name in ['container', 'next_button']:
                        continue
                    
                    try:
                        element = item.locator(selector).first
                        if element:
                            data[field_name] = element.text_content().strip()
                    except:
                        data[field_name] = None
                
                scraped_data.append(data)
            
            # Check for next page
            next_button = selectors.get('next_button', '{config.get('next_button_selector', '')}')
            if next_button and page.locator(next_button).count() > 0:
                page.click(next_button)
                page.wait_for_load_state("networkidle")
                current_page += 1
            else:
                break
        
        browser.close()
    
    return scraped_data

def save_results(data, format='json'):
    """Save scraped data to file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format == 'json':
        filename = f'scraped_data_{{timestamp}}.json'
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    elif format == 'csv':
        filename = f'scraped_data_{{timestamp}}.csv'
        if data:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
    
    print(f"Data saved to {{filename}}")
    return filename

def main():
    # Configuration
    url = "{config.get('url', 'https://example.com')}"
    
    # Define selectors for data extraction
    selectors = {json.dumps(config.get('selectors', {
        'container': '.product',
        'title': 'h2',
        'price': '.price',
        'description': '.description',
        'link': 'a',
        'next_button': '.pagination .next'
    }), indent=4)}
    
    # Scrape data
    data = scrape_website(url, selectors)
    
    # Save results
    if data:
        save_results(data, format='{config.get('output_format', 'json')}')
        print(f"Scraped {{len(data)}} items")
    else:
        print("No data scraped")

if __name__ == "__main__":
    main()
'''
    
    def generate_website_monitor(self, config: Dict) -> str:
        """Generate a website monitoring script."""
        return f'''#!/usr/bin/env python3
"""
Website Monitoring Automation Script
Generated: {datetime.now().isoformat()}
"""

from playwright.sync_api import sync_playwright
import time
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from typing import Dict, List

class WebsiteMonitor:
    def __init__(self, config: Dict):
        self.config = config
        self.alerts = []
    
    def check_availability(self, page) -> bool:
        """Check if website is available."""
        try:
            response = page.goto(self.config['url'], timeout=30000)
            return response.status < 400
        except:
            return False
    
    def check_performance(self, page) -> Dict:
        """Check website performance metrics."""
        metrics = page.evaluate("""() => {{
            const timing = performance.timing;
            return {{
                loadTime: timing.loadEventEnd - timing.navigationStart,
                domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0
            }}
        }}""")
        return metrics
    
    def check_content(self, page, expected_content: List[str]) -> List[str]:
        """Check for expected content on the page."""
        missing_content = []
        for content in expected_content:
            if content not in page.content():
                missing_content.append(content)
        return missing_content
    
    def check_functionality(self, page) -> Dict:
        """Check specific functionality."""
        results = {{}}
        
        # Check for broken links
        links = page.locator('a[href]').all()
        broken_links = []
        for link in links[:10]:  # Check first 10 links
            href = link.get_attribute('href')
            if href and href.startswith('http'):
                try:
                    response = page.request.get(href)
                    if response.status >= 400:
                        broken_links.append(href)
                except:
                    broken_links.append(href)
        
        results['broken_links'] = broken_links
        
        # Check forms
        forms = page.locator('form').count()
        results['forms_count'] = forms
        
        return results
    
    def send_alert(self, message: str):
        """Send alert notification."""
        self.alerts.append({{
            'timestamp': datetime.now().isoformat(),
            'message': message
        }})
        print(f"ALERT: {{message}}")
        
        # Email notification (configure SMTP settings)
        if self.config.get('email_alerts'):
            # Implement email sending logic here
            pass
    
    def monitor(self):
        """Run monitoring checks."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            print(f"Monitoring {{self.config['url']}}...")
            
            # Check availability
            if not self.check_availability(page):
                self.send_alert(f"Website {{self.config['url']}} is DOWN!")
                browser.close()
                return
            
            # Check performance
            metrics = self.check_performance(page)
            if metrics['loadTime'] > self.config.get('max_load_time', 5000):
                self.send_alert(f"Slow load time: {{metrics['loadTime']}}ms")
            
            # Check content
            expected_content = self.config.get('expected_content', [])
            missing = self.check_content(page, expected_content)
            if missing:
                self.send_alert(f"Missing content: {{missing}}")
            
            # Check functionality
            functionality = self.check_functionality(page)
            if functionality['broken_links']:
                self.send_alert(f"Broken links found: {{functionality['broken_links']}}")
            
            # Take screenshot
            page.screenshot(path=f"monitor_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.png")
            
            browser.close()
            
            # Save report
            report = {{
                'timestamp': datetime.now().isoformat(),
                'url': self.config['url'],
                'metrics': metrics,
                'functionality': functionality,
                'alerts': self.alerts
            }}
            
            with open('monitoring_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"Monitoring complete. {{len(self.alerts)}} alerts generated.")

def main():
    config = {json.dumps(config, indent=4)}
    
    monitor = WebsiteMonitor(config)
    
    # Run once or in a loop
    if config.get('continuous'):
        while True:
            monitor.monitor()
            time.sleep(config.get('interval', 300))  # Default 5 minutes
    else:
        monitor.monitor()

if __name__ == "__main__":
    main()
'''
    
    def generate_e2e_test(self, config: Dict) -> str:
        """Generate an end-to-end test script."""
        return f'''#!/usr/bin/env python3
"""
End-to-End Test Automation Script
Generated: {datetime.now().isoformat()}
"""

import pytest
from playwright.sync_api import Page, expect
import os

class TestE2EWorkflow:
    """End-to-end test for {config.get('workflow_name', 'user workflow')}."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup before each test."""
        self.base_url = "{config.get('url', 'https://example.com')}"
        page.goto(self.base_url)
    
    def test_complete_user_journey(self, page: Page):
        """Test complete user journey from start to finish."""
        
        # Step 1: Landing page
        expect(page).to_have_title({repr(config.get('expected_title', ''))})
        expect(page.locator('{config.get('hero_selector', 'h1')}')).to_be_visible()
        
        # Step 2: Navigation
        page.click('{config.get('nav_selector', 'nav a:first-child')}')
        page.wait_for_load_state('networkidle')
        
        # Step 3: User interaction
        # Fill search or filter
        search_input = page.locator('{config.get('search_selector', 'input[type="search"]')}')
        if search_input.count() > 0:
            search_input.fill('{config.get('search_term', 'test')}')
            search_input.press('Enter')
            page.wait_for_load_state('networkidle')
        
        # Step 4: Select item/product
        items = page.locator('{config.get('item_selector', '.item')}')
        if items.count() > 0:
            items.first.click()
            page.wait_for_load_state('networkidle')
        
        # Step 5: Perform action (add to cart, submit form, etc.)
        action_button = page.locator('{config.get('action_button_selector', 'button.primary')}')
        if action_button.count() > 0:
            action_button.click()
            
            # Wait for confirmation
            confirmation = page.locator('{config.get('confirmation_selector', '.success')}')
            expect(confirmation).to_be_visible(timeout=10000)
        
        # Step 6: Verify final state
        # Check URL changed
        assert page.url != self.base_url
        
        # Take screenshot of final state
        page.screenshot(path='e2e_test_result.png')
    
    def test_error_handling(self, page: Page):
        """Test error handling in the workflow."""
        
        # Test invalid input
        form = page.locator('form').first
        if form:
            # Submit empty form
            submit_button = form.locator('button[type="submit"]')
            if submit_button.count() > 0:
                submit_button.click()
                
                # Check for validation errors
                error_messages = page.locator('.error, .invalid, [aria-invalid="true"]')
                expect(error_messages.first).to_be_visible()
    
    def test_responsive_behavior(self, page: Page):
        """Test responsive behavior across devices."""
        
        viewports = [
            {{'width': 1920, 'height': 1080, 'name': 'desktop'}},
            {{'width': 768, 'height': 1024, 'name': 'tablet'}},
            {{'width': 375, 'height': 667, 'name': 'mobile'}}
        ]
        
        for viewport in viewports:
            page.set_viewport_size(width=viewport['width'], height=viewport['height'])
            page.reload()
            
            # Check main elements are visible
            main_content = page.locator('main, #main, .main-content')
            expect(main_content.first).to_be_visible()
            
            # Check navigation works
            if viewport['name'] == 'mobile':
                # Check for mobile menu
                menu_button = page.locator('.menu-toggle, .hamburger, [aria-label*="menu"]')
                if menu_button.count() > 0:
                    menu_button.click()
                    nav = page.locator('nav, .navigation')
                    expect(nav.first).to_be_visible()

if __name__ == "__main__":
    pytest.main([__file__, '-v'])
'''
    
    def generate_api_test(self, config: Dict) -> str:
        """Generate API testing script."""
        return f'''#!/usr/bin/env python3
"""
API Testing Automation Script
Generated: {datetime.now().isoformat()}
"""

from playwright.sync_api import sync_playwright
import json
from typing import Dict, List

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = []
    
    def test_endpoint(self, context, method: str, endpoint: str, **kwargs) -> Dict:
        """Test a single API endpoint."""
        url = f"{{self.base_url}}{{endpoint}}"
        
        try:
            if method.upper() == 'GET':
                response = context.request.get(url, **kwargs)
            elif method.upper() == 'POST':
                response = context.request.post(url, **kwargs)
            elif method.upper() == 'PUT':
                response = context.request.put(url, **kwargs)
            elif method.upper() == 'DELETE':
                response = context.request.delete(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {{method}}")
            
            result = {{
                'endpoint': endpoint,
                'method': method,
                'status': response.status,
                'ok': response.ok,
                'headers': dict(response.headers),
                'body': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text()
            }}
            
            # Validate response
            if 'data' in kwargs:
                result['request_data'] = kwargs['data']
            
            return result
            
        except Exception as e:
            return {{
                'endpoint': endpoint,
                'method': method,
                'error': str(e)
            }}
    
    def run_tests(self, test_cases: List[Dict]):
        """Run multiple API tests."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            
            for test in test_cases:
                print(f"Testing {{test['method']}} {{test['endpoint']}}...")
                result = self.test_endpoint(
                    context,
                    test['method'],
                    test['endpoint'],
                    **test.get('options', {{}})
                )
                
                # Validate expectations
                if 'expected_status' in test:
                    result['status_ok'] = result.get('status') == test['expected_status']
                
                if 'expected_fields' in test and 'body' in result:
                    missing_fields = []
                    for field in test['expected_fields']:
                        if field not in result['body']:
                            missing_fields.append(field)
                    result['missing_fields'] = missing_fields
                
                self.results.append(result)
            
            browser.close()
        
        return self.results
    
    def generate_report(self):
        """Generate test report."""
        passed = sum(1 for r in self.results if r.get('ok') and not r.get('error'))
        failed = len(self.results) - passed
        
        report = {{
            'total_tests': len(self.results),
            'passed': passed,
            'failed': failed,
            'results': self.results
        }}
        
        with open('api_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\\nAPI Test Results:")
        print(f"Total: {{len(self.results)}}")
        print(f"Passed: {{passed}}")
        print(f"Failed: {{failed}}")
        
        if failed > 0:
            print("\\nFailed tests:")
            for result in self.results:
                if result.get('error') or not result.get('ok'):
                    error_msg = result.get('error') or f"Status {result.get('status')}"
                    print(f"  - {{result['method']}} {{result['endpoint']}}: {{error_msg}}")

def main():
    # Configuration
    base_url = "{config.get('api_base_url', 'https://api.example.com')}"
    
    # Define test cases
    test_cases = {json.dumps(config.get('test_cases', [
        {
            'method': 'GET',
            'endpoint': '/health',
            'expected_status': 200
        },
        {
            'method': 'GET',
            'endpoint': '/api/users',
            'expected_status': 200,
            'expected_fields': ['users', 'total']
        },
        {
            'method': 'POST',
            'endpoint': '/api/users',
            'options': {
                'data': {'name': 'Test User', 'email': 'test@example.com'}
            },
            'expected_status': 201
        }
    ]), indent=4)}
    
    # Run tests
    tester = APITester(base_url)
    tester.run_tests(test_cases)
    tester.generate_report()

if __name__ == "__main__":
    main()
'''
    
    def generate_visual_test(self, config: Dict) -> str:
        """Generate visual regression testing script."""
        return f'''#!/usr/bin/env python3
"""
Visual Testing Automation Script
Generated: {datetime.now().isoformat()}
"""

from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
import os
from datetime import datetime
from typing import List, Dict

class VisualTester:
    def __init__(self, config: Dict):
        self.config = config
        self.baseline_dir = config.get('baseline_dir', 'visual_baselines')
        self.results_dir = config.get('results_dir', 'visual_results')
        self.threshold = config.get('threshold', 0.1)  # 10% difference threshold
        
        # Create directories
        os.makedirs(self.baseline_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
    
    def capture_screenshot(self, page, name: str, full_page: bool = True) -> str:
        """Capture screenshot of current page."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{{name}}_{{timestamp}}.png"
        filepath = os.path.join(self.results_dir, filename)
        
        page.screenshot(path=filepath, full_page=full_page)
        return filepath
    
    def compare_images(self, baseline_path: str, current_path: str) -> Dict:
        """Compare two images and return difference metrics."""
        baseline = Image.open(baseline_path)
        current = Image.open(current_path)
        
        # Resize if needed
        if baseline.size != current.size:
            current = current.resize(baseline.size)
        
        # Calculate difference
        diff = ImageChops.difference(baseline, current)
        
        # Calculate difference percentage
        pixels = list(diff.getdata())
        total_pixels = len(pixels)
        different_pixels = sum(1 for pixel in pixels if sum(pixel[:3]) > 30)  # RGB threshold
        
        diff_percentage = (different_pixels / total_pixels) * 100
        
        # Save diff image
        diff_path = current_path.replace('.png', '_diff.png')
        diff.save(diff_path)
        
        return {{
            'different_pixels': different_pixels,
            'total_pixels': total_pixels,
            'difference_percentage': diff_percentage,
            'passed': diff_percentage <= self.threshold,
            'diff_image': diff_path
        }}
    
    def test_page_visual(self, page, url: str, name: str) -> Dict:
        """Test visual appearance of a page."""
        page.goto(url, wait_until='networkidle')
        
        # Capture current screenshot
        current_path = self.capture_screenshot(page, name)
        
        # Check for baseline
        baseline_filename = f"{{name}}_baseline.png"
        baseline_path = os.path.join(self.baseline_dir, baseline_filename)
        
        if not os.path.exists(baseline_path):
            # Create baseline
            page.screenshot(path=baseline_path, full_page=True)
            return {{
                'name': name,
                'url': url,
                'status': 'baseline_created',
                'baseline_path': baseline_path
            }}
        
        # Compare with baseline
        comparison = self.compare_images(baseline_path, current_path)
        
        return {{
            'name': name,
            'url': url,
            'status': 'passed' if comparison['passed'] else 'failed',
            'comparison': comparison,
            'screenshot': current_path
        }}
    
    def test_responsive_visual(self, page, url: str, name: str) -> List[Dict]:
        """Test visual appearance across different viewports."""
        viewports = [
            {{'width': 1920, 'height': 1080, 'name': 'desktop'}},
            {{'width': 768, 'height': 1024, 'name': 'tablet'}},
            {{'width': 375, 'height': 667, 'name': 'mobile'}}
        ]
        
        results = []
        
        for viewport in viewports:
            page.set_viewport_size(width=viewport['width'], height=viewport['height'])
            viewport_name = f"{{name}}_{{viewport['name']}}"
            result = self.test_page_visual(page, url, viewport_name)
            result['viewport'] = viewport
            results.append(result)
        
        return results
    
    def run_visual_tests(self, test_pages: List[Dict]):
        """Run visual tests on multiple pages."""
        all_results = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            for test_page in test_pages:
                print(f"Testing {{test_page['name']}}...")
                
                if test_page.get('responsive', False):
                    results = self.test_responsive_visual(
                        page,
                        test_page['url'],
                        test_page['name']
                    )
                    all_results.extend(results)
                else:
                    result = self.test_page_visual(
                        page,
                        test_page['url'],
                        test_page['name']
                    )
                    all_results.append(result)
            
            browser.close()
        
        # Generate report
        self.generate_report(all_results)
        
        return all_results
    
    def generate_report(self, results: List[Dict]):
        """Generate visual testing report."""
        passed = sum(1 for r in results if r.get('status') == 'passed')
        failed = sum(1 for r in results if r.get('status') == 'failed')
        baseline_created = sum(1 for r in results if r.get('status') == 'baseline_created')
        
        print(f"\\nVisual Test Results:")
        print(f"Passed: {{passed}}")
        print(f"Failed: {{failed}}")
        print(f"Baselines Created: {{baseline_created}}")
        
        if failed > 0:
            print("\\nFailed tests:")
            for result in results:
                if result['status'] == 'failed':
                    diff = result['comparison']['difference_percentage']
                    print(f"  - {{result['name']}}: {{diff:.2f}}% difference")
                    print(f"    Diff image: {{result['comparison']['diff_image']}}")

def main():
    config = {json.dumps(config.get('visual_config', {
        'baseline_dir': 'visual_baselines',
        'results_dir': 'visual_results',
        'threshold': 0.1
    }), indent=4)}
    
    test_pages = {json.dumps(config.get('test_pages', [
        {'name': 'homepage', 'url': 'https://example.com', 'responsive': True},
        {'name': 'about', 'url': 'https://example.com/about'},
        {'name': 'contact', 'url': 'https://example.com/contact'}
    ]), indent=4)}
    
    tester = VisualTester(config)
    tester.run_visual_tests(test_pages)

if __name__ == "__main__":
    main()
'''
    
    def generate_performance_test(self, config: Dict) -> str:
        """Generate performance testing script."""
        return f'''#!/usr/bin/env python3
"""
Performance Testing Automation Script
Generated: {datetime.now().isoformat()}
"""

from playwright.sync_api import sync_playwright
import json
import statistics
from typing import Dict, List
from datetime import datetime

class PerformanceTester:
    def __init__(self, config: Dict):
        self.config = config
        self.results = []
    
    def measure_page_metrics(self, page) -> Dict:
        """Measure page performance metrics."""
        metrics = page.evaluate("""() => {{
            const timing = performance.timing;
            const paint = performance.getEntriesByType('paint');
            const resources = performance.getEntriesByType('resource');
            
            return {{
                // Navigation timing
                dns: timing.domainLookupEnd - timing.domainLookupStart,
                tcp: timing.connectEnd - timing.connectStart,
                request: timing.responseStart - timing.requestStart,
                response: timing.responseEnd - timing.responseStart,
                dom: timing.domComplete - timing.domLoading,
                load: timing.loadEventEnd - timing.navigationStart,
                domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                
                // Paint timing
                firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
                firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
                
                // Resource timing
                resourceCount: resources.length,
                totalResourceSize: resources.reduce((acc, r) => acc + (r.transferSize || 0), 0),
                totalResourceTime: resources.reduce((acc, r) => acc + r.duration, 0),
                
                // Memory (if available)
                memory: performance.memory ? {{
                    usedJSHeapSize: performance.memory.usedJSHeapSize,
                    totalJSHeapSize: performance.memory.totalJSHeapSize
                }} : null
            }};
        }}""")
        
        return metrics
    
    def measure_core_web_vitals(self, page) -> Dict:
        """Measure Core Web Vitals."""
        # Inject web-vitals library
        page.add_script_tag(url="https://unpkg.com/web-vitals/dist/web-vitals.iife.js")
        
        # Wait for metrics
        page.wait_for_timeout(3000)
        
        vitals = page.evaluate("""() => {{
            return new Promise((resolve) => {{
                const results = {{}};
                
                webVitals.getCLS((metric) => {{ results.CLS = metric.value; }});
                webVitals.getFID((metric) => {{ results.FID = metric.value; }});
                webVitals.getLCP((metric) => {{ results.LCP = metric.value; }});
                webVitals.getFCP((metric) => {{ results.FCP = metric.value; }});
                webVitals.getTTFB((metric) => {{ results.TTFB = metric.value; }});
                
                setTimeout(() => resolve(results), 1000);
            }});
        }}""")
        
        return vitals
    
    def run_performance_test(self, url: str, iterations: int = 3) -> Dict:
        """Run performance test with multiple iterations."""
        all_metrics = []
        all_vitals = []
        
        with sync_playwright() as p:
            for i in range(iterations):
                print(f"  Iteration {{i+1}}/{{iterations}}...")
                
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                
                # Navigate to page
                page.goto(url, wait_until='networkidle')
                
                # Measure metrics
                metrics = self.measure_page_metrics(page)
                vitals = self.measure_core_web_vitals(page)
                
                all_metrics.append(metrics)
                all_vitals.append(vitals)
                
                browser.close()
        
        # Calculate statistics
        stats = self.calculate_statistics(all_metrics, all_vitals)
        
        return {{
            'url': url,
            'iterations': iterations,
            'metrics': all_metrics,
            'vitals': all_vitals,
            'statistics': stats
        }}
    
    def calculate_statistics(self, metrics: List[Dict], vitals: List[Dict]) -> Dict:
        """Calculate statistics from multiple test runs."""
        stats = {{}}
        
        # Calculate averages for metrics
        metric_keys = metrics[0].keys() if metrics else []
        for key in metric_keys:
            if key != 'memory':
                values = [m[key] for m in metrics if isinstance(m.get(key), (int, float))]
                if values:
                    stats[key] = {{
                        'avg': statistics.mean(values),
                        'median': statistics.median(values),
                        'min': min(values),
                        'max': max(values),
                        'stdev': statistics.stdev(values) if len(values) > 1 else 0
                    }}
        
        # Calculate averages for vitals
        vital_keys = vitals[0].keys() if vitals else []
        for key in vital_keys:
            values = [v.get(key) for v in vitals if v.get(key) is not None]
            if values:
                stats[f"vital_{{key}}"] = {{
                    'avg': statistics.mean(values),
                    'median': statistics.median(values),
                    'min': min(values),
                    'max': max(values)
                }}
        
        return stats
    
    def evaluate_performance(self, stats: Dict) -> Dict:
        """Evaluate performance against thresholds."""
        evaluation = {{
            'passed': True,
            'warnings': [],
            'failures': []
        }}
        
        # Check load time
        if stats.get('load', {{}}).get('avg', 0) > 3000:
            evaluation['failures'].append(f"Load time too high: {{stats['load']['avg']:.0f}}ms")
            evaluation['passed'] = False
        
        # Check First Contentful Paint
        if stats.get('vital_FCP', {{}}).get('avg', 0) > 1800:
            evaluation['warnings'].append(f"FCP needs improvement: {{stats['vital_FCP']['avg']:.0f}}ms")
        
        # Check Largest Contentful Paint
        if stats.get('vital_LCP', {{}}).get('avg', 0) > 2500:
            evaluation['failures'].append(f"LCP too high: {{stats['vital_LCP']['avg']:.0f}}ms")
            evaluation['passed'] = False
        
        # Check Cumulative Layout Shift
        if stats.get('vital_CLS', {{}}).get('avg', 0) > 0.1:
            evaluation['warnings'].append(f"CLS needs improvement: {{stats['vital_CLS']['avg']:.3f}}")
        
        return evaluation

def main():
    config = {json.dumps(config, indent=4)}
    
    tester = PerformanceTester(config)
    
    urls = config.get('urls', ['{config.get('url', 'https://example.com')}'])
    
    for url in urls:
        print(f"Testing performance for {{url}}...")
        result = tester.run_performance_test(url, iterations=config.get('iterations', 3))
        
        # Evaluate performance
        evaluation = tester.evaluate_performance(result['statistics'])
        
        # Print results
        print(f"\\nResults for {{url}}:")
        print(f"Load Time: {{result['statistics']['load']['avg']:.0f}}ms")
        print(f"FCP: {{result['statistics'].get('vital_FCP', {{}}).get('avg', 'N/A')}}ms")
        print(f"LCP: {{result['statistics'].get('vital_LCP', {{}}).get('avg', 'N/A')}}ms")
        print(f"CLS: {{result['statistics'].get('vital_CLS', {{}}).get('avg', 'N/A')}}")
        
        if evaluation['warnings']:
            print("\\nWarnings:")
            for warning in evaluation['warnings']:
                print(f"  - {{warning}}")
        
        if evaluation['failures']:
            print("\\nFailures:")
            for failure in evaluation['failures']:
                print(f"  - {{failure}}")
        
        # Save detailed report
        with open(f'performance_report_{{datetime.now().strftime("%Y%m%d_%H%M%S")}}.json', 'w') as f:
            json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
'''
    
    def generate_accessibility_test(self, config: Dict) -> str:
        """Generate accessibility testing script."""
        return f'''#!/usr/bin/env python3
"""
Accessibility Testing Automation Script
Generated: {datetime.now().isoformat()}
"""

from playwright.sync_api import sync_playwright
import json
from typing import Dict, List

class AccessibilityTester:
    def __init__(self, config: Dict):
        self.config = config
        self.issues = []
    
    def inject_axe(self, page):
        """Inject axe-core accessibility testing library."""
        page.add_script_tag(url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.2/axe.min.js")
    
    def run_axe_scan(self, page) -> Dict:
        """Run axe accessibility scan."""
        results = page.evaluate("""() => {{
            return new Promise((resolve) => {{
                axe.run().then(results => {{
                    resolve(results);
                }});
            }});
        }}""")
        
        return results
    
    def check_custom_rules(self, page) -> List[Dict]:
        """Check custom accessibility rules."""
        issues = []
        
        # Check images for alt text
        images = page.locator('img').all()
        for i, img in enumerate(images):
            alt = img.get_attribute('alt')
            src = img.get_attribute('src')
            if alt is None:
                issues.append({{
                    'type': 'missing_alt',
                    'element': f'img[{{i}}]',
                    'src': src,
                    'severity': 'serious'
                }})
        
        # Check form labels
        inputs = page.locator('input, textarea, select').all()
        for i, input_elem in enumerate(inputs):
            input_id = input_elem.get_attribute('id')
            input_name = input_elem.get_attribute('name')
            
            # Check for associated label
            if input_id:
                label = page.locator(f'label[for="{{input_id}}"]')
                if label.count() == 0:
                    # Check if input is wrapped in label
                    parent = input_elem.evaluate("el => el.parentElement.tagName")
                    if parent.lower() != 'label':
                        issues.append({{
                            'type': 'missing_label',
                            'element': f'input[name="{{input_name}}"]',
                            'severity': 'serious'
                        }})
        
        # Check heading hierarchy
        headings = page.locator('h1, h2, h3, h4, h5, h6').all()
        prev_level = 0
        for heading in headings:
            tag_name = heading.evaluate("el => el.tagName")
            level = int(tag_name[1])
            
            if prev_level > 0 and level > prev_level + 1:
                issues.append({{
                    'type': 'heading_skip',
                    'element': tag_name,
                    'text': heading.text_content()[:50],
                    'severity': 'moderate'
                }})
            prev_level = level
        
        # Check color contrast (simplified check)
        elements = page.locator('[style*="color"], [style*="background"]').all()
        for elem in elements[:10]:  # Check first 10 elements
            styles = elem.evaluate("""(el) => {{
                const computed = window.getComputedStyle(el);
                return {{
                    color: computed.color,
                    backgroundColor: computed.backgroundColor
                }};
            }}""")
            
            # You would need a proper contrast calculation here
            # This is a placeholder
            if styles['color'] and styles['backgroundColor']:
                # Add contrast checking logic
                pass
        
        return issues
    
    def check_keyboard_navigation(self, page) -> List[Dict]:
        """Check keyboard navigation."""
        issues = []
        
        # Check for skip links
        skip_links = page.locator('a[href^="#"]:text-matches("skip", "i")').count()
        if skip_links == 0:
            issues.append({{
                'type': 'missing_skip_link',
                'severity': 'moderate',
                'message': 'No skip navigation link found'
            }})
        
        # Check focusable elements
        focusable = page.locator('a, button, input, textarea, select, [tabindex]').all()
        for elem in focusable[:20]:  # Check first 20 elements
            tabindex = elem.get_attribute('tabindex')
            if tabindex and int(tabindex) > 0:
                issues.append({{
                    'type': 'positive_tabindex',
                    'element': elem.evaluate("el => el.outerHTML.substring(0, 100)"),
                    'severity': 'minor',
                    'message': 'Positive tabindex disrupts natural tab order'
                }})
        
        return issues
    
    def check_aria_attributes(self, page) -> List[Dict]:
        """Check ARIA attributes."""
        issues = []
        
        # Check for valid ARIA roles
        elements_with_role = page.locator('[role]').all()
        valid_roles = ['button', 'navigation', 'main', 'banner', 'contentinfo', 'search', 'form', 'region']
        
        for elem in elements_with_role:
            role = elem.get_attribute('role')
            if role not in valid_roles:
                issues.append({{
                    'type': 'invalid_aria_role',
                    'role': role,
                    'severity': 'serious'
                }})
        
        # Check ARIA labels on interactive elements
        interactive = page.locator('button, a[href], input, select, textarea').all()
        for elem in interactive:
            text = elem.text_content()
            aria_label = elem.get_attribute('aria-label')
            aria_labelledby = elem.get_attribute('aria-labelledby')
            
            if not text and not aria_label and not aria_labelledby:
                tag = elem.evaluate("el => el.tagName")
                issues.append({{
                    'type': 'missing_accessible_name',
                    'element': tag,
                    'severity': 'serious'
                }})
        
        return issues
    
    def test_page_accessibility(self, page, url: str) -> Dict:
        """Test accessibility of a page."""
        print(f"Testing accessibility for {{url}}...")
        
        page.goto(url, wait_until='networkidle')
        
        # Inject axe-core
        self.inject_axe(page)
        
        # Run axe scan
        axe_results = self.run_axe_scan(page)
        
        # Run custom checks
        custom_issues = []
        custom_issues.extend(self.check_custom_rules(page))
        custom_issues.extend(self.check_keyboard_navigation(page))
        custom_issues.extend(self.check_aria_attributes(page))
        
        return {{
            'url': url,
            'axe_violations': axe_results.get('violations', []),
            'axe_passes': len(axe_results.get('passes', [])),
            'custom_issues': custom_issues,
            'wcag_compliance': self.calculate_wcag_compliance(axe_results, custom_issues)
        }}
    
    def calculate_wcag_compliance(self, axe_results: Dict, custom_issues: List) -> Dict:
        """Calculate WCAG compliance level."""
        violations = axe_results.get('violations', [])
        
        critical_count = sum(1 for v in violations if v.get('impact') == 'critical')
        serious_count = sum(1 for v in violations if v.get('impact') == 'serious')
        moderate_count = sum(1 for v in violations if v.get('impact') == 'moderate')
        minor_count = sum(1 for v in violations if v.get('impact') == 'minor')
        
        # Add custom issues
        serious_count += sum(1 for i in custom_issues if i.get('severity') == 'serious')
        moderate_count += sum(1 for i in custom_issues if i.get('severity') == 'moderate')
        minor_count += sum(1 for i in custom_issues if i.get('severity') == 'minor')
        
        compliance_level = 'AAA'
        if critical_count > 0:
            compliance_level = 'Fail'
        elif serious_count > 0:
            compliance_level = 'A'
        elif moderate_count > 0:
            compliance_level = 'AA'
        
        return {{
            'level': compliance_level,
            'critical': critical_count,
            'serious': serious_count,
            'moderate': moderate_count,
            'minor': minor_count
        }}

def main():
    config = {json.dumps(config, indent=4)}
    
    tester = AccessibilityTester(config)
    
    urls = config.get('urls', ['{config.get('url', 'https://example.com')}'])
    
    all_results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        for url in urls:
            result = tester.test_page_accessibility(page, url)
            all_results.append(result)
            
            # Print summary
            compliance = result['wcag_compliance']
            print(f"\\nResults for {{url}}:")
            print(f"WCAG Compliance Level: {{compliance['level']}}")
            print(f"Critical Issues: {{compliance['critical']}}")
            print(f"Serious Issues: {{compliance['serious']}}")
            print(f"Moderate Issues: {{compliance['moderate']}}")
            print(f"Minor Issues: {{compliance['minor']}}")
            
            if result['axe_violations']:
                print("\\nTop violations:")
                for violation in result['axe_violations'][:5]:
                    print(f"  - {{violation.get('description', 'No description')}}")
                    print(f"    Impact: {{violation.get('impact', 'Unknown')}}")
        
        browser.close()
    
    # Save detailed report
    with open('accessibility_report.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\\nDetailed report saved to accessibility_report.json")

if __name__ == "__main__":
    main()
'''
    
    def generate_workflow_automation(self, config: Dict) -> str:
        """Generate workflow automation script."""
        workflow_steps = config.get('workflow_steps', [])
        steps_code = ""
        
        for i, step in enumerate(workflow_steps, 1):
            steps_code += f'''
        # Step {i}: {step.get('description', 'Action')}
        print(f"Step {i}: {step.get('description', 'Action')}")
'''
            
            if step['type'] == 'navigate':
                steps_code += f"        page.goto('{step['url']}')\n"
                steps_code += f"        page.wait_for_load_state('networkidle')\n"
            
            elif step['type'] == 'click':
                steps_code += f"        page.click('{step['selector']}')\n"
            
            elif step['type'] == 'fill':
                steps_code += f"        page.fill('{step['selector']}', '{step['value']}')\n"
            
            elif step['type'] == 'wait':
                steps_code += f"        page.wait_for_selector('{step['selector']}')\n"
            
            elif step['type'] == 'screenshot':
                steps_code += f"        page.screenshot(path='step_{i}_screenshot.png')\n"
            
            elif step['type'] == 'extract':
                steps_code += f"        data['{step['name']}'] = page.locator('{step['selector']}').text_content()\n"
            
            steps_code += "\n"
        
        return f'''#!/usr/bin/env python3
"""
Workflow Automation Script
Generated: {datetime.now().isoformat()}
Workflow: {config.get('workflow_name', 'Custom Workflow')}
"""

from playwright.sync_api import sync_playwright
import json
from datetime import datetime

def run_workflow():
    """Execute the automated workflow."""
    
    # Data storage for extracted information
    data = {{}}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless={config.get('headless', True)})
        context = browser.new_context()
        page = context.new_page()
        
        try:
            print("Starting workflow: {config.get('workflow_name', 'Custom Workflow')}")
            print("=" * 50)
            {steps_code}
            
            # Save extracted data
            if data:
                with open('workflow_data.json', 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"\\nExtracted data saved to workflow_data.json")
            
            print("\\nWorkflow completed successfully!")
            
        except Exception as e:
            print(f"\\nWorkflow failed: {{e}}")
            page.screenshot(path='error_screenshot.png')
            raise
        
        finally:
            browser.close()

if __name__ == "__main__":
    run_workflow()
'''
    
    def generate_script(self, template_type: str, config: Dict) -> str:
        """Generate a script based on template type."""
        if template_type in self.templates:
            return self.templates[template_type](config)
        else:
            raise ValueError(f"Unknown template type: {template_type}")


def main():
    """Main function to generate automation scripts."""
    parser = argparse.ArgumentParser(description='Generate Playwright automation scripts')
    parser.add_argument('type', choices=[
        'basic', 'form_filler', 'scraper', 'monitor', 'e2e_test',
        'api_test', 'visual_test', 'performance', 'accessibility', 'workflow'
    ], help='Type of automation script to generate')
    parser.add_argument('--url', default='https://example.com', help='Target URL')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--config', '-c', help='JSON config file')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run in headless mode')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {
        'url': args.url,
        'headless': args.headless
    }
    
    if args.config:
        with open(args.config, 'r') as f:
            config.update(json.load(f))
    
    # Generate script
    generator = AutomationScriptGenerator()
    script = generator.generate_script(args.type, config)
    
    # Save or print script
    if args.output:
        with open(args.output, 'w') as f:
            f.write(script)
        os.chmod(args.output, 0o755)
        print(f"Script generated: {args.output}")
    else:
        print(script)


if __name__ == '__main__':
    main()