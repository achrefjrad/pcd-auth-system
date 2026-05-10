// forgot_password.js - Forgot password form submission

const API_BASE_URL = window.location.origin || "http://127.0.0.1:5000";

console.log('forgot_password.js loaded, API_BASE_URL:', API_BASE_URL);

const form = document.getElementById('forgotPasswordForm');
if (!form) {
  console.error('forgotPasswordForm not found!');
}

form?.addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const errorMsg = document.getElementById('errorMessage');
  const successMsg = document.getElementById('successMessage');
  const submitBtn = document.getElementById('submitBtn');
  const email = document.getElementById('email').value.trim();

  if (!email) {
    errorMsg.textContent = "Email is required";
    errorMsg.classList.remove('hidden');
    successMsg.classList.add('hidden');
    return;
  }

  errorMsg.classList.add('hidden');
  successMsg.classList.add('hidden');
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="inline-flex items-center"><svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-primary-foreground" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>Sending...</span>';

  const formData = new FormData();
  formData.append('email', email);

  try {
    console.log('Fetching:', API_BASE_URL + '/forgot-password');
    
    const res = await fetch(`${API_BASE_URL}/forgot-password`, {
      method: 'POST',
      mode: 'cors',
      body: formData
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      throw new Error(data.message || 'Failed to send reset OTP');
    }

    successMsg.textContent = "OTP has been sent to your email. Please check your inbox (and spam folder).";
    successMsg.classList.remove('hidden');
    
    // Redirect to OTP page
    window.location.href = data.redirect;
  } catch (error) {
    console.error('Error:', error);
    errorMsg.textContent = error.message || 'Unable to connect to server. Please check if Flask is running.';
    errorMsg.classList.remove('hidden');
    submitBtn.disabled = false;
    submitBtn.textContent = 'Send Reset OTP';
  }
});