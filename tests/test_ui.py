from playwright.sync_api import sync_playwright


def run_ui_test():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("file:///app/tests/ui_test_demo.html")

        # Locate the input field and type the text
        page.fill("input[type='text']", "QA_SYSTEM_VERIFIED")

        # Locate the button and click it
        page.click("button")

        # Locate the success message and assert its content
        success_message = page.locator("#success-message")
        assert "QA_SYSTEM_VERIFIED" in success_message.inner_text()

        # Take a screenshot
        page.screenshot(path="screenshot.png")

        browser.close()

if __name__ == "__main__":
    run_ui_test()
