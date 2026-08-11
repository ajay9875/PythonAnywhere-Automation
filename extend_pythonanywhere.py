import os
import sys
import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("PA_USERNAME")
PASSWORD = os.environ.get("PA_PASSWORD")

if not USERNAME or not PASSWORD:
    print("Error: Missing PythonAnywhere credentials in environment variables.")
    sys.exit(1)

LOGIN_URL = "https://www.pythonanywhere.com/login/"
WEBAPPS_URL = f"https://www.pythonanywhere.com/user/{USERNAME}/webapps/"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

print("Fetching login page for CSRF token...")
login_page = session.get(LOGIN_URL)
soup = BeautifulSoup(login_page.text, "html.parser")

csrf_input = soup.find("input", {"name": "csrfmiddlewaretoken"})
if not csrf_input:
    print("Error: Could not find CSRF token on login page.")
    sys.exit(1)

csrf_token = csrf_input["value"]

print("Logging into PythonAnywhere...")
login_payload = {
    "csrfmiddlewaretoken": csrf_token,
    "auth-username": USERNAME,
    "auth-password": PASSWORD,
    "login_view-current_step": "auth",
}

# Explicitly pass CSRF token in headers and cookies
headers = {
    "Referer": LOGIN_URL,
    "X-CSRFToken": csrf_token,
}

login_response = session.post(LOGIN_URL, data=login_payload, headers=headers)

# Check if login was successful by examining session cookies or redirect
if "sessionid" not in session.cookies:
    print("Error: Login failed. Check your credentials in GitHub Secrets.")
    sys.exit(1)

print("Login successful. Checking webapps page...")
webapps_page = session.get(WEBAPPS_URL)
soup = BeautifulSoup(webapps_page.text, "html.parser")

# Find the extend button form
extend_form = soup.find("form", action=lambda x: x and "/extend" in x)

if not extend_form:
    print("Extend button not found or app is already extended.")
    sys.exit(0)

extend_action = extend_form["action"]
extend_url = f"https://www.pythonanywhere.com{extend_action}"

extend_csrf_input = extend_form.find("input", {"name": "csrfmiddlewaretoken"})
extend_csrf = extend_csrf_input["value"] if extend_csrf_input else session.cookies.get("csrftoken")

print("Triggering extension...")
extend_headers = {
    "Referer": WEBAPPS_URL,
    "X-CSRFToken": extend_csrf,
}

extend_response = session.post(
    extend_url,
    data={"csrfmiddlewaretoken": extend_csrf},
    headers=extend_headers
)

if extend_response.status_code == 200:
    print("Success: Web app expiry extended successfully!")
else:
    print(f"Failed to extend app. Status code: {extend_response.status_code}")
    sys.exit(1)