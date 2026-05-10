// reset_password.js - Reset password form submission

const API_BASE_URL = window.location.origin || "http://127.0.0.1:5000";

function togglePassword(fieldId) {
  const passwordInput = document.getElementById(fieldId);
  const fieldName = fieldId === 'new_password' ? 'New' : 'Confirm';
  const eyeIcon = document.getElementById('eyeIcon' + fieldName);
  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    eyeIcon.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>';
  } else {
    passwordInput.type = 'password';
    eyeIcon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
  }
}

document.getElementById('resetPasswordForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const errorMsg = document.getElementById('errorMessage');
  const submitBtn = document.getElementById('submitBtn');
  const newPassword = document.getElementById('new_password').value;
  const confirmPassword = document.getElementById('confirm_password').value;

  if (!newPassword || !confirmPassword) {
    errorMsg.textContent = "Both password fields are required";
    errorMsg.classList.remove('hidden');
    return;
  }

  if (newPassword !== confirmPassword) {
    errorMsg.textContent = "Passwords do not match";
    errorMsg.classList.remove('hidden');
    return;
  }

  if (newPassword.length < 6) {
    errorMsg.textContent = "Password must be at least 6 characters";
    errorMsg.classList.remove('hidden');
    return;
  }

  errorMsg.classList.add('hidden');
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="inline-flex items-center"><svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-primary-foreground" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>Resetting...</span>';

  const formData = new FormData();
  formData.append('new_password', newPassword);
  formData.append('confirm_password', confirmPassword);

  try {
    const res = await fetch(`${API_BASE_URL}/reset-password`, {
      method: 'POST',
      body: formData
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      throw new Error(data.message || 'Failed to reset password');
    }

    // Redirect to login with success message
    window.location.href = data.redirect;
  } catch (error) {
    errorMsg.textContent = error.message || 'Unable to reset password';
    errorMsg.classList.remove('hidden');
    submitBtn.disabled = false;
    submitBtn.textContent = 'Reset Password';
  }
});