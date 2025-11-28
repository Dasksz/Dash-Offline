from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the local HTML file
        file_path = os.path.abspath("EXPORTADOR DASH V7.html")
        page.goto(f"file://{file_path}")

        # Wait for the body to be ready (even if scripts fail due to missing workers or files)
        page.wait_for_selector("body")

        # Verify the presence of the new Foods button
        foods_btn = page.locator("#goals-category-foods-btn")
        if foods_btn.count() > 0:
            print("SUCCESS: Foods category button found.")
        else:
            print("FAILURE: Foods category button NOT found.")

        # Verify the presence of the sub-tabs container
        sub_tabs_container = page.locator("#goals-sub-tabs-container")
        if sub_tabs_container.count() > 0:
            print("SUCCESS: Sub-tabs container found.")
        else:
            print("FAILURE: Sub-tabs container NOT found.")

        # Verify the Foods sub-tabs exist (hidden by default)
        foods_sub_tabs = page.locator("#goals-sub-tabs-foods")
        if foods_sub_tabs.count() > 0:
            print("SUCCESS: Foods sub-tabs container found.")
            # Check for specific brand buttons
            toddynho = foods_sub_tabs.locator("button[data-brand='TODDYNHO']")
            if toddynho.count() > 0:
                print("SUCCESS: TODDYNHO button found.")
            else:
                print("FAILURE: TODDYNHO button NOT found.")
        else:
            print("FAILURE: Foods sub-tabs container NOT found.")

        browser.close()

if __name__ == "__main__":
    run()
