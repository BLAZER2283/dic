<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>DIC Analyzer</h1>
      <p>Автоматизация расчёта оптимальных параметров цифровой корреляции изображений</p>
    </div>

    <div class="page-grid">
      <div class="panel panel--form">
        <v-card>
          <v-card-title class="section-title">
            <v-icon left class="section-icon">mdi-image-outline</v-icon>
            Создать анализ
          </v-card-title>
          <v-card-text class="pa-6">
            <v-form ref="form" v-model="valid">
              <div class="form-group">
                <label>Название анализа</label>
                <v-text-field
                  v-model="formData.name"
                  placeholder="Введите название"
                  variant="outlined"
                  density="compact"
                  hide-details
                  :rules="[rules.required]"
                  class="mb-4"
                />
              </div>

              <v-row>
                <v-col cols="12" md="6">
                  <div class="upload-card" :class="{ 'upload-card--active': dragOver.before }"
                    @dragover.prevent="dragOver.before = true"
                    @dragleave.prevent="dragOver.before = false"
                    @drop.prevent="handleDrop('before', $event)">
                    <div v-if="!formData.image_before">
                      <div class="upload-icon">📷</div>
                      <div class="upload-title">Эталонное изображение</div>
                      <div class="upload-subtitle">До деформации</div>
                      <v-btn
                        variant="outlined"
                        @click="openInput('before')"
                        class="btn-upload"
                      >
                        Выбрать файл
                      </v-btn>
                      <div class="upload-hint">или перетащите сюда</div>
                    </div>
                    <div v-else class="image-preview">
                      <v-img :src="beforePreview" max-height="200" contain class="mb-4" />
                      <div class="file-name">{{ formData.image_before.name }}</div>
                      <v-btn size="small" variant="outlined" color="error" @click="removeImage('before')">
                        Удалить
                      </v-btn>
                    </div>
                    <input id="before-file-input" type="file" accept="image/*" @change="handleFileSelect('before', $event)" style="display: none" />
                  </div>
                </v-col>

                <v-col cols="12" md="6">
                  <div class="upload-card" :class="{ 'upload-card--active': dragOver.after }"
                    @dragover.prevent="dragOver.after = true"
                    @dragleave.prevent="dragOver.after = false"
                    @drop.prevent="handleDrop('after', $event)">
                    <div v-if="!formData.image_after">
                      <div class="upload-icon">📷</div>
                      <div class="upload-title">Деформированное изображение</div>
                      <div class="upload-subtitle">После деформации</div>
                      <v-btn
                        variant="outlined"
                        @click="openInput('after')"
                        class="btn-upload"
                      >
                        Выбрать файл
                      </v-btn>
                      <div class="upload-hint">или перетащите сюда</div>
                    </div>
                    <div v-else class="image-preview">
                      <v-img :src="afterPreview" max-height="200" contain class="mb-4" />
                      <div class="file-name">{{ formData.image_after.name }}</div>
                      <v-btn size="small" variant="outlined" color="error" @click="removeImage('after')">
                        Удалить
                      </v-btn>
                    </div>
                    <input id="after-file-input" type="file" accept="image/*" @change="handleFileSelect('after', $event)" style="display: none" />
                  </div>
                </v-col>
              </v-row>

              <div class="section-divider"></div>

              <div class="form-section">
                <div class="section-title-sm">Информация о образце</div>
                <v-row>
                  <v-col cols="12" md="6">
                    <label class="field-label">Название</label>
                    <v-text-field v-model="formData.sample_name" placeholder="Название образца" variant="outlined" density="compact" hide-details />
                  </v-col>
                  <v-col cols="12" md="6">
                    <label class="field-label">Материал</label>
                    <v-text-field v-model="formData.material" placeholder="Материал" variant="outlined" density="compact" hide-details />
                  </v-col>
                  <v-col cols="12" md="6">
                    <label class="field-label">Производитель</label>
                    <v-text-field v-model="formData.manufacture" placeholder="Производитель" variant="outlined" density="compact" hide-details />
                  </v-col>
                  <v-col cols="12" md="6">
                    <label class="field-label">Дата испытания</label>
                    <v-text-field v-model="formData.test_date" type="date" variant="outlined" density="compact" hide-details />
                  </v-col>
                </v-row>
              </div>

              <div class="section-divider"></div>

              <div class="form-section">
                <div class="section-title-sm">Параметры анализа</div>
                <v-row>
                  <v-col cols="12" md="4">
                    <label class="field-label">Размер подмножества</label>
                    <v-text-field v-model.number="formData.subset_size" type="number" variant="outlined" density="compact" hide-details :rules="[rules.subsetSize]" />
                  </v-col>
                  <v-col cols="12" md="4">
                    <label class="field-label">Шаг</label>
                    <v-text-field v-model.number="formData.step" type="number" variant="outlined" density="compact" hide-details />
                  </v-col>
                  <v-col cols="12" md="4">
                    <label class="field-label">Макс. итераций</label>
                    <v-text-field v-model.number="formData.max_iter" type="number" variant="outlined" density="compact" hide-details />
                  </v-col>
                  <v-col cols="12" md="4">
                    <label class="field-label">Мин. корреляция</label>
                    <v-text-field v-model.number="formData.min_correlation" type="number" step="0.01" variant="outlined" density="compact" hide-details />
                  </v-col>
                </v-row>
              </div>

              <div class="form-actions">
                <v-btn variant="outlined" @click="resetForm" :disabled="creating" class="btn-secondary">
                  Сбросить
                </v-btn>
                <v-btn
                  color="primary"
                  @click="submitForm"
                  :loading="creating"
                  :disabled="!valid || !formData.image_before || !formData.image_after"
                  class="btn-primary"
                >
                  Начать анализ
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </div>

      <div class="panel panel--list">
        <div class="panel-header">
          <div>
            <h2>Последние анализы</h2>
            <p>На основной странице отображается список анализов и статистика.</p>
          </div>
          <v-btn variant="outlined" class="btn-secondary" @click="refreshAnalyses" :loading="analysisStore.loading">
            Обновить
          </v-btn>
        </div>

        <div class="kpi-grid stats-grid">
          <div class="kpi-card">
            <div class="kpi-label">Всего</div>
            <div class="kpi-value">{{ stats.overview.total }}</div>
            <div class="kpi-sub">анализов</div>
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

        <div class="analysis-list-panel">
          <template v-if="analysisStore.loading">
            <div class="loading-panel">
              <div class="spinner"></div>
              <div class="loading-text">Загрузка анализов...</div>
            </div>
          </template>

          <template v-else-if="latestAnalyses.length === 0">
            <div class="empty-panel">
              <p>Список анализов пуст. Создайте первый анализ слева.</p>
            </div>
          </template>

          <template v-else>
            <div class="analysis-list-items">
              <div
                v-for="analysis in latestAnalyses"
                :key="analysis.id"
                class="analysis-item"
                @click="openAnalysis(analysis.id)">
                <div class="analysis-item-top">
                  <div class="analysis-title">{{ analysis.name }}</div>
                  <div :class="['status-chip', getStatusClass(analysis.status)]">{{ analysis.status_display || analysis.status }}</div>
                </div>
                <div class="analysis-item-details">
                  <span>Дата: {{ formatDate(analysis.created_at) }}</span>
                  <span>Время: {{ analysis.processing_time ? analysis.processing_time.toFixed(1) + 's' : '–' }}</span>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import type { DICAnalysis } from '@/types/api'

