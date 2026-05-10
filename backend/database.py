import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "users.db")


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        image_hash TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS otp_codes (
        username TEXT PRIMARY KEY,
        otp_hash TEXT NOT NULL,
        expires_at INTEGER NOT NULL
    )
    """)

    try:
        cursor.execute("SELECT email FROM users LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT NOT NULL DEFAULT ''")
        cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT NOT NULL DEFAULT ''")

    conn.commit()
    conn.close()


# ---------- USERS ----------

def insert_user(username, email, phone, password_hash, image_hash):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, phone, password_hash, image_hash) VALUES (?, ?, ?, ?, ?)",
            (username, email, phone, password_hash, image_hash)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, email, phone, password_hash, image_hash FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, email, phone, password_hash, image_hash FROM users WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_password(username, new_password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (new_password_hash, username)
    )
    conn.commit()
    conn.close()


# ---------- OTP ----------

def store_otp(username, otp_hash, expires_at):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM otp_codes WHERE username = ?", (username,))
    cursor.execute(
        "INSERT INTO otp_codes (username, otp_hash, expires_at) VALUES (?, ?, ?)",
        (username, otp_hash, expires_at)
    )
    conn.commit()
    conn.close()


def get_otp(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT otp_hash, expires_at FROM otp_codes WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    return row


def delete_otp(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM otp_codes WHERE username = ?", (username,))
    conn.commit()
    conn.close()
