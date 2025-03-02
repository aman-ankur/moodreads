#!/usr/bin/env python3
"""
Script to save the HTML content of a Goodreads page for analysis.
"""

from playwright.sync_api import sync_playwright
import time
import argparse

def main():
    parser = argparse.ArgumentParser(description="Save Goodreads page HTML")
    parser.add_argument("--url", default="https://www.goodreads.com/book/show/1885.Pride_and_Prejudice", 
                        help="URL of the Goodreads page")
    parser.add_argument("--output", default="goodreads_page.html", 
                        help="Output file path")
    parser.add_argument("--wait", type=int, default=10, 
                        help="Time to wait for page to load (seconds)")
    args = parser.parse_args()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print(f"Navigating to {args.url}")
        page.goto(args.url, wait_until="domcontentloaded")
        
        print(f"Waiting {args.wait} seconds for content to load...")
        time.sleep(args.wait)
        
        # Scroll down a few times to load more content
        for i in range(3):
            page.evaluate("window.scrollBy(0, 1000)")
            print(f"Scroll {i+1}/3")
            time.sleep(2)
        
        # Save the HTML content
        html = page.content()
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"Page saved to {args.output}")
        
        # Also save a screenshot
        screenshot_path = args.output.replace(".html", ".png")
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved to {screenshot_path}")
        
        # Print some debug info
        print("\nDebug information:")
        print("Looking for review elements...")
        
        # Try different selectors that might contain reviews
        selectors = [
            'div[data-testid="reviewsList"]',
            '.reviewText',
            '.bookReviewBody',
            '.reviewContainer',
            '.review',
            '#bookReviews'
        ]
        
        for selector in selectors:
            elements = page.query_selector_all(selector)
            print(f"Selector '{selector}': {len(elements)} elements found")
        
        browser.close()

if __name__ == "__main__":
    main() 