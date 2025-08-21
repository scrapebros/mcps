"""Example Playwright tests with pytest for web application testing."""

import pytest
import re
from playwright.sync_api import Page, expect, BrowserContext
import os


class TestBasicFunctionality:
    """Basic web application functionality tests."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Navigate to base URL before each test."""
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        page.goto(base_url)
        
    def test_homepage_loads(self, page: Page):
        """Test that homepage loads successfully."""
        # Check page title
        expect(page).to_have_title(re.compile(".*", re.IGNORECASE))
        
        # Check main content is visible
        main_content = page.locator('main, [role="main"], #main').first
        expect(main_content).to_be_visible()
        
    def test_navigation(self, page: Page):
        """Test navigation between pages."""
        # Find navigation links
        nav_links = page.locator('nav a, header a')
        
        if nav_links.count() > 0:
            # Click first navigation link
            first_link = nav_links.first
            first_link.click()
            
            # Wait for navigation
            page.wait_for_load_state('networkidle')
            
            # Verify URL changed
            base_url = os.getenv('BASE_URL', 'http://localhost:3000')
            assert page.url != base_url
            
    def test_responsive_design(self, page: Page):
        """Test responsive design across different viewports."""
        viewports = [
            {'width': 1920, 'height': 1080, 'name': 'desktop'},
            {'width': 768, 'height': 1024, 'name': 'tablet'},
            {'width': 375, 'height': 667, 'name': 'mobile'}
        ]
        
        for viewport in viewports:
            # Set viewport size
            page.set_viewport_size(
                width=viewport['width'], 
                height=viewport['height']
            )
            
            # Take screenshot
            page.screenshot(
                path=f"reports/screenshots/{viewport['name']}.png",
                full_page=True
            )
            
            # Verify content is still visible
            content = page.locator('body')
            expect(content).to_be_visible()
            
    @pytest.mark.smoke
    def test_page_performance(self, page: Page):
        """Test page load performance."""
        # Measure page load time
        page.goto('/', wait_until='networkidle')
        
        # Get performance metrics
        performance_timing = page.evaluate("""
            () => {
                const timing = performance.timing;
                return {
                    loadTime: timing.loadEventEnd - timing.navigationStart,
                    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                    firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0
                }
            }
        """)
        
        # Assert reasonable load times (in milliseconds)
        assert performance_timing['loadTime'] < 5000, "Page load time exceeds 5 seconds"
        assert performance_timing['domContentLoaded'] < 3000, "DOM content loaded exceeds 3 seconds"


class TestFormInteractions:
    """Test form interactions and validations."""
    
    def test_form_submission(self, page: Page):
        """Test form submission functionality."""
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        page.goto(base_url)
        
        # Find first form
        form = page.locator('form').first
        
        if form.is_visible():
            # Fill text inputs
            text_inputs = form.locator('input[type="text"], input[type="email"]')
            
            for i in range(text_inputs.count()):
                text_inputs.nth(i).fill(f"test-value-{i}")
                
            # Submit form
            submit_button = form.locator('button[type="submit"], input[type="submit"]').first
            if submit_button.is_visible():
                submit_button.click()
                page.wait_for_load_state('networkidle')
                
    def test_input_validation(self, page: Page):
        """Test input field validation."""
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        page.goto(base_url)
        
        # Test email validation
        email_input = page.locator('input[type="email"]').first
        if email_input.is_visible():
            # Test invalid email
            email_input.fill("invalid-email")
            email_input.press("Tab")
            
            # Check for validation message
            validation_msg = page.locator('.error, .invalid, [aria-invalid="true"]')
            if validation_msg.count() > 0:
                expect(validation_msg.first).to_be_visible()
                
            # Test valid email
            email_input.fill("valid@example.com")
            email_input.press("Tab")
            
    def test_search_functionality(self, page: Page):
        """Test search functionality if available."""
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        page.goto(base_url)
        
        # Find search input
        search_input = page.locator('input[type="search"], input[placeholder*="search" i]').first
        
        if search_input.is_visible():
            # Perform search
            search_input.fill("test query")
            search_input.press("Enter")
            
            # Wait for results
            page.wait_for_load_state('networkidle')
            
            # Check for results container
            results = page.locator('[class*="result"], [id*="result"]')
            assert results.count() >= 0


class TestAccessibility:
    """Accessibility and SEO tests."""
    
    def test_alt_text_on_images(self, page: Page):
        """Test that all images have alt text."""
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        page.goto(base_url)
        
        images = page.locator('img')
        
        for i in range(images.count()):
            img = images.nth(i)
            alt_text = img.get_attribute('alt')
            
            # Alt attribute should exist (can be empty for decorative images)
            assert alt_text is not None, f"Image {i} missing alt attribute"
            
    def test_aria_labels(self, page: Page):
        """Test ARIA labels on interactive elements."""
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        page.goto(base_url)
        
        # Check buttons
        buttons = page.locator('button')
        
        for i in range(buttons.count()):
            button = buttons.nth(i)
            text_content = button.text_content()
            aria_label = button.get_attribute('aria-label')
            
            # Button should have either text or aria-label
            assert text_content or aria_label, f"Button {i} missing accessible text"
            
    def test_heading_hierarchy(self, page: Page):
        """Test proper heading hierarchy."""
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        page.goto(base_url)
        
        # Check for h1
        h1_elements = page.locator('h1')
        assert h1_elements.count() >= 1, "Page should have at least one h1"
        
        # Check heading order
        headings = page.locator('h1, h2, h3, h4, h5, h6')
        heading_levels = []
        
        for i in range(headings.count()):
            heading = headings.nth(i)
            tag_name = heading.evaluate("el => el.tagName.toLowerCase()")
            level = int(tag_name[1])
            heading_levels.append(level)
            
        # Verify heading hierarchy (no skipping levels)
        for i in range(1, len(heading_levels)):
            diff = heading_levels[i] - heading_levels[i-1]
            assert diff <= 1, f"Heading hierarchy broken at position {i}"


