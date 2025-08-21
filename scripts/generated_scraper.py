#!/usr/bin/env python3
"""
Web Scraping Automation Script
Generated: 2025-08-21T04:52:05.001393
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
        
        print(f"Scraping {url}...")
        page.goto(url, wait_until="networkidle")
        
        # Handle pagination if needed
        max_pages = 1
        current_page = 1
        
        while current_page <= max_pages:
            print(f"Processing page {current_page}...")
            
            # Extract items based on container selector
            container_selector = selectors.get('container', '.item')
            items = page.locator(container_selector).all()
            
            for item in items:
                data = {'url': url, 'page': current_page}
                
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
            next_button = selectors.get('next_button', '')
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
        filename = f'scraped_data_{timestamp}.json'
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    elif format == 'csv':
        filename = f'scraped_data_{timestamp}.csv'
        if data:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
    
    print(f"Data saved to {filename}")
    return filename

def main():
    # Configuration
    url = "https://news.ycombinator.com"
    
    # Define selectors for data extraction
    selectors = {
    "container": ".product",
    "title": "h2",
    "price": ".price",
    "description": ".description",
    "link": "a",
    "next_button": ".pagination .next"
}
    
    # Scrape data
    data = scrape_website(url, selectors)
    
    # Save results
    if data:
        save_results(data, format='json')
        print(f"Scraped {len(data)} items")
    else:
        print("No data scraped")

if __name__ == "__main__":
    main()
