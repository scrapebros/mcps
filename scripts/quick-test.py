#!/usr/bin/env python3
"""
Quick test script for Claude Code to test web applications automatically.
This script can be called directly to test any URL without manual setup.
"""

import sys
import os
import argparse
from playwright.sync_api import sync_playwright
import json
from datetime import datetime


def test_website(url, options=None):
    """
    Run basic tests on a website.
    
    Args:
        url: The URL to test
        options: Dictionary of test options
    
    Returns:
        Dictionary with test results
    """
    if options is None:
        options = {}
    
    results = {
        'url': url,
        'timestamp': datetime.now().isoformat(),
        'tests': [],
        'passed': 0,
        'failed': 0,
        'errors': []
    }
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=options.get('headless', True))
        context = browser.new_context()
        page = context.new_page()
        
        # Test 1: Page loads successfully
        test_name = "Page loads successfully"
        try:
            response = page.goto(url, wait_until='networkidle')
            if response and response.ok:
                results['tests'].append({'name': test_name, 'status': 'passed'})
                results['passed'] += 1
            else:
                results['tests'].append({
                    'name': test_name, 
                    'status': 'failed',
                    'error': f"HTTP {response.status if response else 'No response'}"
                })
                results['failed'] += 1
        except Exception as e:
            results['tests'].append({
                'name': test_name,
                'status': 'failed',
                'error': str(e)
            })
            results['failed'] += 1
            results['errors'].append(str(e))
        
        # Test 2: Page has title
        test_name = "Page has title"
        try:
            title = page.title()
            if title:
                results['tests'].append({
                    'name': test_name,
                    'status': 'passed',
                    'value': title
                })
                results['passed'] += 1
            else:
                results['tests'].append({
                    'name': test_name,
                    'status': 'failed',
                    'error': 'No title found'
                })
                results['failed'] += 1
        except Exception as e:
            results['tests'].append({
                'name': test_name,
                'status': 'failed',
                'error': str(e)
            })
            results['failed'] += 1
        
        # Test 3: Check for main content
        test_name = "Main content exists"
        try:
            main_selectors = ['main', '[role="main"]', '#main', '#content', '.content', 'article']
            content_found = False
            
            for selector in main_selectors:
                if page.locator(selector).count() > 0:
                    content_found = True
                    break
            
            if content_found:
                results['tests'].append({'name': test_name, 'status': 'passed'})
                results['passed'] += 1
            else:
                results['tests'].append({
                    'name': test_name,
                    'status': 'warning',
                    'error': 'No main content container found'
                })
        except Exception as e:
            results['tests'].append({
                'name': test_name,
                'status': 'failed',
                'error': str(e)
            })
            results['failed'] += 1
        
        # Test 4: Check for navigation
        test_name = "Navigation exists"
        try:
            nav_selectors = ['nav', 'header nav', '[role="navigation"]', '.nav', '.navbar']
            nav_found = False
            
            for selector in nav_selectors:
                if page.locator(selector).count() > 0:
                    nav_found = True
                    break
            
            if nav_found:
                results['tests'].append({'name': test_name, 'status': 'passed'})
                results['passed'] += 1
            else:
                results['tests'].append({
                    'name': test_name,
                    'status': 'warning',
                    'error': 'No navigation found'
                })
        except Exception as e:
            results['tests'].append({
                'name': test_name,
                'status': 'failed',
                'error': str(e)
            })
            results['failed'] += 1
        
        # Test 5: Check page performance
        test_name = "Page performance"
        try:
            metrics = page.evaluate("""() => {
                const timing = performance.timing;
                return {
                    loadTime: timing.loadEventEnd - timing.navigationStart,
                    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart
                }
            }""")
            
            if metrics['loadTime'] < 3000:
                status = 'passed'
            elif metrics['loadTime'] < 5000:
                status = 'warning'
            else:
                status = 'failed'
            
            results['tests'].append({
                'name': test_name,
                'status': status,
                'value': f"Load time: {metrics['loadTime']}ms, DOM ready: {metrics['domContentLoaded']}ms"
            })
            
            if status == 'passed':
                results['passed'] += 1
            elif status == 'failed':
                results['failed'] += 1
                
        except Exception as e:
            results['tests'].append({
                'name': test_name,
                'status': 'failed',
                'error': str(e)
            })
            results['failed'] += 1
        
        # Test 6: Check for console errors
        test_name = "No console errors"
        console_errors = []
        
        def handle_console(msg):
            if msg.type == 'error':
                console_errors.append(msg.text)
        
        page.on('console', handle_console)
        
        # Reload page to catch console errors
        try:
            page.reload()
            page.wait_for_load_state('networkidle')
            
            if len(console_errors) == 0:
                results['tests'].append({'name': test_name, 'status': 'passed'})
                results['passed'] += 1
            else:
                results['tests'].append({
                    'name': test_name,
                    'status': 'warning',
                    'errors': console_errors[:5]  # Limit to first 5 errors
                })
        except Exception as e:
            results['tests'].append({
                'name': test_name,
                'status': 'failed',
                'error': str(e)
            })
            results['failed'] += 1
        
        # Test 7: Responsive design
        test_name = "Responsive design"
        try:
            viewports = [
                {'width': 1920, 'height': 1080, 'name': 'desktop'},
                {'width': 768, 'height': 1024, 'name': 'tablet'},
                {'width': 375, 'height': 667, 'name': 'mobile'}
            ]
            
            responsive_ok = True
            for viewport in viewports:
                page.set_viewport_size(width=viewport['width'], height=viewport['height'])
                page.wait_for_load_state('networkidle')
                
                # Check if content is still visible
                if page.locator('body').is_visible() == False:
                    responsive_ok = False
                    break
            
            if responsive_ok:
                results['tests'].append({'name': test_name, 'status': 'passed'})
                results['passed'] += 1
            else:
                results['tests'].append({
                    'name': test_name,
                    'status': 'failed',
                    'error': 'Content not visible in some viewports'
                })
                results['failed'] += 1
                
        except Exception as e:
            results['tests'].append({
                'name': test_name,
                'status': 'failed',
                'error': str(e)
            })
            results['failed'] += 1
        
        # Test 8: Accessibility - images have alt text
        test_name = "Images have alt text"
        try:
            images = page.locator('img')
            img_count = images.count()
            
            if img_count > 0:
                missing_alt = 0
                for i in range(min(img_count, 10)):  # Check first 10 images
                    if images.nth(i).get_attribute('alt') is None:
                        missing_alt += 1
                
                if missing_alt == 0:
                    results['tests'].append({'name': test_name, 'status': 'passed'})
                    results['passed'] += 1
                else:
                    results['tests'].append({
                        'name': test_name,
                        'status': 'warning',
                        'error': f'{missing_alt} images missing alt text'
                    })
            else:
                results['tests'].append({
                    'name': test_name,
                    'status': 'skipped',
                    'note': 'No images found'
                })
                
        except Exception as e:
            results['tests'].append({
                'name': test_name,
                'status': 'failed',
                'error': str(e)
            })
            results['failed'] += 1
        
        # Take screenshot if requested
        if options.get('screenshot', False):
            try:
                screenshot_path = f"reports/screenshots/quick-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                results['screenshot'] = screenshot_path
            except Exception as e:
                results['errors'].append(f"Screenshot failed: {str(e)}")
        
        # Close browser
        browser.close()
    
    return results


