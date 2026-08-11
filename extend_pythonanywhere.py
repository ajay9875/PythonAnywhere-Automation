import os
import sys
from playwright.sync_api import sync_playwright

USERNAME = os.environ.get("PA_USERNAME")
PASSWORD = os.environ.get("PA_PASSWORD")

if not USERNAME or not PASSWORD:
    print("Error: Missing PythonAnywhere credentials in environment variables.")
    sys.exit(1)

WEBAPPS_URL = f"https://www.pythonanywhere.com/user/{USERNAME}/webapps/"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("Navigating to login page...")
        page.goto("https://www.pythonanywhere.com/login/")

        print("Entering credentials...")
        page.fill("input[name='id_auth-username']", USERNAME)
        page.fill("input[name='id_auth-password']", PASSWORD)
        
        print("Submitting login form...")
        page.click("button[type='submit']")

        # Wait for navigation after login
        page.wait_for_load_state("networkidle")

        print("Navigating to Web Apps page...")
        page.goto(WEBAPPS_URL)
        page.wait_for_load_state("networkidle")

        # Check if login succeeded
        if "login" in page.url:
            print("Error: Login failed. Please verify PA_USERNAME and PA_PASSWORD in GitHub Secrets.")
            browser.close()
            sys.exit(1)

        print("Login verified. Looking for Extend button...")

        # Search for the extend button
        extend_button = page.locator("form[action*='/extend'] input[type='submit'], form[action*='/extend'] button")

        if extend_button.count() > 0 and extend_button.is_visible():
            print("Clicking 'Run until 1 month from today' button...")
            extend_button.click()
            page.wait_for_load_state("networkidle")
            print("Success: Web app expiry extended successfully!")
        else:
            print("Extend button not found or app is already extended.")

        browser.close()

if __name__ == "__main__":
    run()