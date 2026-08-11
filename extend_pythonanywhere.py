import os
import sys
from playwright.sync_api import sync_playwright

# Parse comma-separated credentials from GitHub Secrets
USERNAMES = [u.strip() for u in os.environ.get("PA_USERNAME", "").split(",") if u.strip()]
PASSWORDS = [p.strip() for p in os.environ.get("PA_PASSWORD", "").split(",") if p.strip()]

if not USERNAMES or not PASSWORDS:
    print("Error: PA_USERNAME or PA_PASSWORD environment variables are missing.")
    sys.exit(1)

if len(USERNAMES) != len(PASSWORDS):
    print("Error: The number of usernames and passwords must match.")
    sys.exit(1)


def extend_single_account(page, username, password):
    webapps_url = f"https://www.pythonanywhere.com/user/{username}/webapps/"
    print(f"\n==========================================")
    print(f"Processing PythonAnywhere Account: {username}")
    print(f"==========================================")

    # Step 1: Navigate to Login
    print("Navigating to login page...")
    page.goto("https://www.pythonanywhere.com/login/")
    page.wait_for_load_state("networkidle")

    # Step 2: Fill & Submit Credentials
    print("Entering credentials...")
    username_input = page.locator("#id_auth-username, input[name='auth-username'], input[type='text']").first
    password_input = page.locator("#id_auth-password, input[name='auth-password'], input[type='password']").first

    username_input.fill(username)
    password_input.fill(password)
    password_input.press("Enter")
    page.wait_for_load_state("networkidle")

    # Step 3: Navigate to Web Apps Dashboard
    print("Navigating to Web Apps page...")
    page.goto(webapps_url)
    page.wait_for_load_state("networkidle")

    if "login" in page.url:
        print(f"Error: Login failed for user '{username}'. Skipping...")
        return False

    print("Login verified. Searching for extend button...")

    # Step 4: Click Extend Button
    extend_button = page.locator(
        "form[action*='/extend'] input[type='submit'], form[action*='/extend'] button, input[value*='Run until']"
    ).first

    if extend_button.count() > 0:
        print("Clicking 'Run until 1 month from today' button...")
        extend_button.scroll_into_view_if_needed()
        extend_button.click(force=True)
        page.wait_for_load_state("networkidle")
        print(f"Success: Web app expiry extended successfully for '{username}'!")
    else:
        print(f"Extend button not found or app is already extended for '{username}'.")

    # Step 5: Log out to clear session for next account
    print("Logging out...")
    page.goto("https://www.pythonanywhere.com/logout/")
    page.wait_for_load_state("networkidle")
    return True


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Loop through each account sequentially
        for user, pwd in zip(USERNAMES, PASSWORDS):
            extend_single_account(page, user, pwd)

        browser.close()

if __name__ == "__main__":
    run()