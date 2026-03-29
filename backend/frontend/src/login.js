console.log("LOGIN JS LOADED");

import { API_BASE_URL } from "./config.js";

const loginForm = document.getElementById("loginForm");
const messageEl = document.getElementById("message");

loginForm?.addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;
    const imageFile = document.getElementById("image").files[0];

    if (!username || !password || !imageFile) {
        if (messageEl) {
            messageEl.innerText = "Username, password, and image are required.";
        }
        return;
    }

    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);
    formData.append("image", imageFile);

    try {
        const res = await fetch(`${API_BASE_URL}/login`, {
            method: "POST",
            body: formData
        });

        let data;
        try {
            data = await res.json();
        } catch {
            throw new Error("Server returned an invalid response.");
        }

        if (!res.ok || !data.success) {
            throw new Error(data.message || "Login failed.");
        }

        if (!data.qr_code) {
            throw new Error("Login succeeded but QR code was not returned by the server.");
        }

        localStorage.setItem("username", username);
        localStorage.setItem("qr", data.qr_code);
        sessionStorage.setItem("username", username);
        sessionStorage.setItem("qr", data.qr_code);

        const params = new URLSearchParams({ username });
        window.location.href = `otp.html?${params.toString()}`;
    } catch (error) {
        if (messageEl) {
            messageEl.innerText = error.message || "Unable to complete login.";
        }
    }
});