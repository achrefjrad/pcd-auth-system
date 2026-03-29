import time
import hashlib
import bcrypt
from database import store_otp, get_otp, delete_otp

OTP_VALIDITY = 300  # 5 minutes


# ---------- GENERATE OTP FROM IMAGE ----------
def generate_otp(username, image_bytes):
    # Current time window (changes every 5 minutes)
    time_window = int(time.time() // OTP_VALIDITY)

    # Combine image + username + time
    data = image_bytes + username.encode() + str(time_window).encode()

    # Hash it
    hash_value = hashlib.sha256(data).hexdigest()

    # Take first 6 digits from hash
    otp = str(int(hash_value, 16))[:6]

    # Hash OTP for storage
    otp_hash = bcrypt.hashpw(otp.encode(), bcrypt.gensalt()).decode()
    expires_at = int(time.time()) + OTP_VALIDITY

    store_otp(username, otp_hash, expires_at)

    return otp


# ---------- VERIFY OTP ----------
def verify_otp(username, otp):
    row = get_otp(username)

    if not row:
        return False, "OTP not found"

    otp_hash, expires_at = row

    if time.time() > expires_at:
        delete_otp(username)
        return False, "OTP expired"

    if not bcrypt.checkpw(otp.encode(), otp_hash.encode()):
        return False, "Invalid OTP"

    delete_otp(username)
    return True, "OTP verified"