console.log("REGISTER JS LOADED");

import { API_BASE_URL } from "./config.js";

const registerForm = document.getElementById("registerForm");
const messageEl = document.getElementById("message");

registerForm?.addEventListener("submit", async function (e) {
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
        const res = await fetch(`${API_BASE_URL}/register`, {
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
            throw new Error(data.message || "Registration failed.");
        }

        setTimeout(() => {
            window.location.href = "login.html";
        }, 1000);
    } catch (error) {
        if (messageEl) {
            messageEl.innerText = error.message || "Unable to register right now.";
        }
    }
});