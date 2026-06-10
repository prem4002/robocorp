from RPA.Email.ImapSmtp import ImapSmtp
import re
import time
from datetime import datetime, timezone

def extract_otp(text):
    m = re.search(r"\b\d{6}\b", text or "")
    return m.group(0) if m else None

def parse_email_date(msg):
    for key in ["Date", "date"]:
        if key in msg and msg[key]:
            try:
                return msg[key]
            except Exception:
                pass
    return None

def get_email_otp(after_epoch, timeout_seconds=120):
    mail = ImapSmtp(imap_server="imap.gmail.com", imap_port=993)
    mail.authorize(account="prem.amorr@gmail.com", password="Graycell9$")

    start = time.time()
    while time.time() - start < timeout_seconds:
        messages = mail.list_messages(criterion='UNSEEN SUBJECT "frame"')

        newest_otp = None
        newest_time = None

        for msg in messages:
            body = msg.get("Body", "") or msg.get("body", "")
            received = msg.get("Date") or msg.get("date")

            msg_time = None
            if hasattr(received, "timestamp"):
                msg_time = received.timestamp()

            if msg_time is not None and msg_time < after_epoch:
                continue

            otp = extract_otp(body)
            if otp:
                if newest_time is None or (msg_time is not None and msg_time > newest_time):
                    newest_otp = otp
                    newest_time = msg_time

        if newest_otp:
            mail.logout()
            return newest_otp

        time.sleep(5)

    mail.logout()
    raise Exception("No fresh OTP email found")

from RPA.Browser.Selenium import Selenium

browser = Selenium()
browser.open_available_browser("https://www.warframe.com/login")
browser.input_text("css:input[type='email']", "your_warframe_email")
browser.input_text("css:input[type='password']", "your_warframe_password")
browser.click_button("css:button[type='submit']")

otp_code = get_email_otp()

browser.input_text("css:input[name='otp']", otp_code)
browser.click_button("css:button[type='submit']")