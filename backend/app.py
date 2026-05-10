from flask import Flask, request, jsonify, render_template, session, redirect
from flask_cors import CORS
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import os
from urllib.parse import quote

from database import create_tables, get_user_by_username, get_user_by_email, update_user_password
from auth.email_service import send_otp_email_with_qr
from auth.auth import register_user, login_user
from auth.otp import generate_otp, verify_otp, OTP_VALIDITY
import bcrypt

import qrcode
import base64
import time
from io import BytesIO

# Get configuration from environment variables
SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'frontend/templates'),
            static_folder=os.path.join(BASE_DIR, 'frontend/static'))
app.secret_key = SECRET_KEY

CORS(app)

# Temporary in-memory store for the most recent QR per user.
pending_qr_codes = {}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/otp")
def otp_page():
    return render_template("otp.html")


# ---------------- REGISTER ----------------
import re

def validate_email(email):
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$'
    return re.match(pattern, phone) is not None

def validate_image(filename):
    allowed = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in allowed

@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    image = request.files.get("image")

    if not username or not email or not phone or not password or not image:
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400

    if len(username) < 3:
        return jsonify({
            "success": False,
            "message": "Username must be at least 3 characters"
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "Password must be at least 6 characters"
        }), 400

    if not validate_email(email):
        return jsonify({
            "success": False,
            "message": "Invalid email format"
        }), 400

    if not validate_phone(phone):
        return jsonify({
            "success": False,
            "message": "Invalid phone number format"
        }), 400

    if not validate_image(image.filename):
        return jsonify({
            "success": False,
            "message": "Invalid image format. Allowed: jpg, jpeg, png, gif, webp"
        }), 400

    result = register_user(username, email, phone, password, image.read())

    if result:
        return jsonify({
            "success": True,
            "message": "User registered successfully"
        }), 201

    return jsonify({
        "success": False,
        "message": "Username already exists"
    }), 409


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    image = request.files.get("image")

    if not username or not password or not image:
        return jsonify({
            "success": False,
            "message": "Username, password, and image are required"
        }), 400

    image_bytes = image.read()

    success, msg = login_user(username, password, image_bytes)

    if not success:
        return jsonify({
            "success": False,
            "message": msg
        }), 401

    # Generate OTP (your image-based OTP)
    otp = generate_otp(username, image_bytes)

    # Create QR content
    qr_data = f"USER:{username}|OTP:{otp}"

    # Generate QR image
    qr = qrcode.make(qr_data)

    # Convert to base64
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    # Store QR for fallback (but don't send to frontend)
    pending_qr_codes[username] = {
        "qr_code": qr_base64,
        "expires_at": int(time.time()) + OTP_VALIDITY
    }

    # Get user email from database
    user = get_user_by_username(username)
    user_email = user['email'] if user else None

    # Send OTP email with QR code
    email_sent = False
    if user_email:
        email_sent = send_otp_email_with_qr(user_email, otp, qr_base64)
    
    if not email_sent:
        print(f"[WARNING] Email could not be sent to {user_email}")

    print(f"[OTP for {username}] => {otp}")

    # Return success without QR code (user receives it via email)
    return jsonify({
        "success": True,
        "message": "OTP sent to your email"
    }), 200


@app.route("/pending-qr", methods=["GET"])
def get_pending_qr():
    username = request.args.get("username")

    if not username:
        return jsonify({
            "success": False,
            "message": "Missing username"
        }), 400

    row = pending_qr_codes.get(username)
    now = int(time.time())

    if not row or now > row["expires_at"]:
        pending_qr_codes.pop(username, None)
        return jsonify({
            "success": False,
            "message": "QR not found or expired"
        }), 404

    return jsonify({
        "success": True,
        "qr_code": row["qr_code"]
    }), 200


# ---------------- VERIFY OTP ----------------
@app.route("/verify-otp", methods=["POST"])
def verify():
    username = request.form.get("username")
    otp = request.form.get("otp")

    if not username or not otp:
        return jsonify({
            "success": False,
            "message": "Missing fields"
        }), 400

    success, msg = verify_otp(username, otp)

    if success:
        pending_qr_codes.pop(username, None)
        
        # Store authenticated user in session
        session['user'] = username
        
        # Check if this is a password reset flow
        if session.get("reset_flow") == username:
            session.pop("reset_flow", None)
            session["reset_allowed"] = True
            session["reset_user"] = username
            return jsonify({
                "success": True,
                "message": "OTP verified - redirecting to reset password",
                "redirect": "/reset-password"
            }), 200
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "redirect": "/dashboard"
        }), 200

    return jsonify({
        "success": False,
        "message": msg
    }), 401