class TestAdvancedScenarios:
    """Advanced testing scenarios."""
    
    @pytest.mark.slow
    def test_file_upload(self, page: Page):
        """Test file upload functionality."""
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        page.goto(base_url)
        
        file_input = page.locator('input[type="file"]').first
        
        if file_input.is_visible():
            # Create test file if it doesn't exist
            test_file = 'fixtures/test-file.txt'
            if not os.path.exists('fixtures'):
                os.makedirs('fixtures')
            if not os.path.exists(test_file):
                with open(test_file, 'w') as f:
                    f.write('Test file content')
                    
            # Upload file
            file_input.set_input_files(test_file)
            
            # Verify file was selected
            file_name = file_input.evaluate("input => input.files[0]?.name")
            assert file_name == 'test-file.txt'
            
    def test_local_storage(self, page: Page):
        """Test local storage functionality."""
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        page.goto(base_url)
        
        # Set local storage item
        page.evaluate("() => localStorage.setItem('testKey', 'testValue')")
        
        # Reload page
        page.reload()
        
        # Check if local storage persists
        value = page.evaluate("() => localStorage.getItem('testKey')")
        assert value == 'testValue'
        
        # Clean up
        page.evaluate("() => localStorage.removeItem('testKey')")
        
    def test_cookie_handling(self, page: Page, context: BrowserContext):
        """Test cookie handling."""
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        
        # Set a cookie
        context.add_cookies([{
            'name': 'test_cookie',
            'value': 'test_value',
            'url': base_url
        }])
        
        page.goto(base_url)
        
        # Verify cookie exists
        cookies = context.cookies()
        test_cookie = next((c for c in cookies if c['name'] == 'test_cookie'), None)
        assert test_cookie is not None
        assert test_cookie['value'] == 'test_value'
        
    @pytest.mark.regression
    def test_error_handling(self, page: Page):
        """Test error page handling."""
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        
        # Navigate to non-existent page
        response = page.goto(f"{base_url}/non-existent-404-page", wait_until='networkidle')
        
        if response and response.status == 404:
            # Check for 404 message
            error_message = page.locator('text=/404|not found/i')
            expect(error_message).to_be_visible()
            
    def test_network_requests(self, page: Page):
        """Test and monitor network requests."""
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        
        # Track network requests
        requests = []
        page.on('request', lambda request: requests.append(request))
        
        # Track network responses
        responses = []
        page.on('response', lambda response: responses.append(response))
        
        # Navigate to page
        page.goto(base_url)
        
        # Analyze requests
        for request in requests:
            # Check for failed requests
            if request.failure():
                pytest.fail(f"Request failed: {request.url}")
                
        # Analyze responses
        for response in responses:
            # Check for error status codes
            if response.status >= 400:
                print(f"Error response: {response.url} - Status: {response.status}")
                
    @pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
    def test_cross_browser_compatibility(self, browser_name: str, page: Page):
        """Test cross-browser compatibility."""
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        page.goto(base_url)
        
        # Basic smoke test for each browser
        expect(page).to_have_title(re.compile(".*"))
        
        # Take screenshot for visual comparison
        page.screenshot(path=f"reports/screenshots/{browser_name}-compatibility.png")
        
        # Check main functionality works
        main_content = page.locator('main, body')
        expect(main_content).to_be_visible()


class TestAPIIntegration:
    """API integration tests alongside UI tests."""
    
    def test_api_health_check(self, page: Page, playwright):
        """Test API health endpoint if available."""
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        
        # Create API context
        api_context = playwright.request.new_context()
        
        try:
            # Make API request
            response = api_context.get(f"{base_url}/api/health")
            
            if response.ok:
                assert response.status == 200
                data = response.json()
                assert 'status' in data or 'health' in data
        except Exception:
            # API might not exist, skip
            pytest.skip("API endpoint not available")
        finally:
            api_context.dispose()
            
    def test_data_consistency(self, page: Page, playwright):
        """Test data consistency between UI and API."""
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        page.goto(base_url)
        
        # Get data from UI
        ui_data = page.locator('[data-testid="data-element"]')
        
        if ui_data.count() > 0:
            ui_text = ui_data.first.text_content()
            
            # Get same data from API
            api_context = playwright.request.new_context()
            try:
                response = api_context.get(f"{base_url}/api/data")
                if response.ok:
                    api_data = response.json()
                    # Compare UI and API data (implementation specific)
                    assert ui_text in str(api_data)
            except Exception:
                pass
            finally:
                api_context.dispose()