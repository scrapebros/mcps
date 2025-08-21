#!/usr/bin/env python3
"""
Basic Automation Script
Generated: 2025-08-21T04:52:29.849799
"""

from playwright.sync_api import sync_playwright
import time

def run_automation():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to URL
        page.goto("https://example.com")
        page.wait_for_load_state("networkidle")
        
        # Close browser
        browser.close()
        print("Automation completed successfully!")

if __name__ == "__main__":
    run_automation()
