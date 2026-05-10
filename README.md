# Secure Mobile Cloud Authentication

> A multi-factor authentication system for Mobile Cloud Computing environments, combining identity credentials, image-based hashing, and a dynamically generated image-based OTP — formally verified using the Scyther tool.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Authentication Flow](#authentication-flow)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Application](#running-the-application)
- [Security Design](#security-design)
- [Formal Verification](#formal-verification)
- [Screenshots](#screenshots)
- [Authors](#authors)

---

## Overview

**pcd-auth** is a Flask-based web application that implements a secure authentication protocol designed for mobile cloud environments. The system goes beyond standard username/password authentication by requiring four independent verification layers:

1. **Identity** — username
2. **Knowledge** — password
3. **Image factor** — a secret profile image registered by the user
4. **Dynamic factor** — a time-windowed OTP derived from the image itself

The authentication protocol was formally modelled and verified using **Scyther**, an automated cryptographic protocol verification tool, confirming resistance to replay attacks, MITM attacks, and impersonation under the Dolev-Yao adversary model.

This project was developed as a Design and Development Project (PCD) at the **National School of Computer Science (ENSI), University of Manouba** — Academic Year 2025/2026.

---

## Features

- ✅ Multi-factor authentication: username + password + image + image-based OTP
- ✅ Image-based OTP generation using SHA-256 and time windows
- ✅ OTP delivered by email with QR code attachment
- ✅ bcrypt hashing for passwords and OTP storage
- ✅ SHA-256 hashing for profile image fingerprinting
- ✅ Dynamic session alias for user anonymity
- ✅ Session-protected dashboard after authentication
- ✅ Password recovery via OTP email flow
- ✅ Formally verified protocol using Scyther (all claims: Ok, no attacks)
- ✅ Modular Flask architecture with separated auth, OTP, and email modules

---

## Authentication Flow

```
User                        Server
 |                             |
 |--- username            --->|  ← Identity
 |--- password            --->|  ← Knowledge factor
 |--- profile image       --->|  ← Image factor
 |                             |
 |                    [bcrypt.verify(password)]
 |                    [SHA-256(image) == stored_hash]
 |                             |
 |                    [generate image-based OTP]
 |                    [bcrypt(OTP) → otp_codes table]
 |                             |
 |<----------- OTP + QR code via email ------------|
 |                             |
 |--- submit OTP          --->|  ← Dynamic factor
 |                             |
 |                    [bcrypt.verify(OTP)]
 |                    [timestamp check]
 |                             |
 |<-------- session token + dashboard --------------|
```

---

## Project Structure

```
pcd-auth/
├── backend/
│   ├── app.py                  # Flask routes and session management
│   ├── database.py             # SQLite interface (schema, queries)
│   ├── auth/
│   │   ├── auth.py             # Password and image verification
│   │   ├── otp.py              # Image-based OTP generation/verification
│   │   └── email_service.py    # SMTP email with QR code attachment
│   └── frontend/
│       ├── templates/          # HTML templates (7 pages)
│       │   ├── index.html
│       │   ├── login.html
│       │   ├── register.html
│       │   ├── otp.html
│       │   ├── dashboard.html
│       │   ├── forgot_password.html
│       │   └── reset_password.html
│       └── static/
│           ├── css/style.css
│           └── js/             # Per-page JavaScript modules
├── .env                        # Environment variables (not committed)
├── requirements.txt
└── README.md
```

---

## Technology Stack

| Component           | Technology                  |
| ------------------- | --------------------------- |
| Web Framework       | Flask (Python 3)            |
| Database            | SQLite                      |
| Password Hashing    | bcrypt                      |
| Image Hashing       | SHA-256 (hashlib)           |
| OTP Storage         | bcrypt                      |
| Email Delivery      | SMTP / Gmail TLS (port 587) |
| QR Code             | Python `qrcode` library     |
| Frontend            | HTML / CSS / JavaScript     |
| Formal Verification | Scyther                     |

---

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip
- A Gmail account with an **App Password** enabled (for SMTP email delivery)

### Installation

**1. Clone the repository:**

```bash
git clone https://github.com/your-username/pcd-auth.git
cd pcd-auth
```

**2. Create and activate a virtual environment:**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies:**

```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root of the project with the following variables:

```env
FLASK_SECRET_KEY=your_secret_key_here
EMAIL_ADDRESS=your_gmail_address@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
```

> **Important:** Use a Gmail **App Password**, not your regular Gmail password.
> To generate one: Google Account → Security → 2-Step Verification → App Passwords.

### Running the Application

```bash
cd backend
python app.py
```

Then open your browser and go to:

```
http://127.0.0.1:5000
```

---

## Security Design

### Database Schema

No plaintext credentials are ever stored. The database contains only hashed values:

```sql
-- Users table
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    UNIQUE NOT NULL,
    email         TEXT    NOT NULL,
    phone         TEXT    NOT NULL,
    password_hash TEXT    NOT NULL,   -- bcrypt hash
    image_hash    TEXT    NOT NULL    -- SHA-256 hash
);

-- OTP table (ephemeral — expires after 300 seconds)
CREATE TABLE otp_codes (
    username   TEXT    PRIMARY KEY,
    otp_hash   TEXT    NOT NULL,      -- bcrypt hash of OTP
    expires_at INTEGER NOT NULL       -- UNIX timestamp
);
```

### Image-Based OTP Algorithm

The OTP is derived from the user's registered image and the current time window:

```
w    = floor(unix_timestamp / 300)
seed = image_bytes || encode(username) || encode(w)
H    = SHA-256(seed)
otp  = hex(H)[0:6]
```

This ensures:

- The OTP changes every 5 minutes automatically
- Two users with the same image receive different OTPs (username binding)
- An attacker cannot reproduce the OTP without the original image file

### Cryptographic Primitives

| Primitive        | Algorithm         | Justification                                      |
| ---------------- | ----------------- | -------------------------------------------------- |
| Password hashing | bcrypt            | Adaptive cost factor; GPU-resistant; built-in salt |
| Image hashing    | SHA-256           | Collision-resistant; deterministic; NIST standard  |
| OTP hashing      | bcrypt            | Prevents offline recovery from DB breach           |
| Transport        | TLS 1.3 (SMTP)    | Encrypts OTP email delivery channel                |
| Session cookies  | HMAC-SHA1 (Flask) | Prevents cookie forgery                            |

---

## Formal Verification

The authentication protocol was formally modelled using **Scyther** and verified under the **Dolev-Yao adversary model** in unbounded mode (any number of concurrent sessions).

**Verification results — all claims: ✅ Ok / No attacks**

| Claim | Property                      | Type      | Result |
| ----- | ----------------------------- | --------- | ------ |
| C1    | Session key secrecy           | Secret    | ✅ Ok  |
| C2    | Session key secrecy (Server)  | Secret    | ✅ Ok  |
| C3    | Partner agreement (User)      | Niagree   | ✅ Ok  |
| C4    | Partner agreement (Server)    | Niagree   | ✅ Ok  |
| C5    | Server liveness               | Alive     | ✅ Ok  |
| C6    | Weak partner agreement        | Weakagree | ✅ Ok  |
| C7    | Full synchronisation (User)   | Nisynch   | ✅ Ok  |
| C8    | Full synchronisation (Server) | Nisynch   | ✅ Ok  |

The SPDL model file is included in the repository as `SecureMCA.spdl`.

---

## Screenshots

| Page             | Description                                                             |
| ---------------- | ----------------------------------------------------------------------- |
| Registration     | User registers with username, email, phone, password, and profile image |
| Login            | User submits credentials and image for verification                     |
| OTP Verification | User enters the 6-character code received by email                      |
| Dashboard        | Secure landing page after successful authentication                     |
| Forgot Password  | OTP-based password reset flow                                           |

---

## Authors

- **Ayoub SLITI**
- **Achref JRAD**
- **Mohamed Nour MESBEHI**

**Supervisor:** Dr. Chrif GHZEL

National School of Computer Science (ENSI) — University of Manouba
Academic Year 2025/2026
