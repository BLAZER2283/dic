<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>DIC Analyzer</h1>
      <p>Автоматизация расчёта оптимальных параметров цифровой корреляции изображений</p>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p style="margin-top: 12px">Загрузка...</p>
    </div>

    <div v-else-if="error" class="error-box">
      <strong>Ошибка:</strong> {{ error }}
    </div>

    <div v-else-if="!stats || stats.overview.total === 0" class="empty-state">
      <p>Пока нет анализов. Создайте первый!</p>
      <p style="font-size: 12px; margin-top: 8px; color: #6b5e4a;">Загрузите изображения и получите результаты анализа</p>
    </div>

    <div v-else class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Всего анализов</div>
        <div class="kpi-value">{{ stats.overview.total }}</div>
        <div class="kpi-sub">выполнено</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">Завершено</div>
        <div class="kpi-value text-green">{{ stats.overview.completed }}</div>
        <div class="kpi-sub">успешно</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">В процессе</div>
        <div class="kpi-value text-yellow">{{ stats.overview.processing }}</div>
        <div class="kpi-sub">обрабатывается</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">Ошибки</div>
        <div class="kpi-value text-red">{{ stats.overview.error }}</div>
        <div class="kpi-sub">требуют внимания</div>
      </div>
    </div>

    <div v-if="stats && stats.overview.total > 0" class="actions">
      <button @click="$router.push('/analyses/create')" class="btn-primary">
        Новый анализ
      </button>
      <button @click="$router.push('/analyses')" class="btn-secondary">
        Все анализы
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
    
    if (Array.isArray(response.data)) {
      analyses.value = response.data
    } else if (response.data.results) {
      analyses.value = response.data.results
    } else {
      analyses.value = []
    }
  } catch (err: any) {
    error.value = err.message || 'Ошибка загрузки данных'
    analyses.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
}

.dashboard-header {
  margin-bottom: 24px;
  padding: 1.5rem 0 1rem;
  border-bottom: 2px solid #b8aa95;
}

.dashboard-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
}

.dashboard-header p {
  font-size: 1rem;
  color: #6b5e4a;
  font-weight: 400;
}

.loading, .error, .empty-state {
  text-align: center;
  padding: 40px 20px;
  margin: 20px 0;
  background: #f0ebe0;
  border: 1px solid #b8aa95;
}

.spinner {
  display: inline-block;
  width: 2rem;
  height: 2rem;
  border: 3px solid #d4c9b8;
  border-top-color: #2c2c2c;
  border-radius: 0;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-box {
  background: #fee2e2;
  border: 1px solid #b88a8a;
  color: #5c2e2e;
  padding: 12px;
  margin-bottom: 16px;
  font-weight: 600;
}

.empty-state {
  color: #6b5e4a;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin: 24px 0;
}

@media (min-width: 768px) {
  .kpi-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.kpi-card {
  background: #fffdf9;
  border: 1px solid #b8aa95;
  padding: 16px;
}

.kpi-label {
  font-size: 0.75rem;
  color: #6b5e4a;
  margin-bottom: 8px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.kpi-value {
  font-size: 2rem;
  font-weight: 700;
  color: #2c2c2c;
}

.kpi-sub {
  font-size: 0.7rem;
  color: #8b7a62;
  margin-top: 4px;
}

.text-green { color: #3d6b3d; }
.text-yellow { color: #9e7b3e; }
.text-red { color: #8b3a3a; }

.actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  flex-wrap: wrap;
}

.btn-primary, .btn-secondary {
  padding: 12px 24px;
  border: none;
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
}

.btn-primary {
  background: #2c2c2c;
  color: #f0ebe0;
}

.btn-primary:hover {
  background: #1a1a1a;
}

.btn-secondary {
  background: #d4c9b8;
  color: #2c2c2c;
  border: 1px solid #b8aa95;
}

.btn-secondary:hover {
  background: #c4b8a5;
}
</style>

