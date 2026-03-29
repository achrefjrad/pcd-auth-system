import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "APP_PASSWORD"


def send_otp_email(to_email, otp):
    msg = EmailMessage()
    msg.set_content(
        f"Your OTP code is: {otp}\n\nValid for 5 minutes."
    )
    msg["Subject"] = "Your Login OTP"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
