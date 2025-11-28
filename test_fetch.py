#!/usr/bin/env python3
"""
Test script to fetch a URL using Playwright with the same configuration as youtube_crawler.py

Usage:
    python test_fetch.py "https://www.youtube.com/results?search_query=audiobook"
    python test_fetch.py "https://sports.yahoo.com/nba"
"""

import sys
import os
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from fake_useragent import UserAgent


def fetch_url(url: str, timeout: int = 30000, headless: bool = True) -> str:
    """
    Fetch a URL using Playwright with stealth mode.

    Args:
        url: The URL to fetch
        timeout: Timeout in milliseconds (default 30s)
        headless: Run browser in headless mode (default True)

    Returns:
        The HTML content of the page
    """
    print(f"[DEBUG] Starting Playwright...")
    print(f"[DEBUG] URL: {url}")
    print(f"[DEBUG] Timeout: {timeout}ms")
    print(f"[DEBUG] Headless: {headless}")

    with sync_playwright() as p:
        print(f"[DEBUG] Launching Chromium browser...")
        browser = p.chromium.launch(headless=headless)

        # Generate user agent (same as youtube_crawler.py)
        ua_generator = UserAgent(
            browsers=["Chrome", "Firefox", "Edge"],
            os=["Windows", "Mac OS X"],
            min_version=0.0,
            platforms=["desktop"],
            fallback="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/116.0.0.0 Safari/537.36",
        )
        ua = ua_generator.random
        print(f"[DEBUG] User-Agent: {ua}")

        # Create context with viewport and user agent (same as youtube_crawler.py)
        print(f"[DEBUG] Creating browser context...")
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=ua
        )

        page = context.new_page()

        # Apply stealth mode (same as youtube_crawler.py)
        print(f"[DEBUG] Applying stealth mode...")
        stealth_sync(page)

        # Navigate to URL
        # Use "commit" - YouTube's JS never fires load/domcontentloaded properly
        print(f"[DEBUG] Navigating to URL (wait_until=commit)...")
        try:
            response = page.goto(url, timeout=timeout, wait_until="commit")
            print(f"[DEBUG] Response status: {response.status if response else 'No response'}")
            print(f"[DEBUG] Response URL: {response.url if response else 'N/A'}")
        except Exception as e:
            print(f"[ERROR] Navigation failed: {type(e).__name__}: {e}")

            # Take screenshot on error
            screenshot_path = "tmp/error_screenshot.png"
            os.makedirs("tmp", exist_ok=True)
            try:
                page.screenshot(path=screenshot_path)
                print(f"[DEBUG] Error screenshot saved to {screenshot_path}")
            except Exception as se:
                print(f"[DEBUG] Failed to take screenshot: {se}")

            browser.close()
            raise

        # Wait for page content to render (YouTube needs time for JS)
        print(f"[DEBUG] Waiting for page to render...")
        page.wait_for_timeout(5000)

        # Get page content
        html = page.content()
        print(f"[DEBUG] Page content length: {len(html)} characters")

        # Get page title
        title = page.title()
        print(f"[DEBUG] Page title: {title}")

        browser.close()
        print(f"[DEBUG] Browser closed.")

        return html


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_fetch.py <url> [timeout_ms] [--visible]")
        print("")
        print("Examples:")
        print('  python test_fetch.py "https://www.youtube.com/results?search_query=audiobook"')
        print('  python test_fetch.py "https://sports.yahoo.com/nba" 60000')
        print('  python test_fetch.py "https://www.google.com" 30000 --visible')
        sys.exit(1)

    url = sys.argv[1]
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 30000
    headless = "--visible" not in sys.argv

    try:
        html = fetch_url(url, timeout=timeout, headless=headless)

        # Print first 2000 chars of HTML
        print("\n" + "=" * 60)
        print("HTML OUTPUT (first 2000 chars):")
        print("=" * 60)
        print(html[:2000])

        if len(html) > 2000:
            print(f"\n... [{len(html) - 2000} more characters]")

        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[FATAL] {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
