// register.js - Extracted from register.html
// Contains: password toggle, image upload, form validation, submission

const API_BASE_URL = "http://127.0.0.1:5000";

let selectedImage = null;

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
        <img src="${e.target.result}" alt="Uploaded" class="w-16 h-16 mx-auto rounded-full object-cover border-2 border-success" />
        <p class="text-sm text-success mt-2 font-medium">Image uploaded</p>
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

document.getElementById('registerForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const errorMsg = document.getElementById('errorMessage');
  const successMsg = document.getElementById('successMessage');
  const submitBtn = document.getElementById('submitBtn');
  
  const username = document.getElementById('username').value.trim();
  const email = document.getElementById('email').value.trim();
  const phone = document.getElementById('phone').value.trim();
  const password = document.getElementById('password').value;

  if (!username || !email || !phone || !password || !selectedImage) {
    errorMsg.textContent = "All fields are required";
    errorMsg.classList.remove('hidden');
    successMsg.classList.add('hidden');
    return;
  }

  if (username.length < 3) {
    errorMsg.textContent = "Username must be at least 3 characters";
    errorMsg.classList.remove('hidden');
    successMsg.classList.add('hidden');
    return;
  }

  if (password.length < 6) {
    errorMsg.textContent = "Password must be at least 6 characters";
    errorMsg.classList.remove('hidden');
    successMsg.classList.add('hidden');
    return;
  }

  errorMsg.classList.add('hidden');
  successMsg.classList.add('hidden');
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="inline-flex items-center"><svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-primary-foreground" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>Creating Account...</span>';

  const formData = new FormData();
  formData.append('username', username);
  formData.append('email', email);
  formData.append('phone', phone);
  formData.append('password', password);
  formData.append('image', selectedImage);

  try {
    const res = await fetch(`${API_BASE_URL}/register`, {
      method: 'POST',
      body: formData
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      throw new Error(data.message || 'Registration failed');
    }

    successMsg.textContent = "Registration successful! Redirecting to login...";
    successMsg.classList.remove('hidden');
    
    setTimeout(() => {
      window.location.href = '/login';
    }, 1500);
  } catch (error) {
    errorMsg.textContent = error.message || 'Unable to register right now';
    errorMsg.classList.remove('hidden');
    submitBtn.disabled = false;
    submitBtn.textContent = 'Register';
  }
});