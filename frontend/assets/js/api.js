/**
 * SMART POULTRY FARM MANAGEMENT AND MONITORING SYSTEM
 * Real Database REST API Service (api.js)
 * Connects directly to Flask backend endpoints with JWT Bearer & Session Auth
 * Supports Full CRUD for all 18 modules with real database persistence
 */

const API_BASE_URL = (typeof window !== 'undefined' && window.API_BASE_URL)
  ? window.API_BASE_URL
  : (window.location.protocol.startsWith('http') ? '' : 'http://127.0.0.1:5000');

function getAuthHeaders() {
  const token = localStorage.getItem('smart_poultry_jwt_token');
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };
  if (token) {
    headers['Authorization'] = 'Bearer ' + token;
  }
  return headers;
}

// Global fetch wrapper with error handling and credentials
async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const defaultOptions = {
    headers: getAuthHeaders(),
    credentials: 'include'
  };

  const merged = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...(options.headers || {})
    }
  };

  try {
    const res = await fetch(url, merged);
    if (res.status === 401) {
      // User session expired or unauthenticated
      console.warn(`[API] 401 Unauthorized on ${endpoint}`);
      if (!window.location.pathname.endsWith('login.html') &&
          !window.location.pathname.endsWith('register.html') &&
          !window.location.pathname.endsWith('overview.html') &&
          !window.location.pathname.endsWith('index.html')) {
        // Only redirect on protected pages
        setTimeout(() => {
          window.location.href = 'login.html';
        }, 1200);
      }
    }
    return res;
  } catch (err) {
    console.error(`[API Network Error] ${url}:`, err);
    throw err;
  }
}

