// otp.js - OTP verification without QR display
// OTP is now sent via email instead of displaying QR code

const API_BASE_URL = "http://127.0.0.1:5000";

const query = new URLSearchParams(window.location.search);
const username = query.get("username") || sessionStorage.getItem("username") || localStorage.getItem("username");

const errorMsg = document.getElementById('errorMessage');
const successMsg = document.getElementById('successMessage');
const otpForm = document.getElementById("otpForm");

// Store username for OTP verification
if (username) {
  localStorage.setItem('username', username);
}

otpForm?.addEventListener("submit", async function(e) {
  e.preventDefault();
  
  const submitBtn = document.getElementById('submitBtn');
  const otpValue = document.getElementById("otp").value.trim();

  if (!username || !otpValue) {
    errorMsg.textContent = "Missing username or OTP";
    errorMsg.classList.remove('hidden');
    successMsg.classList.add('hidden');
    return;
  }

  errorMsg.classList.add('hidden');
  successMsg.classList.add('hidden');
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="inline-flex items-center"><svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-primary-foreground" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>Verifying...</span>';

  const formData = new FormData();
  formData.append("username", username);
  formData.append("otp", otpValue);

  try {
    const res = await fetch(`${API_BASE_URL}/verify-otp`, {
      method: "POST",
      body: formData
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      throw new Error(data.message || "OTP verification failed");
    }

    successMsg.textContent = "Login successful!";
    successMsg.classList.remove('hidden');
    
    localStorage.removeItem("username");
    sessionStorage.removeItem("username");
    
    setTimeout(() => {
      window.location.href = '/';
    }, 1500);
  } catch (error) {
    errorMsg.textContent = error.message || "Unable to verify OTP";
    errorMsg.classList.remove('hidden');
    submitBtn.disabled = false;
    submitBtn.textContent = 'Verify OTP';
  }
});