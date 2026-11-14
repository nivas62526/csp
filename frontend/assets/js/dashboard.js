/**
 * SMART POULTRY HEALTH MONITORING & DISEASE-RISK PREDICTION SYSTEM
 * Core Dashboard & UI Interaction Controller (dashboard.js)
 */

document.addEventListener('DOMContentLoaded', async () => {
  initSidebar();
  initFarmSelector();
  initNotificationsDropdown();
  initGlobalSearch();
  initProfileSync();
  highlightActiveNavLink();
});

// 1. Sidebar Toggler & Responsive Mobile Drawer
function initSidebar() {
  const toggleBtn = document.getElementById('sidebarToggleBtn');
  const overlay = document.getElementById('sidebarOverlay');

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      if (window.innerWidth >= 992) {
        document.body.classList.toggle('sidebar-collapsed');
        localStorage.setItem('smart_poultry_sidebar_collapsed', document.body.classList.contains('sidebar-collapsed'));
      } else {
        document.body.classList.toggle('sidebar-mobile-open');
      }
    });
  }

  if (overlay) {
    overlay.addEventListener('click', () => {
      document.body.classList.remove('sidebar-mobile-open');
    });
  }

  // Restore desktop collapsed state
  if (window.innerWidth >= 992 && localStorage.getItem('smart_poultry_sidebar_collapsed') === 'true') {
    document.body.classList.add('sidebar-collapsed');
  }
}

// 2. Farm Selector Synchronization
async function initFarmSelector() {
  const farmSelect = document.getElementById('topbarFarmSelect');
  if (!farmSelect) return;

  const farms = await MockAPI.getFarms();
  const selectedFarmId = MockAPI.getSelectedFarmId();

  if (farms.length === 0) {
    farmSelect.innerHTML = `<option value="">+ Add Your Farm</option>`;
  } else {
    farmSelect.innerHTML = farms.map(f => `
      <option value="${f.id}" ${f.id === selectedFarmId ? 'selected' : ''}>
        ${f.name} (${(parseInt(f.currentBirds) || 0).toLocaleString()} Birds)
      </option>
    `).join('');
  }

  farmSelect.addEventListener('change', (e) => {
    if (!e.target.value) {
      window.location.href = 'farms.html';
      return;
    }
    MockAPI.setSelectedFarmId(e.target.value);
    showToast(`Switched farm view to: ${e.target.options[e.target.selectedIndex].text}`, 'info', 'Farm Changed');
    window.dispatchEvent(new CustomEvent('farmChanged', { detail: { farmId: e.target.value } }));
  });
}

// 3. Topbar Notifications Menu
async function initNotificationsDropdown() {
  const notifContainer = document.getElementById('topbarNotificationsList');
  const notifBadge = document.getElementById('topbarNotifBadge');
  const markAllBtn = document.getElementById('markAllNotifsReadBtn');

  if (!notifContainer) return;

  const alerts = await MockAPI.getAlerts();
  const unreadAlerts = alerts.filter(a => !a.isRead);

  if (notifBadge) {
    notifBadge.style.display = unreadAlerts.length > 0 ? 'block' : 'none';
  }

  if (alerts.length === 0) {
    notifContainer.innerHTML = '<div class="p-3 text-center text-muted small">No notifications</div>';
    return;
  }

  notifContainer.innerHTML = alerts.slice(0, 4).map(alert => {
    let iconClass = 'bi-bell text-primary';
    let bgClass = 'bg-primary-subtle';
    if (alert.severity === 'Critical') {
      iconClass = 'bi-exclamation-octagon-fill text-danger';
      bgClass = 'bg-danger-subtle';
    } else if (alert.severity === 'Warning') {
      iconClass = 'bi-exclamation-triangle-fill text-warning';
      bgClass = 'bg-warning-subtle';
    }

    return `
      <div class="notif-item ${alert.isRead ? '' : 'unread'}" onclick="handleNotifClick('${alert.id}')">
        <div class="notif-icon ${bgClass}">
          <i class="bi ${iconClass}"></i>
        </div>
        <div class="flex-grow-1">
          <div class="notif-title">${alert.title}</div>
          <div class="notif-text">${alert.description}</div>
          <div class="notif-time"><i class="bi bi-clock me-1"></i>${alert.timestamp} &bull; ${alert.batchName || ''}</div>
        </div>
      </div>
    `;
  }).join('');

  if (markAllBtn) {
    markAllBtn.addEventListener('click', async () => {
      await MockAPI.markAllAlertsAsRead();
      initNotificationsDropdown();
      showToast('All notifications marked as read', 'success');
    });
  }
}

async function handleNotifClick(alertId) {
  await MockAPI.markAlertAsRead(alertId);
  window.location.href = 'alerts.html';
}