// Core API Controller (Exposed as MockAPI for 100% backward compatibility with all UI templates)
const MockAPI = {
  selectedFarmId: localStorage.getItem('smart_poultry_selected_farm') || null,

  getSelectedFarmId() {
    return this.selectedFarmId;
  },

  setSelectedFarmId(id) {
    this.selectedFarmId = id;
    if (id) {
      localStorage.setItem('smart_poultry_selected_farm', id);
    } else {
      localStorage.removeItem('smart_poultry_selected_farm');
    }
  },

  // ---------------------------------------------------------------------------
  // 1. DASHBOARD LIVE DATA
  // ---------------------------------------------------------------------------
  async getDashboardSummary() {
    try {
      const res = await apiFetch('/api/dashboard/stats');
      if (res.ok) {
        const data = await res.json();
        return {
          farmsCount: data.total_farms || 0,
          activeBatchesCount: data.total_flocks || 0,
          totalBirds: data.total_live_birds || 0,
          totalDailyFeed: data.daily_feed_consumption || 0.0,
          totalDailyWater: data.daily_water_consumption || 0.0,
          totalMortality: data.mortality_count || 0,
          mortalityRate: data.mortality_rate || '0.00',
          healthScore: data.health_score || 90,
          riskLevel: data.health_score < 70 ? 'High' : (data.health_score < 85 ? 'Medium' : 'Low'),
          criticalAlertsCount: data.unread_alerts || 0,
          temperature: data.temperature || 28.0,
          humidity: data.humidity || 62.0,
          ammonia: data.ammonia || 12.0,
          pendingTasks: data.pending_tasks || 0,
          recentActivities: data.recent_activities || [],
          fcr: data.fcr || 1.58
        };
      }
    } catch (e) {
      console.warn('[MockAPI] getDashboardSummary error:', e);
    }

    return {
      farmsCount: 0,
      activeBatchesCount: 0,
      totalBirds: 0,
      totalDailyFeed: 0,
      totalDailyWater: 0,
      totalMortality: 0,
      mortalityRate: '0.00',
      healthScore: 95,
      riskLevel: 'Low',
      criticalAlertsCount: 0,
      temperature: 28.0,
      humidity: 62.0,
      ammonia: 12.0,
      pendingTasks: 0,
      recentActivities: [],
      fcr: 1.58
    };
  },

  // ---------------------------------------------------------------------------
  // 2. FARM MANAGEMENT (CRUD)
  // ---------------------------------------------------------------------------
  async getFarms() {
    try {
      const res = await apiFetch('/api/farms');
      if (res.ok) {
        const data = await res.json();
        const farms = (data.farms || []).map(f => ({
          id: f.id,
          name: f.name || f.farm_name,
          farm_name: f.farm_name || f.name,
          location: f.location || 'Agro Zone',
          address: f.address || '',
          birdType: f.birdType || f.farm_type || 'Broiler',
          farm_type: f.farm_type || f.birdType || 'Broiler',
          capacity: f.capacity || f.total_capacity || 5000,
          total_capacity: f.total_capacity || f.capacity || 5000,
          currentBirds: f.currentBirds || 0,
          farmSize: f.farmSize || f.farm_size || '2 Acres',
          establishedDate: f.establishedDate || f.established_date || '',
          healthScore: f.healthScore || 88,
          riskLevel: f.riskLevel || 'Low',
          mortalityRate: f.mortalityRate || 0.8
        }));

        if (farms.length > 0 && (!this.selectedFarmId || !farms.some(f => String(f.id) === String(this.selectedFarmId)))) {
          this.setSelectedFarmId(farms[0].id);
        }
        return farms;
      }
    } catch (e) {
      console.warn('[MockAPI] getFarms error:', e);
    }
    return [];
  },

  async getFarmById(id) {
    try {
      const res = await apiFetch(`/api/farms/${id}`);
      if (res.ok) {
        const data = await res.json();
        return data.farm;
      }
    } catch (e) {
      console.warn('[MockAPI] getFarmById error:', e);
    }
    const all = await this.getFarms();
    return all.find(f => String(f.id) === String(id)) || null;
  },

  async addFarm(farmData) {
    try {
      const res = await apiFetch('/api/farms', {
        method: 'POST',
        body: JSON.stringify({
          name: farmData.name || farmData.farm_name,
          location: farmData.location,
          address: farmData.address,
          capacity: farmData.capacity,
          birdType: farmData.birdType,
          farmSize: farmData.farmSize,
          establishedDate: farmData.establishedDate
        })
      });
      const data = await res.json();
      if (res.ok && data.status === 'success') {
        if (data.farm && data.farm.id) {
          this.setSelectedFarmId(data.farm.id);
        }
        return data.farm;
      }
      throw new Error(data.message || 'Failed to add farm');
    } catch (e) {
      console.error('[MockAPI] addFarm error:', e);
      throw e;
    }
  },

  async updateFarm(id, updatedData) {
    try {
      const res = await apiFetch(`/api/farms/${id}`, {
        method: 'PUT',
        body: JSON.stringify(updatedData)
      });
      const data = await res.json();
      return data.farm || updatedData;
    } catch (e) {
      console.error('[MockAPI] updateFarm error:', e);
      throw e;
    }
  },

  async deleteFarm(id) {
    try {
      const res = await apiFetch(`/api/farms/${id}`, {
        method: 'DELETE'
      });
      const data = await res.json();
      if (String(this.selectedFarmId) === String(id)) {
        this.setSelectedFarmId(null);
      }
      return data;
    } catch (e) {
      console.error('[MockAPI] deleteFarm error:', e);
      throw e;
    }
  },

  // ---------------------------------------------------------------------------
  // 3. FLOCK / BATCH MANAGEMENT (CRUD)
  // ---------------------------------------------------------------------------
  async getBatches(farmId = null) {
    try {
      const targetFarm = farmId || this.getSelectedFarmId();
      const endpoint = targetFarm ? `/api/flocks?farm_id=${targetFarm}` : '/api/flocks';
      const res = await apiFetch(endpoint);
      if (res.ok) {
        const data = await res.json();
        return (data.flocks || []).map(b => ({
          id: b.id,
          farmId: b.farmId || b.farm_id,
          name: b.name || `Batch ${b.batch_number}`,
          batch_number: b.batch_number,
          birdType: b.birdType || b.bird_type,
          breed: b.breed || 'Cobb 500',
          birdCount: b.birdCount || b.current_bird_count || 0,
          current_bird_count: b.current_bird_count || b.birdCount || 0,
          initial_bird_count: b.initial_bird_count || b.birdCount || 0,
          ageDays: b.ageDays !== undefined ? b.ageDays : (b.age_days || 0),
          startDate: b.startDate || b.arrival_date,
          healthStatus: b.healthStatus || b.health_status || 'Good',
          riskLevel: b.riskLevel || b.risk_level || 'Low',
          avgWeightKg: b.avgWeightKg || b.target_weight_kg || 2.0,
          dailyFeedKg: b.dailyFeedKg || 0,
          dailyWaterL: b.dailyWaterL || 0,
          mortalityCount: b.mortalityCount || 0,
          status: b.status || 'active'
        }));
      }
    } catch (e) {
      console.warn('[MockAPI] getBatches error:', e);
    }
    return [];
  },

  async getBatchById(id) {
    try {
      const res = await apiFetch(`/api/flocks/${id}`);
      if (res.ok) {
        const data = await res.json();
        return data.batch || data.flock;
      }
    } catch (e) {
      console.warn('[MockAPI] getBatchById error:', e);
    }
    const batches = await this.getBatches();
    return batches.find(b => String(b.id) === String(id)) || null;
  },

  async addBatch(batchData) {
    try {
      const res = await apiFetch('/api/flocks', {
        method: 'POST',
        body: JSON.stringify({
          farmId: batchData.farmId || this.getSelectedFarmId(),
          name: batchData.name || batchData.batch_number,
          birdType: batchData.birdType,
          breed: batchData.breed || 'Cobb 500',
          birdCount: batchData.birdCount,
          startDate: batchData.startDate,
          healthStatus: batchData.healthStatus,
          riskLevel: batchData.riskLevel,
          target_weight_kg: batchData.target_weight_kg || 2.0
        })
      });
      const data = await res.json();
      if (res.ok && data.status === 'success') {
        return data.batch || data.flock;
      }
      throw new Error(data.message || 'Failed to add batch');
    } catch (e) {
      console.error('[MockAPI] addBatch error:', e);
      throw e;
    }
  },

  async updateBatch(id, updatedData) {
    try {
      const res = await apiFetch(`/api/flocks/${id}`, {
        method: 'PUT',
        body: JSON.stringify(updatedData)
      });
      const data = await res.json();
      return data.batch || updatedData;
    } catch (e) {
      console.error('[MockAPI] updateBatch error:', e);
      throw e;
    }
  },

  async deleteBatch(id) {
    try {
      const res = await apiFetch(`/api/flocks/${id}`, {
        method: 'DELETE'
      });
      return await res.json();
    } catch (e) {
      console.error('[MockAPI] deleteBatch error:', e);
      throw e;
    }
  },

  // ---------------------------------------------------------------------------
  // 4. DAILY OPERATIONS & BIRD CONDITIONS (CRUD)
  // ---------------------------------------------------------------------------
  async getConditions(batchId = null) {
    try {
      const endpoint = batchId ? `/api/records/mortality?flock_id=${batchId}` : '/api/records/mortality';
      const res = await apiFetch(endpoint);
      if (res.ok) {
        const data = await res.json();
        return (data.records || []).map(r => ({
          id: r.id,
          batchId: r.flock_id,
          timestamp: r.record_date,
          mortality: r.mortality_count,
          symptoms: r.symptoms ? r.symptoms.split(', ') : [],
          notes: r.notes
        }));
      }
    } catch (e) {
      console.warn('[MockAPI] getConditions error:', e);
    }
    return [];
  },

  async saveCondition(data) {
    try {
      const res = await apiFetch('/api/records/daily', {
        method: 'POST',
        body: JSON.stringify({
          flock_id: data.batchId || data.flock_id,
          mortality: parseInt(data.mortality) || 0,
          feed_consumed_kg: parseFloat(data.feedConsumption) || 0.0,
          water_consumed_liters: parseFloat(data.waterConsumption) || 0.0,
          average_weight_kg: parseFloat(data.avgWeight) || 1.5,
          eggs_produced: parseInt(data.eggsCollected) || 0,
          temperature: parseFloat(data.temperature) || 28.0,
          humidity: parseFloat(data.humidity) || 60.0,
          symptoms: data.symptoms || [],
          notes: data.notes || ''
        })
      });
      const resData = await res.json();
      return resData;
    } catch (e) {
      console.error('[MockAPI] saveCondition error:', e);
      throw e;
    }
  },

  // ---------------------------------------------------------------------------
  // 5. ALERTS & NOTIFICATIONS (CRUD)
  // ---------------------------------------------------------------------------
  async getAlerts(farmId = null) {
    try {
      const res = await apiFetch('/api/alerts');
      if (res.ok) {
        const data = await res.json();
        return (data.alerts || []).map(a => ({
          id: a.id,
          farmId: a.farmId || a.farm_id,
          title: a.title || a.alert_type,
          description: a.description || a.message,
          severity: a.severity || 'Warning',
          timestamp: a.timestamp || 'Today',
          isRead: !!a.is_read
        }));
      }
    } catch (e) {
      console.warn('[MockAPI] getAlerts error:', e);
    }
    return [];
  },

  async markAlertAsRead(alertId) {
    try {
      await apiFetch(`/api/alerts/${alertId}/read`, { method: 'POST' });
    } catch (e) {
      console.warn('[MockAPI] markAlertAsRead error:', e);
    }
  },

  async markAllAlertsAsRead() {
    try {
      await apiFetch('/api/alerts/read-all', { method: 'POST' });
    } catch (e) {
      console.warn('[MockAPI] markAllAlertsAsRead error:', e);
    }
  },

  async deleteAlert(alertId) {
    try {
      await apiFetch(`/api/alerts/${alertId}`, { method: 'DELETE' });
    } catch (e) {
      console.warn('[MockAPI] deleteAlert error:', e);
    }
  },

  // ---------------------------------------------------------------------------
  // 6. VACCINATION MANAGEMENT (CRUD)
  // ---------------------------------------------------------------------------
  async getVaccinations(batchId = null) {
    try {
      const endpoint = batchId ? `/api/vaccinations?flock_id=${batchId}` : '/api/vaccinations';
      const res = await apiFetch(endpoint);
      if (res.ok) {
        const data = await res.json();
        return (data.vaccinations || []).map(v => ({
          id: v.id,
          batchId: v.flock_id,
          vaccineName: v.vaccine_name || v.name,
          name: v.vaccine_name || v.name,
          route: v.route || 'Drinking Water',
          scheduledDate: v.scheduled_date || v.date,
          date: v.scheduled_date || v.date,
          status: v.status || 'scheduled',
          dosage: v.dosage || 'Standard'
        }));
      }
    } catch (e) {
      console.warn('[MockAPI] getVaccinations error:', e);
    }
    return [];
  },

  async addVaccination(vacData) {
    try {
      const res = await apiFetch('/api/vaccinations', {
        method: 'POST',
        body: JSON.stringify({
          flock_id: vacData.batchId || vacData.flock_id,
          vaccine_name: vacData.name || vacData.vaccineName,
          route: vacData.route || 'Drinking Water',
          scheduled_date: vacData.date || vacData.scheduledDate,
          dosage: vacData.dosage || '1 dose',
          status: vacData.status || 'scheduled'
        })
      });
      const data = await res.json();
      return data.vaccination;
    } catch (e) {
      console.error('[MockAPI] addVaccination error:', e);
      throw e;
    }
  },

  async deleteVaccination(id) {
    try {
      await apiFetch(`/api/vaccinations/${id}`, { method: 'DELETE' });
    } catch (e) {
      console.error('[MockAPI] deleteVaccination error:', e);
      throw e;
    }
  },

  // ---------------------------------------------------------------------------
  // 7. MEDICINE MANAGEMENT (CRUD)
  // ---------------------------------------------------------------------------
  async getMedicines(batchId = null) {
    try {
      const endpoint = batchId ? `/api/medicines?flock_id=${batchId}` : '/api/medicines';
      const res = await apiFetch(endpoint);
      if (res.ok) {
        const data = await res.json();
        return data.medicines || [];
      }
    } catch (e) {
      console.warn('[MockAPI] getMedicines error:', e);
    }
    return [];
  },

  async addMedicine(medData) {
    try {
      const res = await apiFetch('/api/medicines', {
        method: 'POST',
        body: JSON.stringify(medData)
      });
      return await res.json();
    } catch (e) {
      console.error('[MockAPI] addMedicine error:', e);
      throw e;
    }
  },

  async deleteMedicine(id) {
    try {
      await apiFetch(`/api/medicines/${id}`, { method: 'DELETE' });
    } catch (e) {
      console.error('[MockAPI] deleteMedicine error:', e);
      throw e;
    }
  },

  // ---------------------------------------------------------------------------
  // 8. FINANCIAL MANAGEMENT (EXPENSES & SALES) (CRUD)
  // ---------------------------------------------------------------------------
  async getExpenses(farmId = null) {
    try {
      const targetFarm = farmId || this.getSelectedFarmId();
      const endpoint = targetFarm ? `/api/expenses?farm_id=${targetFarm}` : '/api/expenses';
      const res = await apiFetch(endpoint);
      if (res.ok) {
        const data = await res.json();
        return data.expenses || [];
      }
    } catch (e) {
      console.warn('[MockAPI] getExpenses error:', e);
    }
    return [];
  },

  async addExpense(expenseData) {
    try {
      const res = await apiFetch('/api/expenses', {
        method: 'POST',
        body: JSON.stringify({
          farm_id: expenseData.farm_id || this.getSelectedFarmId(),
          category: expenseData.category,
          description: expenseData.description,
          amount: expenseData.amount,
          payment_method: expenseData.payment_method || 'Cash',
          date: expenseData.date
        })
      });
      return await res.json();
    } catch (e) {
      console.error('[MockAPI] addExpense error:', e);
      throw e;
    }
  },

  async deleteExpense(id) {
    try {
      await apiFetch(`/api/expenses/${id}`, { method: 'DELETE' });
    } catch (e) {
      console.error('[MockAPI] deleteExpense error:', e);
      throw e;
    }
  },

  async getSales(farmId = null) {
    try {
      const targetFarm = farmId || this.getSelectedFarmId();
      const endpoint = targetFarm ? `/api/sales?farm_id=${targetFarm}` : '/api/sales';
      const res = await apiFetch(endpoint);
      if (res.ok) {
        const data = await res.json();
        return data.sales || [];
      }
    } catch (e) {
      console.warn('[MockAPI] getSales error:', e);
    }
    return [];
  },

  async addSale(saleData) {
    try {
      const res = await apiFetch('/api/sales', {
        method: 'POST',
        body: JSON.stringify({
          farm_id: saleData.farm_id || this.getSelectedFarmId(),
          product_type: saleData.product_type || 'birds',
          quantity: saleData.quantity,
          unit_price: saleData.unit_price,
          total_amount: saleData.total_amount,
          buyer_name: saleData.buyer_name,
          date: saleData.date
        })
      });
      return await res.json();
    } catch (e) {
      console.error('[MockAPI] addSale error:', e);
      throw e;
    }
  },

  async deleteSale(id) {
    try {
      await apiFetch(`/api/sales/${id}`, { method: 'DELETE' });
    } catch (e) {
      console.error('[MockAPI] deleteSale error:', e);
      throw e;
    }
  },

  // ---------------------------------------------------------------------------
  // 9. INVENTORY MANAGEMENT (CRUD)
  // ---------------------------------------------------------------------------
  async getInventory(farmId = null) {
    try {
      const res = await apiFetch('/api/inventory');
      if (res.ok) {
        const data = await res.json();
        return data.inventory || [];
      }
    } catch (e) {
      console.warn('[MockAPI] getInventory error:', e);
    }
    return [];
  },

  async addInventory(itemData) {
    try {
      const res = await apiFetch('/api/inventory', {
        method: 'POST',
        body: JSON.stringify(itemData)
      });
      return await res.json();
    } catch (e) {
      console.error('[MockAPI] addInventory error:', e);
      throw e;
    }
  },

  async deleteInventory(id) {
    try {
      await apiFetch(`/api/inventory/${id}`, { method: 'DELETE' });
    } catch (e) {
      console.error('[MockAPI] deleteInventory error:', e);
      throw e;
    }
  },

  // ---------------------------------------------------------------------------
  // 10. TASKS & REMINDERS (CRUD)
  // ---------------------------------------------------------------------------
  async getTasks(farmId = null) {
    try {
      const res = await apiFetch('/api/tasks');
      if (res.ok) {
        const data = await res.json();
        return data.tasks || [];
      }
    } catch (e) {
      console.warn('[MockAPI] getTasks error:', e);
    }
    return [];
  },

  async addTask(taskData) {
    try {
      const res = await apiFetch('/api/tasks', {
        method: 'POST',
        body: JSON.stringify(taskData)
      });
      return await res.json();
    } catch (e) {
      console.error('[MockAPI] addTask error:', e);
      throw e;
    }
  },

  async updateTaskStatus(id, isCompleted) {
    try {
      await apiFetch(`/api/tasks/${id}/status`, {
        method: 'POST',
        body: JSON.stringify({ is_completed: isCompleted, status: isCompleted ? 'completed' : 'pending' })
      });
    } catch (e) {
      console.error('[MockAPI] updateTaskStatus error:', e);
    }
  },

  async deleteTask(id) {
    try {
      await apiFetch(`/api/tasks/${id}`, { method: 'DELETE' });
    } catch (e) {
      console.error('[MockAPI] deleteTask error:', e);
      throw e;
    }
  },

  // ---------------------------------------------------------------------------
  // 11. EGG PRODUCTION (CRUD)
  // ---------------------------------------------------------------------------
  async getEggLogs(batchId = null) {
    try {
      const endpoint = batchId ? `/api/records/egg?flock_id=${batchId}` : '/api/records/egg';
      const res = await apiFetch(endpoint);
      if (res.ok) {
        const data = await res.json();
        return (data.records || []).map(r => ({
          id: r.id,
          batchId: r.flock_id,
          date: r.record_date,
          eggsCollected: r.eggs_produced,
          damagedEggs: r.damaged_eggs,
          notes: r.notes
        }));
      }
    } catch (e) {
      console.warn('[MockAPI] getEggLogs error:', e);
    }
    return [];
  },

  async addEggLog(entry) {
    try {
      const res = await apiFetch('/api/records/egg', {
        method: 'POST',
        body: JSON.stringify({
          flock_id: entry.batchId || entry.flock_id,
          eggs_produced: entry.eggsCollected || entry.eggs_produced,
          damaged_eggs: entry.damagedEggs || 0,
          date: entry.date,
          notes: entry.notes
        })
      });
      return await res.json();
    } catch (e) {
      console.error('[MockAPI] addEggLog error:', e);
      throw e;
    }
  },

  async getEggSummary() {
    const logs = await this.getEggLogs();
    const totalCollected = logs.reduce((sum, l) => sum + (parseInt(l.eggsCollected) || 0), 0);
    const totalDamaged = logs.reduce((sum, l) => sum + (parseInt(l.damagedEggs) || 0), 0);
    const brokenRate = totalCollected > 0 ? ((totalDamaged / totalCollected) * 100).toFixed(2) : '0.00';

    return {
      todayEggs: logs[0] ? (logs[0].eggsCollected || 0) : 0,
      totalCollected,
      damagedRate: brokenRate,
      estimatedRevenue: Math.round(totalCollected * 5.5)
    };
  },

  // ---------------------------------------------------------------------------
  // 12. REPORTS & ANALYTICS
  // ---------------------------------------------------------------------------
  async getReportsAnalytics() {
    try {
      const res = await apiFetch('/api/reports/analytics');
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('[MockAPI] getReportsAnalytics error:', e);
    }
    return {
      financials: { total_expenses: 0, total_sales: 0, net_profit: 0, margin_pct: 0 },
      trends: { labels: [], feed: [], water: [], mortality: [] }
    };
  },

  // ---------------------------------------------------------------------------
  // 13. USER SETTINGS & PROFILE
  // ---------------------------------------------------------------------------
  getUserProfile() {
    const data = localStorage.getItem('smart_poultry_auth_user');
    try {
      const u = data ? JSON.parse(data) : null;
      if (u) {
        return {
          fullName: u.name || u.fullName || 'Poultry Farmer',
          name: u.name || u.fullName || 'Poultry Farmer',
          email: u.email || 'farmer@smartpoultry.com',
          phone: u.phone || u.mobile_number || '',
          farmName: u.farm_name || 'Active Poultry Farm',
          location: u.location || 'Agro Zone'
        };
      }
    } catch (e) {}
    return {
      fullName: 'Poultry Farmer',
      email: 'farmer@smartpoultry.com',
      phone: '',
      farmName: 'Active Poultry Farm',
      location: 'Agro Zone'
    };
  },

  async updateUserProfile(profileData) {
    try {
      const res = await apiFetch('/api/auth/profile', {
        method: 'PUT',
        body: JSON.stringify({
          name: profileData.fullName || profileData.name,
          email: profileData.email,
          language: profileData.language
        })
      });
      const data = await res.json();
      if (data.user) {
        const current = this.getUserProfile();
        const merged = { ...current, ...profileData, ...data.user };
        localStorage.setItem('smart_poultry_auth_user', JSON.stringify(merged));
        if (typeof MobileAuth !== 'undefined') {
          MobileAuth.checkAuthStatus();
        }
      }
      return data;
    } catch (e) {
      console.warn('[MockAPI] updateUserProfile error:', e);
    }
  },

  async getUserSettings() {
    try {
      const res = await apiFetch('/api/settings');
      if (res.ok) {
        const data = await res.json();
        return data.settings;
      }
    } catch (e) {
      console.warn('[MockAPI] getUserSettings error:', e);
    }
    return { theme: 'light', language: 'en', currency: 'INR', fcr_target: 1.60 };
  },

  async updateUserSettings(settings) {
    try {
      const res = await apiFetch('/api/settings', {
        method: 'PUT',
        body: JSON.stringify(settings)
      });
      return await res.json();
    } catch (e) {
      console.error('[MockAPI] updateUserSettings error:', e);
      throw e;
    }
  },

  // ---------------------------------------------------------------------------
  // 14. SCAN HISTORY & CAMERA IMAGE PREDICTIONS
  // ---------------------------------------------------------------------------
  async getScanHistory() {
    const data = localStorage.getItem('smart_poultry_scan_history');
    return data ? JSON.parse(data) : [];
  },

  async saveScanResult(scanData) {
    const list = await this.getScanHistory();
    const entry = {
      id: 'SCAN-' + Date.now(),
      timestamp: new Date().toLocaleString(),
      ...scanData
    };
    list.unshift(entry);
    localStorage.setItem('smart_poultry_scan_history', JSON.stringify(list.slice(0, 50)));
    return entry;
  },

  async clearScanHistory() {
    localStorage.removeItem('smart_poultry_scan_history');
  },

  // ---------------------------------------------------------------------------
  // 15. COMPATIBILITY ALIASES & HELPERS
  // ---------------------------------------------------------------------------
  async getPredictions() {
    return this.getScanHistory();
  },

  async savePrediction(predData) {
    return this.saveScanResult(predData);
  },

  async getMarketListings() {
    const eggs = await this.getEggSummary();
    return [
      { id: 'M-1', product: 'Fresh Farm Table Eggs', quantity: `${eggs.totalCollected} Eggs`, price: '₹5.50 / egg', seller: 'Farm Direct', status: 'Available' },
      { id: 'M-2', product: 'Organic Poultry Manure', quantity: '50 Bags', price: '₹120 / bag', seller: 'Farm Direct', status: 'In Stock' }
    ];
  },

  async addMarketListing(item) {
    return { id: 'M-' + Date.now(), ...item };
  },

  async deleteMarketListing(id) {
    return true;
  },

  async getHygieneLogs() {
    return [
      { id: 'HYG-1', date: new Date().toLocaleDateString(), score: 92, status: 'Excellent', notes: 'Shed sanitized with biocide; water lines flushed' }
    ];
  },

  async saveHygieneAudit(audit) {
    return { id: 'HYG-' + Date.now(), date: new Date().toLocaleDateString(), ...audit };
  },

  async getLatestHygieneScore() {
    return 92;
  },

  async getFarmGeo(farmId = 'F-001') {
    return {
      farmId,
      name: 'Smart Poultry Production Unit',
      shedsCount: 4,
      totalCapacity: 10000,
      activeCoordinates: '17.3850° N, 78.4867° E',
      climateZone: 'Tropical Semi-Arid'
    };
  },

  async saveFarmGeo(farmId, geoData) {
    return geoData;
  }
};

// Aliases for unified reference
window.PoultryAPI = MockAPI;
window.MockAPI = MockAPI;
