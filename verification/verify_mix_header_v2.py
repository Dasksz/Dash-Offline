
from playwright.sync_api import sync_playwright
import os
import re

def extract_template_and_verify():
    # 1. Read the generator file
    with open("EXPORTADOR DASH V7.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 2. Extract the reportTemplate string
    # We look for: const reportTemplate = ` ... `;
    # It seems to start around line 1860 based on previous context, but let's find it dynamically.
    start_marker = "const reportTemplate = `"
    end_marker = "`;\n                // FIM DO TEMPLATE MODIFICADO"

    start_index = content.find(start_marker)
    if start_index == -1:
        print("Could not find start of reportTemplate")
        return

    start_content = start_index + len(start_marker)

    # Find the end. It's a big string.
    # We can look for the specific comment I noticed in the code reading: "// FIM DO TEMPLATE MODIFICADO"
    end_index = content.find(end_marker, start_content)

    if end_index == -1:
        # Fallback: find the last backtick before the end of the file or function
        # But the comment is reliable if I saw it.
        print("Could not find end of reportTemplate")
        # Let's try to find the last backtick before "const blob ="
        backup_end_marker = "const blob ="
        end_limit = content.find(backup_end_marker, start_content)
        if end_limit != -1:
            end_index = content.rfind("`;", start_content, end_limit)

        if end_index == -1:
             print("Failed to extract template.")
             return

    template_html = content[start_content:end_index]

    # 3. Save to temporary file
    temp_file_path = os.path.abspath("verification/temp_report.html")
    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write(template_html)

    print(f"Extracted template to {temp_file_path}")

    # 4. Verify with Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(f"file://{temp_file_path}")

        # The page will likely have JS errors because ${jsonDataString} is invalid JS.
        # But the HTML structure should parse.

        # We need to show the mix-view.
        # Since the JS won't run to hide/show things (it crashes on syntax error),
        # the CSS might hide it by default: class="hidden".
        # We need to remove "hidden" from #mix-view and #content-wrapper/main-dashboard issues?
        # The HTML structure:
        # <body> ... <div id="mix-view" class="hidden ..."> ...

        try:
            page.evaluate("""
                const mixView = document.getElementById('mix-view');
                if (mixView) {
                    mixView.classList.remove('hidden');
                    mixView.style.display = 'block'; // Force display just in case
                }
                // Hide others to clean up
                const main = document.getElementById('main-dashboard');
                if (main) main.style.display = 'none';
            """)
        except Exception as e:
            print(f"JS Eval failed (expected due to broken template variables): {e}")
            # Fallback: The browser might have stopped JS execution.
            # But we can try to inject CSS to force visibility?
            # Or reliance on the fact that `evaluate` might work if the error was in a script tag but the DOM is live.
            # Playwright evaluate runs in the page context. If the page's own scripts crashed, evaluate might still run.

        # Wait for selector. If JS crashed hard, maybe DOM is there.
        try:
            page.wait_for_selector("#mix-view", state="attached", timeout=2000)

            # Force visibility via style attribute if class removal didn't take or CSS is blocking
            page.eval_on_selector("#mix-view", "el => { el.classList.remove('hidden'); el.style.display = 'block'; }")

            header_selector = "#mix-view table thead"
            page.wait_for_selector(header_selector, timeout=2000)

            page.set_viewport_size({"width": 1920, "height": 1080})

            # Locate and screenshot
            header = page.locator(header_selector)
            screenshot_path = "verification/mix_view_header_fixed.png"
            header.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"Verification failed during DOM manipulation: {e}")
            # Take a full page screenshot to see what's going on
            page.screenshot(path="verification/debug_full_page.png")

        browser.close()

if __name__ == "__main__":
    extract_template_and_verify()
