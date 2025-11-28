from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the local HTML file
        file_path = os.path.abspath("EXPORTADOR DASH V7.html")
        page.goto(f"file://{file_path}")

        # Wait for the body to be ready
        page.wait_for_selector("body")

        # 1. Verify "RESUMO" button exists
        resumo_btn = page.locator("#goals-category-summary-btn")
        if resumo_btn.count() > 0:
            print("SUCCESS: RESUMO button found.")
        else:
            print("FAILURE: RESUMO button NOT found.")
            return

        # 2. Click "RESUMO" button
        # We need to simulate the click. However, since the page logic requires data to be loaded to fully function,
        # we might need to mock data or just check if the click handler toggles classes.
        # But the click handler is set up in DOMContentLoaded.

        # Let's try to verify the Summary Container exists in the DOM (hidden by default)
        summary_content = page.locator("#goals-summary-content")
        if summary_content.count() > 0:
            print("SUCCESS: Summary content container found.")
        else:
            print("FAILURE: Summary content container NOT found.")
            return

        # 3. Verify the Summary Logic function exists (via checking if cards are generated when calling it manually)
        # We can execute JS in the page context.
        try:
            # Manually trigger the view update to Summary to check rendering
            page.evaluate("document.getElementById('goals-category-summary-btn').click()")

            # Check if summary grid is visible
            is_visible = summary_content.is_visible()
            if is_visible:
                print("SUCCESS: Summary content became visible after click.")
            else:
                print("FAILURE: Summary content is NOT visible after click.")

            # Check if cards are rendered inside
            cards = page.locator("#goals-summary-grid > div")
            count = cards.count()
            if count >= 6:
                print(f"SUCCESS: Found {count} summary cards.")
            else:
                print(f"FAILURE: Expected at least 6 summary cards, found {count}.")

        except Exception as e:
            print(f"FAILURE: JS Execution error: {e}")

        browser.close()

if __name__ == "__main__":
    run()
