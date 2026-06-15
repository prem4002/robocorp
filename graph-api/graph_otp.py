import msal
import requests
import re
import time
from playwright.sync_api import sync_playwright

# azure credentials
TENANT_ID = "tenant-id"
CLIENT_ID = "client-id"
CLIENT_SECRET = "client-secret"
EMAIL = "lolol@email.com"
GRAPHURL = "https://graph.microsoft.com/v1.0"
SCOPE = ["https://graph.microsoft.com/.default"]


def get_access_token():
    # create the app session and request a token from azure
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=SCOPE)
    if "access_token" in result:
        return result["access_token"]
    raise Exception(result.get("error_description"))


def get_emails(access_token, number_of_mails=2):
    # auth header so graph api knows who we are
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    # fetch last n emails, newest first
    url = (
        f"{GRAPHURL}/users/{EMAIL}/messages"
        f"?$top={number_of_mails}"
        f"&$orderby=receivedDateTime desc"
        f"&$select=subject,receivedDateTime,body,from"
    )
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("value", [])
    print(f"failed to fetch emails: {response.status_code}")
    return []


def get_otp(email_body):
    #scan the email body string for a 4-6 digit number
    matches = re.findall(r'\b\d{4,6}\b', email_body)
    return matches[0] if matches else None


def wait_for_otp(subject_keyword="OTP", timeout=120, poll_interval=10):
    token = get_access_token()
    elapsed = 0

    while elapsed < timeout:
        emails = get_emails(token)
        for email in emails:
            subject = email.get("subject", "")
            body = email.get("body", {}).get("content", "")
            #check subject line first, thengo into body for the number
            if subject_keyword.lower() in subject.lower():
                otp = get_otp(body)
                if otp:
                    return otp
        print(f"no otp yet, waiting {poll_interval}s...")
        time.sleep(poll_interval)
        elpased += poll_interval

    print("timed out waiting for OTP")
    return None


def rpa_login_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://dummmysite.com/login")
        page.wait_for_load_state("networkidle")

        page.fill("#username", "username")
        page.fill("#password", "password")
        page.click("#loginBtn")

        # wait for the otp screen to load before fetching
        page.wait_for_selector("#otpInput")
        otp = wait_for_otp(subject_keyword="OTP", timeout_seconds=120)

        if otp:
            page.fill("#otpInput", otp)
            page.click("#verifyBtn")
            print("logged In")
        else:
            print("OTP not received")

        browser.close()
