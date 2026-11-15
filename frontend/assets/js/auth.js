/**
 * SMART POULTRY HEALTH & PRECISION FARMING SYSTEM
 * Mobile Number & Password Authentication Service (auth.js)
 * Connects directly to backend API: /api/auth/* with JWT Token Management
 * NO OTP Required for Registration or Login
 */

const AUTH_STORAGE_KEY = 'smart_poultry_auth_user';
const JWT_TOKEN_KEY = 'smart_poultry_jwt_token';
const API_BASE_URL = (typeof window !== 'undefined' && window.API_BASE_URL)
  ? window.API_BASE_URL
  : (window.location.protocol.startsWith('http') ? '' : 'http://127.0.0.1:5000');

const MobileAuth = {
  currentOtp: null,
  countdownInterval: null,
  pendingMobile: null,
  pendingRegistrationData: null,

  init() {
    this.checkAuthStatus();
  },

  getToken() {
    return localStorage.getItem(JWT_TOKEN_KEY);
  },

  getLoggedInUser() {
    const data = localStorage.getItem(AUTH_STORAGE_KEY);
    try {
      return data ? JSON.parse(data) : null;
    } catch (e) {
      return null;
    }
  },

  isLoggedIn() {
    return !!this.getToken() && !!this.getLoggedInUser();
  },

  checkAuthStatus() {
    const user = this.getLoggedInUser();
    const statusPill = document.getElementById('authStatusPill');
    const authBtnText = document.getElementById('authBtnText');
    const syncNameEls = document.querySelectorAll('.sync-user-name');
    const syncPhoneEls = document.querySelectorAll('.sync-user-phone');
    const syncFarmEls = document.querySelectorAll('.sync-user-farm');

    if (user) {
      if (statusPill) {
        statusPill.innerHTML = `<i class="bi bi-person-check-fill text-success me-1"></i><span class="small fw-bold text-dark">${user.phone || user.mobile_number}</span>`;
      }
      if (authBtnText) authBtnText.textContent = 'Account';
      syncNameEls.forEach(el => el.textContent = user.name || user.fullName || 'Poultry Farmer');
      syncPhoneEls.forEach(el => el.textContent = user.phone || user.mobile_number || '');
      if (syncFarmEls) {
        syncFarmEls.forEach(el => el.textContent = user.farm_name || 'Active Farmer');
      }
    } else {
      if (statusPill) {
        statusPill.innerHTML = `<i class="bi bi-person-circle text-muted me-1"></i><span class="small text-muted">Guest / Farmer</span>`;
      }
      if (authBtnText) authBtnText.textContent = 'Login';
      syncNameEls.forEach(el => el.textContent = 'Poultry Farmer');
      syncPhoneEls.forEach(el => el.textContent = 'Not Logged In');
    }
  },

  // 1. Direct Password Login (No OTP Required)
  async loginWithPassword(identifier, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ identifier: identifier, password: password })
      });

      const data = await response.json();
      if (response.ok && data.status === 'success') {
        localStorage.setItem(JWT_TOKEN_KEY, data.token);
        localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(data.user));
        this.checkAuthStatus();
        return { success: true, user: data.user, token: data.token };
      } else {
        return { success: false, message: data.message || 'Invalid mobile number or password.' };
      }
    } catch (e) {
      console.error('Error in loginWithPassword:', e);
      return { success: false, message: 'Could not connect to backend server. Make sure the server is online.' };
    }
  },

  // 2. Direct Password Registration (No OTP Required)
  async registerWithPassword(regData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          fullName: regData.fullName,
          phone: regData.phone,
          email: regData.email || null,
          password: regData.password,
          confirmPassword: regData.password,
          role: regData.role || 'farmer',
          farmName: regData.farmName,
          location: regData.location
        })
      });

      const data = await response.json();
      if (response.ok && data.status === 'success') {
        if (data.token) {
          localStorage.setItem(JWT_TOKEN_KEY, data.token);
        }
        if (data.user) {
          localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(data.user));
        }
        this.checkAuthStatus();
        return { success: true, message: data.message, user: data.user, token: data.token };
      } else {
        return { success: false, message: data.message || 'Registration failed.' };
      }
    } catch (e) {
      console.error('Error in registerWithPassword:', e);
      return { success: false, message: 'Could not connect to backend server. Make sure the server is online.' };
    }
  },

  // 3. User Logout
  async logout() {
    try {
      await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      });
    } catch (e) {
      // ignore network error on logout
    }
    localStorage.removeItem(AUTH_STORAGE_KEY);
    localStorage.removeItem(JWT_TOKEN_KEY);
    localStorage.removeItem('smart_poultry_selected_farm');
    this.checkAuthStatus();
    window.location.href = 'login.html';
  },

  // 4. Send OTP for Mobile Login / Reset
  async sendOtpForLogin(phone, countryCode = '+91') {
    try {
      const digits = String(phone || '').replace(/\D/g, '').slice(-10);
      this.pendingMobile = `${countryCode} ${digits}`;
      const response = await fetch(`${API_BASE_URL}/api/auth/send-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ phone: digits, countryCode: countryCode })
      });

      const data = await response.json();
      if (response.ok && data.status === 'success') {
        this.currentOtp = data.otp || null;
        if (data.otp) {
          console.info(`[SmartPoultry OTP] Verification code: ${data.otp}`);
        }
        return { success: true, message: data.message, phone: data.phone || this.pendingMobile, otp: data.otp };
      } else {
        return { success: false, message: data.message || 'Failed to dispatch OTP.' };
      }
    } catch (e) {
      console.error('Error in sendOtpForLogin:', e);
      return { success: false, message: 'Could not connect to server. Please try again.' };
    }
  },

  // 5. Verify OTP and Sign In
  async verifyOtpAndLogin(otp, phone = null) {
    try {
      const targetPhone = phone || this.pendingMobile || '';
      const response = await fetch(`${API_BASE_URL}/api/auth/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ phone: targetPhone, otp: otp })
      });

      const data = await response.json();
      if (response.ok && data.status === 'success') {
        if (data.token) localStorage.setItem(JWT_TOKEN_KEY, data.token);
        if (data.user) localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(data.user));
        this.checkAuthStatus();
        return { success: true, user: data.user, token: data.token, message: data.message };
      } else {
        return { success: false, message: data.message || 'Invalid OTP code.' };
      }
    } catch (e) {
      console.error('Error in verifyOtpAndLogin:', e);
      return { success: false, message: 'Could not connect to server. Please try again.' };
    }
  },

  // 6. Reset Password via OTP
  async resetPassword(phone, otp, newPassword) {
    try {
      const digits = String(phone || '').replace(/\D/g, '').slice(-10);
      const response = await fetch(`${API_BASE_URL}/api/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ phone: digits, otp: otp, password: newPassword })
      });

      const data = await response.json();
      if (response.ok && data.status === 'success') {
        return { success: true, message: data.message };
      } else {
        return { success: false, message: data.message || 'Failed to reset password.' };
      }
    } catch (e) {
      console.error('Error in resetPassword:', e);
      return { success: false, message: 'Could not connect to server. Please try again.' };
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  MobileAuth.init();
});

window.MobileAuth = MobileAuth;
