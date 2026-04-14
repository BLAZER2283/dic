<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <p>Welcome to DIC Analyzer Dashboard!</p>

    <div v-if="loading" class="loading">
      <p>Загрузка статистики...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="!stats || stats.overview.total === 0" class="empty-state">
      <p>Пока нет анализов. Создайте первый!</p>
      <button @click="$router.push('/analyses/create')" class="btn-primary">
        Create New Analysis
      </button>
    </div>

    <div v-else class="stats-grid">
      <div class="stat-card">
        <h3>Total Tasks</h3>
        <div class="stat-number">{{ stats.overview.total }}</div>
      </div>

      <div class="stat-card">
        <h3>Completed</h3>
        <div class="stat-number">{{ stats.overview.completed }}</div>
      </div>

      <div class="stat-card">
        <h3>Processing</h3>
        <div class="stat-number">{{ stats.overview.processing }}</div>
      </div>

      <div class="stat-card">
        <h3>Errors</h3>
        <div class="stat-number">{{ stats.overview.error }}</div>
      </div>
    </div>

    <div v-if="stats && stats.overview.total > 0" class="actions">
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
import { ref, onMounted, computed } from 'vue'
import { apiService } from '@/services/api'
import type { DICAnalysis } from '@/types/api'

const analyses = ref<DICAnalysis[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const stats = computed(() => {
  const total = analyses.value.length
  const completed = analyses.value.filter(a => a.status === 'completed').length
  const processing = analyses.value.filter(a => a.status === 'processing').length
  const pending = analyses.value.filter(a => a.status === 'pending').length
  const errors = analyses.value.filter(a => a.status === 'error').length
  const cancelled = analyses.value.filter(a => a.status === 'cancelled').length
  
  return {
    overview: {
      total,
      completed,
      processing,
      pending,
      error: errors,
      cancelled,
      success_rate: total > 0 ? Math.round((completed / total) * 100) : 0
    }
  }
})

onMounted(async () => {
  try {
    loading.value = true
    const response = await apiService.getAnalyses({ page_size: 1000 })
    console.log('API Response:', response.data)
    
    // API может возвращать массив или объект { results: [...] }
    if (Array.isArray(response.data)) {
      analyses.value = response.data
    } else if (response.data.results) {
      analyses.value = response.data.results
    } else {
      analyses.value = []
    }
    
    console.log('Analyses count:', analyses.value.length)
    console.log('First analysis:', analyses.value[0])
  } catch (err: any) {
    console.error('Failed to fetch analyses:', err)
    error.value = 'Не удалось загрузить данные: ' + (err.message || err)
    analyses.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.loading, .error, .empty-state {
  text-align: center;
  padding: 40px 20px;
  margin: 20px 0;
  background: #f5f5f5;
  border-radius: 8px;
}

.error {
  color: #d32f2f;
  background: #ffebee;
}

.empty-state {
  color: #666;
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

