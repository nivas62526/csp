/**
 * SMART POULTRY HEALTH MONITORING & DISEASE-RISK PREDICTION SYSTEM
 * Public Site & Global Utility Controller (app.js)
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavbarScroll();
  initSmoothScroll();
  initAuthValidation();
});

// 1. Landing Page Navbar Shrink on Scroll
function initNavbarScroll() {
  const navbar = document.querySelector('.landing-nav');
  if (!navbar) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });
}

// 2. Smooth Scroll for Anchor Links
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#' || !targetId) return;
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        e.preventDefault();
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

// 3. Frontend Authentication Form Validation & Demo Auto-Fill
function initAuthValidation() {
  // Login Form
  const loginForm = document.getElementById('farmerLoginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = document.getElementById('loginEmail').value.trim();
      const password = document.getElementById('loginPassword').value;

      if (!email || !password) {
        showAuthAlert('Please fill in all required fields.', 'danger');
        return;
      }

      // Check simple mock credentials
      showAuthAlert('Authenticating...', 'info');
      setTimeout(() => {
        if (email.includes('admin')) {
          window.location.href = 'admin.html';
        } else {
          window.location.href = 'dashboard.html';
        }
      }, 700);
    });
  }

  // Register Form
  const registerForm = document.getElementById('farmerRegisterForm');
  if (registerForm) {
    registerForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const fullName = document.getElementById('regFullName').value.trim();
      const email = document.getElementById('regEmail').value.trim();
      const phone = document.getElementById('regPhone').value.trim();
      const password = document.getElementById('regPassword').value;
      const confirmPassword = document.getElementById('regConfirmPassword').value;
      const farmName = document.getElementById('regFarmName').value.trim();
      const farmLocation = document.getElementById('regFarmLocation').value.trim();

      if (!fullName || !email || !phone || !password || !farmName || !farmLocation) {
        showAuthAlert('Please fill in all registration fields.', 'danger');
        return;
      }

      if (password !== confirmPassword) {
        showAuthAlert('Passwords do not match.', 'danger');
        return;
      }

      // Save new user profile
      const newUser = {
        fullName,
        email,
        phone,
        farmName,
        location: farmLocation,
        role: 'Farm Owner & Operator',
        memberSince: 'August 2026'
      };
      MockAPI.updateUserProfile(newUser);

      showAuthAlert('Registration successful! Redirecting to dashboard...', 'success');
      setTimeout(() => {
        window.location.href = 'dashboard.html';
      }, 1000);
    });
  }
}

function showAuthAlert(message, type = 'danger') {
  const alertBox = document.getElementById('authAlertBox');
  if (!alertBox) return;
  alertBox.className = `alert alert-${type} py-2 px-3 mb-3 small d-flex align-items-center gap-2`;
  alertBox.innerHTML = `<i class="bi bi-info-circle-fill"></i> <span>${message}</span>`;
  alertBox.style.display = 'flex';
}

// Quick Demo Login Helper Buttons
function fillDemoFarmer() {
  const emailInput = document.getElementById('loginEmail');
  const passInput = document.getElementById('loginPassword');
  if (emailInput && passInput) {
    emailInput.value = 'farmer@poultrysmart.com';
    passInput.value = 'demo1234';
  }
}

function fillDemoAdmin() {
  const emailInput = document.getElementById('loginEmail');
  const passInput = document.getElementById('loginPassword');
  if (emailInput && passInput) {
    emailInput.value = 'admin@poultrysmart.com';
    passInput.value = 'admin1234';
  }
}