const router = useRouter()
const analysisStore = useAnalysisStore()

const formData = reactive({
  name: '',
  image_before: null as File | null,
  image_after: null as File | null,
  subset_size: 25,
  step: 12,
  max_iter: 35,
  min_correlation: 0.4,
  sample_name: '',
  material: '',
  manufacture: '',
  test_date: '',
})

const valid = ref(false)
const creating = ref(false)
const beforePreview = ref('')
const afterPreview = ref('')
const dragOver = reactive({ before: false, after: false })
const form = ref<any>(null)

const rules = {
  required: (value: any) => !!value || 'Это поле обязательно',
  subsetSize: (value: number) => {
    if (value < 21 || value > 31) return 'Размер подмножества должен быть от 21 до 31'
    if (value % 2 === 0) return 'Размер подмножества должен быть нечетным'
    return true
  },
}

const stats = computed(() => {
  const list = analysisStore.analyses
  const total = list.length
  const completed = list.filter(item => item.status === 'completed').length
  const processing = list.filter(item => item.status === 'processing').length
  const error = list.filter(item => ['failed', 'error', 'cancelled'].includes(item.status)).length
  const pending = list.filter(item => item.status === 'pending').length

  return {
    overview: {
      total,
      completed,
      processing,
      pending,
      error,
      success_rate: total > 0 ? Math.round((completed / total) * 100) : 0,
    },
  }
})

const latestAnalyses = computed(() => analysisStore.analyses.slice(0, 10))

const getStatusClass = (status: string) => {
  if (!status) return 'status-default'
  if (status === 'completed') return 'status-success'
  if (status === 'processing') return 'status-warning'
  if (['failed', 'error', 'cancelled'].includes(status)) return 'status-danger'
  return 'status-default'
}

const formatDate = (value: string | undefined) => {
  if (!value) return '–'
  return new Date(value).toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' })
}

const openAnalysis = (id: string) => {
  router.push(`/analyses/${id}`)
}

const refreshAnalyses = () => {
  analysisStore.fetchAnalyses(1)
}

const handleFileSelect = (type: 'before' | 'after', event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) setImage(type, file)
}

const handleDrop = (type: 'before' | 'after', event: DragEvent) => {
  dragOver[type] = false
  const file = event.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) setImage(type, file)
}