// 4. Global Search Modal & Filter
function initGlobalSearch() {
  const searchInput = document.getElementById('topbarSearchInput');
  const searchModalEl = document.getElementById('globalSearchModal');
  
  if (searchInput && searchModalEl) {
    const searchModal = new bootstrap.Modal(searchModalEl);
    searchInput.addEventListener('focus', () => {
      searchModal.show();
      setTimeout(() => {
        const modalInput = document.getElementById('modalSearchInput');
        if (modalInput) modalInput.focus();
      }, 300);
    });

    const modalInput = document.getElementById('modalSearchInput');
    const modalResults = document.getElementById('modalSearchResults');

    if (modalInput && modalResults) {
      modalInput.addEventListener('input', async (e) => {
        const q = e.target.value.toLowerCase().trim();
        if (!q) {
          modalResults.innerHTML = '<div class="text-center text-muted py-4 small">Type to search across farms, batches, predictions, alerts, and reports...</div>';
          return;
        }

        const farms = await MockAPI.getFarms();
        const batches = await MockAPI.getBatches();
        const alerts = await MockAPI.getAlerts();

        const matchFarms = farms.filter(f => f.name.toLowerCase().includes(q) || f.location.toLowerCase().includes(q));
        const matchBatches = batches.filter(b => b.name.toLowerCase().includes(q) || b.birdType.toLowerCase().includes(q));
        const matchAlerts = alerts.filter(a => a.title.toLowerCase().includes(q) || a.description.toLowerCase().includes(q));

        let html = '';
        if (matchFarms.length > 0) {
          html += '<h6 class="text-muted small fw-bold px-3 pt-2">FARMS</h6>';
          matchFarms.forEach(f => {
            html += `<a href="farms.html" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
              <div><i class="bi bi-building me-2 text-primary"></i><strong>${f.name}</strong> <span class="text-muted small">(${f.location})</span></div>
              <span class="badge bg-light text-dark">${f.currentBirds} birds</span>
            </a>`;
          });
        }
        if (matchBatches.length > 0) {
          html += '<h6 class="text-muted small fw-bold px-3 pt-3">BATCHES</h6>';
          matchBatches.forEach(b => {
            html += `<a href="batches.html" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
              <div><i class="bi bi-grid-fill me-2 text-info"></i><strong>${b.name}</strong> <span class="text-muted small">(${b.birdType})</span></div>
              <span class="badge ${b.riskLevel === 'High' ? 'bg-danger' : b.riskLevel === 'Medium' ? 'bg-warning text-dark' : 'bg-success'}">${b.riskLevel} Risk</span>
            </a>`;
          });
        }
        if (matchAlerts.length > 0) {
          html += '<h6 class="text-muted small fw-bold px-3 pt-3">ALERTS</h6>';
          matchAlerts.forEach(a => {
            html += `<a href="alerts.html" class="list-group-item list-group-item-action">
              <i class="bi bi-bell-fill me-2 text-warning"></i><strong>${a.title}</strong>
              <div class="text-muted small">${a.description}</div>
            </a>`;
          });
        }

        if (!html) {
          html = `<div class="text-center text-muted py-4 small">No results matching "<strong>${q}</strong>"</div>`;
        }

        modalResults.innerHTML = html;
      });
    }
  }
}

// 5. User Profile Synchronization
function initProfileSync() {
  const user = MockAPI.getUserProfile();
  const nameEls = document.querySelectorAll('.sync-user-name');
  const emailEls = document.querySelectorAll('.sync-user-email');
  const farmEls = document.querySelectorAll('.sync-user-farm');

  nameEls.forEach(el => el.textContent = user.fullName);
  emailEls.forEach(el => el.textContent = user.email);
  farmEls.forEach(el => el.textContent = user.farmName);
}

// 6. Highlight Current Active Nav Link
function highlightActiveNavLink() {
  const currentPath = window.location.pathname.split('/').pop() || 'dashboard.html';
  const links = document.querySelectorAll('.app-sidebar .nav-link-item');
  links.forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
}

// 7. Toast Notification Trigger Utility
function showToast(message, type = 'success', title = '') {
  let container = document.getElementById('appToastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'appToastContainer';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1095';
    document.body.appendChild(container);
  }

  const toastId = 'toast-' + Date.now();
  const bgClass = type === 'success' ? 'text-bg-success' : type === 'danger' ? 'text-bg-danger' : type === 'warning' ? 'text-bg-warning' : 'text-bg-primary';
  const iconClass = type === 'success' ? 'bi-check-circle-fill' : type === 'danger' ? 'bi-exclamation-circle-fill' : 'bi-info-circle-fill';

  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 shadow-lg" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center gap-2">
          <i class="bi ${iconClass} fs-5"></i>
          <div>
            ${title ? `<strong class="d-block">${title}</strong>` : ''}
            <span>${message}</span>
          </div>
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;

  container.insertAdjacentHTML('beforeend', toastHtml);
  const toastEl = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastEl, { delay: 3500 });
  toast.show();

  toastEl.addEventListener('hidden.bs.toast', () => {
    toastEl.remove();
  });
}
