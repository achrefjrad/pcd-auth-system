import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime, timedelta

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Email configuration from environment variables
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# OTP validity in minutes (from auth/otp.py)
OTP_VALIDITY_MINUTES = 5


def send_otp_email(user_email, otp, qr_image_path=None):
    """
    Send OTP email to the user with QR code attachment and OTP text.
    
    Args:
        user_email: User's email address
        otp: The OTP code to send
        qr_image_path: Path to QR code image file (optional)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = user_email
        msg['Subject'] = "Your SecureAuth OTP Code"
        
        # Calculate expiration time
        expiration_time = (datetime.now() + timedelta(minutes=OTP_VALIDITY_MINUTES)).strftime("%H:%M")
        
        # Email body
        body = f"""Hello,

Your SecureAuth verification code is: {otp}

This code will expire at {expiration_time}.

If you didn't request this, please ignore this email.

Best regards,
SecureAuth Team
"""
        
        # Attach body
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach QR code if provided
        if qr_image_path and os.path.exists(qr_image_path):
            try:
                with open(qr_image_path, 'rb') as f:
                    img_data = f.read()
                image = MIMEImage(img_data, name='qr_code.png')
                image.add_header('Content-Disposition', 'attachment', filename='qr_code.png')
                msg.attach(image)
            except Exception as e:
                print(f"Warning: Could not attach QR code: {e}")
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"[EMAIL SENT] OTP sent to {user_email}")
        return True
        
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email: {e}")
        return False


def send_otp_email_with_qr(user_email, otp, qr_base64=None):
    """
    Send OTP email with QR code from base64 data.
    
    Args:
        user_email: User's email address
        otp: The OTP code to send
        qr_base64: Base64 encoded QR code image (optional)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    import base64
    
    qr_path = None
    
    # Save QR code temporarily if provided
    if qr_base64:
        try:
            qr_data = base64.b64decode(qr_base64)
            # Save to temp directory
            temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            qr_path = os.path.join(temp_dir, f'qr_{user_email}.png')
            with open(qr_path, 'wb') as f:
                f.write(qr_data)
        except Exception as e:
            print(f"Warning: Could not save QR code: {e}")
    
    result = send_otp_email(user_email, otp, qr_path)
    
    # Clean up temp file
    if qr_path and os.path.exists(qr_path):
        try:
            os.remove(qr_path)
        except Exception:
            pass
    
    return result