const setImage = (type: 'before' | 'after', file: File) => {
  if (type === 'before') {
    formData.image_before = file
    createPreview(file, 'before')
  } else {
    formData.image_after = file
    createPreview(file, 'after')
  }
}

const createPreview = (file: File, type: 'before' | 'after') => {
  const reader = new FileReader()
  reader.onload = (e) => {
    if (type === 'before') beforePreview.value = e.target?.result as string
    else afterPreview.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

const removeImage = (type: 'before' | 'after') => {
  if (type === 'before') {
    formData.image_before = null
    beforePreview.value = ''
  } else {
    formData.image_after = null
    afterPreview.value = ''
  }
}

const openInput = (type: 'before' | 'after') => {
  const inputId = type === 'before' ? 'before-file-input' : 'after-file-input'
  const input = document.getElementById(inputId) as HTMLInputElement | null
  input?.click()
}

const resetForm = () => {
  formData.name = ''
  formData.image_before = null
  formData.image_after = null
  formData.subset_size = 25
  formData.step = 12
  formData.max_iter = 35
  formData.min_correlation = 0.4
  formData.sample_name = ''
  formData.material = ''
  formData.manufacture = ''
  formData.test_date = ''
  beforePreview.value = ''
  afterPreview.value = ''
  form.value?.resetValidation()
}

const submitForm = async () => {
  if (!form.value) return
  const isValid = form.value.validate()
  if (!isValid || !formData.image_before || !formData.image_after) return
  creating.value = true
  try {
    await analysisStore.createAnalysis(formData)
    refreshAnalyses()
    resetForm()
  } catch (err) {
    console.error(err)
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  const now = new Date()
  formData.name = `DIC Analysis ${now.toLocaleDateString()} ${now.toLocaleTimeString()}`
  refreshAnalyses()
})
</script>

<style scoped>
.dashboard {
  padding: 1.5rem;
  max-width: 1400px;
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

.page-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

@media (min-width: 1024px) {
  .page-grid {
    grid-template-columns: 0.95fr 1.05fr;
  }
}

.panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title {
  font-size: 0.95rem !important;
  font-weight: 700 !important;
  color: #2c2c2c !important;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #b8aa95;
  padding-bottom: 8px;
}

.section-icon {
  font-size: 18px !important;
  margin-right: 8px;
}

.form-group {
  margin-bottom: 16px;
}

.upload-card {
  background: #fffdf9;
  border: 2px dashed #b8aa95;
  padding: 28px 16px;
  text-align: center;
  min-height: 260px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}

.upload-card--active {
  border-color: #2c2c2c;
  background: #f5f0e5;
}

.upload-icon {
  font-size: 46px;
  margin-bottom: 16px;
}

.upload-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #2c2c2c;
  margin-bottom: 4px;
}

.upload-subtitle,
.file-name,
.upload-hint {
  font-size: 0.78rem;
  color: #6b5e4a;
}

.btn-upload {
  text-transform: uppercase;
  border: 1px solid #b8aa95 !important;
  background: #d4c9b8 !important;
  color: #2c2c2c !important;
}

.section-divider {
  height: 2px;
  background: #b8aa95;
  margin: 24px 0;
}

.form-section {
  margin-bottom: 16px;
}

.field-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  color: #6b5e4a;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  padding: 12px 24px;
  border-radius: 0 !important;
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif !important;
  font-size: 0.85rem !important;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.btn-primary {
  background: #2c2c2c !important;
  color: #f0ebe0 !important;
}

.btn-secondary {
  background: #d4c9b8 !important;
  color: #2c2c2c !important;
  border: 1px solid #b8aa95 !important;
}

.panel--list {
  background: #f7f2e8;
  border: 1px solid #d2c5af;
  padding: 24px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.panel-header h2 {
  margin: 0;
  font-size: 1.3rem;
  color: #2c2c2c;
}

.panel-header p {
  color: #6b5e4a;
  margin: 4px 0 0;
}

.stats-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

@media (min-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.analysis-list-panel {
  border: 1px solid #d6c9b4;
  background: #fff;
  padding: 18px;
  min-height: 360px;
}

.analysis-list-items {
  display: grid;
  gap: 12px;
}

.analysis-item {
  padding: 16px;
  border: 1px solid #d6c9b4;
  background: #fffdf9;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.analysis-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
}

.analysis-item-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.analysis-title {
  font-weight: 700;
  color: #2c2c2c;
}

.analysis-item-details {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 10px;
  color: #6b5e4a;
  font-size: 0.9rem;
}

.status-chip {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.status-success { background: #d4f2da; color: #1f5d30; }
.status-warning { background: #fff4d9; color: #7c5c19; }
.status-danger { background: #f4d8d8; color: #7a2424; }
.status-default { background: #e8e2d7; color: #5a4f44; }

.loading-panel,
.empty-panel {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 220px;
  color: #6b5e4a;
}

.loading-text {
  margin-left: 12px;
}
</style>

