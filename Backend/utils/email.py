import os
import yagmail

def send_otp_email(recipient_email, otp_code):
    # Read credentials from env vars!
    sender_email = os.environ.get("GMAIL_USER")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")

    # Strong error if credentials are missing
    if not sender_email or not app_password:
        raise EnvironmentError("Missing GMAIL credentials in environment variables.")

    yag = yagmail.SMTP(sender_email, app_password)
    subject = "Your LawGPT OTP Verification Code"
    content = f"Your OTP is: {otp_code}\nThis code is valid for 10 minutes.\nLawGPT - Indian Legal AI Platform"
    yag.send(recipient_email, subject, content)
