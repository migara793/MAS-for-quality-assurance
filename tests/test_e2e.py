from playwright.sync_api import sync_playwright

def test_example_e2e():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://example.com")
        page.screenshot(path="example.png")
        browser.close()

if __name__ == "__main__":
    test_example_e2e()