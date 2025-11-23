
from playwright.sync_api import Page, expect, sync_playwright
import os

def verify_sidebar(page: Page):
    # 1. Load the verification page
    page.goto(f"file://{os.getcwd()}/verify_sidebar_fixed.html")

    # 2. Verify Sidebar is visible on desktop (lg breakpoint)
    # Set viewport to desktop
    page.set_viewport_size({"width": 1280, "height": 720})

    # Sidebar should be translated 0 (visible)
    # Wait for transition
    page.wait_for_timeout(500)

    # Check if sidebar is visible
    # The class `lg:translate-x-0` should apply.
    # We can check bounding box or visibility.
    sidebar = page.locator('#side-menu')
    expect(sidebar).to_be_visible()

    # Screenshot Desktop
    page.screenshot(path="/home/jules/verification/sidebar_desktop.png")

    # 3. Verify Mobile Behavior
    page.set_viewport_size({"width": 375, "height": 667})
    page.wait_for_timeout(500)

    # Click the toggle button
    toggle_btn = page.locator('button.sidebar-toggle').first
    toggle_btn.click()
    page.wait_for_timeout(500) # wait for transition

    # Screenshot Mobile Open
    page.screenshot(path="/home/jules/verification/sidebar_mobile_open.png")

    # Click overlay to close - Click on the right side of the screen to avoid sidebar
    # Overlay is full screen, sidebar is 256px. 375 - 256 = 119px space remaining.
    # Click at x=300, y=300
    page.mouse.click(300, 300)
    page.wait_for_timeout(500)

    # Screenshot Mobile Closed
    page.screenshot(path="/home/jules/verification/sidebar_mobile_closed.png")

if __name__ == "__main__":
    os.makedirs("/home/jules/verification", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_sidebar(page)
            print("Verification script finished successfully.")
        except Exception as e:
            print(f"Verification failed: {e}")
        finally:
            browser.close()
