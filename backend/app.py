from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import os

from database import create_tables, get_user_by_username
from auth.email_service import send_otp_email_with_qr
from auth.auth import register_user, login_user
from auth.otp import generate_otp, verify_otp, OTP_VALIDITY

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
        return jsonify({
            "success": True,
            "message": "Login successful"
        }), 200

    return jsonify({
        "success": False,
        "message": msg
    }), 401


if __name__ == "__main__":
    print("CREATING TABLES...")
    create_tables()
    app.run(debug=True)