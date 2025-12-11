<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <p>Welcome to DIC Analyzer Dashboard!</p>

    <div class="stats-grid">
      <div class="stat-card">
        <h3>Total Tasks</h3>
        <div class="stat-number">{{ stats?.overview?.total || 0 }}</div>
      </div>

      <div class="stat-card">
        <h3>Completed</h3>
        <div class="stat-number">{{ stats?.overview?.completed || 0 }}</div>
      </div>

      <div class="stat-card">
        <h3>Processing</h3>
        <div class="stat-number">{{ stats?.overview?.processing || 0 }}</div>
      </div>

      <div class="stat-card">
        <h3>Errors</h3>
        <div class="stat-number">{{ stats?.overview?.error || 0 }}</div>
      </div>
    </div>

    <div class="actions">
      <button @click="$router.push('/analyses/create')" class="btn-primary">
        Create New Analysis
      </button>
      <button @click="$router.push('/analyses')" class="btn-secondary">
        View All Analyses
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const stats = ref(null)

onMounted(() => {
  console.log('Dashboard component mounted successfully!')
  // Временно отключим API запросы для тестирования
  stats.value = {
    overview: {
      total: 5,
      completed: 3,
      processing: 1,
      pending: 0,
      error: 1,
      cancelled: 0,
      success_rate: 60
    },
    processing_stats: {
      avg_processing_time: 45.2,
      total_processing_time: 135.6
    },
    deformation_stats: {
      avg_max_displacement: 0.023,
      avg_mean_displacement: 0.015
    },
    recent_tasks: [],
    timeline: {
      last_24_hours: 2,
      last_week: 5,
      last_month: 12
    }
  }
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin: 30px 0;
}

.stat-card {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-card h3 {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat-number {
  font-size: 2.5em;
  font-weight: bold;
  color: #1976D2;
  margin: 0;
}

.actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
  flex-wrap: wrap;
}

.btn-primary, .btn-secondary {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #1976D2;
  color: white;
}

.btn-primary:hover {
  background: #1565C0;
}

.btn-secondary {
  background: #757575;
  color: white;
}

.btn-secondary:hover {
  background: #616161;
}
</style>

