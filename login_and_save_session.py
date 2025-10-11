from playwright.sync_api import sync_playwright

URL = "https://ecc-uoft-coop-csm.symplicity.com/students/app/jobs/search?perPage=20&page=1&sort=!postdate"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # visible so you can log in
    context = browser.new_context()
    page = context.new_page()
    page.goto(URL)

    print("Logging in manually with UofT credentials.")
    print("After the page loads the job listings, close this window.")
    page.wait_for_timeout(60000 * 3)  # wait up to 3 minutes
    context.storage_state(path="auth.json")
    print("Session saved to auth.json.")
    browser.close()
