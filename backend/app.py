from flask import Flask, request, jsonify
from flask_cors import CORS

from database import create_tables
from auth.auth import register_user, login_user
from auth.otp import generate_otp, verify_otp, OTP_VALIDITY

import qrcode
import base64
import time
from io import BytesIO

app = Flask(__name__)
app.secret_key = "pcd-secret-key"

CORS(app)

# Temporary in-memory store for the most recent QR per user.
pending_qr_codes = {}


@app.route("/")
def home():
    return jsonify({
        "success": True,
        "message": "PCD Authentication Backend Running"
    })


# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    image = request.files.get("image")

    if not username or not password or not image:
        return jsonify({
            "success": False,
            "message": "Missing fields"
        }), 400

    result = register_user(username, password, image.read())

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
            "message": "Missing fields"
        }), 400

    image_bytes = image.read()

    success, msg = login_user(username, password, image_bytes)

    if not success:
        return jsonify({
            "success": False,
            "message": msg
        }), 401

    # 🔥 Generate OTP (your image-based OTP)
    otp = generate_otp(username, image_bytes)

    # 🔥 Create QR content
    qr_data = f"USER:{username}|OTP:{otp}"

    # 🔥 Generate QR image
    qr = qrcode.make(qr_data)

    # 🔥 Convert to base64
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    pending_qr_codes[username] = {
        "qr_code": qr_base64,
        "expires_at": int(time.time()) + OTP_VALIDITY
    }

    print(f"[OTP for {username}] => {otp}")

    return jsonify({
        "success": True,
        "message": "OTP generated",
        "qr_code": qr_base64
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