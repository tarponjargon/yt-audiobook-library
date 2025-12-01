#!/usr/bin/env python3
"""
Test script to verify SOCKS5 proxy is working with Playwright.
Loads ifconfig.me to show the external IP address.

Usage:
    python test_proxy.py
"""

import os
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync


def test_proxy():
    proxy_url = os.getenv("PROXY_URL", "socks5://host.docker.internal:1080")
    print(f"[DEBUG] Using proxy: {proxy_url}")

    with sync_playwright() as p:
        print("[DEBUG] Launching browser...")
        browser = p.chromium.launch(headless=True)

        print("[DEBUG] Creating context with proxy...")
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            proxy={"server": proxy_url} if proxy_url else None,
        )

        page = context.new_page()
        stealth_sync(page)

        print("[DEBUG] Navigating to ifconfig.me...")
        try:
            page.goto("https://ifconfig.me/", timeout=30000)
            page.wait_for_timeout(3000)

            # Get the IP address displayed
            ip_text = page.locator("body").inner_text()
            print(f"[DEBUG] Page content:\n{ip_text[:500]}")

            # Take screenshot
            os.makedirs("tmp", exist_ok=True)
            screenshot_path = "tmp/proxy_test.png"
            page.screenshot(path=screenshot_path)
            print(f"[DEBUG] Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"[ERROR] {type(e).__name__}: {e}")
            os.makedirs("tmp", exist_ok=True)
            try:
                page.screenshot(path="tmp/proxy_test_error.png")
                print("[DEBUG] Error screenshot saved to tmp/proxy_test_error.png")
            except:
                pass

        browser.close()
        print("[DEBUG] Done.")


if __name__ == "__main__":
    test_proxy()
