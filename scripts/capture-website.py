#!/usr/bin/env python3
"""
Website capture script for retrieving data and screenshots using Playwright.
This script can be used to automate browser interactions and extract data.
"""

import sys
import os
import json
import argparse
from datetime import datetime
from playwright.sync_api import sync_playwright
import base64


def capture_website(url, options=None):
    """
    Capture website screenshot and extract data.
    
    Args:
        url: The URL to capture
        options: Dictionary of capture options
    
    Returns:
        Dictionary with captured data
    """
    if options is None:
        options = {}
    
    result = {
        'url': url,
        'timestamp': datetime.now().isoformat(),
        'success': False,
        'data': {},
        'screenshot': None,
        'error': None
    }
    
    with sync_playwright() as p:
        try:
            # Launch browser
            browser = p.chromium.launch(
                headless=options.get('headless', True),
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            # Create context with custom viewport
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # Create page
            page = context.new_page()
            
            # Navigate to URL
            print(f"Navigating to {url}...")
            response = page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load
            page.wait_for_load_state('domcontentloaded')
            
            # Extract page data
            result['data']['status_code'] = response.status if response else None
            result['data']['title'] = page.title()
            result['data']['url'] = page.url
            
            # Extract specific data based on the website
            if 'ipchicken.com' in url:
                # Extract IP information from ipchicken.com
                try:
                    ip_data = page.evaluate("""() => {
                        const result = {};
                        
                        // Get IP address
                        const ipElement = document.querySelector('b:first-of-type');
                        if (ipElement) {
                            result.ip = ipElement.textContent.trim();
                        }
                        
                        // Get all table data
                        const rows = document.querySelectorAll('tr');
                        rows.forEach(row => {
                            const cells = row.querySelectorAll('td');
                            if (cells.length >= 2) {
                                const key = cells[0].textContent.trim().replace(':', '');
                                const value = cells[1].textContent.trim();
                                if (key && value) {
                                    result[key.toLowerCase().replace(/\\s+/g, '_')] = value;
                                }
                            }
                        });
                        
                        return result;
                    }""")
                    result['data']['extracted_info'] = ip_data
                    print(f"Extracted IP data: {json.dumps(ip_data, indent=2)}")
                except Exception as e:
                    print(f"Error extracting IP data: {e}")
            
            # Extract general page information
            page_info = page.evaluate("""() => {
                return {
                    url: window.location.href,
                    hostname: window.location.hostname,
                    protocol: window.location.protocol,
                    userAgent: navigator.userAgent,
                    language: navigator.language,
                    cookieEnabled: navigator.cookieEnabled,
                    onlineStatus: navigator.onLine,
                    screenResolution: {
                        width: window.screen.width,
                        height: window.screen.height
                    },
                    viewport: {
                        width: window.innerWidth,
                        height: window.innerHeight
                    },
                    documentHeight: document.documentElement.scrollHeight,
                    documentWidth: document.documentElement.scrollWidth
                }
            }""")
            result['data']['page_info'] = page_info
            
            # Take screenshot
            screenshot_path = options.get('screenshot_path')
            if not screenshot_path:
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                screenshot_path = f"reports/screenshots/capture-{timestamp}.png"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            
            # Take full page screenshot
            screenshot_bytes = page.screenshot(
                path=screenshot_path,
                full_page=options.get('full_page', True)
            )
            result['screenshot'] = screenshot_path
            
            # Optionally encode screenshot as base64 for API response
            if options.get('base64_screenshot', False):
                result['screenshot_base64'] = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            print(f"Screenshot saved to: {screenshot_path}")
            
            # Extract all text content if requested
            if options.get('extract_text', False):
                text_content = page.evaluate("""() => {
                    return document.body.innerText;
                }""")
                result['data']['text_content'] = text_content
            
            # Extract all links if requested
            if options.get('extract_links', False):
                links = page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('a')).map(a => ({
                        text: a.textContent.trim(),
                        href: a.href,
                        target: a.target
                    }));
                }""")
                result['data']['links'] = links
            
            # Get cookies
            cookies = context.cookies()
            result['data']['cookies'] = [
                {'name': c['name'], 'value': c['value'], 'domain': c['domain']} 
                for c in cookies
            ]
            
            result['success'] = True
            
            # Close browser
            browser.close()
            
        except Exception as e:
            result['error'] = str(e)
            print(f"Error: {e}")
            if 'browser' in locals():
                browser.close()
    
    return result


def create_api_driver():
    """
    Create an API-driven browser automation class.
    This can be used to control the browser programmatically.
    """
    class BrowserAPI:
        def __init__(self):
            self.playwright = None
            self.browser = None
            self.context = None
            self.page = None
        
        def start(self, headless=True):
            """Start the browser."""
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            self.page = self.context.new_page()
            return True
        
        def navigate(self, url):
            """Navigate to a URL."""
            response = self.page.goto(url, wait_until='networkidle')
            return {
                'status': response.status if response else None,
                'url': self.page.url,
                'title': self.page.title()
            }
        
        def screenshot(self, path=None, full_page=True):
            """Take a screenshot."""
            if not path:
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                path = f"reports/screenshots/api-capture-{timestamp}.png"
            
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.page.screenshot(path=path, full_page=full_page)
            return path
        
        def extract_text(self, selector='body'):
            """Extract text from a selector."""
            return self.page.locator(selector).text_content()
        
        def extract_data(self, javascript):
            """Execute JavaScript and return data."""
            return self.page.evaluate(javascript)
        
        def click(self, selector):
            """Click an element."""
            self.page.click(selector)
            return True
        
        def fill(self, selector, text):
            """Fill a text input."""
            self.page.fill(selector, text)
            return True
        
        def wait_for(self, selector, timeout=30000):
            """Wait for an element to appear."""
            self.page.wait_for_selector(selector, timeout=timeout)
            return True
        
        def get_cookies(self):
            """Get all cookies."""
            return self.context.cookies()
        
        def set_cookie(self, name, value, domain=None):
            """Set a cookie."""
            cookie = {'name': name, 'value': value}
            if domain:
                cookie['domain'] = domain
                cookie['url'] = f'https://{domain}'
            else:
                cookie['url'] = self.page.url
            self.context.add_cookies([cookie])
            return True
        
        def stop(self):
            """Stop the browser."""
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            return True
    
    return BrowserAPI


def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description='Capture website data and screenshots')
    parser.add_argument('url', help='URL to capture')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run in headless mode (default: True)')
    parser.add_argument('--headed', action='store_true',
                       help='Run in headed mode (show browser)')
    parser.add_argument('--full-page', action='store_true', default=True,
                       help='Capture full page screenshot')
    parser.add_argument('--extract-text', action='store_true',
                       help='Extract all text content')
    parser.add_argument('--extract-links', action='store_true',
                       help='Extract all links')
    parser.add_argument('--base64', action='store_true',
                       help='Include base64 encoded screenshot in output')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    parser.add_argument('--screenshot', '-s', help='Screenshot file path')
    parser.add_argument('--api-demo', action='store_true',
                       help='Run API driver demonstration')
    
    args = parser.parse_args()
    
    if args.api_demo:
        # Demonstrate API-driven browser
        print("=== API-Driven Browser Demonstration ===\n")
        
        BrowserAPI = create_api_driver()
        api = BrowserAPI()
        
        try:
            print("1. Starting browser...")
            api.start(headless=not args.headed)
            
            print(f"2. Navigating to {args.url}...")
            nav_result = api.navigate(args.url)
            print(f"   Title: {nav_result['title']}")
            print(f"   Status: {nav_result['status']}")
            
            print("3. Taking screenshot...")
            screenshot_path = api.screenshot()
            print(f"   Saved to: {screenshot_path}")
            
            if 'ipchicken.com' in args.url:
                print("4. Extracting IP information...")
                ip_data = api.extract_data("""() => {
                    const ipElement = document.querySelector('b:first-of-type');
                    return ipElement ? ipElement.textContent.trim() : null;
                }""")
                print(f"   Your IP: {ip_data}")
            
            print("5. Getting cookies...")
            cookies = api.get_cookies()
            print(f"   Found {len(cookies)} cookies")
            
            print("\n✅ API demonstration complete!")
            
        finally:
            print("\nStopping browser...")
            api.stop()
        
        return
    
    # Regular capture mode
    options = {
        'headless': not args.headed,
        'full_page': args.full_page,
        'extract_text': args.extract_text,
        'extract_links': args.extract_links,
        'base64_screenshot': args.base64,
        'screenshot_path': args.screenshot
    }
    
    # Ensure URL has protocol
    url = args.url
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print(f"Capturing {url}...")
    result = capture_website(url, options)
    
    # Print summary
    if result['success']:
        print("\n✅ Capture successful!")
        if 'extracted_info' in result['data']:
            print("\nExtracted Information:")
            for key, value in result['data']['extracted_info'].items():
                print(f"  {key}: {value}")
    else:
        print(f"\n❌ Capture failed: {result['error']}")
    
    # Save to file if requested
    if args.output:
        # Remove base64 screenshot from file output if it's large
        output_data = result.copy()
        if 'screenshot_base64' in output_data and not args.base64:
            del output_data['screenshot_base64']
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Print JSON output
    if args.base64:
        # Truncate base64 for display
        if 'screenshot_base64' in result:
            result['screenshot_base64'] = result['screenshot_base64'][:100] + '...'
    
    print(f"\nJSON Output:\n{json.dumps(result, indent=2)}")
    
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    # Ensure we're using the virtual environment
    venv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'venv')
    if os.path.exists(venv_path):
        activate_this = os.path.join(venv_path, 'bin', 'activate_this.py')
        if os.path.exists(activate_this):
            exec(open(activate_this).read(), {'__file__': activate_this})
    
    main()