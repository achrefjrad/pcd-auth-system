import bcrypt
import hashlib
from database import insert_user, get_user_by_username


# ---------- PASSWORD ----------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, stored_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), stored_hash.encode())


# ---------- IMAGE ----------

def hash_image(image_bytes: bytes) -> str:
    return hashlib.sha256(image_bytes).hexdigest()


def verify_image(image_bytes: bytes, stored_hash: str) -> bool:
    return hash_image(image_bytes) == stored_hash


# ---------- REGISTER ----------

def register_user(username, password, image_bytes):
    return insert_user(
        username,
        hash_password(password),
        hash_image(image_bytes)
    )


# ---------- LOGIN (STEP 1) ----------

def login_user(username, password, image_bytes):
    user = get_user_by_username(username)

    if not user:
        return False, "User not found"

    if not verify_password(password, user["password_hash"]):
        return False, "Invalid password"

    if not verify_image(image_bytes, user["image_hash"]):
        return False, "Invalid image"

    return True, "Credentials verified"