def print_results(results):
    """Print test results in a formatted way."""
    print("\n" + "="*60)
    print(f"Test Results for: {results['url']}")
    print(f"Timestamp: {results['timestamp']}")
    print("="*60)
    
    # Summary
    total = results['passed'] + results['failed']
    print(f"\nSummary: {results['passed']}/{total} tests passed")
    
    if results['passed'] == total:
        print("✅ All tests passed!")
    elif results['failed'] > 0:
        print(f"❌ {results['failed']} tests failed")
    
    # Detailed results
    print("\nDetailed Results:")
    print("-"*40)
    
    for test in results['tests']:
        status_symbol = {
            'passed': '✅',
            'failed': '❌',
            'warning': '⚠️',
            'skipped': '⏭️'
        }.get(test['status'], '❓')
        
        print(f"{status_symbol} {test['name']}")
        
        if 'value' in test:
            print(f"   Value: {test['value']}")
        if 'error' in test:
            print(f"   Error: {test['error']}")
        if 'errors' in test:
            print(f"   Errors: {', '.join(test['errors'][:3])}")
    
    if results.get('screenshot'):
        print(f"\n📸 Screenshot saved: {results['screenshot']}")
    
    if results['errors']:
        print("\n⚠️ General Errors:")
        for error in results['errors']:
            print(f"  - {error}")
    
    print("\n" + "="*60)


def main():
    """Main function to run tests from command line."""
    parser = argparse.ArgumentParser(description='Quick website testing tool')
    parser.add_argument('url', help='URL to test')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run in headless mode (default: True)')
    parser.add_argument('--headed', action='store_true',
                       help='Run in headed mode (show browser)')
    parser.add_argument('--screenshot', action='store_true',
                       help='Take screenshot of the page')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON')
    parser.add_argument('--output', '-o', help='Save results to file')
    
    args = parser.parse_args()
    
    # Prepare options
    options = {
        'headless': not args.headed,
        'screenshot': args.screenshot
    }
    
    # Ensure URL has protocol
    url = args.url
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    # Run tests
    print(f"Testing {url}...")
    results = test_website(url, options)
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_results(results)
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 else 1)


if __name__ == '__main__':
    # Ensure we're using the virtual environment
    venv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'venv')
    if os.path.exists(venv_path):
        activate_this = os.path.join(venv_path, 'bin', 'activate_this.py')
        if os.path.exists(activate_this):
            exec(open(activate_this).read(), {'__file__': activate_this})
    
    main()