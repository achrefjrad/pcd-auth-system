console.log("OTP JS LOADED");

import { API_BASE_URL } from "./config.js";

const qrImageEl = document.getElementById("qrImage");
const messageEl = document.getElementById("message");
const otpForm = document.getElementById("otpForm");

const query = new URLSearchParams(window.location.search);
const username = query.get("username") || sessionStorage.getItem("username") || localStorage.getItem("username");

async function loadQrCode() {
    const qrFromStorage = sessionStorage.getItem("qr") || localStorage.getItem("qr");

    if (qrFromStorage && qrImageEl) {
        qrImageEl.src = "data:image/png;base64," + qrFromStorage;
        return;
    }

    if (!username) {
        if (messageEl) {
            messageEl.innerText = "QR code not found. Please log in again.";
        }
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/pending-qr?username=${encodeURIComponent(username)}`);

        let data;
        try {
            data = await res.json();
        } catch {
            throw new Error("Server returned an invalid response.");
        }

        if (!res.ok || !data.success || !data.qr_code) {
            throw new Error(data.message || "QR code not found. Please log in again.");
        }

        sessionStorage.setItem("qr", data.qr_code);
        localStorage.setItem("qr", data.qr_code);

        if (qrImageEl) {
            qrImageEl.src = "data:image/png;base64," + data.qr_code;
        }
    } catch (error) {
        if (messageEl) {
            messageEl.innerText = error.message || "QR code not found. Please log in again.";
        }
    }
}

loadQrCode();

otpForm?.addEventListener("submit", async function (e) {
    e.preventDefault();

    const otpValue = document.getElementById("otp").value.trim();

    if (!username || !otpValue) {
        if (messageEl) {
            messageEl.innerText = "Missing username or OTP. Please login again.";
        }
        return;
    }

    const formData = new FormData();
    formData.append("username", username);
    formData.append("otp", otpValue);

    try {
        const res = await fetch(`${API_BASE_URL}/verify-otp`, {
            method: "POST",
            body: formData
        });

        let data;
        try {
            data = await res.json();
        } catch {
            throw new Error("Server returned an invalid response.");
        }

        if (messageEl) {
            messageEl.innerText = data.message || "Request completed.";
        }

        if (!res.ok || !data.success) {
            throw new Error(data.message || "OTP verification failed.");
        }

        alert("Login successful!");
        localStorage.removeItem("qr");
        localStorage.removeItem("username");
        sessionStorage.removeItem("qr");
        sessionStorage.removeItem("username");
    } catch (error) {
        if (messageEl) {
            messageEl.innerText = error.message || "Unable to verify OTP.";
        }
    }
});