// login.js - Extracted from login.html
// Contains: password toggle, image upload, form submission

const API_BASE_URL = window.location.origin || "http://127.0.0.1:5000";

let selectedImage = null;

// Check for password reset success message
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('reset') === 'success') {
  const successMessage = document.createElement('div');
  successMessage.className = 'p-3 rounded-lg bg-success/10 border border-success text-success text-sm text-center mb-4';
  successMessage.textContent = 'Password reset successful! Please log in with your new password.';
  const form = document.getElementById('loginForm');
  form.insertBefore(successMessage, form.firstChild);
}

function handleImageSelect(input) {
  if (input.files && input.files[0]) {
    selectedImage = input.files[0];
    const reader = new FileReader();
    reader.onload = function(e) {
      const uploadDiv = document.getElementById('imageUpload');
      const preview = document.getElementById('imagePreview');
      uploadDiv.classList.remove('border-border', 'hover:border-primary/50', 'hover:bg-secondary/50');
      uploadDiv.classList.add('border-success', 'bg-success/5');
      preview.innerHTML = `
        <img src="${e.target.result}" alt="Uploaded" class="w-20 h-20 mx-auto rounded-full object-cover border-2 border-success" />
        <p class="text-sm text-success mt-3 font-medium">Image uploaded successfully</p>
      `;
    };
    reader.readAsDataURL(selectedImage);
  }
}

function togglePassword() {
  const passwordInput = document.getElementById('password');
  const eyeIcon = document.getElementById('eyeIcon');
  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    eyeIcon.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>';
  } else {
    passwordInput.type = 'password';
    eyeIcon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
  }
}

document.getElementById('loginForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const errorMsg = document.getElementById('errorMessage');
  const submitBtn = document.getElementById('submitBtn');
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;

  if (!username || !password || !selectedImage) {
    errorMsg.textContent = "Username, password, and image are required";
    errorMsg.classList.remove('hidden');
    return;
  }

  errorMsg.classList.add('hidden');
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="inline-flex items-center"><svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-primary-foreground" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>Authenticating...</span>';

  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  formData.append('image', selectedImage);

  try {
    const res = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      body: formData
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      throw new Error(data.message || 'Login failed');
    }

    localStorage.setItem('username', username);
    
    // Redirect to OTP page - QR code sent via email
    window.location.href = `/otp?username=${encodeURIComponent(username)}`;
  } catch (error) {
    errorMsg.textContent = error.message || 'Unable to complete login';
    errorMsg.classList.remove('hidden');
    submitBtn.disabled = false;
    submitBtn.textContent = 'Login';
  }
});