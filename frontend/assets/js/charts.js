/**
 * SMART POULTRY HEALTH MONITORING & DISEASE-RISK PREDICTION SYSTEM
 * Chart.js Visualizations & Analytics Engine (charts.js)
 */

// Global Chart.js Defaults
if (typeof Chart !== 'undefined') {
  Chart.defaults.font.family = "'Plus Jakarta Sans', 'Inter', sans-serif";
  Chart.defaults.color = '#64748b';
  Chart.defaults.plugins.tooltip.backgroundColor = '#0f172a';
  Chart.defaults.plugins.tooltip.titleColor = '#ffffff';
  Chart.defaults.plugins.tooltip.bodyColor = '#e2e8f0';
  Chart.defaults.plugins.tooltip.padding = 10;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
  Chart.defaults.plugins.tooltip.borderColor = 'rgba(255,255,255,0.1)';
  Chart.defaults.plugins.tooltip.borderWidth = 1;
}

const PoultryCharts = {
  // 1. Dashboard Temperature & Humidity Trend
  initDashboardEnvChart(canvasId = 'dashboardEnvChart') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const labels = ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'];
    const tempData = [23.2, 22.8, 23.5, 25.1, 27.8, 28.2, 26.4, 24.5];
    const humidityData = [68, 70, 67, 62, 55, 53, 59, 64];

    return new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Temperature (°C)',
            data: tempData,
            borderColor: '#f59e0b',
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            fill: true,
            tension: 0.4,
            borderWidth: 2.5,
            pointRadius: 4,
            pointBackgroundColor: '#f59e0b',
            yAxisID: 'y'
          },
          {
            label: 'Humidity (%)',
            data: humidityData,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.06)',
            fill: true,
            tension: 0.4,
            borderWidth: 2.5,
            pointRadius: 4,
            pointBackgroundColor: '#3b82f6',
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { position: 'top', align: 'end', labels: { boxWidth: 12, usePointStyle: true } }
        },
        scales: {
          x: { grid: { color: '#f1f5f9' } },
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            title: { display: true, text: 'Temp (°C)', font: { size: 11, weight: '600' } },
            min: 15,
            max: 35,
            grid: { color: '#f1f5f9' }
          },
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            title: { display: true, text: 'Humidity (%)', font: { size: 11, weight: '600' } },
            min: 30,
            max: 90,
            grid: { drawOnChartArea: false }
          }
        }
      }
    });
  },

  // 2. Monitoring Page - Detailed Sensors & Feeds
  initMonitoringCharts() {
    // Temp & Humidity Chart
    const envCtx = document.getElementById('monitoringEnvTrendChart');
    if (envCtx) {
      new Chart(envCtx, {
        type: 'line',
        data: {
          labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
          datasets: [
            {
              label: 'Avg Temperature (°C)',
              data: [24.2, 24.8, 25.1, 26.5, 27.2, 25.8, 25.0],
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              fill: true,
              tension: 0.4,
              borderWidth: 2.5
            },
            {
              label: 'Target Temp Range (24°C)',
              data: [24, 24, 24, 24, 24, 24, 24],
              borderColor: '#94a3b8',
              borderDash: [5, 5],
              borderWidth: 1.5,
              pointRadius: 0
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top', align: 'end' } },
          scales: {
            y: { min: 20, max: 32, grid: { color: '#f1f5f9' } },
            x: { grid: { color: '#f1f5f9' } }
          }
        }
      });
    }

    // Feed & Water Intake Chart
    const intakeCtx = document.getElementById('monitoringIntakeChart');
    if (intakeCtx) {
      new Chart(intakeCtx, {
        type: 'bar',
        data: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          datasets: [
            {
              type: 'bar',
              label: 'Feed Consumption (kg)',
              data: [420, 435, 440, 410, 460, 450, 455],
              backgroundColor: '#10b981',
              borderRadius: 6,
              yAxisID: 'y'
            },
            {
              type: 'line',
              label: 'Water Intake (L)',
              data: [810, 830, 850, 790, 890, 860, 875],
              borderColor: '#0284c7',
              backgroundColor: 'rgba(2, 132, 199, 0.15)',
              tension: 0.3,
              borderWidth: 2.5,
              yAxisID: 'y1'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top', align: 'end' } },
          scales: {
            y: { title: { display: true, text: 'Feed (kg)' }, grid: { color: '#f1f5f9' } },
            y1: { position: 'right', title: { display: true, text: 'Water (L)' }, grid: { drawOnChartArea: false } },
            x: { grid: { display: false } }
          }
        }
      });
    }

    // Growth Curve vs Benchmark
    const weightCtx = document.getElementById('monitoringWeightGrowthChart');
    if (weightCtx) {
      new Chart(weightCtx, {
        type: 'line',
        data: {
          labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
          datasets: [
            {
              label: 'Actual Flock Weight (kg)',
              data: [0.18, 0.45, 0.92, 1.45, 2.05, 2.65],
              borderColor: '#059669',
              backgroundColor: '#059669',
              borderWidth: 3,
              pointRadius: 5,
              tension: 0.3
            },
            {
              label: 'Breed Standard Benchmark (Cobb 500)',
              data: [0.19, 0.48, 0.95, 1.50, 2.12, 2.70],
              borderColor: '#94a3b8',
              borderDash: [6, 4],
              borderWidth: 2,
              pointRadius: 3
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top', align: 'end' } },
          scales: {
            y: { title: { display: true, text: 'Avg Weight (kg)' }, grid: { color: '#f1f5f9' } },
            x: { grid: { color: '#f1f5f9' } }
          }
        }
      });
    }

    // Mortality Rate Trend Chart
    const mortCtx = document.getElementById('monitoringMortalityChart');
    if (mortCtx) {
      new Chart(mortCtx, {
        type: 'bar',
        data: {
          labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
          datasets: [
            {
              label: 'Daily Bird Mortality',
              data: [1, 2, 0, 1, 3, 2, 1],
              backgroundColor: '#ef4444',
              borderRadius: 4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top', align: 'end' } },
          scales: {
            y: { beginAtZero: true, max: 6, grid: { color: '#f1f5f9' } },
            x: { grid: { display: false } }
          }
        }
      });
    }
  },

  // 3. Reports Page Analytics
  initReportsCharts() {
    // Disease Risk Trend Distribution Doughnut
    const riskCtx = document.getElementById('reportsRiskDistChart');
    if (riskCtx) {
      new Chart(riskCtx, {
        type: 'doughnut',
        data: {
          labels: ['Low Risk (Healthy)', 'Medium Risk (Monitor)', 'High Risk (Action Needed)'],
          datasets: [{
            data: [72, 22, 6],
            backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
            borderWidth: 2,
            borderColor: '#ffffff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { boxWidth: 14, padding: 16 } }
          },
          cutout: '70%'
        }
      });
    }

    // Comprehensive Population & Mortality Multi-Axis
    const popCtx = document.getElementById('reportsPopulationTrendChart');
    if (popCtx) {
      new Chart(popCtx, {
        type: 'line',
        data: {
          labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
          datasets: [
            {
              label: 'Active Flock Count',
              data: [5000, 4985, 4968, 4952, 4938, 4920],
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.08)',
              fill: true,
              tension: 0.2,
              yAxisID: 'y'
            },
            {
              label: 'Cumulative Mortality %',
              data: [0.3, 0.6, 0.9, 1.1, 1.3, 1.6],
              borderColor: '#ef4444',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              tension: 0.2,
              yAxisID: 'y1'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top', align: 'end' } },
          scales: {
            y: { title: { display: true, text: 'Total Birds' }, min: 4800, max: 5100, grid: { color: '#f1f5f9' } },
            y1: { position: 'right', title: { display: true, text: 'Mortality %' }, min: 0, max: 3, grid: { drawOnChartArea: false } },
            x: { grid: { color: '#f1f5f9' } }
          }
        }
      });
    }

    // Feed Conversion Ratio (FCR) Trend
    const fcrCtx = document.getElementById('reportsFCRChart');
    if (fcrCtx) {
      new Chart(fcrCtx, {
        type: 'line',
        data: {
          labels: ['Batch 1', 'Batch 2', 'Batch 3', 'Batch 4', 'Batch 5 (Current)'],
          datasets: [
            {
              label: 'Feed Conversion Ratio (FCR)',
              data: [1.62, 1.58, 1.55, 1.52, 1.48],
              borderColor: '#6366f1',
              backgroundColor: 'rgba(99, 102, 241, 0.12)',
              fill: true,
              borderWidth: 2.5,
              tension: 0.3,
              pointRadius: 5
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top', align: 'end' } },
          scales: {
            y: { title: { display: true, text: 'FCR (kg feed / kg gain)' }, min: 1.3, max: 1.8, grid: { color: '#f1f5f9' } },
            x: { grid: { display: false } }
          }
        }
      });
    }
  },

  // 4. Admin Dashboard Platform Analytics
  initAdminCharts() {
    // Farms by Location (Bar)
    const locCtx = document.getElementById('adminFarmsByLocationChart');
    if (locCtx) {
      new Chart(locCtx, {
        type: 'bar',
        data: {
          labels: ['Punjab Zone', 'Haryana Belt', 'Maharashtra', 'Andhra Pradesh', 'Tamil Nadu', 'Karnataka'],
          datasets: [{
            label: 'Registered Farms',
            data: [94, 78, 62, 45, 38, 23],
            backgroundColor: '#10b981',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { grid: { color: '#f1f5f9' } },
            x: { grid: { display: false } }
          }
        }
      });
    }

    // Monthly AI Predictions Volume (Area)
    const predVolCtx = document.getElementById('adminPredictionVolumeChart');
    if (predVolCtx) {
      new Chart(predVolCtx, {
        type: 'line',
        data: {
          labels: ['Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
          datasets: [
            {
              label: 'CV Image Inferences',
              data: [1200, 1850, 2400, 3100, 4200, 5450],
              borderColor: '#0284c7',
              backgroundColor: 'rgba(2, 132, 199, 0.12)',
              fill: true,
              tension: 0.4
            },
            {
              label: 'Condition ML Predictions',
              data: [2100, 2900, 3800, 4900, 6200, 8100],
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.12)',
              fill: true,
              tension: 0.4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top', align: 'end' } },
          scales: {
            y: { grid: { color: '#f1f5f9' } },
            x: { grid: { color: '#f1f5f9' } }
          }
        }
      });
    }

    // Risk Distribution Pie
    const adminRiskCtx = document.getElementById('adminRiskDistributionChart');
    if (adminRiskCtx) {
      new Chart(adminRiskCtx, {
        type: 'pie',
        data: {
          labels: ['Low Risk (Healthy)', 'Medium Risk (Monitor)', 'High Risk (Critical Alert)'],
          datasets: [{
            data: [248, 78, 14],
            backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' } }
        }
      });
    }
  }
};
