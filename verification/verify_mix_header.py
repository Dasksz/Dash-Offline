
from playwright.sync_api import sync_playwright
import os

def verify_mix_view_header():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the HTML file directly
        file_path = os.path.abspath("EXPORTADOR DASH V7.html")
        page.goto(f"file://{file_path}")

        # Since we don't have data to load, we will manually unhide the mix-view
        # and hide the main-dashboard to inspect the static HTML structure we modified.
        page.evaluate("""
            document.getElementById('main-dashboard').classList.add('hidden');
            document.getElementById('mix-view').classList.remove('hidden');
        """)

        # Wait for the view to be visible (though it's immediate with class manipulation)
        page.wait_for_selector("#mix-view")

        # We need to focus on the table header to see the borders
        # The table body will be empty, but the header is static in the HTML.
        header_selector = "#mix-view table thead"
        page.wait_for_selector(header_selector)

        # Take a screenshot of the header area
        # We might need to set a viewport size to capture enough width
        page.set_viewport_size({"width": 1920, "height": 1080})

        # Locate the specific header rows
        header = page.locator(header_selector)

        # Screenshot the header
        screenshot_path = "verification/mix_view_header.png"
        header.screenshot(path=screenshot_path)

        print(f"Screenshot saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    verify_mix_view_header()
