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
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print(f"Navigating to login page for '{USERNAME}'...")
        page.goto("https://www.pythonanywhere.com/login/")
        page.wait_for_load_state("networkidle")

        print("Entering credentials...")
        username_input = page.locator("#id_auth-username, input[name='auth-username']").filter(has_not_class="tt-hint").first
        password_input = page.locator("#id_auth-password, input[name='auth-password']").first

        username_input.wait_for(state="visible", timeout=10000)
        username_input.fill(USERNAME)
        password_input.fill(PASSWORD)
        password_input.press("Enter")
        page.wait_for_load_state("networkidle")

        print("Navigating to Web Apps page...")
        page.goto(WEBAPPS_URL)
        page.wait_for_load_state("networkidle")

        if "login" in page.url:
            print(f"Error: Login failed for user '{USERNAME}'. Check secrets.")
            browser.close()
            sys.exit(1)

        print("Login verified. Looking for Extend button...")

        extend_button = page.locator(
            "form[action*='/extend'] input[type='submit'], form[action*='/extend'] button, input[value*='Run until']"
        ).first

        if extend_button.count() > 0:
            print("Clicking 'Run until 1 month from today' button...")
            extend_button.scroll_into_view_if_needed()
            extend_button.click(force=True)
            page.wait_for_load_state("networkidle")
            print(f"Success: Web app expiry extended successfully for '{USERNAME}'!")
        else:
            print(f"Extend button not found or app is already extended for '{USERNAME}'.")

        browser.close()

if __name__ == "__main__":
    run()