# ---------------- FORGOT PASSWORD ----------------
@app.route("/forgot-password")
def forgot_password_page():
    return render_template("forgot_password.html")


@app.route("/test-forgot", methods=["GET"])
def test_forgot():
    return jsonify({"success": True, "message": "Route working"})


@app.route("/debug-forgot", methods=["POST"])
def debug_forgot():
    """Debug route to find the error"""
    email = request.form.get("email", "")
    try:
        from database import get_user_by_email
        user = get_user_by_email(email)
        if user:
            return jsonify({"success": True, "user": user["username"], "email": user["email"]})
        return jsonify({"success": False, "message": "User not found"})
    except Exception as e:
        import traceback
        return jsonify({"success": False, "error": str(e), "trace": traceback.format_exc()})


@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    try:
        email = request.form.get("email")

        if not email:
            return jsonify({
                "success": False,
                "message": "Email is required"
            }), 400

        if not validate_email(email):
            return jsonify({
                "success": False,
                "message": "Invalid email format"
            }), 400

        # Find user by email
        user = get_user_by_email(email)
        
        if not user:
            return jsonify({
                "success": False,
                "message": "No account found with this email"
            }), 404

        username = user["username"]
        user_email = user["email"]

        # Generate OTP for password reset
        # Use empty image bytes since we're not using image-based OTP for password reset
        otp = generate_otp(username, b"reset")

        # Create QR content
        qr_data = f"RESET:{username}|OTP:{otp}"

        # Generate QR image
        qr = qrcode.make(qr_data)

        # Convert to base64
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Store QR for fallback
        pending_qr_codes[username] = {
            "qr_code": qr_base64,
            "expires_at": int(time.time()) + OTP_VALIDITY
        }

        # Send OTP email with QR code
        email_sent = send_otp_email_with_qr(user_email, otp, qr_base64, is_password_reset=True)
        
        if not email_sent:
            print(f"[WARNING] Email could not be sent to {user_email}")

        print(f"[PASSWORD RESET OTP for {username}] => {otp}")

        # Set session flag to indicate this is a password reset flow
        session["reset_flow"] = username

        # Redirect to OTP page for verification
        return jsonify({
            "success": True,
            "message": "OTP sent to your email for password reset",
            "redirect": f"/otp?username={quote(username)}&reset=true"
        }), 200
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Forgot password failed: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


# ---------------- RESET PASSWORD ----------------
@app.route("/reset-password")
def reset_password_page():
    # Only allow if reset was successful
    if not session.get("reset_allowed"):
        return render_template("login_error.html", message="Invalid access. Please start password reset process from the beginning.")
    
    return render_template("reset_password.html", username=session.get("reset_user"))


@app.route("/reset-password", methods=["POST"])
def reset_password():
    if not session.get("reset_allowed"):
        return jsonify({
            "success": False,
            "message": "Invalid access"
        }), 403

    username = session.get("reset_user")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if not new_password or not confirm_password:
        return jsonify({
            "success": False,
            "message": "Both password fields are required"
        }), 400

    if new_password != confirm_password:
        return jsonify({
            "success": False,
            "message": "Passwords do not match"
        }), 400

    if len(new_password) < 6:
        return jsonify({
            "success": False,
            "message": "Password must be at least 6 characters"
        }), 400

    # Hash the new password
    password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

    # Update user's password in database
    update_user_password(username, password_hash)

    # Clear session flags
    session.pop("reset_allowed", None)
    session.pop("reset_user", None)

    return jsonify({
        "success": True,
        "message": "Password reset successful",
        "redirect": "/login?reset=success"
    }), 200


@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect("/login")
    
    username = session['user']
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template("dashboard.html", username=username, session_time=current_time)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    print("CREATING TABLES...")
    create_tables()
    app.run(debug=True)